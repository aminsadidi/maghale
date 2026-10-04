# Colab results summary

## Stage A: gold sphere vs exact Mie (radial dipole, 5 nm gap)

| grid (nm) | median abs err Fp | max abs err Fp | median abs err T | Fp peak Meep | Fp peak Mie |
|---|---|---|---|---|---|
| 2.00 | 215.3% | 532.9% | 10.2% | 2184 @ 520 | 802 @ 506 |
| 1.33 | 108.0% | 155.1% | 8.4% | 1628 @ 510 | 802 @ 506 |
| 1.00 | 93.2% | 127.1% | 7.2% | 1525 @ 510 | 802 @ 506 |
| extrapolated (0) | 47.7% | 366.5% | 4.4% | 974 @ 501 | 802 @ 506 |

PML check (1-nm grid, 0.15 vs 0.30 um): median |dFp| 8.9%, max 19.6%; median |dT| 0.1%

## Stage B: mesh convergence, rod, axial dipole, 5 nm gap

| grid (nm) | Fp max | lambda_Fp | T max | lambda_T | eta at T peak | coll NA0.9 at T peak |
|---|---|---|---|---|---|---|
| 2.00 | 3129 | 624 | 148.7 | 631 | 5.0% | 0.18 |
| 1.33 | 3364 | 534 | 134.4 | 617 | 5.6% | 0.18 |
| 1.00 | 2319 | 604 | 124.9 | 611 | 5.9% | 0.18 |

Change between the two finest grids: Fp 31.1%, T 7.0%, lambda_T 7 nm.
Extrapolated to zero grid spacing: Fp 2694 @ 604 nm, T 222.4 @ 604 nm, eta at T peak 8.3%

## Orientation ratios (grid 1.00 nm)

- rod Fp_axial/Fp_transverse: max 169789 at 492 nm; min -118670.49
- rod T ratio: max 518 at 611 nm
- sphere radial/tangential Fp: -74087.07 to 111444.54
