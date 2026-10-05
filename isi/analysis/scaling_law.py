"""Closed-form single-mode model of the resonant Purcell enhancement at a nanorod tip, tested against all BEM runs,
and the semi-analytic multipole solution for the prolate spheroid (spheroid_qs.py) against the BEM spheroid.

Closed form (no adjustable parameter), axial dipole at distance d from the apex of a rod (length L, diameter D, volume V):
    Fp_res = (3 / 2k^3) Im(alpha_L) E1(z0)^2 ,   T_res = (1 + Im(alpha_L) E1(z0))^2
    Im(alpha_L) = [4 pi eps'' / (V (1 - eps')^2) + (2/3) k^3]^-1      (quasistatic Lorentzian peak + radiation damping)
    E1(z0) = (3 / f^3) [xi / (xi^2 - 1) - 1/2 ln((xi + 1) / (xi - 1))],  xi = z0 / f,  z0 = L/2 + d
E1 is the on-axis field of the dipolar (n = 1) mode of the prolate spheroid with the rod's half-length a = L/2 and
apex radius of curvature b^2/a = D/2 (f = sqrt(a^2 - b^2) = sqrt(L (L - D)) / 2), per unit dipole moment.
eps = eps' + i eps'' is taken at the computed radiative peak lambda_L.
usage: python isi/analysis/scaling_law.py   (from repo root)
"""
import sys, os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spheroid_qs import Spheroid, decay_rates, gold_jc

plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'lines.linewidth': 1.4,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'figure.dpi': 150})
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def silver_jc(lam):
    a = np.loadtxt(os.path.join(HERE, 'silver_jc.dat'), comments='%')
    l = 1239.84193 / a[:, 0]; o = np.argsort(l)
    return (CubicSpline(l[o], a[o, 1])(lam) + 1j * CubicSpline(l[o], a[o, 2])(lam)) ** 2


CASES = [  # label, file, D, L, metal, shape
    ('AR 2', 'bem_raw/rod_L40_h2_air.csv', 20, 40, 'Au', 'rod'), ('AR 2.5', 'bem_raw/rod_L50_h2_air.csv', 20, 50, 'Au', 'rod'),
    ('AR 3', 'bem_raw/rod_L60_h2_air.csv', 20, 60, 'Au', 'rod'), ('AR 4', 'bem_raw/rod_L80_h2_air.csv', 20, 80, 'Au', 'rod'),
    ('AR 5', 'bem_raw/rod_L100_h2_air.csv', 20, 100, 'Au', 'rod'), ('D 15', 'bem_extra/shape_D15.csv', 15, 45, 'Au', 'rod'),
    ('D 25', 'bem_extra/shape_D25.csv', 25, 75, 'Au', 'rod'), ('D 30', 'bem_extra/shape_D30.csv', 30, 90, 'Au', 'rod'),
    ('Ag', 'bem_extra/shape_Ag60.csv', 20, 60, 'Ag', 'rod'), ('spheroid', 'bem_extra/shape_spheroid60.csv', 20, 60, 'Au', 'sph')]


def E1(z0, a, b):
    f = np.sqrt(a * a - b * b); xi = z0 / f
    return (3 / f ** 3) * (xi / (xi * xi - 1) - 0.5 * np.log((xi + 1) / (xi - 1)))


def closed_form(D, L, shape, gap, lamL, eps):
    a = L / 2
    b = D / 2 if shape == 'sph' else np.sqrt(L * D) / 2          # equal apex curvature b^2/a = D/2
    V = 4 / 3 * np.pi * (D / 2) ** 2 * a if shape == 'sph' else np.pi * (D / 2) ** 2 * (L - D) + 4 / 3 * np.pi * (D / 2) ** 3
    k = 2 * np.pi / lamL
    ima = 1 / (4 * np.pi * eps.imag / (V * (1 - eps.real) ** 2) + 2 / 3 * k ** 3)
    E = E1(a + gap, a, b)
    return 1.5 * ima * E ** 2 / k ** 3, (1 + ima * E) ** 2


def load(f):
    return np.genfromtxt(os.path.join(RES, f), delimiter=',', names=True, skip_header=1)


def main():
    rows = []
    for lab, f, D, L, met, shp in CASES:
        d = load(f); lam = d['lambda_nm']
        for g in (5, 10, 20):
            Tz, Fz, Fx = d[f'T_z_g{g}'], d[f'Fp_z_g{g}'], d[f'Fp_x_g{g}']
            i = np.argmax(Tz); lL = lam[i]
            e = (gold_jc if met == 'Au' else silver_jc)(np.array([lL]))[0]
            Fm, Tm = closed_form(D, L, shp, g, lL, e)
            rows.append((lab, g, lL, Fz[i], Fm, Tz[i], Tm, Fz[i] / Fx[i], Fm / Fx[i]))
    # semi-analytic spheroid vs BEM spheroid
    d = load('bem_extra/shape_spheroid60.csv'); lam = d['lambda_nm']; eps = gold_jc(lam)
    S = Spheroid(30, 10, nmax=50)
    sa = {(g, o): decay_rates(S, g, lam, eps, orient=o, ldd=30) for g in (5, 10) for o in 'zx'}

    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    a = ax[0]
    for g, c in zip((5, 10), ('C0', 'C3')):
        a.semilogy(lam, d[f'Fp_z_g{g}'], c=c, label=f'{g} nm, BEM'); a.semilogy(lam, sa[(g, 'z')][0], '--', c=c, label=f'{g} nm, analytic')
        a.semilogy(lam, d[f'Fp_x_g{g}'], c=c, lw=0.9); a.semilogy(lam, sa[(g, 'x')][0], ':', c=c, lw=1.2)
    a.set_xlabel('wavelength (nm)'); a.set_ylabel(r'$F_p$'); a.set_xlim(450, 900)
    a.legend(fontsize=6, loc='lower left'); a.set_title('(a)', loc='left', fontsize=9)
    mk = {5: 'o', 10: 's', 20: '^'}
    for j, (key, lab) in enumerate(((3, r'$F_p$ at resonance'), (5, r'$T$ at resonance'))):
        a = ax[j + 1]
        for r in rows:
            col = 'C1' if r[0] == 'Ag' else ('C2' if r[0] == 'spheroid' else ('C0' if r[0].startswith('AR') else 'C4'))
            a.loglog(r[key + 1], r[key], mk[r[1]], mfc='none', c=col, ms=4.5)
        lo, hi = (1, 1e4)
        x = np.logspace(0, 4, 10); a.loglog(x, x, 'k-', lw=0.7); a.fill_between(x, x / 1.4, x * 1.4, color='0.85', lw=0)
        a.set_xlim(lo, hi); a.set_ylim(lo, hi); a.set_xlabel('closed form'); a.set_ylabel('BEM'); a.set_title(f'({"bc"[j]}) ' + lab, loc='left', fontsize=9)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls='', marker=mk[g], mfc='none', c='k', label=f'{g} nm') for g in (5, 10, 20)]
    h += [Line2D([], [], ls='', marker='o', c=c, label=l) for c, l in (('C0', 'Au, AR 2–5'), ('C4', 'Au, D 15–30'), ('C1', 'Ag'), ('C2', 'spheroid'))]
    ax[2].legend(handles=h, fontsize=6, loc='upper left')
    fig.tight_layout(); fig.savefig(os.path.join(HERE, '..', 'figures', 'fig_law.pdf'))
    fig.savefig(os.path.join(HERE, '..', 'figures', 'fig_law.png'), dpi=130)

    with open(os.path.join(RES, 'scaling_law.md'), 'w') as fo:
        fo.write('# Closed-form single-mode model vs BEM (axial dipole, at the radiative peak)\n\n')
        fo.write('| case | gap | lambda_L | Fp BEM | Fp model | ratio | T BEM | T model | ratio | Fp_z/Fp_x BEM | model |\n|' + '---|' * 11 + '\n')
        for r in rows:
            fo.write(f'| {r[0]} | {r[1]} | {r[2]:.0f} | {r[3]:.0f} | {r[4]:.0f} | {r[3]/r[4]:.2f} | {r[5]:.1f} | {r[6]:.1f} | {r[5]/r[6]:.2f} | {r[7]:.0f} | {r[8]:.0f} |\n')
        for g in (5, 10, 20):
            rf = np.array([r[3] / r[4] for r in rows if r[1] == g]); rt = np.array([r[5] / r[6] for r in rows if r[1] == g])
            rf2 = np.array([r[3] / r[4] for r in rows if r[1] == g and r[0] != 'AR 2']); rt2 = np.array([r[5] / r[6] for r in rows if r[1] == g and r[0] != 'AR 2'])
            fo.write(f'\ngap {g}: Fp ratio {rf.min():.2f}-{rf.max():.2f} (without AR 2: {rf2.min():.2f}-{rf2.max():.2f}), '
                     f'T ratio {rt.min():.2f}-{rt.max():.2f} (without AR 2: {rt2.min():.2f}-{rt2.max():.2f})')
        fo.write('\n\n## Semi-analytic multipole solution vs BEM, spheroid 60 x 20 nm\n\n')
        for g in (5, 10):
            Fz, Tz = sa[(g, 'z')]; Fx, Tx = sa[(g, 'x')]
            i500 = np.argmin(abs(lam - 500))
            fo.write(f'- gap {g}: Fp_z max {Fz.max():.0f} @ {lam[Fz.argmax()]:.0f} (BEM {d[f"Fp_z_g{g}"].max():.0f} @ {lam[d[f"Fp_z_g{g}"].argmax()]:.0f}); '
                     f'T_z max {Tz.max():.1f} @ {lam[Tz.argmax()]:.0f} (BEM {d[f"T_z_g{g}"].max():.1f} @ {lam[d[f"T_z_g{g}"].argmax()]:.0f}); '
                     f'Fp_z(500) {Fz[i500]:.0f} vs {d[f"Fp_z_g{g}"][i500]:.0f}; Fp_x(500) {Fx[i500]:.1f} vs {d[f"Fp_x_g{g}"][i500]:.1f}; '
                     f'median |dev| Fp_x {np.median(abs(Fx / d[f"Fp_x_g{g}"] - 1)) * 100:.1f}%\n')
    print(open(os.path.join(RES, 'scaling_law.md')).read()[-1600:])


if __name__ == '__main__':
    main()
