"""Quantum model of the emitter coupled to the antenna modes obtained from the Green function (gmodes.py).

Hilbert space: two-level emitter (g, e) x Fock spaces of the antenna modes b_j (vacuum fluctuations; the coherent part driven by the
laser is the classical amplitude alpha_j(t), see below). Frame rotating at the laser frequency omega_L (hbar = 1, energies in eV):
    H(t) = -De s+s-  - sum_j Dj b_j^+ b_j  + sum_j g_j (b_j^+ s- + s+ b_j)  + (1/2) Om_loc(t) (s+ + s-)
    De = omega_L - (omega_e + delta_bg),   Dj = omega_L - omega_j
    Om_loc(t) = Om_inc(t) [1 + sum_j 2 g_j alpha_j / Om_inc]  =  K Om_inc(t)  (laser field + field scattered by the antenna)
dissipators: kappa_j D[b_j] (antenna mode loss: radiation + absorption), Gamma_d D[s-] (direct decay: free-space Gamma0 + the small
part of ImG the modes do not reproduce), 2 gamma* D[s+ s-] (pure dephasing).
The laser drives the antenna modes far harder than the emitter (antenna dipole >> emitter dipole); because kappa_j (60-300 meV) is much
larger than the pulse bandwidth (~9 meV for 200 fs), the antenna follows the laser instantaneously and the emitter sees the laser
multiplied by the local-field enhancement K (from reciprocity, |K|^2 = T D(+z)/D0(+z)). The pulse is set so that the LOCAL pulse is a
Gaussian pi pulse; K then only fixes the incident pulse energy (reported) and the coherent background.
Outputs, from the two-time correlations of the emitted field (quantum regression):
    N, g2(0) = 2 int int G2 / N^2, I = 2 int int |G1|^2 / N^2
for the detection operator A = sum_j sqrt(kappa_j) b_j + sqrt(Gamma_d) s-  (the field leaving the emitter-antenna system) and for A = s-.
Effective (Markov, adiabatic elimination of the modes) model for comparison: two-level emitter with
    Gamma = Gamma_d + sum_j g_j^2 kappa_j / (Dej^2 + kappa_j^2/4),  delta = delta_bg + sum_j g_j^2 Dej / (Dej^2 + kappa_j^2/4), Dej = omega_e - omega_j
usage: from qmodel import params, solve"""
import os, sys
import numpy as np
from scipy.linalg import expm
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gmodes  # noqa: E402
HB = 6.582119569e-16; HC = 1239.841984


def params(stem='L275_R295_A0_Y160_H3', tau0=2e-9, lam_e=1550.0, nmodes=2):
    """emitter-antenna parameters (eV) from the BEM Green function of one geometry"""
    d = gmodes.load(stem); Ee = HC / lam_e
    f = gmodes.fit(d, nmodes, Ee)
    E = d['E']; pr = gmodes.model_re(f['p'], E, Ee)
    X = np.c_[(Ee / E) ** 3, np.ones_like(E)]; c, *_ = np.linalg.lstsq(X, d['ReG'] - pr, rcond=None)   # non-resonant ReG background
    rms_re = float(np.sqrt(np.mean((d['ReG'] - pr - X @ c) ** 2)) / np.ptp(d['ReG']))
    hg0 = HB / tau0                                   # hbar Gamma0 (eV) in the host, at lam_e
    modes = gmodes.couplings(f, tau0)
    ImG_e = gmodes.at(d, 'ImG', lam_e); ReG_e = gmodes.at(d, 'ReG', lam_e)
    ImG_fit = float(gmodes.model_im(f['p'], np.array([Ee]), Ee)[0])
    delta_bg = -0.5 * hg0 * float(c[0] + c[1])        # constant non-resonant Lamb shift (eV)
    P = dict(stem=stem, Ee=Ee, hg0=hg0, modes=modes, Gd=hg0 * (1 + max(ImG_e - ImG_fit, 0.0)), delta_bg=delta_bg,
             ImG_e=ImG_e, ReG_e=ReG_e, ImG_fit=ImG_fit, rms_im=f['rms_im'], rms_re=rms_re, Fp=gmodes.at(d, 'Fp', lam_e),
             T=gmodes.at(d, 'T', lam_e), na09=gmodes.at(d, 'na09', lam_e), na13=gmodes.at(d, 'na13', lam_e),
             ratio=gmodes.at(d, 'py', lam_e) / gmodes.at(d, 'my', lam_e))
    # effective Markov rate and shift at the emitter frequency
    G = P['Gd']; dl = delta_bg
    for m in modes:
        D = Ee - m['E']; den = D ** 2 + m['kappa'] ** 2 / 4
        G += m['g'] ** 2 * m['kappa'] / den; dl += m['g'] ** 2 * D / den
    P['G_eff'], P['delta_eff'] = G, dl
    P['delta_green'] = -0.5 * hg0 * ReG_e             # Lamb shift directly from the BEM ReG
    # local-field enhancement by reciprocity: |K|^2 = T * D(+z) / D0(+z), D from the NA 0.9 cone fractions (x dipole, n = 1.5)
    P['K'] = float(np.sqrt(P['T'] * P['na09'] / na_fraction_dipole(0.9)))
    return P


def na_fraction_dipole(NA, n=1.5):
    """fraction of the power of an x-oriented dipole in a homogeneous medium collected in a cone of numerical aperture NA about +z"""
    tm = np.arcsin(NA / n); th = np.linspace(0, tm, 4001)
    # angular power density ~ 1 - sin^2(th) cos^2(phi); integrate phi analytically: 2 pi - pi sin^2(th)
    return float(np.trapezoid((2 * np.pi - np.pi * np.sin(th) ** 2) * np.sin(th), th) * 3 / (8 * np.pi))


# ------------------------------------------------------------------------------------------------- generic Lindblad solver
def _liou(H, cops):
    I = np.eye(H.shape[0])
    L = -1j * (np.kron(I, H) - np.kron(H.T, I))
    for c in cops:
        cd = c.conj().T @ c
        L += np.kron(c.conj(), c) - 0.5 * np.kron(I, cd) - 0.5 * np.kron(cd.T, I)
    return L


def build(P, gstar, laser_detuning=0.0, explicit=True, nf=2):
    """operators in units where the effective decay rate G_eff = 1. laser_detuning: omega_L - (omega_e + delta_eff) in eV
    (0 = laser on the shifted, i.e. dressed, transition)."""
    s = P['G_eff']                                         # energy scale (eV)
    wL = P['Ee'] + P['delta_eff'] + laser_detuning
    sm2 = np.array([[0, 1], [0, 0]], complex)
    if not explicit:
        De = (wL - (P['Ee'] + P['delta_eff'])) / s
        H0 = -De * sm2.conj().T @ sm2; Hd = 0.5 * (sm2 + sm2.conj().T)
        c = [np.sqrt(1.0) * sm2, np.sqrt(2 * gstar / s) * sm2.conj().T @ sm2]
        return H0, Hd, c, sm2, sm2, (2,)
    nm = len(P['modes']); dims = [2] + [nf] * nm
    def op(k, o):
        mats = [np.eye(dd, dtype=complex) for dd in dims]; mats[k] = o
        out = mats[0]
        for m in mats[1:]: out = np.kron(out, m)
        return out
    b1 = np.diag(np.sqrt(np.arange(1, nf)), 1).astype(complex)
    sm = op(0, sm2); sp = sm.conj().T; bs = [op(j + 1, b1) for j in range(nm)]
    De = (wL - (P['Ee'] + P['delta_bg'])) / s
    H0 = -De * sp @ sm
    for m, b in zip(P['modes'], bs):
        H0 += -((wL - m['E']) / s) * b.conj().T @ b + (m['g'] / s) * (b.conj().T @ sm + sp @ b)
    Hd = 0.5 * (sm + sp)
    cops = [np.sqrt(m['kappa'] / s) * b for m, b in zip(P['modes'], bs)] + [np.sqrt(P['Gd'] / s) * sm, np.sqrt(2 * gstar / s) * sp @ sm]
    A = sum(np.sqrt(m['kappa'] / s) * b for m, b in zip(P['modes'], bs)) + np.sqrt(P['Gd'] / s) * sm
    return H0, Hd, cops, A, sm, tuple(dims)


def solve(P, tau_p, gstar, laser_detuning=0.0, explicit=True, nf=2, dt=0.004, detect='A'):
    """tau_p (s): intensity FWHM of the LOCAL Gaussian pi pulse; gstar (eV). Returns N (relative), g2, I."""
    H0, Hd, cops, A, sm, dims = build(P, gstar, laser_detuning, explicit, nf)
    if detect == 's': A = sm
    s = P['G_eff'] / HB                                    # 1/s
    taup = tau_p * s
    sf = np.sqrt(2) * taup / (2 * np.sqrt(2 * np.log(2))); Am = np.pi / (np.sqrt(2 * np.pi) * sf); t0 = 4 * sf
    tp_end = t0 + 4 * sf; T = tp_end + 12.0; df = min(sf / 25, dt)
    t = np.unique(np.r_[np.arange(0, tp_end, df), np.arange(tp_end, T + dt / 2, dt)]); nt = len(t) - 1; h = np.diff(t)
    Om = lambda tt: Am * np.exp(-0.5 * ((tt - t0) / sf) ** 2)
    L0 = _liou(H0, cops); Ld = _liou(Hd, []) - _liou(np.zeros_like(Hd), [])
    cache = {}; U = []
    for k in range(nt):
        o = Om(t[k] + h[k] / 2)
        if o < 1e-10 * Am:
            key = round(h[k], 12)
            if key not in cache: cache[key] = expm(L0 * h[k])
            U.append(cache[key])
        else: U.append(expm((L0 + o * Ld) * h[k]))
    D = H0.shape[0]; vec = lambda X: X.reshape(-1, order='F'); unvec = lambda v: v.reshape(D, D, order='F')
    rho0 = np.zeros((D, D), complex); rho0[0, 0] = 1
    rho = np.zeros((nt + 1, D * D), complex); rho[0] = vec(rho0)
    for k in range(nt): rho[k + 1] = U[k] @ rho[k]
    Ad = A.conj().T; n_op = Ad @ A
    flux = np.real(rho @ vec(n_op.T)); N = np.trapezoid(flux, t)
    pe = np.real(rho @ vec((np.kron(np.array([[0, 0], [0, 1]]), np.eye(D // 2)) if explicit else np.array([[0, 0], [0, 1]])).T))
    w = np.zeros(nt + 1); w[:-1] += h / 2; w[1:] += h / 2
    trAd = vec(Ad.T); trN = vec(n_op.T)
    X = np.zeros((nt + 1, D * D), complex); Y = np.zeros((nt + 1, D * D), complex); S1 = S2 = 0.0
    for k in range(nt + 1):
        r = unvec(rho[k]); X[k] = vec(A @ r); Y[k] = vec(A @ r @ Ad)
        g1 = X[:k + 1] @ trAd; g2 = Y[:k + 1] @ trN
        wtau = np.full(k + 1, (h[k - 1] if k > 0 else 0) / 2 + (h[k] if k < nt else 0) / 2); wtau[k] = (h[k] if k < nt else 0) / 2
        S1 += np.sum(w[:k + 1] * wtau * np.abs(g1) ** 2); S2 += np.sum(w[:k + 1] * wtau * np.real(g2))
        if k < nt:
            UT = U[k].T; X[:k + 1] = X[:k + 1] @ UT; Y[:k + 1] = Y[:k + 1] @ UT
    return dict(N=N, g2=2 * S2 / N ** 2, I=2 * S1 / N ** 2, pe_max=float(pe.max()), npts=nt + 1)


if __name__ == '__main__':
    P = params()
    for k in ('Ee', 'hg0', 'Gd', 'delta_bg', 'G_eff', 'delta_eff', 'delta_green', 'K', 'Fp', 'T'):
        print(k, P[k])
    for m in P['modes']: print(m)
