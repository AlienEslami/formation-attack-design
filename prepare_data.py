"""Verify and unpack the data archives supplied with this release."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent

def main():
    hashes = json.loads((ROOT / 'SHA256SUMS.json').read_text())
    names = ['linear_models.zip', 'numerical_records.zip']
    names += sorted(p.name for p in ROOT.glob('nonlinear_trajectories_*.zip'))
    if len(names) < 3:
        raise FileNotFoundError('Download all release data archives before running this script.')
    count = 0
    for name in names:
        path = ROOT / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != hashes[name]:
            raise ValueError(f'Integrity check failed: {name}')
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                destination = (ROOT / entry.filename).resolve()
                if not destination.is_relative_to(ROOT):
                    raise ValueError(f'Invalid archive path: {entry.filename}')
            archive.extractall(ROOT)
            count += len(archive.infolist())
    print(f'Verified {len(names)} archives and unpacked {count} files.')

if __name__ == '__main__':
    main()
