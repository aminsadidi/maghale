"""Quantum regime of the nanorod antenna, from the BEM results (no new simulation).
1) Coupling regime. For a single mode in the bad-cavity limit, the mode-induced rate is Gamma_mode = 4 g^2 / kappa, with
   Gamma_mode = Fp_mode * Gamma_0. Hence hbar g = sqrt(Fp_mode * hbar Gamma_0 * hbar kappa) / 2. Strong coupling requires
   2g > (kappa + gamma)/2 (Torma & Barnes 2015), i.e. g > kappa/4 for a narrow emitter, or Fp_mode > kappa / (4 Gamma_0).
   kappa and Fp_mode are taken from the retarded pole fits (isi/analysis/pole_fit.py); Gamma_0 is bounded from above by
   a radiative lifetime of 1 ns (dyes, quantum dots, colour centres have tau_rad >= ~1 ns).
2) Indistinguishability I = Gamma / (Gamma + 2 gamma*) for an emitter with pure dephasing gamma* in the bad-cavity regime
   (Grange et al. PRL 2015), Gamma = total decay rate of an emitter with q0 = 1, Gamma = Fp * Gamma_0.
usage: python isi/analysis/quantum.py -> isi/results/quantum.md"""
import numpy as np
hbar_eVs = 6.582e-16
hG0 = hbar_eVs / 1e-9                       # hbar * Gamma_0 for tau_rad = 1 ns  (0.66 ueV)
# from the retarded pole fits: (aspect ratio, gap) -> (Fp_z at pole, mode share, full width hbar*kappa in eV)
fits = {(3, 3): (2628, 0.726, 0.145), (3, 5): (1464, 0.882, 0.133), (3, 10): (444, 0.939, 0.132),
        (4, 5): (3581, 0.972, 0.086), (4, 10): (1074, 0.971, 0.089), (5, 5): (4454, 1.00, 0.085), (5, 10): (1379, 1.00, 0.085)}
out = ['# Quantum regime', '', f'hbar Gamma_0 = {1e6*hG0:.2f} ueV (tau_rad = 1 ns, upper bound for single molecular/solid-state emitters)', '',
       '| AR | gap | Fp_mode | hbar kappa (meV) | hbar g (meV) | g/(kappa/4) | Fp_mode needed for strong coupling | gap in orders of magnitude |',
       '|---|---|---|---|---|---|---|---|']
for (ar, g), (F, sh, k) in fits.items():
    Fm = F * sh
    hg = np.sqrt(Fm * hG0 * k) / 2
    need = k / (4 * hG0)
    out.append(f'| {ar} | {g} | {Fm:.0f} | {1e3*k:.0f} | {1e3*hg:.1f} | {hg/(k/4):.2f} | {need:.1e} | {np.log10(need/Fm):.1f} |')
out += ['', '## Indistinguishability I = Gamma/(Gamma + 2 gamma*) (q0 = 1, tau_rad = 1 ns)', '',
        '| Fp | hbar Gamma (meV) | gamma* = 1 ueV (4 K) | 10 ueV | 1 meV | 10 meV (room T) |', '|---|---|---|---|---|---|']
for F in (1, 78, 453, 1638, 4454):
    hG = F * hG0
    out.append(f'| {F} | {1e3*hG:.4f} | ' + ' | '.join(f'{100*hG/(hG+2*gs):.1f}%' for gs in (1e-6, 1e-5, 1e-3, 1e-2)) + ' |')
open('isi/results/quantum.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
