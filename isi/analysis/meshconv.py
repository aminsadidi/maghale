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


if __name__ == '__main__':
    main()
