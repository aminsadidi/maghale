"""Antenna modes from the Green function (BEM, MNPBEM job_tri2): spectral density -> Lorentzian modes (omega_j, kappa_j, g_j).

Normalised Green function at the emitter (columns ImG_x_c, ReG_x_c of job_tri2, x dipole at the gap centre):
    Gamma(omega) / Gamma0(omega) = 1 + ImG(omega)          (Purcell factor, Fp = 1 + ImG)
    delta(omega)                 = -(Gamma0(omega) / 2) ReG(omega)   (Lamb shift of the transition)
with Gamma0(omega) = Gamma0(omega_e) (omega / omega_e)^3 the rate in the homogeneous host.
Emitter coupled to N damped bosonic modes (quasi-normal-mode / Lorentzian spectral density):
    Gamma_sc(omega) = sum_j g_j^2 kappa_j / ((omega - omega_j)^2 + kappa_j^2 / 4)
    delta(omega)    = sum_j g_j^2 (omega - omega_j) / ((omega - omega_j)^2 + kappa_j^2 / 4) + delta_bg
The fit uses ImG only; the Lamb shift it predicts is then compared with the BEM ReG (Kramers-Kronig consistency).
All energies in eV (hbar omega); the coupling g_j depends on Gamma0 (dipole moment): g_j^2 = A_j kappa_j hbarGamma0 / 4.
usage: python isi/analysis/gmodes.py [stem]   (default L275_R295_A0_Y160_H3)"""
import os, sys
import numpy as np
from scipy.optimize import least_squares
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tri2  # noqa: E402
HC = 1239.841984


def load(stem='L275_R295_A0_Y160_H3', dip='x'):
    b, n = tri2.series(stem)
    if b is None: raise FileNotFoundError(stem)
    E = HC / b['lambda_nm']; o = np.argsort(E)
    g = lambda k: np.asarray(b[f'{k}_{dip}_c'])[o]
    return dict(E=E[o], ImG=g('ImG'), ReG=g('ReG'), Fp=g('Fp'), T=g('T'), na09=g('f_zNA09'), na13=g('f_zNA13'),
                py=g('f_py60'), my=g('f_my60'), stem=stem, chunks=n)


def lor(E, A, Ej, kj):
    """peak-normalised Lorentzian: A at E = Ej, FWHM kj"""
    return A * (kj / 2) ** 2 / ((E - Ej) ** 2 + (kj / 2) ** 2)


def model_im(p, E, Ee):
    """ImG(E): modes scaled by (Ee/E)^3 because ImG is normalised to Gamma0(E) ~ E^3; p = [A1, E1, k1, A2, E2, k2, ...]"""
    s = np.zeros_like(E)
    for j in range(len(p) // 3): s += lor(E, *p[3 * j:3 * j + 3])
    return s * (Ee / E) ** 3


def model_re(p, E, Ee):
    """ReG predicted by the same modes: delta_j / Gamma0(Ee) = A_j (k_j/4) (E - E_j) / ((E-E_j)^2 + k_j^2/4);  ReG = -2 delta / Gamma0(E)"""
    s = np.zeros_like(E)
    for j in range(len(p) // 3):
        A, Ej, kj = p[3 * j:3 * j + 3]
        s += A * (kj / 4) * (E - Ej) / ((E - Ej) ** 2 + (kj / 2) ** 2)
    return -2 * s * (Ee / E) ** 3


def fit(d, nmodes=2, Ee=HC / 1550):
    E, y = d['E'], d['ImG']
    i = int(np.argmax(y))
    p0 = [y[i], E[i], 0.06]
    if nmodes >= 2: p0 += [0.6 * y[i], HC / 1650, 0.35]
    if nmodes >= 3: p0 += [0.2 * y[i], HC / 1150, 0.3]
    lo = [0, 0.45, 0.005] * nmodes; hi = [1e5, 1.3, 1.5] * nmodes
    r = least_squares(lambda p: (model_im(p, E, Ee) - y) / np.maximum(y, 5), p0, bounds=(lo, hi))
    p = r.x
    # the modes predict ReG up to a constant (non-resonant, quasi-static higher-order modes): fit only that offset
    off = float(np.mean(d['ReG'] - model_re(p, E, Ee)))
    resid_im = np.sqrt(np.mean(((model_im(p, E, Ee) - y) / y) ** 2))
    resid_re = np.sqrt(np.mean((model_re(p, E, Ee) + off - d['ReG']) ** 2)) / np.ptp(d['ReG'])
    modes = sorted([dict(A=p[3 * j], E=p[3 * j + 1], kappa=p[3 * j + 2]) for j in range(nmodes)], key=lambda m: -m['E'])
    return dict(p=p, modes=modes, ReG_offset=off, rms_im=resid_im, rms_re=resid_re, Ee=Ee)


def at(d, k, lam=1550.0):
    return float(np.interp(HC / lam, d['E'], d[k]))


def couplings(f, tau0=2e-9):
    """g_j (eV) for an emitter of intrinsic lifetime tau0 at Ee: g_j^2 = A_j kappa_j hbarGamma0 / 4"""
    hg0 = 6.582119569e-16 / tau0
    return [dict(m, g=np.sqrt(m['A'] * m['kappa'] * hg0 / 4)) for m in f['modes']]


if __name__ == '__main__':
    stem = sys.argv[1] if len(sys.argv) > 1 else 'L275_R295_A0_Y160_H3'
    d = load(stem)
    for nm in (1, 2, 3):
        f = fit(d, nm)
        print(f'--- {nm} mode(s): rms rel. error ImG {f["rms_im"]:.3f}, ReG (predicted, one offset) {f["rms_re"]:.3f}, offset {f["ReG_offset"]:.1f}')
        for m in couplings(f):
            print(f"   E = {m['E']:.4f} eV ({HC/m['E']:.0f} nm)  hbar*kappa = {m['kappa']*1e3:.1f} meV (Q = {m['E']/m['kappa']:.1f})  "
                  f"A = {m['A']:.1f}  hbar*g = {m['g']*1e3:.3f} meV")
        Ee = f['Ee']; E = np.array([Ee])
        print(f"   at 1550 nm: ImG fit {model_im(f['p'], E, Ee)[0]:.1f} vs BEM {at(d, 'ImG'):.1f};  ReG fit {model_re(f['p'], E, Ee)[0] + f['ReG_offset']:.1f} vs BEM {at(d, 'ReG'):.1f}")
