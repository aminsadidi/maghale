"""Main-text figures from the converged BEM (MNPBEM17) results, same style as make_figures.py.
usage: python isi/analysis/make_figures_bem.py [raw_dir]   (run from repo root; raw_dir = isi/results/bem_raw)"""
import sys, os, re, glob
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'isi/sim'); from mie import radial_dipole, tangential_dipole

RAW = sys.argv[1] if len(sys.argv) > 1 else 'isi/results/bem_raw'
OUT = 'isi/figures'
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'lines.linewidth': 1.4,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'figure.dpi': 150})
C1, C2, C3, C4, C5, C6 = '#1f4e9c', '#c0392b', '#2a9d5c', '#8a5a00', '#7b3fa0', '#5f6b73'
W1, W2 = 3.4, 7.0
def lab(ax, t): ax.text(0.03, 0.93, t, transform=ax.transAxes, fontweight='bold')
_t = open('isi/sim/jc_au.yml').read().split('data: |')[1]
_d = np.array([list(map(float, l.split())) for l in _t.strip().split('\n') if re.match(r'\s*[\d.]', l)])
eps = lambda lam: (np.interp(np.asarray(lam) / 1000, _d[:, 0], _d[:, 1]) + 1j * np.interp(np.asarray(lam) / 1000, _d[:, 0], _d[:, 2]))**2

def load(name):
    p = os.path.join(RAW, name + '.csv')
    L = open(p).read().splitlines(); hdr = L[1].split(',')
    d = np.loadtxt(p, delimiter=',', skiprows=2, ndmin=2); d = d[np.argsort(d[:, 0])]
    return {k: d[:, i] for i, k in enumerate(hdr)}
def finest(prefix):
    hs = sorted(float(re.search(r'_h([\d.]+)_air', f).group(1)) for f in glob.glob(f'{RAW}/{prefix}_h*_air.csv'))
    return hs[0]

hR = finest('rod_L60')
rod = load(f'rod_L60_h{hR:g}_air'); sph = load('sph_n1444_air')
lam = rod['lambda_nm']; R = 15.874
Mz, MTz = radial_dipole(lam, R, 5, eps); Mx, MTx = tangential_dipole(lam, R, 5, eps)

# ---- Fig: spectra (axial / transverse rod, radial sphere)
fig, ax = plt.subplots(3, 1, figsize=(W1, 6.2), sharex=True)
cur = [(rod['Fp_z_g5'], rod['T_z_g5'], C1, 'rod, axial'), (rod['Fp_x_g5'], rod['T_x_g5'], C2, 'rod, transverse'),
       (sph['Fp_z_g5'], sph['T_z_g5'], C3, 'sphere, radial'), (sph['Fp_x_g5'], sph['T_x_g5'], C4, 'sphere, tangential')]
for F, T, c, n in cur:
    ax[0].semilogy(lam, F, c=c, label=n); ax[1].semilogy(lam, T, c=c); ax[2].semilogy(lam, 100 * T / F, c=c)
for a in ax[:2]: a.axhline(1, c='k', ls=':', lw=0.8)
ax[0].set_ylabel(r'$F_p$'); ax[1].set_ylabel(r'$T=P_{\rm rad}/P_0$'); ax[2].set_ylabel(r'$\eta_a$ (%)')
ax[2].set_xlabel('Wavelength (nm)'); ax[0].legend(fontsize=7, loc='upper right')
for a, t in zip(ax, 'abc'): lab(a, f'({t})')
fig.savefig(f'{OUT}/fig_spectra.pdf'); plt.close(fig)

# ---- Fig: orientation ratios
fig, ax = plt.subplots(1, 2, figsize=(W2, 2.5))
for j, (k, yl) in enumerate([('Fp', r'$F_p$ ratio'), ('T', r'$T$ ratio')]):
    ax[j].semilogy(lam, rod[f'{k}_z_g5'] / rod[f'{k}_x_g5'], c=C1, label='rod: axial / transverse')
    ax[j].semilogy(lam, sph[f'{k}_z_g5'] / sph[f'{k}_x_g5'], c=C3, label='sphere: radial / tangential (BEM)')
    ax[j].semilogy(lam, (Mz / Mx) if k == 'Fp' else (MTz / MTx), c=C3, ls='--', lw=1, label='sphere, exact Mie')
    ax[j].axhline(2, c='0.5', ls=':', lw=0.8); ax[j].set_xlabel('Wavelength (nm)'); ax[j].set_ylabel(yl)
    lab(ax[j], f'({"ab"[j]})')
ax[0].text(890, 2.15, 'quasi-static limit 2', ha='right', fontsize=7, color='0.4')
from matplotlib.ticker import ScalarFormatter, NullFormatter
for a, tk in zip(ax, [[2, 5, 10, 20, 50], [2, 5, 10, 20, 50, 100, 200, 500]]):
    a.set_yticks(tk); a.yaxis.set_major_formatter(ScalarFormatter()); a.yaxis.set_minor_formatter(NullFormatter())
ax[0].legend(fontsize=7, loc='center right'); fig.savefig(f'{OUT}/fig_orientation.pdf'); plt.close(fig)

# ---- Fig: validation against Mie (sphere, both orientations, three meshes)
fig, ax = plt.subplots(1, 2, figsize=(W2, 2.5))
for j, (q, Mr, Mt) in enumerate([('Fp', Mz, Mx), ('T', MTz, MTx)]):
    ax[j].semilogy(lam, Mr, c='k', lw=2.4, alpha=0.25, label='exact Mie')
    ax[j].semilogy(lam, Mt, c='k', lw=2.4, alpha=0.25)
    for n, c in [(400, C4), (784, C2), (1444, C1)]:
        s = load(f'sph_n{n}_air')
        ax[j].semilogy(s['lambda_nm'], s[f'{q}_z_g5'], c=c, lw=1, label=f'BEM, {n} vertices')
        ax[j].semilogy(s['lambda_nm'], s[f'{q}_x_g5'], c=c, lw=1, ls='--')
    ax[j].set_xlabel('Wavelength (nm)'); ax[j].set_ylabel([r'$F_p$', r'$T$'][j]); lab(ax[j], f'({"ab"[j]})')
ax[0].legend(fontsize=7, loc='upper right'); ax[1].text(0.97, 0.06, 'solid: radial, dashed: tangential', transform=ax[1].transAxes, ha='right', fontsize=7, color='0.4')
fig.savefig(f'{OUT}/fig_mie.pdf'); plt.close(fig)

# ---- Fig: gap dependence (rod BEM, top; sphere exact Mie, bottom)
fig, ax = plt.subplots(2, 3, figsize=(W2, 4.3), sharex=True)
cols = [C1, C2, C3, C4, C5, C6]
for c, g in zip(cols, [3, 5, 7, 10, 15, 20]):
    F, T = rod[f'Fp_z_g{g}'], rod[f'T_z_g{g}']
    ax[0, 0].semilogy(lam, F, c=c, label=f'{g} nm'); ax[0, 1].semilogy(lam, T, c=c); ax[0, 2].plot(lam, 100 * T / F, c=c)
    F, T = radial_dipole(lam, R, g, eps)
    ax[1, 0].semilogy(lam, F, c=c); ax[1, 1].semilogy(lam, T, c=c); ax[1, 2].plot(lam, 100 * T / F, c=c)
for r, nm in enumerate(['rod, axial (BEM)', 'sphere, radial (Mie)']):
    ax[r, 0].set_ylabel(r'$F_p$'); ax[r, 1].set_ylabel(r'$T$'); ax[r, 2].set_ylabel(r'$\eta_a$ (%)')
    ax[r, 1].set_title(nm, fontsize=8)
for a in ax[1]: a.set_xlabel('Wavelength (nm)')
ax[0, 0].legend(fontsize=6, title='gap', title_fontsize=6)
for a, t in zip(ax.flat, 'abcdef'): lab(a, f'({t})')
fig.tight_layout(); fig.savefig(f'{OUT}/fig_gap.pdf'); plt.close(fig)

# ---- Fig: eta(q0) at the radiative peak, per gap
q0 = np.logspace(-3, 0, 200)
fig, ax = plt.subplots(figsize=(W1, 2.6))
rows = []
for c, g in zip(cols, [3, 5, 7, 10, 15, 20]):
    j = np.argmax(rod[f'T_z_g{g}']); F, T = rod[f'Fp_z_g{g}'][j], rod[f'T_z_g{g}'][j]
    ax.loglog(q0, T / (F + (1 - q0) / q0), c=c, label=f'{g} nm'); rows.append((g, lam[j], F, T))
ax.loglog(q0, q0, 'k:', lw=1); ax.text(0.0016, 0.0024, 'no antenna', fontsize=7, rotation=33, color='0.3')
ax.set_xlabel(r'Intrinsic quantum yield $q_0$'); ax.set_ylabel(r'$\eta(q_0)$ at radiative peak')
ax.legend(fontsize=6, title='gap', title_fontsize=6, ncol=2); fig.savefig(f'{OUT}/fig_q0.pdf'); plt.close(fig)
print('q0 table (gap, lambda_T, Fp, T, eta for q0 = 0.01, 0.1, 0.5, 1):')
for g, l, F, T in rows:
    print(f'{g:>3} {l:.0f} {F:.0f} {T:.1f} ' + ' '.join(f'{T/(F+(1-q)/q):.3f}' for q in (0.01, 0.1, 0.5, 1)))

# ---- Fig: aspect ratio and water (5 nm gap)
fig, ax = plt.subplots(1, 2, figsize=(W2, 2.5))
Ls = sorted(int(re.search(r'rod_L(\d+)_h2_air', f).group(1)) for f in glob.glob(f'{RAW}/rod_L*_h2_air.csv'))
for c, L in zip(cols, Ls):
    d = load(f'rod_L{L}_h2_air'); ax[0].semilogy(d['lambda_nm'], d['T_z_g5'], c=c, label=f'AR {L/20:g}')
w = load('rod_L60_h2_water'); ax[0].semilogy(w['lambda_nm'], w['T_z_g5'], c='k', ls='--', label='AR 3, water')
ax[0].set_xlabel('Wavelength (nm)'); ax[0].set_ylabel(r'$T$ (5 nm gap)'); ax[0].legend(fontsize=6, ncol=2)
for c, g in zip([C1, C3, C2], [5, 10, 20]):
    xs, ys = [], []
    for L in Ls:
        d = load(f'rod_L{L}_h2_air'); j = np.argmax(d[f'T_z_g{g}']); xs.append(d['lambda_nm'][j]); ys.append(100 * d[f'T_z_g{g}'][j] / d[f'Fp_z_g{g}'][j])
    ax[1].plot(xs, ys, 'o-', c=c, ms=3, label=f'air, {g} nm')
    j = np.argmax(w[f'T_z_g{g}']); ax[1].plot(w['lambda_nm'][j], 100 * w[f'T_z_g{g}'][j] / w[f'Fp_z_g{g}'][j], 's', c=c, mfc='none', ms=5)
ax[1].set_xlabel(r'Resonance wavelength $\lambda_T$ (nm)'); ax[1].set_ylabel(r'$\eta_a$ at $\lambda_T$ (%)')
ax[1].legend(fontsize=6); ax[1].text(0.97, 0.06, 'open squares: AR 3 in water', transform=ax[1].transAxes, ha='right', fontsize=7, color='0.4')
for a, t in zip(ax, 'ab'): lab(a, f'({t})')
fig.savefig(f'{OUT}/fig_aspect.pdf'); plt.close(fig)

# ---- SI: BEM mesh convergence of the rod
fig, ax = plt.subplots(1, 3, figsize=(W2, 2.3))
for c, h in zip([C4, C2, C1, C3], sorted({float(re.search(r'_h([\d.]+)_air', f).group(1)) for f in glob.glob(f'{RAW}/rod_L60_h*_air.csv')}, reverse=True)):
    d = load(f'rod_L60_h{h:g}_air')
    ax[0].semilogy(d['lambda_nm'], d['Fp_z_g5'], c=c, label=f'{h:g} nm'); ax[1].semilogy(d['lambda_nm'], d['T_z_g5'], c=c)
    ax[2].plot(d['lambda_nm'], 100 * d['T_z_g5'] / d['Fp_z_g5'], c=c)
for a, t in zip(ax, [r'$F_p$', r'$T$', r'$\eta_a$ (%)']): a.set_ylabel(t); a.set_xlabel('Wavelength (nm)')
ax[0].legend(fontsize=6, title='element size', title_fontsize=6)
fig.tight_layout(); fig.savefig(f'{OUT}/fig_bem_convergence.pdf'); plt.close(fig)
print('figures written; finest rod mesh h =', hR)
