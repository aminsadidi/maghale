"""Final telecom design (gold-nanorod trimer: R1, R2 = 285 nm, gap 40 nm, horizontal R3 = 315 nm at y = 160 nm, D = 60 nm,
host n = 1.5), BEM (MNPBEM, job_tri2) at the 4 nm mesh (R3: 5.6 nm), compared with the earlier 5 nm run and the dimer.
Quantities (x dipole at the gap centre unless stated):
  Fp = total decay rate / rate in the host, T = radiative rate / rate in the host, eta = T/Fp (antenna efficiency),
  f(+y), f(-y) = fraction of the radiated power inside a 60 deg half-angle cone about +y / -y (in-plane directionality),
  f(NA) = fraction collected by an objective of numerical aperture NA along +z (NA 1.3 oil, NA 0.9 air-like).
usage: python isi/analysis/final_design.py -> isi/results/final_design.md, isi/figures/fig_final_design.png"""
import os, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2, meshconv
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})
FINAL, OLD = 'L285_R315_A0_Y160_H4', 'L285_R315_A0_Y160'
C_TRI, C_OLD, C_DIM = '#1f4e9c', '#7f9cc9', '0.35'


def at(d, k, l):
    return float(np.interp(l, d['lambda_nm'], d[k]))


def peak(lam, y):
    return meshconv.peak(lam, y)


def dimer(h=4.0):
    """dimer L = 285 nm, full spectrum from the mirror-symmetric mesh study (x dipole at the gap centre)"""
    S = meshconv.spectra('D_L285')
    return S[h][0] if h in S and S[h][1] == 6 else None


def summary(d, tag):
    lam = d['lambda_nm']; R = d['f_py60_x_c'] / d['f_my60_x_c']; j = int(np.argmax(R))
    lF, Fpk = peak(lam, d['Fp_x_c']); lT, Tpk = peak(lam, d['T_x_c'])
    return {'tag': tag, 'lF': lF, 'Fpk': Fpk, 'lT': lT, 'Tpk': Tpk, 'eta_pk': at(d, 'T_x_c', lT) / at(d, 'Fp_x_c', lT),
            'Fp': at(d, 'Fp_x_c', 1550), 'T': at(d, 'T_x_c', 1550), 'eta': at(d, 'T_x_c', 1550) / at(d, 'Fp_x_c', 1550),
            'fp': at(d, 'f_py60_x_c', 1550), 'fm': at(d, 'f_my60_x_c', 1550), 'ratio': at(d, 'f_py60_x_c', 1550) / at(d, 'f_my60_x_c', 1550),
            'rmax': R[j], 'lrmax': lam[j], 'na13': at(d, 'f_zNA13_x_c', 1550), 'na09': at(d, 'f_zNA09_x_c', 1550)}


def main():
    d, nc = tri2.series(FINAL); d5, nc5 = tri2.series(OLD); D4 = dimer(4.0)
    if d is None or nc < 6: sys.exit('final-design chunks missing: %s (%d/6)' % (FINAL, nc))
    s4, s5 = summary(d, 'h = 4 nm'), summary(d5, 'h = 5 nm')
    out = ['# Final telecom design: trimer R1 = R2 = 285 nm, gap 40 nm, R3 = 315 nm horizontal at y = 160 nm (BEM)', '',
           'D = 60 nm, host n = 1.5, gold = Johnson-Christy (MNPBEM gold.dat), retarded BEM with curved elements.',
           'Mesh: R1/R2 h, R3 1.4 h. x dipole at the gap centre. Spectra 1100-1900 nm in 20 nm steps (parabolic peak refinement).', '',
           '| quantity | h = 4 nm (final) | h = 5 nm (earlier) | change |', '|---|---|---|---|']
    rows = [('peak of Fp (nm)', 'lF', '{:.0f}', 'd'), ('Fp at the peak', 'Fpk', '{:.0f}', '%'), ('peak of T (nm)', 'lT', '{:.0f}', 'd'),
            ('T at its peak', 'Tpk', '{:.0f}', '%'), ('eta at the T peak', 'eta_pk', '{:.1%}', 'pp'),
            ('Fp(1550)', 'Fp', '{:.0f}', '%'), ('T(1550)', 'T', '{:.0f}', '%'), ('eta(1550)', 'eta', '{:.1%}', 'pp'),
            ('f(+y) 60 deg cone (1550)', 'fp', '{:.3f}', '%'), ('f(-y) 60 deg cone (1550)', 'fm', '{:.3f}', '%'),
            ('ratio f(+y)/f(-y) (1550)', 'ratio', '{:.2f}', '%'), ('best ratio', 'rmax', '{:.2f}', '%'), ('  at (nm)', 'lrmax', '{:.0f}', 'd'),
            ('collection NA 1.3 (1550)', 'na13', '{:.3f}', '%'), ('collection NA 0.9 (1550)', 'na09', '{:.3f}', '%')]
    for name, k, f, kind in rows:
        a, b = s4[k], s5[k]
        ch = f'{a-b:+.0f} nm' if kind == 'd' else (f'{100*(a-b):+.1f} pp' if kind == 'pp' else f'{100*(a/b-1):+.1f}%')
        out.append(f'| {name} | {f.format(a)} | {f.format(b)} | {ch} |')
    # dimer reference at the same mesh
    if D4 is not None:
        lam = D4['lambda_nm']; lF, Fpk = peak(lam, D4['Fp_x'])
        F55, T55 = at(D4, 'Fp_x', 1550), at(D4, 'T_x', 1550)
        out += ['', f'Dimer alone (same R1, R2, h = 4 nm, mirror-symmetric run): Fp peak {Fpk:.0f} at {lF:.0f} nm; at 1550 nm Fp = {F55:.0f}, '
                f'T = {T55:.0f}, eta = {T55/F55:.1%}. The third rod changes T(1550) by {100*(s4["T"]/T55-1):+.0f}% and makes the emission '
                f'directional (dimer ratio = 1 by symmetry).']
    # emitter position and dipole orientation (h = 4 nm)
    out += ['', '## Robustness at 1550 nm (h = 4 nm)', '', '| emitter | dipole | Fp | T | eta | f(+y)/f(-y) |', '|---|---|---|---|---|---|']
    for p, plab in (('c', 'gap centre'), ('px5', '5 nm along x'), ('py10', '10 nm along y')):
        for o in 'xyz':
            Fp, T = at(d, f'Fp_{o}_{p}', 1550), at(d, f'T_{o}_{p}', 1550)
            out.append(f'| {plab} | {o} | {Fp:.1f} | {T:.1f} | {T/Fp:.1%} | {at(d, f"f_py60_{o}_{p}", 1550)/at(d, f"f_my60_{o}_{p}", 1550):.2f} |')
    out += ['', 'The x dipole (along the rods) dominates: y and z dipoles couple weakly (Fp ~ 1, no enhancement), so the emitter must be oriented along the dimer axis.',
            'The direction of emission switches with wavelength: f(-y) > f(+y) below 1460-1480 nm, f(+y) > f(-y) above it (Fig. c).']
    open(os.path.join(RES, 'final_design.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

    # ---------------- figure ----------------
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.4)); a, b, c, e = ax.ravel()
    lam = d['lambda_nm']
    a.plot(lam, d['Fp_x_c'], c=C_TRI, lw=1.4, label=r'trimer $F_p$')
    a.plot(lam, d['T_x_c'], c=C_TRI, lw=1.4, ls='--', label=r'trimer $T$')
    a.plot(d5['lambda_nm'], d5['Fp_x_c'], c=C_OLD, lw=0.8, label=r'trimer $F_p$, $h$ = 5 nm')
    if D4 is not None:
        a.plot(D4['lambda_nm'], D4['Fp_x'], c=C_DIM, lw=1.0, label=r'dimer $F_p$')
        a.plot(D4['lambda_nm'], D4['T_x'], c=C_DIM, lw=1.0, ls='--', label=r'dimer $T$')
    a.set_ylabel('enhancement'); a.legend(fontsize=6.5, loc='upper left')
    b.plot(lam, 100 * d['T_x_c'] / d['Fp_x_c'], c=C_TRI, lw=1.4, label='trimer')
    b.plot(d5['lambda_nm'], 100 * d5['T_x_c'] / d5['Fp_x_c'], c=C_OLD, lw=0.8, label=r'trimer, $h$ = 5 nm')
    if D4 is not None: b.plot(D4['lambda_nm'], 100 * D4['T_x'] / D4['Fp_x'], c=C_DIM, lw=1.0, label='dimer')
    b.set_ylabel(r'antenna efficiency $\eta = T/F_p$ (%)'); b.set_ylim(0, 100); b.legend(fontsize=6.5, loc='lower right')
    c.plot(lam, d['f_py60_x_c'], c='#c0392b', lw=1.3, label=r'$f(+y)$')
    c.plot(lam, d['f_my60_x_c'], c='#2a7a4b', lw=1.3, label=r'$f(-y)$')
    c.set_ylabel(r'fraction in a 60$^\circ$ cone'); c.set_ylim(0, 0.8)
    c2 = c.twinx(); c2.plot(lam, d['f_py60_x_c'] / d['f_my60_x_c'], c='k', lw=1.1, label='ratio')
    c2.plot(d5['lambda_nm'], d5['f_py60_x_c'] / d5['f_my60_x_c'], c='0.6', lw=0.8, label=r'ratio, $h$ = 5 nm')
    c2.set_ylabel(r'$f(+y)/f(-y)$'); c2.set_ylim(0, 8); c2.tick_params(direction='in')
    h1, l1 = c.get_legend_handles_labels(); h2, l2 = c2.get_legend_handles_labels(); c.legend(h1 + h2, l1 + l2, fontsize=6.5, loc='upper left')
    e.plot(lam, 100 * d['f_zNA13_x_c'], c=C_TRI, lw=1.3, label='NA 1.3')
    e.plot(lam, 100 * d['f_zNA09_x_c'], c=C_TRI, lw=1.3, ls='--', label='NA 0.9')
    e.set_ylabel('collected along +z (%)'); e.set_ylim(0, 40); e.legend(fontsize=6.5, loc='lower right')
    for k, x in enumerate((a, b, c, e)):
        x.axvline(1550, c='0.6', lw=0.8, ls=':'); x.set_xlim(1100, 1900); x.set_xlabel('wavelength (nm)')
        x.set_title(f'({"abcd"[k]})', loc='left', fontsize=8)
    fig.text(0.01, -0.01, r'BEM, $h$ = 4 nm (R3: 5.6 nm) unless stated; x dipole at the gap centre; host $n$ = 1.5; dotted line: 1550 nm', fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_final_design.png'), dpi=200); fig.savefig(os.path.join(FIG, 'fig_final_design.pdf'))


if __name__ == '__main__':
    main()
