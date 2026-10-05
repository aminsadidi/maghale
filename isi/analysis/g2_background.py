"""Single-photon purity limited by the photoluminescence (PL) of the gold rod itself.

Pulsed excitation at lambda_p, pulse fluence Phi (photons per nm^2), emitter (absorption cross-section sigma_e,
intrinsic quantum yield q0) on the axis at gap d, emitting at the rod resonance:
    signal per pulse      S = [1 - exp(-sigma_e E_exc Phi)] * eta(q0)          (E_exc = |E_z|^2/|E_0|^2, BEM)
    background per pulse  B = Phi * sigma_abs(lambda_p) * Y_PL * f_band          (sigma_abs: BEM, polarisation along rod)
The fluence is chosen so that the emitter is excited with probability 1 - 1/e (sigma_e E_exc Phi = 1). Gold PL is
Poissonian, so for a perfect single-photon emitter plus uncorrelated background
    g2(0) = (2 S B + B^2) / (S + B)^2  ~  2 B / S.
Both are collected with the same efficiency (same dipolar pattern), so the collection drops out.
Y_PL = 1e-6 (single gold nanorods, Yorulmaz et al. 2012), f_band = 1 (all PL in the detection band: upper bound).
usage: python isi/analysis/g2_background.py  -> isi/results/g2_background.md
"""
import os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')


def load(f):
    return np.genfromtxt(os.path.join(RES, f), delimiter=',', names=True, skip_header=1)


def main(Y=1e-6, fband=1.0):
    ab = load('bem_extra/absorption_rod.csv'); ex = load('bem_extra/excitation_rod.csv')
    rod = load('bem_raw/rod_L60_h1.5_air.csv')
    out = ['# Gold-PL background and single-photon purity (rod 60 x 20 nm, axial dipole, pump polarised along the rod)', '',
           f'Y_PL = {Y:g}, f_band = {fband:g}; emitter excited with probability 1-1/e per pulse; emitter emits at the radiative peak.', '']
    lam_ab = ab['lambda_nm']
    out += ['| pump (nm) | sigma_abs rod (nm^2) | sigma_sca rod (nm^2) |', '|---|---|---|']
    for lp in (405, 450, 532, 610):
        i = np.argmin(abs(lam_ab - lp)); out.append(f'| {lp} | {ab["abs_z"][i]:.0f} | {ab["sca_z"][i]:.0f} |')
    out += ['', '| gap | q0 | eta | pump | E_exc | sigma_e (nm^2) | B/S | g2(0) |', '|---|---|---|---|---|---|---|---|']
    res = {}
    for g in (5, 10, 20):
        Tz, Fz = rod[f'T_z_g{g}'], rod[f'Fp_z_g{g}']; i = np.argmax(Tz)
        for q0 in (1.0, 0.1):
            eta = Tz[i] / (Fz[i] + (1 - q0) / q0)
            for lp in (405, 532, 610):
                E = np.interp(lp, ex['lambda_nm'], ex[f'Ez2_polz_g{g}'])
                sa = np.interp(lp, lam_ab, ab['abs_z'])
                for se in (0.01, 1.0):
                    S = (1 - np.exp(-1)) * eta; B = (1 / (se * E)) * sa * Y * fband
                    g2 = (2 * S * B + B * B) / (S + B) ** 2
                    res[(g, q0, lp, se)] = (eta, E, B / S, g2)
                    out.append(f'| {g} | {q0} | {100*eta:.1f}% | {lp} | {E:.1f} | {se} | {B/S:.3g} | {g2:.3f} |')
    # minimum emitter cross-section for g2(0) < 0.1 (B/S < 0.05)
    out += ['', 'Minimum emitter absorption cross-section for g2(0) < 0.1 (B/S < 0.05), q0 = 1:', '']
    for g in (5, 10, 20):
        Tz, Fz = rod[f'T_z_g{g}'], rod[f'Fp_z_g{g}']; i = np.argmax(Tz); eta = Tz[i] / Fz[i]
        row = []
        for lp in (405, 532, 610):
            E = np.interp(lp, ex['lambda_nm'], ex[f'Ez2_polz_g{g}']); sa = np.interp(lp, lam_ab, ab['abs_z'])
            row.append(f'{lp} nm: {sa*Y*fband/(0.05*(1-np.exp(-1))*eta*E):.2g} nm^2')
        out.append(f'- gap {g}: ' + ', '.join(row))
    open(os.path.join(RES, 'g2_background.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
    return res


if __name__ == '__main__':
    main()
