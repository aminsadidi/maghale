"""Semi-analytic decay rates of a dipole on the axis of a metal prolate spheroid (quasistatic multipole solution in
prolate spheroidal harmonics, cf. Gersten & Nitzan, J. Chem. Phys. 75, 1139 (1981)), with the radiation reaction of the
dipolar modes (n = 1) included self-consistently.  Gaussian units, background index n_b, p = 1.

Spheroid: semi-axes a (along z) > b, focal distance f = sqrt(a^2 - b^2), surface xi0 = a / f.
Potential inside  : sum_n A_n P_n^m(xi) P_n^m(eta) cos(m phi)
          outside : incident + sum_n B_n Q_n^m(xi) P_n^m(eta) cos(m phi)
Axial dipole couples to m = 0, transverse (x) dipole to m = 1.  The incident coefficients are obtained by projecting
the dipole potential on the surface onto P_n^m(eta); only ratios of P(xi), Q(xi) enter, so the normalisation of the
Legendre functions drops out.
"""
import numpy as np, mpmath as mp
from scipy.special import lpmv
from numpy.polynomial.legendre import leggauss

mp.mp.dps = 30


class Spheroid:
    def __init__(self, a, b, nmax=60, nquad=1500):
        self.a, self.b, self.f = a, b, np.sqrt(a * a - b * b)
        self.xi0 = a / self.f
        self.nmax = nmax
        self.x, self.w = leggauss(nquad)
        x0 = mp.mpf(self.xi0)
        self.r = {}       # m -> (P'/P, Q'/Q) at xi0 for n = 1..nmax
        for m in (0, 1):
            pp, qq = [], []
            for n in range(1, nmax + 1):
                P = lambda t: mp.legenp(n, m, t, type=3)
                Q = lambda t: mp.legenq(n, m, t, type=3)
                pp.append(float(mp.re(mp.diff(P, x0) / P(x0))))
                qq.append(float(mp.re(mp.diff(Q, x0) / Q(x0))))
            self.r[m] = (np.array(pp), np.array(qq))
        self._qcache = {}

    def qratio(self, m, xi):
        """Q_n^m(xi) / Q_n^m(xi0), n = 1..nmax."""
        key = (m, round(float(xi), 12))
        if key not in self._qcache:
            x0, x1 = mp.mpf(self.xi0), mp.mpf(xi)
            self._qcache[key] = np.array([float(mp.re(mp.legenq(n, m, x1, type=3) / mp.legenq(n, m, x0, type=3)))
                                          for n in range(1, self.nmax + 1)])
        return self._qcache[key]

    def cart2sph(self, x, y, z):
        f = self.f
        r1 = np.sqrt(x * x + y * y + (z - f) ** 2); r2 = np.sqrt(x * x + y * y + (z + f) ** 2)
        return (r1 + r2) / (2 * f), np.clip((r2 - r1) / (2 * f), -1, 1), np.arctan2(y, x)

    def surface_xyz(self, eta):
        f, x0 = self.f, self.xi0
        return f * np.sqrt((x0 ** 2 - 1) * (1 - eta ** 2)), 0 * eta, f * x0 * eta

    def project(self, m, phi_fun):
        """Coefficients s_n = c_n P_n^m(xi0) of a potential with cos(m phi) dependence, n = 1..nmax."""
        X, Y, Z = self.surface_xyz(self.x)
        v = phi_fun(X, Y, Z)
        s = []
        for n in range(1, self.nmax + 1):
            Pn = lpmv(m, n, self.x)
            norm = 2.0 / (2 * n + 1) * np.prod(np.arange(n - m + 1, n + m + 1, dtype=float))
            s.append(np.sum(self.w * v * Pn) / norm)
        return np.array(s)

    def induced_potential(self, m, coef, x, y, z):
        """sum_n coef_n * Q_n^m(xi)/Q_n^m(xi0) * P_n^m(eta) cos(m phi) at one point."""
        xi, eta, ph = self.cart2sph(x, y, z)
        n = np.arange(1, self.nmax + 1)
        return np.sum(coef * self.qratio(m, xi) * lpmv(m, n, eta)) * np.cos(m * ph)


def decay_rates(sph, gap, lam_nm, eps, nb=1.0, orient='z', h=1e-4, radiative=True, ldd=None):
    """Fp (total) and T (radiative) for a dipole at distance gap from the apex, on the axis. eps: complex array."""
    eb = nb ** 2
    z0 = sph.a + gap
    if orient == 'z':
        m = 0; dip = lambda X, Y, Z: (Z - z0) / ((X ** 2 + Y ** 2 + (Z - z0) ** 2) ** 1.5) / eb
        unif = lambda X, Y, Z: -Z
        pts = [(0, 0, z0 + h), (0, 0, z0 - h)]
    else:
        m = 1; dip = lambda X, Y, Z: X / ((X ** 2 + Y ** 2 + (Z - z0) ** 2) ** 1.5) / eb
        unif = lambda X, Y, Z: -X
        pts = [(h, 0, z0), (-h, 0, z0)]
    s = sph.project(m, dip)                     # incident dipole potential
    u = sph.project(m, unif)                    # uniform unit field along the dipole: drives only n = 1
    pp, qq = sph.r[m]
    # induced dipole moment per unit coefficient of the n = 1 outside term (far-field evaluation)
    R = 1e5 * sph.a
    e1 = np.zeros(sph.nmax); e1[0] = 1.0
    if orient == 'z':
        K = sph.induced_potential(m, e1, 0, 0, R) * R ** 2 * eb
    else:
        K = sph.induced_potential(m, e1, R, 0, 0) * R ** 2 * eb
    # induced-field derivative operator at the dipole for unit coefficient of each n
    G = np.array([(sph.induced_potential(m, np.eye(sph.nmax)[i], *pts[0]) -
                   sph.induced_potential(m, np.eye(sph.nmax)[i], *pts[1])) / (2 * h) for i in range(sph.nmax)])
    G = -G                                       # E_parallel = -d(phi)/d(direction)
    Fp, T = [], []
    for lam, e in zip(lam_nm, eps):
        k = 2 * np.pi * nb / lam
        chi = pp * (e - eb) / (eb * qq - e * pp)     # B_n Q_n(xi0) = chi_n * s_n
        coef = chi * s
        if radiative:                               # radiation reaction field i(2/3)k^3 p_ind / eb on mode n = 1
            # coef1 = chi1*(s1 + Err*u1), Err = i(2/3)k^3 K coef1 / eb
            rr = 1j * (2 / 3) * k ** 3
            if ldd:                                 # dynamic depolarisation (MLWA) k^2/l_dd, l_dd ~ semi-axis
                rr = rr + k ** 2 / ldd
            coef[0] = chi[0] * s[0] / (1 - chi[0] * u[0] * rr * K / eb)
        Eind = np.sum(G * coef)
        p_ind = K * coef[0]
        Fp.append(1 + 1.5 / k ** 3 * np.imag(Eind) * eb)
        T.append(abs(1 + p_ind) ** 2)
    return np.array(Fp), np.array(T)


def gold_jc(lam_nm, fn='isi/bem/MNPBEM17/Material/@epstable/gold.dat'):
    import os
    for f in (fn, '/tmp/gold.dat', os.path.join(os.path.dirname(__file__), 'gold_jc.dat')):
        if os.path.exists(f):
            a = np.loadtxt(f, comments='%'); break
    from scipy.interpolate import CubicSpline
    lam = 1239.84193 / a[:, 0]; o = np.argsort(lam)
    n = CubicSpline(lam[o], a[o, 1])(lam_nm); k = CubicSpline(lam[o], a[o, 2])(lam_nm)
    return (n + 1j * k) ** 2
