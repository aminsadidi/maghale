"""Publication figures (vector PDF) for the ISI manuscript, built only from raw Lumerical spectra + exact Mie.
Run from repo root:  python isi/analysis/make_figures.py"""
import numpy as np, matplotlib, sys, os
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, 'isi/sim'); from mie import radial_dipole
import re
ROOT = '.'; OUT = 'isi/figures'
RUNS = {'A': 'New folder3/A_baseline', 'B': 'New folder (2)/B_freespace', 'C': 'New folder (2)/C_tip_transverse',
        'D': 'New folder (2)/D_sphere_R15.9', 'Dp': 'New folder3/D_sphere_R15.9_tan', 'G3': 'New folder3/F_gap3',
        'G10': 'New folder3/F_gap10', 'G20': 'New folder3/F_gap20', 'M3': 'New folder3/G_mesh3', 'M1.5': 'New folder3/G_mesh1.5'}
S = {k: np.loadtxt(os.path.join(ROOT, v + '_spectra.txt'), skiprows=1) for k, v in RUNS.items()}
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'lines.linewidth': 1.4,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'figure.dpi': 150})
C1, C2, C3, C4 = '#1f4e9c', '#c0392b', '#2a9d5c', '#8a5a00'
W1, W2 = 3.4, 7.0  # single / double column (inches)
def lab(ax, t): ax.text(0.03, 0.93, t, transform=ax.transAxes, fontweight='bold')
def jc_eps():
    txt = open('isi/sim/jc_au.yml').read()
    d = np.array([list(map(float, l.split())) for l in txt.split('data: |')[1].strip().split('\n') if re.match(r'\s*[\d.]', l)])
    return lambda lam: np.interp(lam / 1000, d[:, 0], d[:, 1]) + 1j * np.interp(lam / 1000, d[:, 0], d[:, 2])
eps = lambda l: jc_eps()(l) ** 2

# Fig 2: Fp, T, eta for A, C, D (+B)
fig, ax = plt.subplots(3, 1, figsize=(W1, 6.2), sharex=True)
for k, c, n in [('A', C1, 'rod, longitudinal'), ('C', C2, 'rod, transverse'), ('D', C3, 'sphere, radial')]:
    l, F, T = S[k][:, 0], S[k][:, 1], S[k][:, 2]
    ax[0].semilogy(l, F, c=c, label=n); ax[1].semilogy(l, T, c=c); ax[2].semilogy(l, 100 * T / F, c=c)
ax[0].semilogy(S['B'][:, 0], S['B'][:, 1], 'k:', lw=1, label='free space')
ax[1].semilogy(S['B'][:, 0], S['B'][:, 2], 'k:', lw=1)
ax[0].set_ylabel(r'$F_p$'); ax[1].set_ylabel(r'$T=P_{\rm rad}/P_0$'); ax[2].set_ylabel(r'$\eta_a$ (%)')
ax[2].set_xlabel('Wavelength (nm)'); ax[0].legend(fontsize=7, loc='upper right')
for a, t in zip(ax, 'abc'): lab(a, f'({t})'); a.axvline(610, c='0.6', lw=0.6, ls='--')
fig.savefig(f'{OUT}/fig_spectra.pdf'); plt.close(fig)

# Fig 3: orientation ratios rod vs equal-volume sphere
fig, ax = plt.subplots(1, 2, figsize=(W2, 2.5))
l = S['A'][:, 0]
for j, (nm, yl) in enumerate([(1, r'$F_p$ ratio'), (2, r'$T$ ratio')]):
    ax[j].semilogy(l, S['A'][:, nm] / S['C'][:, nm], c=C1, label='rod: longitudinal / transverse')
    ax[j].semilogy(l, S['D'][:, nm] / S['Dp'][:, nm], c=C3, label='sphere: radial / tangential')
    ax[j].axhline(2, c='0.5', lw=0.7, ls=':'); ax[j].set_xlabel('Wavelength (nm)'); ax[j].set_ylabel(yl); lab(ax[j], '(%s)' % 'ab'[j])
ax[0].text(880, 2.15, 'quasi-static limit 2', ha='right', fontsize=7, color='0.4')
ax[0].legend(fontsize=7, loc='upper right'); fig.savefig(f'{OUT}/fig_orientation.pdf'); plt.close(fig)

# Fig 4: Mie validation (sphere)
lm = np.arange(500, 901, 2.0); Fm, Tm = radial_dipole(lm, 15.874, 5.0, eps)
fig, ax = plt.subplots(2, 1, figsize=(W1, 4.2), sharex=True)
ax[0].plot(lm, Fm, 'k-', lw=1, label='Mie (exact)'); ax[0].plot(S['D'][:, 0], S['D'][:, 1], c=C3, ls='--', label='FDTD, 2 nm mesh')
ax[1].plot(lm, Tm, 'k-', lw=1); ax[1].plot(S['D'][:, 0], S['D'][:, 2], c=C3, ls='--')
ax[0].set_ylabel(r'$F_p$'); ax[1].set_ylabel(r'$T$'); ax[1].set_xlabel('Wavelength (nm)'); ax[0].legend(fontsize=7)
lab(ax[0], '(a)'); lab(ax[1], '(b)'); fig.savefig(f'{OUT}/fig_mie.pdf'); plt.close(fig)

# Fig 5: gap sweep rod (FDTD) + sphere (Mie)
fig, ax = plt.subplots(2, 3, figsize=(W2, 4.4), sharex=True)
cols = {'G3': ('#5b2a86', '3 nm*'), 'A': (C1, '5 nm'), 'G10': (C3, '10 nm'), 'G20': (C2, '20 nm')}
for k, (c, n) in cols.items():
    l, F, T = S[k][:, 0], S[k][:, 1], S[k][:, 2]
    ax[0, 0].semilogy(l, F, c=c, label=n); ax[0, 1].semilogy(l, T, c=c); ax[0, 2].semilogy(l, 100 * T / F, c=c)
for g, c in zip([3, 5, 10, 20], ['#5b2a86', C1, C3, C2]):
    F, T = radial_dipole(lm, 15.874, g, eps)
    ax[1, 0].semilogy(lm, F, c=c, label=f'{g} nm'); ax[1, 1].semilogy(lm, T, c=c); ax[1, 2].semilogy(lm, 100 * T / F, c=c)
for a, y in zip(ax[:, 0], ['rod (FDTD)', 'sphere (Mie)']): a.set_ylabel(r'$F_p$' + f'\n{y}')
for r in range(2): ax[r, 1].set_ylabel(r'$T$'); ax[r, 2].set_ylabel(r'$\eta_a$ (%)')
for a in ax[1]: a.set_xlabel('Wavelength (nm)')
ax[0, 0].legend(fontsize=6.5, title='gap', title_fontsize=7); ax[1, 0].legend(fontsize=6.5)
for i, a in enumerate(ax.flat): lab(a, '(%s)' % 'abcdef'[i])
fig.savefig(f'{OUT}/fig_gap.pdf'); plt.close(fig)

# Fig 6: mesh sensitivity (Lumerical)
fig, ax = plt.subplots(1, 3, figsize=(W2, 2.3))
for k, c, n in [('M3', C3, r'$\Delta$=3 nm'), ('A', C1, r'$\Delta$=2 nm'), ('M1.5', C2, r'$\Delta$=1.5 nm')]:
    l, F, T = S[k][:, 0], S[k][:, 1], S[k][:, 2]
    ax[0].plot(l, F, c=c, label=n); ax[1].plot(l, T, c=c); ax[2].plot(l, 100 * T / F, c=c)
for a, y, t in zip(ax, [r'$F_p$', r'$T$', r'$\eta_a$ (%)'], 'abc'): a.set_ylabel(y); a.set_xlabel('Wavelength (nm)'); lab(a, f'({t})')
ax[0].legend(fontsize=7); fig.savefig(f'{OUT}/fig_mesh_lumerical.pdf'); plt.close(fig)
print('figures written to', OUT, sorted(os.listdir(OUT)))

# Fig 7: intrinsic quantum yield q0 -> real quantum efficiency at the radiative peak, vs gap
# eta(q0) = T / (Fp + (1 - q0)/q0)   (Bharadwaj & Novotny 2007)
q0 = np.logspace(-2, 0, 200)
fig, ax = plt.subplots(figsize=(W1, 2.6))
rows = []
for k, g, c in [('G3', 3, '#5b2a86'), ('A', 5, C1), ('G10', 10, C3), ('G20', 20, C2)]:
    l, F, T = S[k][:, 0], S[k][:, 1], S[k][:, 2]
    j = T.argmax()
    eta = T[j] / (F[j] + (1 - q0) / q0)
    ax.loglog(q0, eta, c=c, label=f'{g} nm')
    ax.loglog(q0, q0, 'k:', lw=0.8) if k == 'G3' else None
    rows.append((g, l[j], F[j], T[j], *[T[j] / (F[j] + (1 - q) / q) for q in (0.01, 0.1, 0.5, 1.0)]))
ax.set_xlabel(r'intrinsic quantum yield $q_0$'); ax.set_ylabel(r'quantum efficiency $\eta$')
ax.text(0.012, 0.016, 'no antenna', fontsize=7, rotation=33, color='0.3'); ax.legend(fontsize=7, title='gap', title_fontsize=7)
fig.savefig(f'{OUT}/fig_q0.pdf'); plt.close(fig)
np.savetxt(f'{OUT}/q0_table.csv', np.array(rows), delimiter=',', fmt='%.4g',
           header='gap_nm,lambda_T_nm,Fp_at_T,T_max,eta_q0.01,eta_q0.1,eta_q0.5,eta_q1')
print(open(f'{OUT}/q0_table.csv').read())
