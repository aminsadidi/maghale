"""Quasi-static exact (multipole) decay rates of a point dipole near a gold nanosphere (Gersten & Nitzan 1981, Ruppin 1982),
used in the thesis as the analytic sphere reference for the FDTD nanorod results.
Sphere: same volume as the capped rod (L = 60 nm, D = 20 nm) -> radius a = 15.9 nm; host n = 1; gold: Johnson & Christy.
Dipole radial (normal to the surface, analogue of the axial dipole at the rod tip) or tangential, at distance d from the surface.
  radial:     Gtot/G0 = 1 + 3/(2 k^3) sum_n (n+1)^2 Im(alpha_n)/r^(2n+4),   Grad/G0 = |1 + 2 alpha_1/r^3|^2
  tangential: Gtot/G0 = 1 + 3/(4 k^3) sum_n n(n+1) Im(alpha_n)/r^(2n+4),   Grad/G0 = |1 - alpha_1/r^3|^2
  alpha_n = n (eps-1)/(n eps + n + 1) a^(2n+1)
"""
import numpy as np, sys
E, n_, k_ = np.loadtxt(sys.argv[1], comments='%', unpack=True)
lam_t = 1239.84 / E; o = np.argsort(lam_t); lam_t = lam_t[o]; eps_t = (n_[o] + 1j * k_[o]) ** 2
eps = lambda lam: np.interp(lam, lam_t, eps_t.real) + 1j * np.interp(lam, lam_t, eps_t.imag)
V = np.pi * 10**2 * 40 + 4 / 3 * np.pi * 10**3; a = (3 * V / (4 * np.pi)) ** (1 / 3)
def rates(lam, d, orient='rad', N=120):
    e = eps(lam); k = 2 * np.pi / lam; r = a + d; ns = np.arange(1, N + 1)
    g = ns * (e - 1) / (ns * e + ns + 1) * (a / r) ** (2 * ns + 1) / r**3      # alpha_n / r^(2n+4), no overflow
    if orient == 'rad':
        tot = 1 + 1.5 / k**3 * np.sum((ns + 1) ** 2 * g.imag); rad = abs(1 + 2 * g[0] * r**3) ** 2
    else:
        tot = 1 + 0.75 / k**3 * np.sum(ns * (ns + 1) * g.imag); rad = abs(1 - g[0] * r**3) ** 2
    return tot, rad
print(f'equal-volume sphere: V = {V:.0f} nm^3, a = {a:.2f} nm (diameter {2*a:.1f} nm)')
L = np.arange(450, 801, 1.0)
for d in (10,):
    R = np.array([rates(l, d)[1] for l in L]); print(f'sphere radiative-enhancement peak (d={d}): {L[R.argmax()]:.0f} nm')
print('lam  d   Fp_rad  T_rad  eta | Fp_tan  ratio_rad/tan')
for lam in (616, L[np.array([rates(l, 10)[1] for l in L]).argmax()]):
    for d in (3, 5, 10, 20):
        t, r = rates(lam, d); tt, _ = rates(lam, d, 'tan')
        print(f'{lam:.0f} {d:3d} {t:8.1f} {r:6.2f} {r/t:6.1%} | {tt:7.1f} {t/tt:5.2f}')
