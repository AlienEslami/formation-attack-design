"""Publication plots for the additional ECC studies (run after figures.py)."""
from pathlib import Path
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from threadpoolctl import threadpool_limits
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'evidence/additional_studies'
BASE = ROOT / 'evidence/expanded'
FLOOR = 18.21937582946 / 2
FIG = ROOT / 'reproduced_figures'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.titlesize': 8,
                    'axes.labelsize': 8, 'legend.fontsize': 7, 'pdf.fonttype': 42,
                    'axes.spines.top': False, 'axes.spines.right': False})
TEAL, ORANGE, INK, PURPLE, GREY = '#167b83', '#c27332', '#20384d', '#98658a', '#788591'

def export(fig, name):
    fig.savefig(FIG / (name + '.pdf'), bbox_inches='tight', pad_inches=.025)
    fig.savefig(FIG / (name + '.png'), dpi=190, bbox_inches='tight', pad_inches=.025)
    plt.close(fig)

def dynamic():
    fig, (ax, tx) = plt.subplots(1, 2, figsize=(7.05, 2.55), layout='constrained')
    for side, design, color, style, label in [
        ('above', 'constructed', TEAL, '--', 'Upper: equal weights'),
        ('below', 'constructed', ORANGE, '-', 'Lower: equal weights'),
        ('below', 'tuned', INK, '-.', 'Lower: adjusted weights')]:
        data = np.load(BASE / f'echelon_N5_{side}_{design}.npz')
        ax.plot(data['frequencies'], data['curves'].max(axis=1), color=color, ls=style, lw=1.5, label=label)
    revised = np.load(ROOT / 'figure4_revised_curve.npz')
    ax.plot(revised['frequencies'], revised['curve'], color=PURPLE, ls=(0, (4, 1.5, 1, 1.5)), lw=1.5,
            label='Lower: revised links + weights')
    ax.axhline(FLOOR, color=GREY, ls=':', lw=.85)
    ax.text(.80, FLOOR - .3, 'Steady-state bound', color=GREY, fontsize=7, ha='right', va='top')
    ax.set(xlabel='Attack frequency (rad/s)', ylabel='Worst single-link gain',
           xlim=(0, .82), ylim=(0, 16), xticks=[0, .2, .4, .6, .8], yticks=[0, 4, 8, 12, 16],
           title='(a) Linear attack amplification')
    ax.legend(frameon=False, loc='upper right', handlelength=2.5, fontsize=6.6)
    ax.grid(axis='y', alpha=.18)
    rows = json.loads((OUT / 'nonlinear.json').read_text())['cases']
    edges = np.array([(j, i) for i in range(1, 5) for j in range(i)])
    tx.hlines(1.43, 10, 100, color=GREY, lw=.8)
    tx.vlines([10, 100], 1.40, 1.46, color=GREY, lw=.8)
    tx.text(55, 1.48, 'Attack applied (10-100 s)', color=GREY, fontsize=7, ha='center')
    for name, color, style, label in [('constructed', ORANGE, '-', 'Equal weights'),
                                     ('tuned', INK, '-.', 'Adjusted weights'),
                                     ('budget_tuned', PURPLE, '--', 'Revised links + weights')]:
        row = next(r for r in rows if r['design'] == name and r['omega'] > 0)
        data = np.load(OUT / 'nonlinear_cases' / (row['id'] + '.npz'))
        error = np.linalg.norm(data['position'][:, edges[:, 1]] - data['position'][:, edges[:, 0]], axis=2).max(axis=1)
        tx.plot(data['times'], error / row['amplitude_m'], color=color, ls=style, lw=1.4, label=label)
    tx.set(xlabel='Time (s)', ylabel='Max. pairwise position error / $A$',
           title='(b) Nonlinear response in the lower formation', xlim=(0, 190), ylim=(0, 1.64),
           xticks=[0, 50, 100, 150], yticks=[0, .5, 1, 1.5])
    tx.legend(frameon=False, loc='upper right', fontsize=6.8)
    tx.grid(axis='y', alpha=.18)
    export(fig, 'dynamic_validation')

def tradeoffs():
    b = json.loads((OUT / 'budget.json').read_text())
    fig, (ax, gx) = plt.subplots(1, 2, figsize=(7.05, 2.50), layout='constrained')
    for side, color, marker, label in [('above', TEAL, 'o', 'Upper formation $q_+$'),
                                      ('below', ORANGE, 's', 'Lower formation $q_-$')]:
        rows = b['dynamic'][side]
        ax.plot([r['L'] for r in rows], [r['gain'] for r in rows], color=color, marker=marker,
                ms=3.4, lw=1.5, label=label, zorder=4)
    ax.plot([r['L'] for r in b['steady']], [r['lower'] for r in b['steady']], color=INK,
            ls='--', lw=1.1, label='Analytical lower bound', zorder=3)
    ax.set(xlabel='Maximum number of communication links, $L$', ylabel='Worst single-link gain',
           title='(a) Communication budget', xticks=list(range(4, 11)), xlim=(3.8, 10.2),
           yticks=[9, 11, 13, 15, 17], ylim=(8.65, 17.3))
    ax.legend(frameon=False, loc='upper right', fontsize=6.9)
    ax.grid(axis='y', alpha=.18)
    zoom = ax.inset_axes([.18, .52, .32, .31])
    for side, color, marker in [('above', TEAL, 'o'), ('below', ORANGE, 's')]:
        rows = b['dynamic'][side][3:]
        zoom.plot([r['L'] for r in rows], [r['gain'] for r in rows], color=color,
                  marker=marker, ms=2.5, lw=1.05)
    zoom.axhline(FLOOR, color=INK, ls='--', lw=.75)
    zoom.set(xlim=(6.8, 10.2), ylim=(9.09, 9.32), xticks=[7, 10], yticks=[9.1, 9.3])
    zoom.set_title('Near the limit', fontsize=6.5, pad=2)
    zoom.tick_params(labelsize=6, length=2, pad=1)
    rows = [r for r in json.loads((OUT / 'geometry.json').read_text())['records'] if r['side'] == 'below']
    for name, color, marker, style, label in [('constructed', ORANGE, 'o', '-', 'Equal weights'),
                                            ('tuned', INK, 's', '-.', 'Adjusted weights'),
                                            ('leader_predecessor', TEAL, '^', '--', 'Leader--predecessor')]:
        gx.plot([r['lateral_b'] for r in rows],
                [next(d['gain'] for d in r['designs'] if d['name'] == name) for r in rows],
                color=color, marker=marker, ms=3, ls=style, lw=1.5, label=label)
    gx.axhline(FLOOR, color=GREY, ls=':', lw=.85)
    gx.text(1.0295, FLOOR + .12, 'Analytical lower bound', color=GREY, fontsize=7, ha='left', va='bottom')
    gx.set(xlabel='Lateral spacing between neighbours / $b$', ylabel='Worst single-link gain',
           title='(b) Spacing in the lower formation', xlim=(1.029, 1.041), ylim=(8.7, 15),
           xticks=[1.030, 1.035, 1.040], yticks=[9, 11, 13, 15])
    gx.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    gx.legend(frameon=False, loc='upper right', fontsize=6.9)
    gx.grid(axis='y', alpha=.18)
    export(fig, 'budget_geometry')

if __name__ == '__main__':
    with threadpool_limits(limits=1):
        dynamic()
        tradeoffs()
