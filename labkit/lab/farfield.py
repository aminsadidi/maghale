"""Near-to-far-field transformation from the six faces of a closed box of DFT monitors in a homogeneous medium (numpy only).
Surface-equivalence currents J = n x H, M = -n x E (n = outward normal); radiation vectors
  N(r^) = int J exp(-s i k r^.r') dS,  L(r^) = int M exp(-s i k r^.r') dS      (s = +1 for the exp(-i w t) convention)
Radiant intensity  U = k^2 / (32 pi^2 eta) * ( |L_phi + eta N_theta|^2 + |L_theta - eta N_phi|^2 ),  eta = eta0 / n.
Directions: an equal-area Fibonacci set on the unit sphere, so a cone fraction is a plain sum over the directions inside it.
Self-check returned for every frequency: P_ff / P_box, with P_ff = int U dOmega and P_box = 1/2 Re int (E x H*).n dS.
"""
import numpy as np

ETA0 = 376.730313668


def fib_dirs(n):
    """n equal-area directions; returns (n, 3) unit vectors"""
    i = np.arange(n) + 0.5
    ct = 1 - 2 * i / n; st = np.sqrt(1 - ct ** 2); ph = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=1)


def trap_w(x):
    """trapezoid weights of a (possibly non-uniform) 1D grid"""
    x = np.asarray(x, float).ravel()
    if x.size == 1: return np.ones(1)
    w = np.zeros_like(x); d = np.diff(x); w[:-1] += d / 2; w[1:] += d / 2
    return w


def face(axis, normal, coords, E, H):
    """one face. axis: 0/1/2 (normal axis), normal: +1/-1 (outward), coords: (x, y, z) 1D arrays (length 1 along the normal axis),
    E, H: arrays (nx, ny, nz, nf, 3). Returns a dict with flattened points, weights, currents."""
    x, y, z = [np.asarray(c, float).ravel() for c in coords]
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    W = np.einsum('i,j,k->ijk', *(np.ones(len(c)) if a == axis else trap_w(c) for a, c in enumerate((x, y, z))))
    nf = E.shape[3]
    Ef = E.reshape(-1, nf, 3); Hf = H.reshape(-1, nf, 3)
    nv = np.zeros(3); nv[axis] = normal
    J = np.cross(nv, Hf); M = -np.cross(nv, Ef)
    S = 0.5 * np.real(np.einsum('pfi,i->pf', np.cross(Ef, np.conj(Hf)), nv))
    return {'r': np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1), 'w': W.ravel(), 'J': J, 'M': M, 'S': S}


def project(faces, lam, n_medium, ndir=4000, sign=1, chunk=4000, dirs=None):
    """faces: list of face() dicts (same frequencies), lam: (nf,) vacuum wavelengths [m].
    Returns dirs (nd, 3), U (nf, nd), P_box (nf,), ratio P_ff/P_box (nf,)"""
    d = fib_dirs(ndir) if dirs is None else dirs
    nd = len(d); nf = len(lam); eta = ETA0 / n_medium
    th = np.arccos(np.clip(d[:, 2], -1, 1)); ph = np.arctan2(d[:, 1], d[:, 0])
    eth = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], 1)
    eph = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)], 1)
    U = np.zeros((nf, nd)); Pb = np.zeros(nf)
    for f in range(nf):
        k = 2 * np.pi * n_medium / lam[f]; Nv = np.zeros((nd, 3), complex); Lv = np.zeros((nd, 3), complex)
        for F in faces:
            r, w = F['r'], F['w']; Jw = F['J'][:, f, :] * w[:, None]; Mw = F['M'][:, f, :] * w[:, None]
            for a in range(0, len(r), chunk):
                P = np.exp(-sign * 1j * k * (d @ r[a:a + chunk].T))
                Nv += P @ Jw[a:a + chunk]; Lv += P @ Mw[a:a + chunk]
            Pb[f] += np.sum(F['S'][:, f] * w)
        Nt, Np = np.sum(Nv * eth, 1), np.sum(Nv * eph, 1); Lt, Lp = np.sum(Lv * eth, 1), np.sum(Lv * eph, 1)
        U[f] = k ** 2 / (32 * np.pi ** 2 * eta) * (np.abs(Lp + eta * Nt) ** 2 + np.abs(Lt - eta * Np) ** 2)
    Pff = U.sum(1) * 4 * np.pi / nd
    return d, U, Pb, Pff / Pb


def cone_fraction(d, U, axis_vec, half_angle):
    """fraction of the far-field power inside a cone of half-angle half_angle [rad] about axis_vec, per frequency"""
    a = np.asarray(axis_vec, float); a /= np.linalg.norm(a)
    inside = d @ a >= np.cos(half_angle)
    return U[:, inside].sum(1) / U.sum(1)
