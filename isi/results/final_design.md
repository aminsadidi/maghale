# Final telecom design: trimer R1 = R2 = 285 nm, gap 40 nm, R3 = 315 nm horizontal at y = 160 nm (BEM)

D = 60 nm, host n = 1.5, gold = Johnson-Christy (MNPBEM gold.dat), retarded BEM with curved elements.
Mesh: R1/R2 h, R3 1.4 h. x dipole at the gap centre. Spectra 1100-1900 nm in 20 nm steps (parabolic peak refinement).

| quantity | h = 4 nm (final) | h = 5 nm (earlier) | change |
|---|---|---|---|
| peak of Fp (nm) | 1488 | 1481 | +7 nm |
| Fp at the peak | 467 | 458 | +2.0% |
| peak of T (nm) | 1489 | 1483 | +7 nm |
| T at its peak | 275 | 270 | +1.9% |
| eta at the T peak | 59.1% | 59.1% | -0.0 pp |
| Fp(1550) | 313 | 294 | +6.5% |
| T(1550) | 204 | 196 | +4.1% |
| eta(1550) | 65.1% | 66.7% | -1.5 pp |
| f(+y) 60 deg cone (1550) | 0.623 | 0.617 | +1.0% |
| f(-y) 60 deg cone (1550) | 0.130 | 0.121 | +7.0% |
| ratio f(+y)/f(-y) (1550) | 4.81 | 5.10 | -5.6% |
| best ratio | 5.75 | 5.48 | +5.0% |
|   at (nm) | 1580 | 1560 | +20 nm |
| collection NA 1.3 (1550) | 0.253 | 0.260 | -2.4% |
| collection NA 0.9 (1550) | 0.105 | 0.110 | -4.8% |

Dimer alone (same R1, R2, h = 4 nm, mirror-symmetric run): Fp peak 304 at 1605 nm; at 1550 nm Fp = 288, T = 248, eta = 86.1%. The third rod changes T(1550) by -18% and makes the emission directional (dimer ratio = 1 by symmetry).

## Robustness at 1550 nm (h = 4 nm)

| emitter | dipole | Fp | T | eta | f(+y)/f(-y) |
|---|---|---|---|---|---|
| gap centre | x | 313.3 | 204.1 | 65.1% | 4.81 |
| gap centre | y | 0.8 | 0.3 | 44.7% | 1.09 |
| gap centre | z | 0.7 | 0.3 | 40.7% | 1.04 |
| 5 nm along x | x | 338.2 | 219.9 | 65.0% | 4.80 |
| 5 nm along x | y | 1.0 | 0.3 | 31.1% | 1.09 |
| 5 nm along x | z | 1.0 | 0.3 | 27.7% | 1.04 |
| 10 nm along y | x | 269.4 | 175.9 | 65.3% | 4.79 |
| 10 nm along y | y | 1.4 | 0.8 | 54.6% | 1.33 |
| 10 nm along y | z | 0.7 | 0.3 | 46.7% | 1.03 |

The x dipole (along the rods) dominates: y and z dipoles couple weakly (Fp ~ 1, no enhancement), so the emitter must be oriented along the dimer axis.
The direction of emission switches with wavelength: f(-y) > f(+y) below 1460-1480 nm, f(+y) > f(-y) above it (Fig. c).
