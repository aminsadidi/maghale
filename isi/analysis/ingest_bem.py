"""Ingest MNPBEM results (results_bem_full.zip or folder of CSVs from isi/bem/run_mnpbem.m) and produce:
  - sphere validation vs exact Mie (radial = z, tangential = x), Johnson-Christy table (same data as MNPBEM gold.dat)
  - mesh convergence of the rod (L = 60 nm) and the extrapolated Fp, T
  - orientation ratios, gap dependence, aspect-ratio sweep, water
  -> isi/results/bem/summary.md, isi/figures/fig_bem_*.pdf
usage: python isi/analysis/ingest_bem.py path/to/results_bem_full.zip   (run from repo root)"""
import sys, os, re, glob, zipfile
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'isi/sim')
from mie import radial_dipole, tangential_dipole

DEST = 'isi/results/bem'; FIG = 'isi/figures'
os.makedirs(DEST, exist_ok=True)
src = sys.argv[1]
if src.endswith('.zip'):
    with zipfile.ZipFile(src) as z:
        for n in z.namelist():
            if n.endswith('.csv') or n.endswith('.txt'):
                open(os.path.join(DEST, os.path.basename(n)), 'wb').write(z.read(n))
    folder = DEST
else:
    folder = src

# Johnson-Christy table (refractiveindex.info), linear interpolation of n, k
_t = open('isi/sim/jc_au.yml').read().split('data: |')[1]
_d = np.array([list(map(float, l.split())) for l in _t.strip().split('\n') if re.match(r'\s*[\d.]', l)])
def eps_jc_table(lam_nm):
    l = np.asarray(lam_nm, float) / 1000
    return (np.interp(l, _d[:, 0], _d[:, 1]) + 1j * np.interp(l, _d[:, 0], _d[:, 2]))**2

def load(name):
    p = os.path.join(folder, name + '.csv')
    if not os.path.exists(p): return None
    L = open(p).read().splitlines()
    meta = L[0].lstrip('# ')
    hdr = L[1].split(',')
    d = np.loadtxt(p, delimiter=',', skiprows=2, ndmin=2)
    d = d[np.argsort(d[:, 0])]
    o = {k: d[:, i] for i, k in enumerate(hdr)}
    o['meta'] = meta
    o['gaps'] = sorted({float(m[1]) for k in hdr for m in [re.match(r'Fp_z_g([\d.]+)$', k)] if m})
    return o

def g(o, q, gap):
    return o[f'{q}_g{gap:g}']

lines = ['# MNPBEM (BEM) results', '']
# ---------------- sphere vs Mie
lines += ['## Gold sphere (R = 15.874 nm) vs exact Mie, Johnson-Christy', '',
          '| case | gap | median abs err Fp_z | max | median abs err T_z | median abs err Fp_x | median abs err T_x | Fp_z peak BEM / Mie |',
          '|---|---|---|---|---|---|---|---|']
for f in sorted(glob.glob(os.path.join(folder, 'sph_n*_*.csv'))):
    name = os.path.basename(f)[:-4]; o = load(name)
    nh = 1.33 if 'water' in name else 1.0
    for gap in o['gaps']:
        Fz, Tz = radial_dipole(o['lambda_nm'], 15.874, gap, eps_jc_table, n_host=nh)
        Fx, Tx = tangential_dipole(o['lambda_nm'], 15.874, gap, eps_jc_table, n_host=nh)
        e = lambda a, b: 100 * np.abs(a / b - 1)
        ez = e(g(o, 'Fp_z', gap), Fz)
        lines.append(f'| {name} | {gap:g} | {np.median(ez):.2f}% | {ez.max():.2f}% | {np.median(e(g(o, "T_z", gap), Tz)):.2f}% | '
                     f'{np.median(e(g(o, "Fp_x", gap), Fx)):.2f}% | {np.median(e(g(o, "T_x", gap), Tx)):.2f}% | '
                     f'{g(o, "Fp_z", gap).max():.0f} / {Fz.max():.0f} |')

# ---------------- rod mesh convergence
def peaks(o, gap):
    Fz, Tz = g(o, 'Fp_z', gap), g(o, 'T_z', gap); i, j = Fz.argmax(), Tz.argmax()
    return Fz[i], o['lambda_nm'][i], Tz[j], o['lambda_nm'][j], Tz[j] / Fz[j]
rods = {}
for f in glob.glob(os.path.join(folder, 'rod_L60_h*_air.csv')):
    h = float(re.search(r'_h([\d.]+)_air', f).group(1)); rods[h] = load(os.path.basename(f)[:-4])
H = sorted(rods, reverse=True)
if H:
    lines += ['', '## Rod L = 60 nm, axial dipole, mesh convergence (element size h)', '',
              '| h (nm) | gap | Fp max | lambda_Fp | T max | lambda_T | eta at T peak |', '|---|---|---|---|---|---|---|']
    for gap in rods[H[0]]['gaps']:
        for h in H:
            F, lF, T, lT, eta = peaks(rods[h], gap)
            lines.append(f'| {h:g} | {gap:g} | {F:.0f} | {lF:.0f} | {T:.1f} | {lT:.0f} | {100*eta:.1f}% |')
    if len(H) >= 2:
        a, b = rods[H[-2]], rods[H[-1]]
        lines += ['', 'Change between the two finest meshes (5 nm gap): ' +
                  ', '.join(f'{q} {100*abs(peaks(b, 5)[k]/peaks(a, 5)[k]-1):.1f}%' for q, k in [('Fp', 0), ('T', 2), ('eta', 4)])]
    fin = rods[H[-1]]; lam = fin['lambda_nm']
    lines += ['', f'## Finest rod mesh (h = {H[-1]:g} nm): orientation ratios and gap dependence', '']
    for gap in fin['gaps']:
        r = g(fin, 'Fp_z', gap) / g(fin, 'Fp_x', gap); rt = g(fin, 'T_z', gap) / g(fin, 'T_x', gap)
        F, lF, T, lT, eta = peaks(fin, gap)
        lines.append(f'- gap {gap:g} nm: Fp_z max {F:.0f} @ {lF:.0f} nm, T_z max {T:.1f} @ {lT:.0f} nm, eta(q0=1) {100*eta:.1f}%; '
                     f'Fp ratio z/x max {r.max():.0f} @ {lam[r.argmax()]:.0f} nm; T ratio max {rt.max():.0f}')
    i610 = np.abs(lam - 610).argmin()
    for gap in fin['gaps']:
        Fz, Fx, Tz, Tx = (g(fin, q, gap)[i610] for q in ('Fp_z', 'Fp_x', 'T_z', 'T_x'))
        Fa, Ta = (Fz + 2 * Fx) / 3, (Tz + 2 * Tx) / 3
        if gap == 5: lines.append(f'- orientation average at {lam[i610]:.0f} nm, 5 nm gap: <Fp> {Fa:.0f}, <T> {Ta:.1f}, <eta> {100*Ta/Fa:.1f}%')
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.3))
    for h in H:
        o = rods[h]
        for a, k in zip(ax, ['Fp_z', 'T_z']): a.plot(o['lambda_nm'], g(o, k, 5), label=f'{h:g} nm')
        ax[2].plot(o['lambda_nm'], 100 * g(o, 'T_z', 5) / g(o, 'Fp_z', 5))
    for a, t in zip(ax, [r'$F_p$', r'$T$', r'$\eta_a$ (%)']): a.set_ylabel(t); a.set_xlabel('Wavelength (nm)')
    ax[0].legend(fontsize=7, title='BEM mesh'); fig.tight_layout(); fig.savefig(f'{FIG}/fig_bem_convergence.pdf'); plt.close(fig)

# ---------------- aspect ratio + water
asp = sorted(glob.glob(os.path.join(folder, 'rod_L*_h2_*.csv')))
if asp:
    lines += ['', '## Aspect-ratio sweep (h = 2 nm) and water', '', '| case | gap | lambda_T | T max | Fp at T peak | eta |', '|---|---|---|---|---|---|']
    for f in asp:
        name = os.path.basename(f)[:-4]; o = load(name)
        for gap in o['gaps']:
            Tz = g(o, 'T_z', gap); j = Tz.argmax(); Fz = g(o, 'Fp_z', gap)[j]
            lines.append(f'| {name} | {gap:g} | {o["lambda_nm"][j]:.0f} | {Tz[j]:.1f} | {Fz:.0f} | {100*Tz[j]/Fz:.1f}% |')
open(f'{DEST}/summary.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
