"""Ingest Colab results (results.zip or a folder of CSVs) and produce:
  - benchmark table vs exact Mie (stage A)
  - mesh-convergence table + figure for case A (stage B), orientation ratios (stage B)
  - design maps of Fp, T, eta, collection vs gap x aspect ratio, air/water (stage C)
  - isi/results/summary.md with the numbers that replace the \\TBD markers in the manuscript
usage: python isi/analysis/ingest_colab.py path/to/results.zip   (run from repo root)"""
import sys, os, re, glob, zipfile, json
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'isi/sim')
from mie import radial_dipole
import importlib.util
spec = importlib.util.spec_from_file_location('gp', 'isi/sim/gold_jc.py')

DEST = 'isi/results'; FIG = 'isi/figures'
os.makedirs(DEST, exist_ok=True)
src = sys.argv[1]
if src.endswith('.zip'):
    zipfile.ZipFile(src).extractall(DEST); folder = DEST
else:
    folder = src
P = json.load(open('isi/sim/gold_jc_params.json'))
def eps_fit(lam):
    f = 1000.0 / np.asarray(lam, float)
    return (P['einf'] - P['s0'] * P['f0']**2 / (f**2 + 1j * f * P['g0'])
            + P['s1'] * P['f1']**2 / (P['f1']**2 - f**2 - 1j * f * P['g1'])
            + P['s2'] * P['f2']**2 / (P['f2']**2 - f**2 - 1j * f * P['g2']))
def load(name):
    p = os.path.join(folder, name + '.csv')
    if not os.path.exists(p): return None
    L = open(p).read().splitlines()
    i = next(n for n, l in enumerate(L) if l.lstrip('# ').startswith('lam'))
    hdr = L[i].lstrip('# ').strip().split(',')
    d = np.loadtxt(p, delimiter=',', skiprows=i + 1, ndmin=2)
    return {k: d[:, i] for i, k in enumerate(hdr)}
def peak(o, k):
    i = np.nanargmax(o[k]); return o[k][i], o['lam'][i]

lines = ['# Colab results summary', '']
# ---- Stage A: benchmark
lines += ['## Stage A: gold sphere vs exact Mie (radial dipole, 5 nm gap)', '',
          '| grid (nm) | median abs err Fp | max abs err Fp | Fp peak Meep | Fp peak Mie |', '|---|---|---|---|---|']
for res in [1.0, 2.0, 3.0]:
    o = load(f'bench_sphere_res{res}')
    if o is None: continue
    Fm, Tm = radial_dipole(o['lam'], 15.874, 5.0, eps_fit)
    e = 100 * (o['Fp'] / Fm - 1)
    lines.append(f'| {1/res:.2f} | {np.median(abs(e)):.1f}% | {abs(e).max():.1f}% | {o["Fp"].max():.0f} @ {o["lam"][o["Fp"].argmax()]:.0f} | {Fm.max():.0f} @ {o["lam"][Fm.argmax()]:.0f} |')
# ---- Stage B: convergence of case A
lines += ['', '## Stage B: mesh convergence, rod, axial dipole, 5 nm gap', '',
          '| grid (nm) | Fp max | lambda_Fp | T max | lambda_T | eta at T peak | coll NA0.9 at T peak |', '|---|---|---|---|---|---|---|']
conv = []
fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.3))
for res in [1.0, 1.5, 2.0, 3.0]:
    o = load(f'rodA_z_gap5_res{res}')
    if o is None: continue
    (F, lF), (T, lT) = peak(o, 'Fp'), peak(o, 'T'); j = np.nanargmax(o['T'])
    coll = o.get('coll_NA0.9', np.full_like(o['T'], np.nan))[j]
    conv.append((1 / res, F, lF, T, lT, o['eta'][j], coll))
    lines.append(f'| {1/res:.2f} | {F:.0f} | {lF:.0f} | {T:.1f} | {lT:.0f} | {100*o["eta"][j]:.1f}% | {coll:.2f} |')
    for a, k, s in zip(ax, ['Fp', 'T', 'eta'], [1, 1, 100]): a.plot(o['lam'], s * o[k], label=f'{1/res:.2f} nm')
if conv:
    for a, t in zip(ax, [r'$F_p$', r'$T$', r'$\eta_a$ (%)']): a.set_ylabel(t); a.set_xlabel('Wavelength (nm)')
    ax[0].legend(fontsize=7, title='grid'); fig.tight_layout(); fig.savefig(f'{FIG}/fig_convergence_meep.pdf')
    if len(conv) >= 2:
        a, b = conv[-2], conv[-1]
        lines.append(f'\nChange between the two finest grids: Fp {100*abs(b[1]/a[1]-1):.1f}%, T {100*abs(b[3]/a[3]-1):.1f}%, '
                     f'lambda_T {abs(b[4]-a[4]):.0f} nm.')
plt.close(fig)
# ---- orientation ratios
for res in [2.0, 1.0]:
    A, C = load(f'rodA_z_gap5_res{res}'), load(f'rodC_x_gap5_res{res}')
    Dz, Dx = load(f'bench_sphere_res{res}'), load(f'sphereDp_x_gap5_res{res}')
    if A is not None and C is not None:
        r = A['Fp'] / C['Fp']; rt = A['T'] / C['T']
        lines += ['', f'## Orientation ratios (grid {1/res:.2f} nm)', '',
                  f'- rod Fp_axial/Fp_transverse: max {r.max():.0f} at {A["lam"][r.argmax()]:.0f} nm; min {r.min():.2f}',
                  f'- rod T ratio: max {rt.max():.0f} at {A["lam"][rt.argmax()]:.0f} nm']
        if Dz is not None and Dx is not None:
            rs = Dz['Fp'] / Dx['Fp']
            lines.append(f'- sphere radial/tangential Fp: {rs.min():.2f} to {rs.max():.2f}')
        break
# ---- Stage C: maps
maps = sorted(glob.glob(os.path.join(folder, 'map_*.csv')))
if maps:
    rec = []
    for p in maps:
        m = re.match(r'map_(air|water)_L(\d+)_gap(\d+)_res([\d.]+)\.csv', os.path.basename(p))
        if not m: continue
        o = load(os.path.basename(p)[:-4]); j = np.nanargmax(o['T'])
        rec.append(dict(env=m[1], L=int(m[2]), gap=int(m[3]), lamT=o['lam'][j], Fp=o['Fp'][j], T=o['T'][j],
                        eta=o['eta'][j], coll=o.get('coll_NA0.9', [np.nan] * len(o['T']))[j]))
    json.dump(rec, open(f'{DEST}/maps.json', 'w'), indent=1)
    for env in ['air', 'water']:
        R = [r for r in rec if r['env'] == env]
        if not R: continue
        Ls = sorted({r['L'] for r in R}); Gs = sorted({r['gap'] for r in R})
        fig, ax = plt.subplots(1, 4, figsize=(7.0, 1.9))
        for a, k, t, lg in zip(ax, ['lamT', 'T', 'eta', 'coll'], [r'$\lambda_T$ (nm)', r'$T_{\max}$', r'$\eta_a$', 'NA 0.9 coll.'], [0, 1, 0, 0]):
            Z = np.full((len(Ls), len(Gs)), np.nan)
            for r in R: Z[Ls.index(r['L']), Gs.index(r['gap'])] = r[k]
            im = a.imshow(np.log10(Z) if lg else Z, origin='lower', aspect='auto', cmap='viridis')
            a.set_xticks(range(len(Gs))); a.set_xticklabels(Gs); a.set_yticks(range(len(Ls))); a.set_yticklabels([f'{L/20:g}' for L in Ls])
            a.set_xlabel('gap (nm)'); a.set_title(('log ' if lg else '') + t, fontsize=8); plt.colorbar(im, ax=a)
        ax[0].set_ylabel('aspect ratio'); fig.tight_layout(); fig.savefig(f'{FIG}/fig_maps_{env}.pdf'); plt.close(fig)
    lines += ['', f'## Stage C: {len(rec)} map points processed -> isi/results/maps.json, isi/figures/fig_maps_*.pdf']
open(f'{DEST}/summary.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
