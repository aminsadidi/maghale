"""
dd1d.py - One-dimensional drift-diffusion solar-cell device simulator
=====================================================================

Physics (same model class as SCAPS-1D, Burgelman et al., Thin Solid Films 361 (2000) 527):
  * Poisson equation with free carriers, ionised shallow dopants and charged
    deep defects (donor / acceptor / neutral, single level or Gaussian band)
  * Electron and hole continuity equations, Scharfetter-Gummel discretisation
  * Shockley-Read-Hall recombination through every bulk defect level
  * Heterojunctions: double nodes, continuous electrostatic potential,
    thermionic-emission carrier transfer across band offsets
  * Interface SRH recombination (density Nit, cm^-2)
  * Front/back contacts: Dirichlet potential (flat-band front contact,
    metal work function back contact) + surface recombination velocities
  * Optical generation: Beer-Lambert, alpha = A*sqrt(h*nu - Eg) (SCAPS
    "sqrt" model), ASTM G173 AM1.5G spectrum, illumination from the front
  * Small-signal AC analysis (admittance, C-V, impedance) by linearising the
    stationary system: (J + i*omega*M) dx = -dR/dV dV
  * Quantum efficiency by linear response of the illuminated steady state

Variables per node: electrostatic potential psi (V), electron and hole
quasi-Fermi energies Fn, Fp (eV). Energies in eV, lengths in cm.
The full Newton Jacobian is built exactly by the complex-step method with
graph colouring (no finite-difference error).

Author: thesis simulation package (open source, MIT licence).
"""
from __future__ import annotations

import os
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

Q = 1.602176634e-19        # C
KB = 8.617333262e-5        # eV/K
EPS0 = 8.8541878128e-14    # F/cm
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8

_HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def bern(x):
    """Bernoulli function B(x) = x/(exp(x)-1), complex-step safe."""
    x = np.asarray(x)
    small = np.abs(x.real) < 1e-5
    xs = np.where(small, 1.0, x)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        big = xs / np.expm1(xs)
    ser = 1.0 - x / 2.0 + x * x / 12.0
    out = np.where(small, ser, big)
    # very large positive x -> 0 (expm1 overflow gives nan/0)
    out = np.where(x.real > 700, 0.0, out)
    return out


def load_am15g(lam_min=300.0, lam_max=1000.0, dlam=2.0):
    """Return wavelength (nm) and photon flux (photons cm^-2 s^-1 nm^-1)."""
    path = os.path.join(_HERE, "ASTM_G173_AM15G.csv")
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    lam = np.arange(lam_min, lam_max + 1e-9, dlam)
    irr = np.interp(lam, data[:, 0], data[:, 1])           # W m^-2 nm^-1
    E_ph = H_PLANCK * C_LIGHT / (lam * 1e-9)                  # J
    flux = irr / E_ph * 1e-4                                  # cm^-2 s^-1 nm^-1
    return lam, flux


# --------------------------------------------------------------------------
# device definition
# --------------------------------------------------------------------------
class Layer:
    def __init__(self, name, d_nm, Eg, chi, eps, Nc, Nv, mun, mup, ND, NA,
                 defects=(), vth_n=1e7, vth_p=1e7, A_abs=1e5):
        self.name = name
        self.d = d_nm * 1e-7
        self.d_nm = d_nm
        self.Eg, self.chi, self.eps = Eg, chi, eps
        self.Nc, self.Nv = Nc, Nv
        self.mun, self.mup = mun, mup
        self.ND, self.NA = ND, NA
        self.defects = list(defects)
        self.vth_n, self.vth_p = vth_n, vth_p
        self.A_abs = A_abs

    def copy(self, **kw):
        new = Layer(self.name, self.d_nm, self.Eg, self.chi, self.eps, self.Nc,
                    self.Nv, self.mun, self.mup, self.ND, self.NA,
                    [dict(x) for x in self.defects], self.vth_n, self.vth_p,
                    self.A_abs)
        for k, v in kw.items():
            if k == "d_nm":
                new.d_nm = v
                new.d = v * 1e-7
            else:
                setattr(new, k, v)
        return new


def defect(kind, Nt, Et_above_Ev, sn=1e-15, sp_=1e-15, dist="single",
           Echar=0.1):
    return dict(kind=kind, Nt=Nt, Et=Et_above_Ev, sn=sn, sp=sp_, dist=dist,
                Echar=Echar)


class Device:
    """Stack of layers, front (x=0, illuminated) to back."""

    def __init__(self, layers, T=300.0, front_Sn=1e7, front_Sp=1e5,
                 back_Sn=1e5, back_Sp=1e7, back_wf=5.1, front_flatband=True,
                 interface_defects=None, absorber_index=None,
                 te_velocity=1e7, scale_dos_with_T=True):
        self.layers = layers
        self.T = T
        self.Vt = KB * T
        self.front_Sn, self.front_Sp = front_Sn, front_Sp
        self.back_Sn, self.back_Sp = back_Sn, back_Sp
        self.back_wf = back_wf
        self.front_flatband = front_flatband
        # interface_defects: dict {interface_index: dict(Nit, Et_above_Ev_absorber, sn, sp)}
        self.interface_defects = interface_defects or {}
        self.absorber_index = absorber_index
        self.te_velocity = te_velocity
        self.scale_dos_with_T = scale_dos_with_T
        self._build()

    # ---------------------------------------------------------------- mesh
    @staticmethod
    def _layer_mesh(d, hmin=1e-8, ratio=1.12, nmax_frac=1 / 40.0):
        hmax = max(d * nmax_frac, hmin)
        hmin = min(hmin, d / 20.0)
        # graded from both sides
        steps = []
        h = hmin
        while True:
            steps.append(h)
            h = min(h * ratio, hmax)
            if 2 * sum(steps) >= d:
                break
        left = np.cumsum([0.0] + steps)
        left = left[left < d / 2]
        right = d - left[::-1]
        x = np.unique(np.concatenate([left, right]))
        # remove too-close points around the centre
        keep = [0]
        for i in range(1, len(x)):
            if x[i] - x[keep[-1]] > 0.3 * hmin:
                keep.append(i)
        x = x[keep]
        x[-1] = d
        return x

    def _build(self):
        T = self.T
        tf = (T / 300.0) ** 1.5 if self.scale_dos_with_T else 1.0
        xs, lid = [], []
        x0 = 0.0
        for k, L in enumerate(self.layers):
            xl = self._layer_mesh(L.d)
            xs.append(x0 + xl)
            lid.append(np.full(len(xl), k))
            x0 += L.d
        self.x = np.concatenate(xs)
        self.lid = np.concatenate(lid)
        self.N = len(self.x)
        self.Ltot = x0
        g = lambda attr: np.array([getattr(self.layers[k], attr) for k in self.lid], float)
        self.Eg = g("Eg"); self.chi = g("chi"); self.eps = g("eps")
        self.Nc = g("Nc") * tf; self.Nv = g("Nv") * tf
        self.mun = g("mun"); self.mup = g("mup")
        self.ND = g("ND"); self.NA = g("NA")
        self.vthn = g("vth_n"); self.vthp = g("vth_p")
        # links
        dx = np.diff(self.x)
        self.same = self.lid[:-1] == self.lid[1:]          # SG link vs interface
        self.h = np.where(self.same, dx, 1.0)
        # control volumes
        vol = np.zeros(self.N)
        vol[:-1] += np.where(self.same, dx / 2, 0.0)
        vol[1:] += np.where(self.same, dx / 2, 0.0)
        self.vol = vol
        # interfaces: link index k where same==False ; nodes k (L) and k+1 (R)
        self.iface_links = np.where(~self.same)[0]
        # bulk defect levels (expanded gaussian)
        self._defect_levels()
        # interface recombination parameters
        self._iface_rec()
        # contacts
        L0 = self.layers[0]
        Vt = self.Vt
        Nc0 = self.Nc[0]; Nv0 = self.Nv[0]
        net0 = L0.ND - L0.NA
        # front contact Fermi level for flat band (charge neutral)
        if net0 >= 0:
            n0 = 0.5 * (net0 + np.sqrt(net0 ** 2 + 4 * Nc0 * Nv0 * np.exp(-L0.Eg / Vt)))
            self.EF0 = -L0.chi + Vt * np.log(n0 / Nc0)   # with psi=0
        else:
            p0 = 0.5 * (-net0 + np.sqrt(net0 ** 2 + 4 * Nc0 * Nv0 * np.exp(-L0.Eg / Vt)))
            self.EF0 = -L0.chi - L0.Eg - Vt * np.log(p0 / Nv0)
        self.psi_front = 0.0

    def _defect_levels(self):
        """Expand all bulk defects into discrete levels per node."""
        gh_x, gh_w = np.polynomial.hermite.hermgauss(9)
        levels = []   # tuples (mask_nodes_array(float Nt per node), Et_above_Ev per node, sn, sp, kind)
        for k, L in enumerate(self.layers):
            m = (self.lid == k).astype(float)
            for dft in L.defects:
                if dft["dist"] == "gauss":
                    # SCAPS gauss: N(E) ~ exp(-((E-Et)/Ekar)^2)  ->  E = Et + Ekar*x_k
                    Es = dft["Et"] + dft["Echar"] * gh_x
                    ws = gh_w / np.sqrt(np.pi)
                else:
                    Es, ws = np.array([dft["Et"]]), np.array([1.0])
                for E, w in zip(Es, ws):
                    E = float(np.clip(E, 0.02, L.Eg - 0.02))
                    levels.append(dict(Nt=m * dft["Nt"] * w, Et=E, sn=dft["sn"],
                                       sp=dft["sp"], kind=dft["kind"]))
        self.levels = levels

    def _iface_rec(self):
        self.iface = []
        for j, k in enumerate(self.iface_links):
            if j in self.interface_defects:
                dd = self.interface_defects[j]
                # choose absorber-side node
                lidL, lidR = self.lid[k], self.lid[k + 1]
                if self.absorber_index is not None and lidR == self.absorber_index:
                    node = k + 1
                elif self.absorber_index is not None and lidL == self.absorber_index:
                    node = k
                else:
                    node = k + 1
                self.iface.append(dict(node=node, Nit=dd["Nit"], Et=dd["Et"],
                                       sn=dd.get("sn", 1e-15), sp=dd.get("sp", 1e-15)))

    # ---------------------------------------------------------------- physics
    def carriers(self, psi, Fn, Fp):
        Vt = self.Vt
        Ec = -self.chi - psi
        Ev = Ec - self.Eg
        n = self.Nc * np.exp((Fn - Ec) / Vt)
        p = self.Nv * np.exp((Ev - Fp) / Vt)
        return n, p, Ec, Ev

    def srh(self, n, p):
        """Total bulk SRH rate and trapped charge density (cm^-3)."""
        Vt = self.Vt
        R = 0.0
        rho_t = 0.0
        for lv in self.levels:
            Nt = lv["Nt"]
            if not np.any(Nt):
                continue
            n1 = self.Nc * np.exp(-(self.Eg - lv["Et"]) / Vt)
            p1 = self.Nv * np.exp(-lv["Et"] / Vt)
            cn = lv["sn"] * self.vthn
            cp = lv["sp"] * self.vthp
            den = cn * (n + n1) + cp * (p + p1)
            R = R + Nt * cn * cp * (n * p - n1 * p1) / den
            f = (cn * n + cp * p1) / den        # electron occupancy
            if lv["kind"] == "donor":
                rho_t = rho_t + Nt * (1 - f)
            elif lv["kind"] == "acceptor":
                rho_t = rho_t - Nt * f
        return R, rho_t

    def generation(self, lam, flux):
        """G(x) (cm^-3 s^-1) per node for given spectrum; also returns per-lambda G."""
        E_ph = 1239.84193 / lam  # eV
        alpha_l = []
        for L in self.layers:
            a = L.A_abs * np.sqrt(np.clip(E_ph - L.Eg, 0, None))
            alpha_l.append(a)
        alpha_l = np.array(alpha_l)            # (nlayers, nlam)
        # optical depth at node
        x = self.x
        tau = np.zeros((self.N, len(lam)))
        xstart = 0.0
        acc = np.zeros(len(lam))
        starts = []
        for k, L in enumerate(self.layers):
            starts.append((xstart, acc.copy()))
            acc = acc + alpha_l[k] * L.d
            xstart += L.d
        for i in range(self.N):
            k = self.lid[i]
            xs, a0 = starts[k]
            tau[i] = a0 + alpha_l[k] * (x[i] - xs)
        Gl = alpha_l[self.lid] * flux[None, :] * np.exp(-tau)   # per nm
        return Gl  # (N, nlam)

    # ---------------------------------------------------------------- residual
    def residual(self, X, V, G):
        N = self.N
        psi = X[0::3]; Fn = X[1::3]; Fp = X[2::3]
        Vt = self.Vt
        n, p, Ec, Ev = self.carriers(psi, Fn, Fp)
        R, rho_t = self.srh(n, p)
        rho = p - n + self.ND - self.NA + rho_t
        e0q = EPS0 / Q
        h = self.h
        same = self.same
        # ---- link quantities
        eps_link = np.where(same, self.eps[:-1], 0.0)
        Dlink = np.where(same, self.eps[:-1] * (psi[1:] - psi[:-1]) / h, 0.0)  # eps*dpsi/dx
        # SG currents (particle current densities scaled so that J = q*j)
        Dn = self.mun[:-1] * Vt
        Dp = self.mup[:-1] * Vt
        dEc = (Ec[1:] - Ec[:-1]) / Vt
        dEv = (Ev[1:] - Ev[:-1]) / Vt
        dEc_s = np.where(same, dEc, 0.0)
        dEv_s = np.where(same, dEv, 0.0)
        jn_sg = Dn / h * (bern(-dEc_s) * n[1:] - bern(dEc_s) * n[:-1])
        jp_sg = Dp / h * (bern(-dEv_s) * p[:-1] - bern(dEv_s) * p[1:])
        # thermionic emission across interfaces
        v = self.te_velocity
        chiL, chiR = self.chi[:-1], self.chi[1:]
        EgL, EgR = self.Eg[:-1], self.Eg[1:]
        bn = np.maximum(0.0, chiL - chiR) / Vt           # barrier for e- going L->R
        bp = np.maximum(0.0, (chiR + EgR) - (chiL + EgL)) / Vt  # barrier for h+ going L->R
        bn = np.where(same, 0.0, bn); bp = np.where(same, 0.0, bp)
        argn = np.where(same, 0.0, dEc - bn)
        argp = np.where(same, 0.0, -dEv - bp)
        fl_n = v * (n[:-1] * np.exp(-bn) - n[1:] * (self.Nc[:-1] / self.Nc[1:]) * np.exp(argn))
        fl_p = v * (p[:-1] * np.exp(-bp) - p[1:] * (self.Nv[:-1] / self.Nv[1:]) * np.exp(argp))
        jn_te = -fl_n
        jp_te = fl_p
        jn = np.where(same, jn_sg, jn_te)
        jp = np.where(same, jp_sg, jp_te)
        # ---- contacts
        EF_front = self.EF0
        EF_back = self.EF0 - V
        nf0 = self.Nc[0] * np.exp((EF_front - Ec[0]) / Vt)
        pf0 = self.Nv[0] * np.exp((Ev[0] - EF_front) / Vt)
        nb0 = self.Nc[-1] * np.exp((EF_back - Ec[-1]) / Vt)
        pb0 = self.Nv[-1] * np.exp((Ev[-1] - EF_back) / Vt)
        jn_left = self.front_Sn * (n[0] - nf0)
        jp_left = -self.front_Sp * (p[0] - pf0)
        jn_right = -self.back_Sn * (n[-1] - nb0)
        jp_right = self.back_Sp * (p[-1] - pb0)
        jn_all = np.concatenate([[jn_left], jn, [jn_right]])
        jp_all = np.concatenate([[jp_left], jp, [jp_right]])
        # ---- interface recombination
        Rit = np.zeros(N, dtype=X.dtype)
        for it in self.iface:
            i = it["node"]
            Sn = it["sn"] * self.vthn[i] * it["Nit"]
            Spp = it["sp"] * self.vthp[i] * it["Nit"]
            n1 = self.Nc[i] * np.exp(-(self.Eg[i] - it["Et"]) / Vt)
            p1 = self.Nv[i] * np.exp(-it["Et"] / Vt)
            r = (n[i] * p[i] - n1 * p1) / ((n[i] + n1) / Spp + (p[i] + p1) / Sn)
            Rit = Rit + np.where(np.arange(N) == i, r, 0.0)
        net = (R - G) * self.vol + Rit
        res_n = jn_all[1:] - jn_all[:-1] - net
        res_p = jp_all[1:] - jp_all[:-1] + net
        # ---- Poisson
        res_psi = np.zeros(N, dtype=X.dtype)
        Dl = np.concatenate([[0.0], Dlink])   # flux entering from left link
        Dr = np.concatenate([Dlink, [0.0]])
        res_psi = e0q * (Dr - Dl) + rho * self.vol
        # interface pairs: node k (L) : psi_L - psi_R ; node k+1 (R): combined
        for k in self.iface_links:
            comb = res_psi[k] + res_psi[k + 1]
            res_psi = np.where(np.arange(N) == k, (psi[k] - psi[k + 1]) * 1e12, res_psi)
            res_psi = np.where(np.arange(N) == k + 1, comb, res_psi)
        # Dirichlet contacts
        psi_back = -(EF_back) - self.back_wf
        res_psi = np.where(np.arange(N) == 0, (psi[0] - self.psi_front) * 1e12, res_psi)
        res_psi = np.where(np.arange(N) == N - 1, (psi[-1] - psi_back) * 1e12, res_psi)
        Rv = np.empty(3 * N, dtype=X.dtype)
        Rv[0::3] = res_psi
        Rv[1::3] = res_n
        Rv[2::3] = res_p
        return Rv

    def terminal_current(self, X, V):
        """Total current density (A/cm^2), positive = photocurrent direction."""
        psi = X[0::3]; Fn = X[1::3]; Fp = X[2::3]
        n, p, Ec, Ev = self.carriers(psi, Fn, Fp)
        Vt = self.Vt
        nf0 = self.Nc[0] * np.exp((self.EF0 - Ec[0]) / Vt)
        pf0 = self.Nv[0] * np.exp((Ev[0] - self.EF0) / Vt)
        jn_left = self.front_Sn * (n[0] - nf0)
        jp_left = -self.front_Sp * (p[0] - pf0)
        return Q * (jn_left + jp_left)

    # ---------------------------------------------------------------- jacobian
    def jacobian(self, X, V, G, mode="full"):
        N3 = 3 * self.N
        ncol = 15
        hcs = 1e-30
        rows, cols, vals = [], [], []
        node_of = np.arange(N3) // 3
        R0 = None
        for c in range(ncol):
            idx = np.arange(c, N3, ncol)
            Xc = X.astype(complex)
            Xc[idx] += 1j * hcs
            Rc = self.residual(Xc, V, G)
            if R0 is None:
                R0 = Rc.real
            d = Rc.imag / hcs
            # map each row to the perturbed column within +-2 nodes
            rn = node_of
            var_c = c % 3
            # perturbed columns: k = c + m*ncol ; node(k) = (c + m*15)//3
            # for each row, find perturbed col with |node - rn|<=2
            # node(k) for k in idx
            kn = node_of[idx]
            # create lookup from node -> column idx (node spacing of perturbed cols = 5)
            lookup = -np.ones(self.N + 5, dtype=int)
            lookup[kn] = idx
            col = -np.ones(N3, dtype=int)
            for off in (-2, -1, 0, 1, 2):
                nn = rn + off
                ok = (nn >= 0) & (nn < self.N)
                cand = np.where(ok, lookup[np.clip(nn, 0, self.N + 4)], -1)
                col = np.where((col < 0) & (cand >= 0), cand, col)
            mask = (col >= 0) & (d != 0)
            rows.append(np.where(mask)[0]); cols.append(col[mask]); vals.append(d[mask])
        J = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                          shape=(N3, N3))
        return J, R0

    # ---------------------------------------------------------------- solvers
    def equilibrium_guess(self):
        """Local charge neutrality guess at equilibrium (all Fermi levels = EF0)."""
        Vt = self.Vt
        EF = self.EF0
        net = self.ND - self.NA
        ni2 = self.Nc * self.Nv * np.exp(-self.Eg / Vt)
        n = np.where(net >= 0, 0.5 * (net + np.sqrt(net ** 2 + 4 * ni2)), 0.0)
        p = np.where(net < 0, 0.5 * (-net + np.sqrt(net ** 2 + 4 * ni2)), 0.0)
        n = np.where(net < 0, ni2 / np.maximum(p, 1e-300), n)
        # psi from n: n = Nc exp((EF + chi + psi)/Vt)
        psi = Vt * np.log(np.maximum(n, 1e-300) / self.Nc) - EF - self.chi
        X = np.zeros(3 * self.N)
        X[0::3] = psi
        X[1::3] = EF
        X[2::3] = EF
        return X

    def newton(self, X, V, G, tol=1e-10, maxit=80, verbose=False, damp=0.3,
               poisson_only=False):
        for it in range(maxit):
            J, R = self.jacobian(X, V, G)
            if poisson_only:
                J = J[0::3, :][:, 0::3]
                R = R[0::3]
            # row equilibration
            rs = np.asarray(np.abs(J).max(axis=1).todense()).ravel()
            rs[rs == 0] = 1.0
            Js = sp.diags(1.0 / rs) @ J
            cs = np.asarray(np.abs(Js).max(axis=0).todense()).ravel()
            cs[cs == 0] = 1.0
            Js = Js @ sp.diags(1.0 / cs)
            try:
                dx = spla.spsolve(Js.tocsc(), -(R / rs)) / cs
            except Exception:
                return X, False
            if not np.all(np.isfinite(dx)):
                return X, False
            mx = np.max(np.abs(dx))
            # per-component logarithmic damping (Sesame/Bank-Rose type)
            a = self.Vt
            dx = np.sign(dx) * a * np.log1p(np.abs(dx) / a)
            dx = np.clip(dx, -damp, damp)
            if poisson_only:
                X = X.copy(); X[0::3] += dx
            else:
                X = X + dx
            if verbose:
                print(it, mx)
            if mx < tol:
                return X, True
        return X, False

    def solve_equilibrium(self, verbose=False):
        X = self.equilibrium_guess()
        G0 = np.zeros(self.N)
        X, ok = self.newton(X, 0.0, G0, verbose=verbose, poisson_only=True,
                            maxit=300)
        if not ok:
            raise RuntimeError("equilibrium Poisson did not converge")
        X, ok = self.newton(X, 0.0, G0, verbose=verbose)
        if not ok:
            raise RuntimeError("equilibrium did not converge")
        return X

    def solve_bias(self, X, V0, V1, G, dV=0.05):
        """Continuation in voltage from V0 to V1."""
        V = V0
        step = dV if V1 >= V0 else -dV
        while (V1 - V) * np.sign(step) > 1e-12:
            Vn = V + step
            if (V1 - Vn) * np.sign(step) < 0:
                Vn = V1
            Xn, ok = self.newton(X.copy(), Vn, G)
            if ok:
                X, V = Xn, Vn
            else:
                step /= 2
                if abs(step) < 1e-5:
                    raise RuntimeError(f"bias continuation failed at {V}")
        return X

    def ramp_light(self, X, V, Gfull, nsteps=6):
        for s in np.logspace(-4, 0, nsteps):
            X, ok = self.newton(X, V, Gfull * s)
            if not ok:
                X, ok = self.newton(X, V, Gfull * s, damp=0.05, maxit=300)
                if not ok:
                    raise RuntimeError("light ramp failed")
        return X


# --------------------------------------------------------------------------
# high-level analyses
# --------------------------------------------------------------------------
class Simulation:
    def __init__(self, device: Device, lam_range=(300.0, 900.0), dlam=2.0):
        self.dev = device
        self.lam, self.flux = load_am15g(*lam_range, dlam)
        self.Gl = device.generation(self.lam, self.flux)       # (N, nlam)
        self.G = np.trapezoid(self.Gl, self.lam, axis=1)
        self.Xeq = device.solve_equilibrium()
        self.Xsc = None

    # J-V ---------------------------------------------------------------
    def jv(self, Vmax=1.8, dV=0.01, light=True):
        dev = self.dev
        G = self.G if light else np.zeros(dev.N)
        X = self.Xeq.copy()
        if light:
            X = dev.ramp_light(X, 0.0, G)
            self.Xsc = X.copy()
        Vs, Js, Xs = [], [], []
        V = 0.0
        while V <= Vmax + 1e-9:
            X = dev.solve_bias(X, Vs[-1] if Vs else 0.0, V, G, dV=dV)
            J = dev.terminal_current(X, V)
            Vs.append(V); Js.append(J); Xs.append(X.copy())
            if light and J < -0.03:   # well past Voc
                break
            V = round(V + dV, 10)
        Vs = np.array(Vs); Js = np.array(Js) * 1e3   # mA/cm2
        return Vs, Js, Xs

    @staticmethod
    def jv_params(V, J):
        """Voc (V), Jsc (mA/cm2), FF (%), PCE (%), Vmp, Jmp."""
        Jsc = float(np.interp(0.0, V, J))
        # Voc from sign change
        idx = np.where(J <= 0)[0]
        if len(idx) == 0:
            Voc = np.nan
        else:
            i = idx[0]
            Voc = float(V[i - 1] + (V[i] - V[i - 1]) * J[i - 1] / (J[i - 1] - J[i]))
        Vf = np.linspace(0, V[-1], 4000)
        Jf = np.interp(Vf, V, J)
        P = Vf * Jf
        k = np.argmax(P)
        Pmax = P[k]
        FF = 100 * Pmax / (Voc * Jsc) if Voc == Voc else np.nan
        PCE = Pmax  # mW/cm2 over 100 mW/cm2 input => %
        return dict(Voc=Voc, Jsc=Jsc, FF=FF, PCE=PCE, Vmp=Vf[k], Jmp=Jf[k])

    # QE ------------------------------------------------------------------
    def qe(self, V=0.0, X=None):
        """External QE (%) by linear response around the illuminated state."""
        dev = self.dev
        if X is None:
            X = self.Xsc if self.Xsc is not None else dev.ramp_light(self.Xeq.copy(), 0.0, self.G)
        J, _ = dev.jacobian(X, V, self.G)
        J = J.tocsc()
        lu = spla.splu(J)
        # derivative of terminal current wrt X (only node-0 carriers)
        dJdX = np.zeros(3 * dev.N)
        hcs = 1e-30
        for k in (0, 1, 2):
            Xc = X.astype(complex); Xc[k] += 1j * hcs
            dJdX[k] = dev.terminal_current(Xc, V).imag / hcs
        qe = []
        for il in range(len(self.lam)):
            g = self.Gl[:, il] / self.flux[il]           # per unit photon flux
            dR = np.zeros(3 * dev.N)
            dR[1::3] = -g * dev.vol
            dR[2::3] = +g * dev.vol
            dx = lu.solve(-dR)
            dJ = dJdX @ dx                                   # A/cm2 per (photon/cm2/s)
            qe.append(dJ / Q * 100)
        return self.lam.copy(), np.array(qe)

    # AC -----------------------------------------------------------------
    def admittance(self, X, V, G, freqs):
        """Small-signal admittance Y(f) (S/cm^2) at bias state X."""
        dev = self.dev
        N = dev.N
        J, _ = dev.jacobian(X, V, G)
        psi = X[0::3]; Fn = X[1::3]; Fp = X[2::3]
        n, p, _, _ = dev.carriers(psi, Fn, Fp)
        Vt = dev.Vt
        # mass matrix: d n/dt term: res_n -= vol*dn/dt ; res_p += vol*dp/dt
        rows, cols, vals = [], [], []
        for i in range(N):
            # n = Nc exp((Fn + chi + psi)/Vt): dn/dpsi = n/Vt, dn/dFn = n/Vt
            rows += [3 * i + 1, 3 * i + 1]; cols += [3 * i, 3 * i + 1]
            vals += [-dev.vol[i] * n[i] / Vt, -dev.vol[i] * n[i] / Vt]
            # p = Nv exp((-chi-Eg-psi - Fp)/Vt): dp/dpsi = -p/Vt, dp/dFp = -p/Vt
            rows += [3 * i + 2, 3 * i + 2]; cols += [3 * i, 3 * i + 2]
            vals += [-dev.vol[i] * p[i] / Vt, -dev.vol[i] * p[i] / Vt]
        M = sp.csr_matrix((vals, (rows, cols)), shape=(3 * N, 3 * N))
        # dR/dV : back Dirichlet row psi_N - psi_back(V); psi_back = -(EF0 - V) - wf
        dRdV = np.zeros(3 * N)
        dRdV[3 * (N - 1)] = -1e12
        # also back contact carrier equilibrium densities depend on V
        Xc = X.astype(complex)
        hcs = 1e-30
        Rc = dev.residual(Xc, V + 1j * hcs, G)
        dRdV = Rc.imag / hcs
        # conduction current derivative at front
        dJdX = np.zeros(3 * N, dtype=complex)
        for k in (0, 1, 2):
            Xc = X.astype(complex); Xc[k] += 1j * hcs
            dJdX[k] = dev.terminal_current(Xc, V).imag / hcs
        Y = []
        h0 = dev.x[1] - dev.x[0]
        for f in freqs:
            w = 2 * np.pi * f
            A = (J + 1j * w * M).tocsc()
            dx = spla.spsolve(A, -dRdV.astype(complex))
            dJc = dJdX @ dx
            # displacement current at x=0: eps0*eps*dE/dt, E=-(psi1-psi0)/h
            dE = -(dx[3] - dx[0]) / h0
            dJd = 1j * w * EPS0 * dev.eps[0] * dE
            # sign: terminal current positive = photocurrent direction (front->back
            # inside device). Admittance for forward bias current: Y = -dJ/dV
            Y.append(-(dJc + dJd))
        return np.array(Y)

    # profiles -------------------------------------------------------------
    def profiles(self, X, G):
        dev = self.dev
        psi = X[0::3]; Fn = X[1::3]; Fp = X[2::3]
        n, p, Ec, Ev = dev.carriers(psi, Fn, Fp)
        R, rho_t = dev.srh(n, p)
        E = -np.gradient(psi, dev.x)
        # avoid gradient across double nodes
        x = dev.x
        Ef = np.zeros_like(x)
        for i in range(len(x)):
            if i > 0 and x[i] - x[i - 1] > 0:
                a = i - 1
            elif i > 1:
                a = i - 2
            else:
                a = None
            if i < len(x) - 1 and x[i + 1] - x[i] > 0:
                b = i + 1
            elif i < len(x) - 2:
                b = i + 2
            else:
                b = None
            if a is None:
                a = i
            if b is None:
                b = i
            Ef[i] = -(psi[b] - psi[a]) / (x[b] - x[a])
        return dict(x_nm=x * 1e7, Ec=Ec, Ev=Ev, Fn=Fn, Fp=Fp, n=n, p=p, R=R, G=G,
                    E_Vcm=Ef, psi=psi, layer=dev.lid)
