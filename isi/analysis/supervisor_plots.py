"""Remaining plots requested by the supervisor (from job_trimap and job_tri2 with the G/N/P options):
  fig_maps.png   : |E|^2/|E0|^2 (plane wave, x polarisation) over the dimer and the parallel-R3 trimer, and the partial
                   LDOS (Fp_x) in the gap region -> where to put the emitter (hot spot)
  fig_rho_h.png  : LDOS (Fp_x) and radiative enhancement T_x vs the emitter-tip distance h, for gaps 10-60 nm (1550 nm)
                   and vs wavelength; log scale
  fig_hostn.png  : tuning the resonance with the host index n (dimer L = 270 nm): T spectra and peak wavelength vs n
usage: python isi/analysis/supervisor_plots.py"""
import os, re, glob, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures'); RES = os.path.join(HERE, '..', 'results')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight'})


def load(f):
    return np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1))


def grid(d, key, step):
    xs = np.unique(d['x']); ys = np.unique(d['y'])
    Z = np.full((len(ys), len(xs)), np.nan)
    Z[np.searchsorted(ys, d['y']), np.searchsorted(xs, d['x'])] = d[key]
    return xs, ys, Z


def maps(out):
    cases = [('L270_w1550', 'dimer, 1550 nm'), ('L270_R300_A0_Y160_w1550', 'trimer (R3 parallel), 1550 nm'),
             ('L270_R300_A0_Y160_w1520', 'trimer (R3 parallel), 1520 nm')]
    cases = [c for c in cases if os.path.exists(os.path.join(EX, f'trimap_{c[0]}_field.csv'))]
    if not cases: return
    fig, ax = plt.subplots(2, len(cases), figsize=(3.4 * len(cases), 5.4), squeeze=False,
                           gridspec_kw={'height_ratios': [1.25, 1]})
    out += ['## Field and LDOS maps (z = 0 plane, n = 1.5)', '',
            '| case | max E2/E0^2 (x-pol) | E2 at gap centre | Fp_x at centre | max Fp_x in map (x, y) | min Fp_x in map | Fp_x at (0, +-20) |',
            '|---|---|---|---|---|---|---|']
    for j, (s, lab) in enumerate(cases):
        f = load(os.path.join(EX, f'trimap_{s}_field.csv')); xs, ys, Z = grid(f, 'E2_xpol', 6)
        a = ax[0, j]; im = a.pcolormesh(xs, ys, Z, norm=LogNorm(vmin=1, vmax=np.nanmax(Z)), cmap='inferno', shading='nearest')
        a.set_aspect('equal'); a.set_title(f'({"abc"[j]}) ' + lab, loc='left', fontsize=7.5); a.plot(0, 0, 'c+', ms=7, mew=1.2)
        fig.colorbar(im, ax=a, fraction=0.035, pad=0.02, label=r'$|E|^2/|E_0|^2$'); a.set_xlabel('x (nm)'); a.set_ylabel('y (nm)')
        c0 = f['E2_xpol'][np.argmin(f['x'] ** 2 + f['y'] ** 2)]
        L = load(os.path.join(EX, f'trimap_{s}.csv')); xs, ys, Z = grid(L, 'Fp_x', 2)
        a = ax[1, j]; im = a.pcolormesh(xs, ys, Z, norm=LogNorm(vmin=np.nanmin(Z), vmax=np.nanmax(Z)), cmap='viridis', shading='nearest')
        a.set_aspect('equal'); a.set_title(f'({"def"[j]}) gap region', loc='left', fontsize=7.5); a.plot(0, 0, 'w+', ms=7, mew=1.2)
        fig.colorbar(im, ax=a, fraction=0.05, pad=0.02, label=r'LDOS $F_p$ ($x$ dipole)'); a.set_xlabel('x (nm)'); a.set_ylabel('y (nm)')
        i0 = np.argmin(L['x'] ** 2 + L['y'] ** 2); im_ = np.argmax(L['Fp_x'])
        edge = [L['Fp_x'][np.argmin(L['x'] ** 2 + (L['y'] - s_) ** 2)] for s_ in (20, -20)]
        out.append(f"| {s} | {np.nanmax(f['E2_xpol']):.0f} | {c0:.0f} | {L['Fp_x'][i0]:.0f} | {L['Fp_x'][im_]:.0f} ({L['x'][im_]:g}, {L['y'][im_]:g}) |"
                   f" {L['Fp_x'].min():.0f} | {edge[0]:.0f} / {edge[1]:.0f} |")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_maps.png'), dpi=150)
    out.append('')


def rho_h(out):
    fs = sorted(glob.glob(os.path.join(EX, 'tri2_L270_G*_P_H4_M.csv')), key=lambda f: int(re.search(r'_G(\d+)_', f).group(1)))
    ft = os.path.join(EX, 'tri2_L270_R300_A0_Y160_P_M.csv')
    if not fs: return
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.8))
    out += ['## LDOS vs emitter-tip distance h (x dipole on the dimer axis)', '',
            '| structure | lambda | ' + ' | '.join(f'h = {h}' for h in (3, 5, 10, 20, 30)) + ' |', '|---|---|' + '---|' * 5]
    cols = plt.cm.viridis(np.linspace(0, 0.85, len(fs)))
    for f, c in zip(fs + ([ft] if os.path.exists(ft) else []), list(cols) + ['#c0392b']):
        d = load(f); g = re.search(r'_G(\d+)_', f); lab = f'dimer, gap {g.group(1)} nm' if g else 'trimer (R3 parallel), gap 40'
        hs = sorted({float(n[len('Fp_x_h'):]) for n in d.dtype.names if n.startswith('Fp_x_h')})
        for il, lam in enumerate(d['lambda_nm']):
            Fp = np.array([d[f'Fp_x_h{h:g}'][il] for h in hs]); T = np.array([d[f'T_x_h{h:g}'][il] for h in hs])
            if lam == 1550:
                ax[0].loglog(hs, Fp, 'o-', c=c, ms=3, lw=1, label=lab); ax[1].loglog(hs, T, 'o-', c=c, ms=3, lw=1, label=lab)
                ax[2].semilogx(hs, 100 * T / Fp, 'o-', c=c, ms=3, lw=1, label=lab)
            vals = ' | '.join(f'{np.interp(h, hs, Fp):.0f}' if hs[0] <= h <= hs[-1] else '--' for h in (3, 5, 10, 20, 30))
            out.append(f'| {lab} | {lam:.0f} | {vals} |')
    for a, yl, t in zip(ax, (r'LDOS  $\rho_{xx}/\rho_0 = F_p$', r'radiative enhancement $T$', r'efficiency $T/F_p$ (%)'), 'abc'):
        a.set_xlabel('emitter-tip distance h (nm)'); a.set_ylabel(yl); a.set_title(f'({t}) 1550 nm', loc='left', fontsize=9)
    ax[0].legend(fontsize=6); fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_rho_h.png'), dpi=150)
    out += ['', '(h < 4 nm is below the 4-5 nm mesh resolution: indicative only)', '']


def hostn(out):
    S = {1.5: tri2.series('L270')[0]}
    for f in glob.glob(os.path.join(EX, 'tri2_L270_N*_c1.csv')):
        nn = float(re.search(r'_N([\d.]+)_c1', f).group(1)); d, nc = tri2.series(f'L270_N{nn:g}')
        if d is not None and nc == 6: S[nn] = d
    if len(S) < 2: return
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    out += ['## Tuning with the host index (dimer L = 270 nm, gap 40 nm)', '', '| n | lambda_T | T max | Fp | eta | T(1310) | T(1550) |', '|---|---|---|---|---|---|---|']
    pk = []
    for nn, c in zip(sorted(S), plt.cm.plasma(np.linspace(0, 0.85, len(S)))):
        d = S[nn]; lp, Tm = tri2.peak(d); i = np.argmax(d['T_x_c']); pk.append((nn, lp))
        ax[0].plot(d['lambda_nm'], d['T_x_c'], c=c, lw=1.1, label=f'n = {nn:g}')
        e = lambda k, l: np.interp(l, d['lambda_nm'], d[k])
        out.append(f"| {nn:g} | {lp:.0f} | {Tm:.0f} | {d['Fp_x_c'][i]:.0f} | {100*d['T_x_c'][i]/d['Fp_x_c'][i]:.0f}% | {e('T_x_c',1310):.0f} | {e('T_x_c',1550):.0f} |")
    pk = np.array(pk); cfit = np.polyfit(pk[:, 0], pk[:, 1], 1)
    ax[1].plot(pk[:, 0], pk[:, 1], 'o', c='#1f4e9c'); xx = np.linspace(pk[:, 0].min() - 0.05, pk[:, 0].max() + 0.05, 10)
    ax[1].plot(xx, np.polyval(cfit, xx), 'k-', lw=0.8)
    for le in (1310, 1550): ax[0].axvline(le, c='0.6', lw=0.8, ls=':'); ax[1].axhline(le, c='0.6', lw=0.8, ls=':')
    ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel(r'$T$ (gap centre)'); ax[0].legend(fontsize=6.5); ax[0].set_title('(a)', loc='left', fontsize=9)
    ax[1].set_xlabel('host refractive index n'); ax[1].set_ylabel(r'peak $\lambda_T$ (nm)'); ax[1].set_title('(b)', loc='left', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_hostn.png'), dpi=150)
    out += ['', f'Linear fit: lambda_T = {cfit[0]:.0f} n + {cfit[1]:.0f} nm  ->  n(1310) = {(1310-cfit[1])/cfit[0]:.2f}, n(1550) = {(1550-cfit[1])/cfit[0]:.2f}', '']


if __name__ == '__main__':
    out = ['# Supervisor-requested plots: maps, LDOS vs distance, host-index tuning', '']
    maps(out); rho_h(out); hostn(out)
    open(os.path.join(RES, 'supervisor_plots.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
