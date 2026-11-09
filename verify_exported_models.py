"""Independent full delayed-matrix checks of the exported linear models."""
from pathlib import Path
import json
import numpy as np
try:
    from threadpoolctl import threadpool_limits
except ImportError:
    from contextlib import nullcontext
    def threadpool_limits(**kw):return nullcontext()

def main():
    root=Path(__file__).resolve().parent;records=[]
    for p in sorted((root/'models').glob('*.npz')):
        z=np.load(p);A=z['A'];B=z['B'];C=z['C'];W=z['W'];n=len(W)-1
        values=[]
        for omega in z['frequencies']:
            M=1j*omega*np.eye(len(A))-A
            for tau,Ae in zip(z['delays'],z['delay_matrices']):M-=np.exp(-1j*omega*tau)*Ae
            T=C@np.linalg.solve(M,B)
            gains=[W[i+1].max()*np.linalg.svd(T[:,7*i:7*(i+1)],compute_uv=False)[0] for i in range(n)]
            values.append(max(gains))
        rel=float(np.max(np.abs(np.array(values)-z['reference_single_gain'])/np.maximum(1,z['reference_single_gain'])))
        assert rel<1e-9,(p.name,rel)
        assert np.isclose(values[0],float(z['expected_dc']),rtol=1e-10,atol=1e-10)
        records.append({'model':p.stem,'max_relative_error':rel})
    assert len(records)==117
    print(json.dumps({'passed':True,'model_count':len(records),'frequency_checks':6*len(records),'models':records},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
