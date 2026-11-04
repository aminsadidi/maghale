"""Independent cross-check of the BEM results with 3D FDTD (Ansys Lumerical 2024, lab kit, labkit/lab/lumerical_fdtd.py).
Same geometry in both methods: capsule rods D = 60 nm, R1 = R2 = 285 nm, gap 40 nm, optional R3 = 315 nm along x at y = 160 nm,
host n = 1.5, gold Johnson-Christy, x dipole at the gap centre.
FDTD outputs (41 frequency points, 1300-1700 nm): Fp = dipolepower/sourcepower, T = net power leaving a box around all rods / sourcepower,
eta = T/Fp, f_py / f_my = fraction of the box power through its +y / -y face; waveguide runs (Si3N4 ridge n = 2.0, 600 x 300 nm,
20 nm below the rods, along y): beta_py / beta_my = guided power through y = +-2.5 um divided by the total power emitted by the dipole.
Directionality: BEM gives far-field fractions in 60 deg cones about +-y, FDTD gives near-field box-face fractions; the two ratios are
NOT the same quantity and are compared only qualitatively (same sign and spectral position of the switch).
usage: python isi/analysis/fdtd_vs_bem.py [dir with fdtd_*.csv] [--out DIR]
       default input: the newest isi/data/lab_*/lumerical; output: isi/results (fdtd_vs_bem.md/.json), isi/figures (fig_fdtd_*.png)"""
import argparse, glob, json, os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2, meshconv
HERE = os.path.dirname(os.path.abspath(__file__)); ISI = os.path.join(HERE, '..')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})
WL = (1300.0, 1700.0); L55 = 1550.0
C_F, C_B, C_B2 = '#c0392b', '#1f4e9c', '#7f9cc9'


def load_fdtd(path):
    d = np.atleast_1d(np.genfromtxt(path, delimiter=',', names=True, skip_header=1))
    d = d[np.argsort(d['lambda_nm'])]
    lo, hi = d['lambda_nm'].min(), d['lambda_nm'].max()
    if abs(lo - WL[0]) > 0.02 * WL[0] or abs(hi - WL[1]) > 0.02 * WL[1]:
        raise ValueError(f'{os.path.basename(path)}: spectrum {lo:.0f}-{hi:.0f} nm, expected {WL[0]:.0f}-{WL[1]:.0f} nm (invalid run)')
    if not np.all(np.isfinite(d['Fp'])) or np.any(d['Fp'] <= 0): raise ValueError(f'{os.path.basename(path)}: non-physical Fp')
    return d


def peak(lam, y):
    """maximum refined by a parabola through the 3 highest neighbours (works on a non-uniform grid)"""
    i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        c = np.polyfit(lam[i - 1:i + 2] - lam[i], y[i - 1:i + 2], 2)
        if c[0] < 0:
            x = -c[1] / (2 * c[0]); return lam[i] + x, np.polyval(c, x)
    return lam[i], y[i]


def at(lam, y, l=L55):
    return float(np.interp(l, lam, y))


def figs(lam, Fp, T):
    lT, Tpk = peak(lam, T); lF, Fpk = peak(lam, Fp)
    return {'lT': lT, 'Tpk': Tpk, 'lF': lF, 'Fpk': Fpk, 'Fp': at(lam, Fp), 'T': at(lam, T), 'eta': at(lam, T) / at(lam, Fp),
            'eta_pk': at(lam, T, lT) / at(lam, Fp, lT)}


def bem_refs():
    """BEM spectra for the comparison: {'dimer': {label: (lam, Fp, T)}, 'trimer': {...}, 'trimer_dir': (lam, f+y, f-y)}"""
    R = {'dimer': {}, 'trimer': {}}
    D = meshconv.spectra('D_L285')
    for h in (4.0, 2.0):
        if h in D and D[h][1] == 6: d = D[h][0]; R['dimer'][f'BEM h = {h:g} nm'] = (d['lambda_nm'], d['Fp_x'], d['T_x'])
    t, n = tri2.series('L285_R315_A0_Y160_H4')
    if t is not None and n == 6:
        R['trimer']['BEM h = 4 nm'] = (t['lambda_nm'], t['Fp_x_c'], t['T_x_c'])
        R['trimer_dir'] = (t['lambda_nm'], t['f_py60_x_c'], t['f_my60_x_c'])
    Q = meshconv.spectra('Q_L285_R315_Y160')
    if 2.5 in Q and Q[2.5][1] == 6:
        d = Q[2.5][0]; R['trimer']['BEM h = 2.5 nm (sym.)'] = (d['lambda_nm'], d['Fp_x'], d['T_x'])
    return R


def newest_input():
    c = sorted(glob.glob(os.path.join(ISI, 'data', 'lab_*', 'lumerical')))
    return c[-1] if c else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('inp', nargs='?'); ap.add_argument('--out')
    a = ap.parse_args()
    inp = a.inp or newest_input()
    if not inp or not os.path.isdir(inp): sys.exit('no FDTD folder found (give the folder with fdtd_*.csv)')
    RES = a.out or os.path.join(ISI, 'results'); FIG = a.out or os.path.join(ISI, 'figures'); os.makedirs(RES, exist_ok=True)
    F, bad = {}, []
    for f in sorted(glob.glob(os.path.join(inp, 'fdtd_*.csv'))):
        name = os.path.basename(f)[5:-4]
        if name == 'smoke': continue
        try: F[name] = load_fdtd(f)
        except ValueError as e: bad.append(str(e))
    if bad: print('REJECTED:\n  ' + '\n  '.join(bad))
    if not F: sys.exit('no valid FDTD spectra')
    B = bem_refs(); out = [f'# FDTD (Lumerical) versus BEM (MNPBEM): final telecom design', '', f'FDTD input: `{os.path.relpath(inp, ISI)}`', '']
    if bad: out += ['Rejected FDTD files: ' + '; '.join(bad), '']
    J = {}

    # ---------------- 1. dimer and trimer: FDTD (1 nm gap mesh) vs BEM ----------------
    out += ['## 1. Peak, Purcell factor and efficiency', '',
            '| structure | method | peak of T (nm) | T max | eta at T peak | peak of Fp (nm) | Fp max | Fp(1550) | T(1550) | eta(1550) |',
            '|---|---|---|---|---|---|---|---|---|---|']
    pairs = (('dimer', 'dimer_L285', 'BEM h = 4 nm'), ('trimer', 'trimer_L285_R315', 'BEM h = 4 nm'))
    for st, fn, bref in pairs:
        rows = []
        if fn in F: d = F[fn]; rows.append(('FDTD (gap 1 nm)', figs(d['lambda_nm'], d['Fp'], d['T'])))
        for lab, (lam, Fp, T) in B[st].items():
            sel = (lam >= WL[0] - 1) & (lam <= WL[1] + 1); rows.append((lab, figs(lam[sel], Fp[sel], T[sel])))
        for lab, s in rows:
            out.append(f"| {st} | {lab} | {s['lT']:.0f} | {s['Tpk']:.0f} | {s['eta_pk']:.1%} | {s['lF']:.0f} | {s['Fpk']:.0f} | {s['Fp']:.0f} | {s['T']:.0f} | {s['eta']:.1%} |")
        S = dict(rows)
        if 'FDTD (gap 1 nm)' in S and bref in S:
            f_, b_ = S['FDTD (gap 1 nm)'], S[bref]
            J[st] = {'lT': f_['lT'] - b_['lT'], 'Fp': 100 * (f_['Fp'] / b_['Fp'] - 1), 'T': 100 * (f_['T'] / b_['T'] - 1),
                     'eta': 100 * (f_['eta'] - b_['eta']), 'Tpk': 100 * (f_['Tpk'] / b_['Tpk'] - 1), 'ratio': 'different definition'}
            out.append(f"| {st} | **FDTD - BEM (h = 4)** | **{J[st]['lT']:+.0f} nm** | **{J[st]['Tpk']:+.1f}%** | | | | **{J[st]['Fp']:+.1f}%** | "
                       f"**{J[st]['T']:+.1f}%** | **{J[st]['eta']:+.1f} pp** |")
            fin = [k for k in S if k.startswith('BEM') and k != bref]
            if fin:
                b2 = S[fin[-1]]
                J[st]['vs_finest'] = {'bem': fin[-1], 'lT': f_['lT'] - b2['lT'], 'Fp': 100 * (f_['Fp'] / b2['Fp'] - 1),
                                      'T': 100 * (f_['T'] / b2['T'] - 1), 'eta': 100 * (f_['eta'] - b2['eta']), 'Tpk': 100 * (f_['Tpk'] / b2['Tpk'] - 1)}
                v = J[st]['vs_finest']
                out.append(f"| {st} | FDTD - {fin[-1]} | {v['lT']:+.0f} nm | {v['Tpk']:+.1f}% | | | | {v['Fp']:+.1f}% | {v['T']:+.1f}% | {v['eta']:+.1f} pp |")
    out.append('')

    # ---------------- 2. FDTD mesh convergence (gap override 2, 1, 0.5 nm) ----------------
    conv = [(dx, F[n]) for dx, n in ((2.0, 'dimer_L285_dx2'), (1.0, 'dimer_L285'), (0.5, 'dimer_L285_dx0.5')) if n in F]
    if len(conv) >= 2:
        out += ['## 2. FDTD mesh convergence (dimer, mesh override in the gap; 2 nm on the rods)', '',
                '| gap mesh (nm) | peak of T (nm) | T max | Fp(1550) | T(1550) | eta(1550) |', '|---|---|---|---|---|---|']
        for dx, d in conv:
            s = figs(d['lambda_nm'], d['Fp'], d['T'])
            out.append(f"| {dx:g} | {s['lT']:.0f} | {s['Tpk']:.0f} | {s['Fp']:.0f} | {s['T']:.0f} | {s['eta']:.1%} |")
        s1, s2 = figs(conv[-2][1]['lambda_nm'], conv[-2][1]['Fp'], conv[-2][1]['T']), figs(conv[-1][1]['lambda_nm'], conv[-1][1]['Fp'], conv[-1][1]['T'])
        J['fdtd_mesh'] = {'lT': s2['lT'] - s1['lT'], 'Fp': 100 * (s2['Fp'] / s1['Fp'] - 1), 'T': 100 * (s2['T'] / s1['T'] - 1)}
        out += ['', f"Last refinement ({conv[-2][0]:g} -> {conv[-1][0]:g} nm): peak {J['fdtd_mesh']['lT']:+.1f} nm, Fp(1550) {J['fdtd_mesh']['Fp']:+.1f}%, "
                f"T(1550) {J['fdtd_mesh']['T']:+.1f}%. The rods themselves stay at a 2 nm mesh in all three runs.", '']

    # ---------------- 3. directionality (qualitative) ----------------
    if 'trimer_L285_R315' in F and 'trimer_dir' in B:
        d = F['trimer_L285_R315']; lam = d['lambda_nm']; rF = d['f_py'] / d['f_my']
        lb, fp, fm = B['trimer_dir']; rB = fp / fm
        def switch(l, r):
            k = np.where(np.diff(np.sign(r - 1)))[0]
            return [float(l[i] + (1 - r[i]) * (l[i + 1] - l[i]) / (r[i + 1] - r[i])) for i in k]
        sF, sB = switch(lam, rF), switch(lb, rB); jF, jB = int(np.argmax(rF)), int(np.argmax(rB))
        J['direction'] = {'fdtd_switch_nm': sF, 'bem_switch_nm': sB, 'fdtd_box_ratio_1550': at(lam, d['f_py']) / at(lam, d['f_my']),
                          'bem_cone_ratio_1550': at(lb, fp) / at(lb, fm), 'fdtd_max': [float(rF[jF]), float(lam[jF])], 'bem_max': [float(rB[jB]), float(lb[jB])]}
        out += ['## 3. In-plane directionality (trimer)', '',
                'FDTD: power through the +y / -y faces of the monitor box; BEM: far-field power in 60 deg cones about +y / -y. Different quantities:',
                'only the sign of the asymmetry and the wavelength where it switches are compared.', '',
                '| | +y/-y at 1550 nm | maximum (at nm) | switch from -y to +y (nm) |', '|---|---|---|---|',
                f"| FDTD box faces | {J['direction']['fdtd_box_ratio_1550']:.2f} | {rF[jF]:.2f} ({lam[jF]:.0f}) | {', '.join(f'{x:.0f}' for x in sF) or 'none in 1300-1700'} |",
                f"| BEM 60 deg cones (h = 4) | {J['direction']['bem_cone_ratio_1550']:.2f} | {rB[jB]:.2f} ({lb[jB]:.0f}) | {', '.join(f'{x:.0f}' for x in sB) or 'none'} |", '']

    # ---------------- 4. waveguide coupling ----------------
    wg = [(n, lab) for n, lab in (('wg_dimer_L285', 'dimer'), ('wg_trimer_L285_R315', 'trimer')) if n in F]
    if wg:
        out += ['## 4. Coupling into a Si3N4 waveguide along y (FDTD only)', '',
                'beta = guided power through y = +-2.5 um / total power emitted by the dipole (radiated + absorbed).', '',
                '| structure | beta(+y) 1550 | beta(-y) 1550 | beta(+y)+beta(-y) 1550 | +y/-y 1550 | max +y/-y (nm) | max beta total (nm) | Fp(1550) with / without waveguide |',
                '|---|---|---|---|---|---|---|---|']
        J['waveguide'] = {}
        for n, lab in wg:
            d = F[n]; lam = d['lambda_nm']; bp, bm = d['beta_py'], d['beta_my']; r = bp / bm; j = int(np.argmax(r)); k = int(np.argmax(bp + bm))
            free = F.get('dimer_L285' if lab == 'dimer' else 'trimer_L285_R315')
            fr = f"{at(lam, d['Fp']):.0f} / {at(free['lambda_nm'], free['Fp']):.0f}" if free is not None else 'n/a'
            out.append(f"| {lab} | {at(lam, bp):.3f} | {at(lam, bm):.3f} | {at(lam, bp + bm):.3f} | {at(lam, bp)/at(lam, bm):.2f} | {r[j]:.2f} ({lam[j]:.0f}) | "
                       f"{(bp + bm)[k]:.3f} ({lam[k]:.0f}) | {fr} |")
            J['waveguide'][lab] = {'beta_py_1550': at(lam, bp), 'beta_my_1550': at(lam, bm), 'ratio_1550': at(lam, bp) / at(lam, bm),
                                   'ratio_max': [float(r[j]), float(lam[j])]}
        out += ['', 'The dimer is mirror-symmetric about y = 0, so its +y/-y ratio must be 1: any deviation measures the numerical noise of this quantity.', '']

    open(os.path.join(RES, 'fdtd_vs_bem.md'), 'w').write('\n'.join(out) + '\n')
    json.dump(J, open(os.path.join(RES, 'fdtd_vs_bem.json'), 'w'), indent=1, default=float); print('\n'.join(out))

    # ---------------- figures ----------------
    fig, ax = plt.subplots(2, 3, figsize=(10.2, 5.8))
    for r, (st, fn, _) in enumerate(pairs):
        for lab, (lam, Fp, T) in B[st].items():
            sel = (lam >= 1290) & (lam <= 1710); c = C_B if '= 4' in lab else C_B2
            ax[r, 0].plot(lam[sel], Fp[sel], c=c, lw=1.2, label=lab); ax[r, 1].plot(lam[sel], T[sel], c=c, lw=1.2, label=lab)
            ax[r, 2].plot(lam[sel], 100 * T[sel] / Fp[sel], c=c, lw=1.2, label=lab)
        if fn in F:
            d = F[fn]
            for k, y in enumerate((d['Fp'], d['T'], 100 * d['eta'])): ax[r, k].plot(d['lambda_nm'], y, 'o', c=C_F, ms=2.6, label='FDTD (gap 1 nm)')
        for k, yl in enumerate((r'$F_p$', r'$T$', r'$\eta = T/F_p$ (%)')):
            ax[r, k].set_ylabel(yl); ax[r, k].set_xlabel('wavelength (nm)'); ax[r, k].set_xlim(*WL); ax[r, k].axvline(L55, c='0.6', lw=0.8, ls=':')
            ax[r, k].set_title(f'({"abcdef"[3*r+k]}) {st}', loc='left', fontsize=8)
        ax[r, 2].set_ylim(0, 100); ax[r, 0].legend(fontsize=6.5)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_fdtd_vs_bem.png'), dpi=200); fig.savefig(os.path.join(FIG, 'fig_fdtd_vs_bem.pdf'))

    fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.0))
    for dx, d in conv:
        ax[0].plot(d['lambda_nm'], d['Fp'], lw=1.1, label=f'gap mesh {dx:g} nm')
    if conv: ax[0].set_ylabel(r'$F_p$ (dimer, FDTD)'); ax[0].legend(fontsize=6.5); ax[0].set_title('(a) FDTD mesh convergence', loc='left', fontsize=8)
    if 'direction' in J:
        d = F['trimer_L285_R315']; lb, fp, fm = B['trimer_dir']
        ax[1].plot(d['lambda_nm'], d['f_py'] / d['f_my'], 'o-', c=C_F, ms=2.5, lw=0.8, label='FDTD, box faces')
        ax[1].plot(lb, fp / fm, c=C_B, lw=1.2, label=r'BEM, 60$^\circ$ cones')
        ax[1].axhline(1, c='0.5', lw=0.6); ax[1].set_ylabel('+y / -y'); ax[1].legend(fontsize=6.5); ax[1].set_title('(b) trimer directionality', loc='left', fontsize=8)
    for n, lab in wg:
        d = F[n]; c = C_B if lab == 'trimer' else '0.4'
        ax[2].plot(d['lambda_nm'], 100 * d['beta_py'], c=c, lw=1.2, label=f'{lab} +y'); ax[2].plot(d['lambda_nm'], 100 * d['beta_my'], c=c, lw=1.2, ls='--', label=f'{lab} -y')
    if wg: ax[2].set_ylabel(r'guided fraction $\beta$ (%)'); ax[2].legend(fontsize=6.5); ax[2].set_title('(c) coupling into the Si$_3$N$_4$ waveguide', loc='left', fontsize=8)
    for x in ax: x.set_xlim(*WL); x.set_xlabel('wavelength (nm)'); x.axvline(L55, c='0.6', lw=0.8, ls=':')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_fdtd_extra.png'), dpi=200); fig.savefig(os.path.join(FIG, 'fig_fdtd_extra.pdf'))


if __name__ == '__main__':
    main()
