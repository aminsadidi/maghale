"""Transfer-matrix model of the Tamm device: thin-film stack on a thick (incoherent) glass substrate, oblique incidence, s and p.

Layers are given from the incidence side. The coherent stack is computed with 2x2 characteristic matrices; the thick glass
substrate is added incoherently (intensities, multiple reflections), as in an integrating-sphere R/T measurement.
Materials: tabulated n,k (data/optical/*.csv) or Sellmeier; porous nanoparticle layers and the island silver film by the
Bruggeman effective-medium approximation; Ag damping/plasma-frequency changes by adding a Drude correction to the measured epsilon.
usage: import tmm; see tests() for analytic checks:  python tamm/analysis/tmm.py"""
import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OPT = os.path.join(HERE, '..', 'data', 'optical')
HC = 1239.841984


# ---------------------------------------------------------------- materials (complex refractive index, lam in nm)
def tab(name):
    d = np.genfromtxt(os.path.join(OPT, name), delimiter=',', skip_header=2)
    lam = d[:, 0] * 1000
    return lambda l: np.interp(l, lam, d[:, 1]) + 1j * np.interp(l, lam, d[:, 2])


def sellmeier(B, C):
    return lambda l: np.sqrt(1 + sum(b * (l / 1000) ** 2 / ((l / 1000) ** 2 - c ** 2) for b, c in zip(B, C)) + 0j)


SiO2 = sellmeier((0.6961663, 0.4079426, 0.8974794), (0.0684043, 0.1162414, 9.896161))
BK7 = sellmeier((1.03961212, 0.231792344, 1.01046945), (0.0774642, 0.141484679, 10.1765))   # crown glass, n(589) = 1.517
TiO2 = tab('TiO2_Sarkar2019_film.csv')
AG = {'JC': tab('Ag_JohnsonChristy1972.csv'), 'Yang': tab('Ag_Yang2015.csv'), 'Ciesielski': tab('Ag_Ciesielski2017_20nm.csv')}
const = lambda n: (lambda l: np.full(np.shape(l), n, dtype=complex))
AIR, WATER = const(1.0), const(1.333)


def bruggeman(e1, e2, f2):
    """two-phase Bruggeman EMA (spheres): f2 = volume fraction of phase 2. Returns eps_eff (branch with Im >= 0, Re > 0 for dielectrics)"""
    b = (3 * f2 - 1) * e2 + (2 - 3 * f2) * e1
    r = np.sqrt(b ** 2 + 8 * e1 * e2)
    e = (b + r) / 4
    e_alt = (b - r) / 4
    bad = (e.imag < -1e-9) | ((e.imag < 1e-9) & (e.real < 0) & (np.real(e1) > 0) & (np.real(e2) > 0))
    return np.where(bad, e_alt, e)


def bruggeman_L(e1, e2, f2, L):
    """Polder-van Santen (generalised Bruggeman) EMA with depolarisation factor L of the inclusions (L = 1/3: spheres; flat islands
    seen by an in-plane field: L < 1/3). Solves (1-L) e^2 - b e - L e1 e2 = 0, b = f1 (e1 (1-L) - L e2) + f2 (e2 (1-L) - L e1)."""
    f1 = 1 - f2
    b = f1 * (e1 * (1 - L) - L * e2) + f2 * (e2 * (1 - L) - L * e1)
    r = np.sqrt(b ** 2 + 4 * (1 - L) * L * e1 * e2)
    ea, eb = (b + r) / (2 * (1 - L)), (b - r) / (2 * (1 - L))
    return np.where(ea.imag >= eb.imag, ea, eb)


def porous(mat, fill, p):
    """nanoparticle film: solid `mat` with pore volume fraction p filled by `fill`"""
    return lambda l: np.sqrt(bruggeman(mat(l) ** 2, fill(l) ** 2, p))


def silver(model='JC', dgamma=0.0, wp_scale=1.0, void=0.0, fill=AIR, L=1/3):
    """Ag with an extra Drude damping dgamma (eV) and a change of the free-electron plasma energy (wp -> wp*wp_scale),
    applied as a correction to the free-electron part of the measured eps (wp = 9.0 eV, gamma0 = 0.021 eV for JC);
    void: volume fraction of the ambient `fill` in the film (Bruggeman)."""
    base = AG[model]; wp, g0 = 9.0, 0.021
    def n(l):
        E = HC / l
        e = base(l) ** 2
        drude0 = -wp ** 2 / (E * (E + 1j * g0))
        drude1 = -(wp * wp_scale) ** 2 / (E * (E + 1j * (g0 + dgamma)))
        e = e - drude0 + drude1
        if void > 0: e = bruggeman(e, fill(l) ** 2, void) if abs(L - 1/3) < 1e-9 else bruggeman_L(fill(l) ** 2, e, 1 - void, L)
        return np.sqrt(e)
    return n


# ---------------------------------------------------------------- transfer matrices
def _stack(ns, ds, lam, n0, ns_, s0, pol):
    """coherent stack between semi-infinite media n0 (incidence) and ns_ (exit). s0 = n0 sin(theta0). Returns r, t, and the
    admittances needed for intensity transmission."""
    def cos_(n):
        c = np.sqrt(1 - (s0 / n) ** 2 + 0j); return np.where(c.imag < 0, -c, c)
    def eta(n, c): return n * c if pol == 's' else n / c
    c0, cs = cos_(n0), cos_(ns_)
    e0, es = eta(n0, c0), eta(ns_, cs)
    M11 = np.ones_like(lam, dtype=complex); M12 = np.zeros_like(M11); M21 = np.zeros_like(M11); M22 = np.ones_like(M11)
    for n, d in zip(ns, ds):
        c = cos_(n); ej = eta(n, c); dl = 2 * np.pi * n * c * d / lam
        a, b, cc, dd = np.cos(dl), -1j * np.sin(dl) / ej, -1j * ej * np.sin(dl), np.cos(dl)
        M11, M12, M21, M22 = M11 * a + M12 * cc, M11 * b + M12 * dd, M21 * a + M22 * cc, M21 * b + M22 * dd
    B = M11 + M12 * es; C = M21 + M22 * es
    r = (e0 * B - C) / (e0 * B + C); t = 2 * e0 / (e0 * B + C)
    R = np.abs(r) ** 2; T = np.real(es) / np.real(e0) * np.abs(t) ** 2
    return R, T


def device(lam, layers, side='film', theta=8.0, sub=BK7, ambient=AIR):
    """R, T (fractions) of  ambient / layers / thick substrate / air (side='film': light from the film side) or
    air / substrate / layers / ambient (side='glass'). layers: list of (n_func, thickness_nm) from the AMBIENT side.
    Unpolarised average of s and p; the substrate is incoherent."""
    lam = np.asarray(lam, float)
    na, ng, nair = ambient(lam), sub(lam), AIR(lam)
    nl = [f(lam) for f, d in layers]; dl = [d for f, d in layers]
    out = []
    for pol in ('s', 'p'):
        if side == 'film':
            s0 = na * np.sin(np.radians(theta))
            Rf, Tf = _stack(nl, dl, lam, na, ng, s0, pol)                      # ambient -> stack -> glass
            Rf2, _ = _stack(nl[::-1], dl[::-1], lam, ng, na, s0, pol)           # glass -> stack -> ambient (internal)
            Rb, Tb = _stack([], [], lam, ng, nair, s0, pol)                     # glass -> air (back face)
            # incoherent multiple reflections in the glass: forward intensity Tf, back face Rb, returning to the stack from the glass side
            # (absorption in the stack makes the stack's glass-side transmission back to the ambient equal to Tf by reciprocity)
            R = Rf + Tf * Rb * Tf / (1 - Rb * Rf2)
            T = Tf * Tb / (1 - Rb * Rf2)
        else:
            s0 = nair * np.sin(np.radians(theta))
            Ra, Ta = _stack([], [], lam, nair, ng, s0, pol)                     # air -> glass
            Rg, Tg = _stack(nl[::-1], dl[::-1], lam, ng, na, s0, pol)           # glass -> stack -> ambient
            Rg2, _ = _stack(nl, dl, lam, na, ng, s0, pol)
            R = Ra + Ta * Rg * Ta / (1 - Ra * Rg)
            T = Ta * Tg / (1 - Ra * Rg)
        out.append((R, T))
    return 0.5 * (out[0][0] + out[1][0]), 0.5 * (out[0][1] + out[1][1])


def tamm_layers(p):
    """parameter dict -> layer list from the ambient (silver) side: Ag / [TiO2 / SiO2] x N ... (top DBR layer under Ag first)"""
    sio = porous(SiO2, p.get('pore_fill', AIR), p['pS']); tio = porous(TiO2, p.get('pore_fill', AIR), p['pT'])
    L = []
    if p.get('dAg', 0) > 0:
        L.append((silver(p.get('ag', 'JC'), p.get('dgamma', 0.0), p.get('wp_scale', 1.0), p.get('void', 0.0), p.get('void_fill', AIR), p.get('L', 1/3)), p['dAg']))
    order = p.get('top', 'SiO2')                                   # material of the DBR layer touching the silver
    pair = [(sio, p['dS']), (tio, p['dT'])] if order == 'SiO2' else [(tio, p['dT']), (sio, p['dS'])]
    for k in range(p.get('N', 5)): L += pair
    return L


def tests():
    lam = np.linspace(400, 800, 5)
    # 1. bare glass, normal incidence: R = 2 * ((n-1)/(n+1))^2 / (1 + ((n-1)/(n+1))^2) (two faces, incoherent)
    n = BK7(lam).real; r = ((n - 1) / (n + 1)) ** 2; Rex = r + (1 - r) ** 2 * r / (1 - r ** 2)
    R, T = device(lam, [], theta=0.0); assert np.allclose(R, Rex, atol=1e-10) and np.allclose(R + T, 1, atol=1e-10)
    # 2. quarter-wave layer of index sqrt(n_glass) at 600 nm on glass: front-face reflection vanishes at 600 nm
    nq = np.sqrt(BK7(np.array([600.0])).real[0])
    Rf, _ = _stack([np.full(1, nq + 0j)], [600 / (4 * nq)], np.array([600.0]), np.ones(1, complex), BK7(np.array([600.0])), 0, 's')
    assert Rf[0] < 1e-12
    # 3. lossless stack: R + T = 1 for both sides and angles
    L = [(const(2.3), 70), (const(1.45), 100)] * 5
    for side in ('film', 'glass'):
        R, T = device(lam, L, side, 30.0); assert np.allclose(R + T, 1, atol=1e-10)
    # 4. 5-pair quarter-wave mirror at normal incidence: analytic peak reflectance of the coherent stack
    nH, nL, ng = 2.3, 1.45, 1.52; l0 = 600.0
    Ls = [np.full(1, nH + 0j), np.full(1, nL + 0j)] * 5; ds = [l0 / 4 / nH, l0 / 4 / nL] * 5
    Rq, _ = _stack(Ls, ds, np.array([l0]), np.ones(1, complex), np.full(1, ng + 0j), 0, 's')
    Y = (nH / nL) ** 10 * ng; Ra = ((1 - Y) / (1 + Y)) ** 2
    assert abs(Rq[0] - Ra) < 1e-12, (Rq, Ra)
    # 5. Bruggeman limits
    e1, e2 = np.array([2.0 + 0j]), np.array([5.0 + 0j]); assert np.allclose(bruggeman(e1, e2, 0.0), e1) and np.allclose(bruggeman(e1, e2, 1.0), e2)
    # 5b. generalised Bruggeman reduces to the spherical one at L = 1/3
    e1, e2 = np.array([1.0 + 0j]), np.array([-15 + 1j])
    assert np.allclose(bruggeman_L(e1, e2, 0.6, 1 / 3), bruggeman(e2, e1, 0.4)), (bruggeman_L(e1, e2, 0.6, 1/3), bruggeman(e2, e1, 0.4))
    # 6. silver(): no change -> identical to the table
    assert np.allclose(silver('JC')(lam), AG['JC'](lam))
    print('tmm tests passed')


if __name__ == '__main__':
    tests()
