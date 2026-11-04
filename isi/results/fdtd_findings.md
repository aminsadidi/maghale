# FDTD cross-check: interpretation (run of 2026-11-04, Lumerical 2024 R1, 6 of 7 runs; wg_dimer still running)

Data: `isi/data/lab_20261104b/lumerical`, tables in `fdtd_vs_bem.md`, figures `fig_fdtd_vs_bem.png`, `fig_fdtd_extra.png`.

1. **The two methods agree once the BEM mesh error is included.** FDTD lies inside the BEM band between the h^2 and the
   fitted-order extrapolation (h -> 0), see `meshconv_spectra.md`:

   | | BEM h -> 0 band | FDTD (gap 1 nm, rods 2 nm) |
   |---|---|---|
   | dimer, peak of Fp (nm) | 1630 - 1672 | 1657 |
   | dimer, Fp max | 314 - 332 | 324 |
   | trimer, peak of Fp (nm) | 1511 - 1529 | 1533 (at the edge) |
   | trimer, Fp max | 508 - 547 | 533 |
   | antenna efficiency at the peak | dimer 86.0%, trimer 58.4% (h = 2 / 2.5 nm) | 87.2%, 58.9% |

   The efficiency agrees within 1.2 pp; the finite-mesh BEM (h = 4 nm) places the resonances 43 - 53 nm too blue.
2. **Consequence for the design.** With the converged resonance the trimer peaks at about 1530 nm instead of 1489 nm, so 1550 nm
   lies close to the resonance (FDTD: Fp(1550) = 502, eta = 59%) and the in-plane asymmetry switches sign near 1554 nm (FDTD box
   faces) instead of 1468 nm (BEM cones). The design must be retuned about 40 nm to the blue (rods about 10 nm shorter, from
   d(lambda_T)/dL = 4.2 nm/nm of the dimer sweep) to put the directional window back on 1550 nm.
3. **Directionality, FDTD.** Box-face ratio +y/-y: maximum 2.37 at 1649 nm, below 1 under 1554 nm. Box faces are a near-field
   measure and not the far-field cone measure of BEM; a far-field projection in FDTD is needed for a quantitative comparison.
4. **Waveguide (trimer above Si3N4, FDTD only).** Wavelength-dependent routing: -y dominates below about 1580 nm
   (beta(-y) = 15% near 1400 - 1450 nm), +y above (beta(+y) = 14% at about 1660 nm, +y/-y up to 6.2 at 1700 nm). At 1550 nm:
   beta(+y) = 8.0%, beta(-y) = 12.1%, total 20%.
5. **FDTD convergence.** Gap mesh 2 -> 1 nm: changes below 1%; 1 -> 0.5 nm: peak +5 nm, Fp max +7%, T(1550) -3%. The rods stay
   at 2 nm (staircased metal surface) in all runs, so the FDTD values carry a few per cent and a few nm of their own uncertainty.
