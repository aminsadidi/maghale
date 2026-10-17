"""Sweeps of the gold-nanorod trimer (job_tri2.m, host n = 1.5, D = 60 nm, gap 40 nm):
  (1) dimer arm length L -> resonance tuning to 1310 / 1550 nm,
  (2) length of the third rod R3 on the L = 270 nm dimer -> directionality (+y vs -y) and Purcell,
  (3) mesh convergence (single rod and dimer at 1310, 1480, 1550, 1660 nm).
usage: python isi/analysis/tri2.py -> isi/results/tri2.md, isi/figures/fig_tri2.pdf"""
import os, re, glob
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})


def load(f):
    return np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1))


def series(stem):
    fs = sorted(glob.glob(os.path.join(EX, f'tri2_{stem}_c*.csv')), key=lambda f: int(re.search(r'_c(\d+)\.csv', f).group(1)))
    if not fs: return None, 0
    d = np.concatenate([load(f) for f in fs]); return d[np.argsort(d['lambda_nm'])], len(fs)


def peak(d, key='T_x_c'):
    """parabolic refinement of the maximum of key(lambda)"""
    lam, y = d['lambda_nm'], d[key]; i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]; s = 0.5 * (a - c) / (a - 2 * b + c); return lam[i] + s * (lam[1] - lam[0]), b
    return lam[i], y[i]


def main():
    out = ['# Gold-nanorod trimer sweeps (job_tri2, n = 1.5, D = 60 nm, gap 40 nm)', '',
           '## (1) Dimer arm length (emitter at the gap centre, dipole x)', '',
           '| L (nm) | chunks | lambda_T | T max | Fp | eta | T(1310) | T(1550) | Fp(1550) | eta(1550) | f NA1.3 (1550) |', '|---|---|---|---|---|---|---|---|---|---|---|']
    dim = {}
    for f in sorted(glob.glob(os.path.join(EX, 'tri2_L*_c1.csv'))):
        stem = re.search(r'tri2_(L\d+)_c1', f)
        if not stem: continue
        L = int(stem.group(1)[1:]); d, nc = series(stem.group(1)); dim[L] = d
        lp, Tm = peak(d); i = np.argmax(d['T_x_c']); e = lambda k, l: np.interp(l, d['lambda_nm'], d[k])
        out.append(f"| {L} | {nc}/6 | {lp:.0f} | {Tm:.0f} | {d['Fp_x_c'][i]:.0f} | {100*d['T_x_c'][i]/d['Fp_x_c'][i]:.0f}% | {e('T_x_c',1310):.0f} |"
                   f" {e('T_x_c',1550):.0f} | {e('Fp_x_c',1550):.0f} | {100*e('T_x_c',1550)/e('Fp_x_c',1550):.0f}% | {e('f_zNA13_x_c',1550):.2f} |")
    if len(dim) >= 2:
        Ls = sorted(dim); lp = [peak(dim[L])[0] for L in Ls]; c = np.polyfit(lp, Ls, 1)
        out += ['', f'Linear fit: L(lambda_T) = {c[0]:.4f} lambda_T + {c[1]:.1f} nm  ->  L(1310) = {np.polyval(c,1310):.0f} nm, L(1550) = {np.polyval(c,1550):.0f} nm']
    out += ['', '## (2) Third rod R3 (35 deg, centre (0,160) nm) on the L = 270 nm dimer', '',
            '| L3 (nm) | chunks | lambda_T | T max | eta | T(1550) / dimer | f(+y) / f(-y) at 1550 | max f(+y)/f(-y) (lambda) | f NA1.3 (1550) |',
            '|---|---|---|---|---|---|---|---|---|']
    tri = {}
    for f in sorted(glob.glob(os.path.join(EX, 'tri2_L270_R*_c1.csv'))):
        stem = re.search(r'tri2_(L270_R(\d+)_A35_Y160)_c1', f)
        if not stem: continue
        L3 = int(stem.group(2)); d, nc = series(stem.group(1)); tri[L3] = d
        lp, Tm = peak(d); i = np.argmax(d['T_x_c']); e = lambda k, l: np.interp(l, d['lambda_nm'], d[k])
        r = d['f_py60_x_c'] / d['f_my60_x_c']; j = np.argmax(r)
        ref = np.interp(1550, dim[270]['lambda_nm'], dim[270]['T_x_c']) if 270 in dim else np.nan
        out.append(f"| {L3} | {nc}/6 | {lp:.0f} | {Tm:.0f} | {100*d['T_x_c'][i]/d['Fp_x_c'][i]:.0f}% | {e('T_x_c',1550)/ref:.2f} |"
                   f" {e('f_py60_x_c',1550):.2f} / {e('f_my60_x_c',1550):.2f} | {r[j]:.2f} ({d['lambda_nm'][j]:.0f}) | {e('f_zNA13_x_c',1550):.2f} |")
    out += ['', '## (2b) All R3 geometries on the L = 270 nm dimer (values at 1550 nm; dimer: T = %s)' % (
            f"{np.interp(1550, dim[270]['lambda_nm'], dim[270]['T_x_c']):.0f}" if 270 in dim else '?'), '',
            '| L3 | angle | X3 | Y3 | chunks | T(1550) | Fp(1550) | eta | f(+y) | f(-y) | ratio | best ratio (lambda) | f NA1.3 |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    allg = {}
    for f in sorted(glob.glob(os.path.join(EX, 'tri2_L270_R*_c1.csv'))):
        stem = re.search(r'tri2_(L270_R[^/]*?)_c1\.csv', f).group(1)
        p = {'A': 35, 'X': 0, 'Y': 160}
        for t in stem.split('_')[1:]: p[t[0]] = float(t[1:])
        d, nc = series(stem); allg[stem] = (p, d); e = lambda k: np.interp(1550, d['lambda_nm'], d[k])
        r = d['f_py60_x_c'] / d['f_my60_x_c']; j = np.argmax(r)
        out.append(f"| {p['R']:g} | {p['A']:g} | {p['X']:g} | {p['Y']:g} | {nc}/6 | {e('T_x_c'):.0f} | {e('Fp_x_c'):.0f} | {100*e('T_x_c')/e('Fp_x_c'):.0f}% |"
                   f" {e('f_py60_x_c'):.2f} | {e('f_my60_x_c'):.2f} | {e('f_py60_x_c')/e('f_my60_x_c'):.2f} | {r[j]:.2f} ({d['lambda_nm'][j]:.0f}) | {e('f_zNA13_x_c'):.2f} |")
    out += ['', '## (3) Mesh convergence (Fp / T, emitter at the gap centre or 20 nm from the tip, dipole x)', '',
            '| structure | h (nm) | faces | 1310 | 1480 | 1550 | 1660 |', '|---|---|---|---|---|---|---|']
    mesh = {}
    for f in sorted(glob.glob(os.path.join(EX, 'tri2_*_M.csv'))):
        m = re.search(r'tri2_(S_)?(L\d+(?:_R300_A35_Y160)?)_H([\d.]+)_M', f)
        if not m: continue
        st = ('single ' if m.group(1) else '') + m.group(2); h = float(m.group(3)); d = load(f)
        faces = re.search(r'faces=(\d+)', open(f).readline()).group(1)
        mesh.setdefault(st, {})[h] = d
        out.append(f'| {st} | {h:g} | {faces} | ' + ' | '.join(f"{a:.1f} / {b:.1f}" for a, b in zip(d['Fp_x_c'], d['T_x_c'])) + ' |')
    for st, M in mesh.items():
        if len(M) < 2: continue
        hs = sorted(M); fine = M[hs[0]]
        out.append(f'\n{st}: max deviation from the finest mesh (h = {hs[0]:g}) in Fp: ' +
                   ', '.join(f'h={h:g}: {100*np.max(np.abs(M[h]["Fp_x_c"]/fine["Fp_x_c"]-1)):.1f}%' for h in hs[1:]))
    open(os.path.join(RES, 'tri2.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
    if not dim and not tri: return

    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.7))
    cm = plt.cm.viridis
    for k, L in enumerate(sorted(dim)):
        d = dim[L]; ax[0].plot(d['lambda_nm'], d['T_x_c'], c=cm(k / max(1, len(dim) - 1)), lw=1.1, label=f'L = {L} nm')
    for le in (1310, 1550): ax[0].axvline(le, c='0.6', lw=0.8, ls=':')
    ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel(r'$T$ (gap centre, $x$ dipole)'); ax[0].legend(fontsize=6); ax[0].set_title('(a) dimer', loc='left', fontsize=9)
    for k, L3 in enumerate(sorted(tri)):
        d = tri[L3]; c = plt.cm.plasma(k / max(1, len(tri) - 1) * 0.8)
        ax[1].plot(d['lambda_nm'], d['T_x_c'], c=c, lw=1.1, label=f'L3 = {L3} nm')
        ax[2].plot(d['lambda_nm'], d['f_py60_x_c'] / d['f_my60_x_c'], c=c, lw=1.1, label=f'L3 = {L3} nm')
    if 270 in dim:
        ax[1].plot(dim[270]['lambda_nm'], dim[270]['T_x_c'], c='k', lw=0.9, ls='--', label='dimer L = 270')
        ax[2].plot(dim[270]['lambda_nm'], dim[270]['f_py60_x_c'] / dim[270]['f_my60_x_c'], c='k', lw=0.9, ls='--', label='dimer')
    for a in ax[1:]:
        for le in (1310, 1550): a.axvline(le, c='0.6', lw=0.8, ls=':')
        a.set_xlabel('wavelength (nm)'); a.legend(fontsize=6)
    ax[1].set_ylabel(r'$T$'); ax[1].set_title('(b) trimer, L = 270 nm', loc='left', fontsize=9)
    ax[2].set_ylabel(r'$f(+y)/f(-y)$ (60$^\circ$ cones)'); ax[2].set_title('(c) directionality', loc='left', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_tri2.pdf')); fig.savefig(os.path.join(FIG, 'fig_tri2.png'), dpi=130)


if __name__ == '__main__':
    main()


def figure_tradeoff():
    """directionality vs radiative enhancement for all R3 geometries on the L = 270 nm dimer -> fig_tri3"""
    dim, _ = series('L270'); T0 = np.interp(1550, dim['lambda_nm'], dim['T_x_c'])
    G = {}
    for f in sorted(glob.glob(os.path.join(EX, 'tri2_L270_R*_c1.csv'))):
        stem = re.search(r'tri2_(L270_R[^/]*?)_c1\.csv', f).group(1)
        p = {'A': 35, 'X': 0, 'Y': 160}
        for t in stem.split('_')[1:]: p[t[0]] = float(t[1:])
        G[stem] = (p, series(stem)[0])
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.8))
    for A, c in ((0, '#c0392b'), (20, '#e67e22'), (27, '#2a9d5c'), (35, '#1f4e9c')):
        k = f'L270_R300_A{A}_Y160'
        if k in G:
            d = G[k][1]; ax[0].plot(d['lambda_nm'], d['f_py60_x_c'] / d['f_my60_x_c'], c=c, lw=1.1, label=rf'$\theta_3$ = {A}$^\circ$')
            ax[1].plot(d['lambda_nm'], d['T_x_c'], c=c, lw=1.1, label=rf'$\theta_3$ = {A}$^\circ$')
    ax[0].plot(dim['lambda_nm'], dim['f_py60_x_c'] / dim['f_my60_x_c'], 'k--', lw=0.9, label='dimer')
    ax[1].plot(dim['lambda_nm'], dim['T_x_c'], 'k--', lw=0.9, label='dimer')
    for a in ax[:2]:
        for le in (1310, 1550): a.axvline(le, c='0.6', lw=0.8, ls=':')
        a.set_xlabel('wavelength (nm)'); a.legend(fontsize=6)
    ax[0].set_ylabel(r'$f(+y)/f(-y)$'); ax[0].set_title(r'(a) $L_3$ = 300 nm, $Y_3$ = 160 nm', loc='left', fontsize=9)
    ax[1].set_ylabel(r'$T$ (gap centre, $x$ dipole)'); ax[1].set_title('(b)', loc='left', fontsize=9)
    a = ax[2]
    for k, (p, d) in G.items():
        r = np.interp(1550, d['lambda_nm'], d['f_py60_x_c'] / d['f_my60_x_c']); t = np.interp(1550, d['lambda_nm'], d['T_x_c']) / T0
        a.plot(t, r, 'o', ms=4, c=plt.cm.viridis(p['A'] / 70))
        a.annotate(f"{p['R']:g}/{p['A']:g}°/{p['Y']:g}" + (f"/x{p['X']:+g}" if p['X'] else ''), (t, r), fontsize=5, xytext=(3, 2), textcoords='offset points')
    a.plot(1, 1, 'ks', ms=5); a.annotate('dimer', (1, 1), fontsize=6, xytext=(3, 2), textcoords='offset points')
    a.set_xlabel(r'$T$(1550) / $T_{\rm dimer}$(1550)'); a.set_ylabel(r'$f(+y)/f(-y)$ at 1550 nm')
    a.set_title(r'(c) all geometries ($L_3$/$\theta_3$/$Y_3$)', loc='left', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_tri3.pdf')); fig.savefig(os.path.join(FIG, 'fig_tri3.png'), dpi=150)


if __name__ == '__main__':
    figure_tradeoff()
