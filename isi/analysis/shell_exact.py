"""Exact decay rates of an electric dipole at the CENTRE of a concentric spherical shell (core n1, shell n2, outer n3),
used to validate the BEM nanoshell runs (job_nshell.m, spec 'sph_tX', position 'centre').

A dipole at the centre couples only to the TM l = 1 spherical wave. With Riccati-Bessel functions psi = x j1(x),
xi = x h1(x) (outgoing, e^{-i w t}), the radial functions are
    core : u1 = xi(k1 r) + R psi(k1 r)      shell: u2 = A psi(k2 r) + B xi(k2 r)      outside: u3 = T xi(k3 r)
and the TM boundary conditions (tangential H and E) are  n_i u_i = n_j u_j  and  u_i' = u_j'  (derivative with respect
to the argument), which reproduce the Mie coefficient a_n for a homogeneous sphere. Then
    Gamma / Gamma_0 = Re(1 + R)          (Gamma_0: dipole in the core medium)
    Gamma_rad / Gamma_0 = (n3 / n1) |T|^2
usage: python isi/analysis/shell_exact.py   (self-test, then comparison with BEM if nshell_sph_t*.csv exist)
"""
import os, glob, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spheroid_qs import gold_jc

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')


def psi(z): return np.sin(z) / z - np.cos(z)
def dpsi(z): return np.cos(z) / z - np.sin(z) / z ** 2 + np.sin(z)
def chi(z): return -np.cos(z) / z - np.sin(z)
def dchi(z): return np.sin(z) / z + np.cos(z) / z ** 2 - np.cos(z)
def xi(z): return psi(z) + 1j * chi(z)
def dxi(z): return dpsi(z) + 1j * dchi(z)


def rates(lam, a, b, n1, n2, n3):
    """lam, a, b in nm; n2 may be complex. Returns (Fp, T)."""
    k0 = 2 * np.pi / lam
    x1a, x2a, x2b, x3b = k0 * n1 * a, k0 * n2 * a, k0 * n2 * b, k0 * n3 * b
    # unknowns R, A, B, T
    M = np.array([[n1 * psi(x1a), -n2 * psi(x2a), -n2 * xi(x2a), 0],
                  [dpsi(x1a), -dpsi(x2a), -dxi(x2a), 0],
                  [0, n2 * psi(x2b), n2 * xi(x2b), -n3 * xi(x3b)],
                  [0, dpsi(x2b), dxi(x2b), -dxi(x3b)]], dtype=complex)
    rhs = np.array([-n1 * xi(x1a), -dxi(x1a), 0, 0], dtype=complex)
    R, A, B, T = np.linalg.solve(M, rhs)
    return float(np.real(1 + R)), float(n3 / n1 * abs(T) ** 2)


def selftest():
    # lossless, index-matched shell: no reflection -> Fp = T = 1
    for lam in (500, 900):
        f, t = rates(lam, 10, 17, 1.45, 1.45, 1.45)
        assert abs(f - 1) < 1e-9 and abs(t - 1) < 1e-9, (f, t)
    # lossless dielectric shell: energy conservation Fp = T
    for lam in (500, 700, 1200):
        f, t = rates(lam, 10, 25, 1.45, 2.5, 1.0)
        assert abs(f - t) < 1e-9 * max(1, f), (lam, f, t)
    print('self-test passed (index-matched: Fp = T = 1; lossless shell: Fp = T)')


def main():
    selftest()
    files = sorted(glob.glob(os.path.join(RES, 'bem_extra', 'nshell_sph_t*.csv')))
    out = ['# Dipole at the centre of a spherical gold nanoshell: exact solution vs BEM', '',
           '| shell t (nm) | quantity | exact max (lambda) | BEM max (lambda) | median abs. dev. |', '|---|---|---|---|---|']
    for f in files:
        t = float(re.search(r'sph_t(\d+)', f).group(1))
        d = np.genfromtxt(f, delimiter=',', names=True, skip_header=1); lam = d['lambda_nm']
        eps = gold_jc(lam); n2 = np.sqrt(eps)
        ex = np.array([rates(l, 10, 10 + t, 1.45, nn, 1.45) for l, nn in zip(lam, n2)])
        for k, q in enumerate(('z', 'x')):
            for j, key in enumerate(('Fp', 'T')):
                bem = d[f'{key}_{q}_centre']; e = ex[:, j]
                dev = np.median(np.abs(bem / e - 1))
                out.append(f'| {t:g} | {key}_{q} | {e.max():.3g} ({lam[e.argmax()]:.0f}) | {bem.max():.3g} ({lam[bem.argmax()]:.0f}) | {100*dev:.1f}% |')
    open(os.path.join(RES, 'shell_exact.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__':
    main()
