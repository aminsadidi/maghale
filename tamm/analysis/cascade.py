"""Normal-incidence amplitude cascade (e^{-i omega t}, E-field amplitudes) to combine the 3D film S-parameters (Meep) with the
planar DBR, and analytic S-parameters of planar layers for the validation of the Meep pipeline.
Section = (r12, t12, r21, t21, n1, n2): reflection/transmission amplitudes for incidence from medium 1 (above) and medium 2 (below).
usage: import cascade; python tamm/analysis/cascade.py runs the self-tests"""
import numpy as np


def interface(n1, n2):
    return ((n1 - n2) / (n1 + n2), 2 * n1 / (n1 + n2), (n2 - n1) / (n1 + n2), 2 * n2 / (n1 + n2), n1, n2)


def layer(n, d, lam):
    """propagation through thickness d of index n (both ways)"""
    ph = np.exp(2j * np.pi * n * d / lam); z = 0 * ph
    return (z, ph, z, ph, n, n)


def join(A, B):
    """A above B (Redheffer star product for 2x2 scalar S-matrices)"""
    rA, tA, rA2, tA2, n1, _ = A; rB, tB, rB2, tB2, _, n3 = B
    D = 1 - rA2 * rB
    return (rA + tA * rB * tA2 / D, tA * tB / D, rB2 + tB2 * rA2 * tB / D, tB2 * tA2 / D, n1, n3)


def chain(*S):
    out = S[0]
    for s in S[1:]: out = join(out, s)
    return out


def RT(S):
    r, t, r2, t2, n1, n2 = S
    return np.abs(r) ** 2, np.real(n2) / np.real(n1) * np.abs(t) ** 2


def slab(nl, d, n1, n2, lam, top_gap=0.0):
    """medium n1 / [gap of n1 of thickness top_gap] / layer nl, d / medium n2, reference planes at the top of the gap and the bottom"""
    return chain(layer(n1, top_gap, lam), interface(n1, nl), layer(nl, d, lam), interface(nl, n2))


def tests():
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import tmm
    lam = np.linspace(400, 850, 7)
    nAg = tmm.AG['JC'](lam)
    # cascade of a film on a substrate == tmm._stack (coherent, normal incidence)
    S = slab(nAg, 33, 1.0, 1.93, lam)
    R, T = RT(S)
    R2, T2 = tmm._stack([nAg], [33], lam, np.ones_like(lam, complex), np.full(len(lam), 1.93 + 0j), 0, 's')
    assert np.allclose(R, R2) and np.allclose(T, T2), (R, R2, T, T2)
    # reciprocity and energy for a lossless stack
    S = chain(interface(1.0, 2.0), layer(2.0, 80, lam), interface(2.0, 1.45), layer(1.45, 100, lam), interface(1.45, 1.52))
    R, T = RT(S); assert np.allclose(R + T, 1)
    print('cascade tests passed')


if __name__ == '__main__':
    tests()
