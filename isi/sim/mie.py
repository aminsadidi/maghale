"""Exact (Mie) decay rates of a radial dipole outside a sphere [Ruppin 1982; Kim et al. 1988].
Units: lengths in nm. eps_sphere(lam_nm) -> complex permittivity; n_host real."""
import numpy as np
from scipy.special import spherical_jn as jn, spherical_yn as yn

def _h(n, z, d=False):
    return jn(n, z, d) + 1j * yn(n, z, d)

def mie_an(n, x, m):
    mx = m * x
    psi = lambda z: z * jn(n, z)
    dpsi = lambda z: jn(n, z) + z * jn(n, z, True)
    xi = lambda z: z * _h(n, z)
    dxi = lambda z: _h(n, z) + z * _h(n, z, True)
    return (m * psi(mx) * dpsi(x) - psi(x) * dpsi(mx)) / (m * psi(mx) * dxi(x) - xi(x) * dpsi(mx))

def radial_dipole(lam_nm, R, d, eps_sphere, n_host=1.0, nmax=60):
    """Return (F_p, T) = (Gamma_tot/Gamma_0, Gamma_rad/Gamma_0) for a radial dipole at distance d."""
    Fp, T = [], []
    for lam in np.atleast_1d(lam_nm):
        k = 2 * np.pi * n_host / lam
        xs, x = k * R, k * (R + d)
        m = np.sqrt(eps_sphere(lam) + 0j) / n_host
        st = sr = 0
        for n in range(1, nmax):
            B = -mie_an(n, xs, m)
            c = n * (n + 1) * (2 * n + 1)
            st += c * B * (_h(n, x) / x) ** 2
            sr += c * abs(jn(n, x) + B * _h(n, x)) ** 2
        Fp.append(1 + 1.5 * np.real(st))
        T.append(1.5 / x**2 * sr)
    return np.array(Fp), np.array(T)
