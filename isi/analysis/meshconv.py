"""Wide-range mesh convergence (job_meshsym, mirror symmetry) of Fp and T at the gap centre for the final 1550 nm design:
dimer L = 285 nm (h = 8 ... 3 nm, symmetry 'xy') and trimer L = 285 nm + horizontal R3 = 315 nm (h = 8 ... 4 nm,
symmetry 'x'). Validation against the full (non-symmetric) runs at h = 5 nm. Richardson extrapolation in h^2.
usage: python isi/analysis/meshconv.py -> isi/results/meshconv.md, isi/figures/fig_meshconv.png"""
import os, re, glob, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})


def load(f):
    return np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1))


def series(prefix):
    S = {}
    for f in glob.glob(os.path.join(EX, f'meshsym_{prefix}_H*.csv')):
        S[float(re.search(r'_H([\d.]+)\.csv', f).group(1))] = load(f)
    return dict(sorted(S.items(), reverse=True))


def main():
    cases = [('D_L285', 'dimer (L = 285 nm)', 'tri2_L285_M.csv', None),
             ('T_L285_R315_Y160', 'trimer (L = 285, R3 = 315 nm, horizontal)', None, 'L285_R315_A0_Y160')]
    out = ['# Wide-range mesh convergence (mirror symmetry), emitter at the gap centre, x dipole, n = 1.5', '']
    fig, ax = plt.subplots(2, 2, figsize=(7.6, 5.6))
    for r, (pre, lab, ref_m, ref_c) in enumerate(cases):
        S = series(pre)
        if not S: continue
        hs = np.array(list(S)); lam = S[hs[0]]['lambda_nm']
        out += [f'## {lab}', '', '| h (nm) | faces (meshed / full) | ' + ' | '.join(f'Fp {l:.0f} / T {l:.0f}' for l in lam) + ' |',
                '|---|---|' + '---|' * len(lam)]
        for h, d in S.items():
            out.append(f"| {h:g} | {int(d['faces_meshed'][0])} / {int(d['faces_full'][0])} | " +
                       ' | '.join(f'{a:.1f} / {b:.1f}' for a, b in zip(d['Fp_x'], d['T_x'])) + ' |')
        Fp = np.array([S[h]['Fp_x'] for h in hs]); T = np.array([S[h]['T_x'] for h in hs])
        fine = hs <= 5
        ext = [np.polyfit(hs[fine] ** 2, Fp[fine, j], 1)[1] if fine.sum() >= 2 else np.nan for j in range(len(lam))]
        out += ['', 'Richardson (h^2 -> 0, from h <= 5 nm): ' + ', '.join(f'Fp({l:.0f}) = {e:.1f}' for l, e in zip(lam, ext)),
                'Deviation of each mesh from the extrapolated value (Fp): ' +
                '; '.join(f'h={h:g}: ' + '/'.join(f'{100*(Fp[i,j]/ext[j]-1):+.1f}%' for j in range(len(lam))) for i, h in enumerate(hs))]
        # validation against full (non-symmetric) h = 5 runs
        if ref_m and os.path.exists(os.path.join(EX, ref_m)):
            d = load(os.path.join(EX, ref_m)); v = np.interp(lam, d['lambda_nm'], d['Fp_x_c'])
            if 5.0 in S: out.append('Full (no symmetry) h = 5 nm: ' + ', '.join(f'{a:.1f} (sym {b:.1f})' for a, b in zip(v, S[5.0]['Fp_x'])))
        if ref_c:
            d, nc = tri2.series(ref_c)
            if d is not None and 5.0 in S:
                v = np.interp(lam, d['lambda_nm'], d['Fp_x_c'])
                out.append('Full (no symmetry) h = 5 nm, interpolated: ' + ', '.join(f'{a:.1f} (sym {b:.1f})' for a, b in zip(v, S[5.0]['Fp_x'])))
        out.append('')
        cols = plt.cm.viridis(np.linspace(0, 0.85, len(lam)))
        for j, (l, c) in enumerate(zip(lam, cols)):
            ax[r, 0].plot(hs, Fp[:, j], 'o-', c=c, ms=4, label=f'{l:.0f} nm')
            if np.isfinite(ext[j]): ax[r, 0].plot(0, ext[j], '*', c=c, ms=8)
            ax[r, 1].plot(hs, 100 * T[:, j] / Fp[:, j], 'o-', c=c, ms=4, label=f'{l:.0f} nm')
        ax[r, 0].set_ylabel(r'$F_p$ (gap centre)'); ax[r, 1].set_ylabel(r'efficiency $T/F_p$ (%)')
        ax[r, 0].set_title(f'({"ac"[r]}) {lab}', loc='left', fontsize=8); ax[r, 1].set_title(f'({"bd"[r]})', loc='left', fontsize=8)
        for a in ax[r]: a.set_xlabel('element size h (nm)'); a.set_xlim(-0.3, 8.5)
        ax[r, 0].legend(fontsize=6.5, ncol=2)
    fig.text(0.01, 0.005, 'stars at h = 0: Richardson extrapolation in h$^2$ from h $\\leq$ 5 nm', fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_meshconv.png'), dpi=150)
    open(os.path.join(RES, 'meshconv.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__' and len(sys.argv) == 1:
    main()


def spectra(prefix):
    """merge the chunked spectra meshsym_<prefix>_H<h>_c<k>.csv -> {h: array}"""
    S = {}
    for f in glob.glob(os.path.join(EX, f'meshsym_{prefix}_H*_c*.csv')):
        h = float(re.search(r'_H([\d.]+)_c\d+\.csv', f).group(1)); S.setdefault(h, []).append(load(f))
    out = {}
    for h, L in S.items():
        d = np.concatenate(L); out[h] = (d[np.argsort(d['lambda_nm'])], len(L))
    return dict(sorted(out.items(), reverse=True))


def peak(lam, y):
    i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]; s = 0.5 * (a - c) / (a - 2 * b + c)
        return lam[i] + s * (lam[1] - lam[0]), b - 0.25 * (a - c) * s
    return lam[i], y[i]


def spectral():
    cases = [('D_L285', 'dimer (L = 285 nm)'), ('T_L285_R315_Y160', 'trimer (L = 285, R3 = 315 nm horizontal)')]
    out = ['# Mesh convergence of the full spectra (1300-1700 nm, mirror symmetry), gap centre, x dipole', '']
    fig, ax = plt.subplots(2, 3, figsize=(10, 5.6))
    for r, (pre, lab) in enumerate(cases):
        S = {h: v for h, v in spectra(pre).items() if v[1] == 6}
        if pre.startswith('T_'):                             # add the quarter-symmetric (rotated) trimer levels
            for h, v in spectra('Q' + pre[1:]).items():
                if v[1] == 6 and h not in S: S[h] = v
            S = dict(sorted(S.items(), reverse=True))
        if len(S) < 2: continue
        out += [f'## {lab}', '', '| h (nm) | faces (full) | peak lambda (nm) | peak Fp | T at peak | eta at peak | Fp(1550) | T(1550) |', '|---|---|---|---|---|---|---|---|']
        rows = []
        cols = plt.cm.viridis(np.linspace(0, 0.85, len(S)))
        for (h, (d, _)), c in zip(S.items(), cols):
            lam = d['lambda_nm']; lp, Fpk = peak(lam, d['Fp_x']); Tp = np.interp(lp, lam, d['T_x'])
            F55, T55 = np.interp(1550, lam, d['Fp_x']), np.interp(1550, lam, d['T_x'])
            rows.append((h, lp, Fpk, Tp, F55, T55))
            out.append(f"| {h:g} | {int(d['faces_full'][0])} | {lp:.1f} | {Fpk:.1f} | {Tp:.1f} | {100*Tp/Fpk:.1f}% | {F55:.1f} | {T55:.1f} |")
            ax[r, 0].plot(lam, d['Fp_x'], c=c, lw=1.1, label=f'h = {h:g} nm')
        R = np.array(rows); fine = R[:, 0] <= 5
        fits = {k: np.polyfit(R[fine, 0] ** 2, R[fine, k], 1) for k in (1, 2, 4)}
        out += ['', 'Richardson (h^2 -> 0, h <= 5 nm): peak lambda = %.1f nm, peak Fp = %.1f, Fp(1550) = %.1f' % (fits[1][1], fits[2][1], fits[4][1]),
                'Change from the finest computed mesh to the extrapolated limit: peak lambda %+.1f nm, peak Fp %+.1f%%, Fp(1550) %+.1f%%' % (
                    fits[1][1] - R[-1, 1], 100 * (fits[2][1] / R[-1, 2] - 1), 100 * (fits[4][1] / R[-1, 4] - 1)), '']
        x = np.linspace(0, R[:, 0].max() ** 2, 50)
        for k, a, yl in ((1, ax[r, 1], 'peak wavelength (nm)'), (2, ax[r, 2], r'peak $F_p$')):
            a.plot(R[:, 0] ** 2, R[:, k], 'o', c='#1f4e9c'); a.plot(x, np.polyval(fits[k], x), 'k--', lw=0.8)
            a.plot(0, fits[k][1], '*', c='#c0392b', ms=9); a.set_xlabel(r'$h^2$ (nm$^2$)'); a.set_ylabel(yl)
            a2 = a.secondary_xaxis('top', functions=(lambda v: np.sqrt(np.maximum(v, 0)), lambda v: v ** 2)); a2.set_xlabel('h (nm)', fontsize=7)
        ax[r, 0].axvline(1550, c='0.6', lw=0.8, ls=':'); ax[r, 0].set_xlabel('wavelength (nm)'); ax[r, 0].set_ylabel(r'$F_p$ (gap centre)')
        ax[r, 0].legend(fontsize=6); ax[r, 0].set_title(f'({"ad"[r]}) {lab}', loc='left', fontsize=8)
        ax[r, 1].set_title(f'({"be"[r]})', loc='left', fontsize=8); ax[r, 2].set_title(f'({"cf"[r]})', loc='left', fontsize=8)
    fig.text(0.01, 0.005, r'red stars: Richardson extrapolation (h$^2$ $\to$ 0) from h $\leq$ 5 nm', fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_meshconv.png'), dpi=150)
    open(os.path.join(RES, 'meshconv_spectra.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'spectra':
    spectral()
