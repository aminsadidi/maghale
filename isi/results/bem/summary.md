# MNPBEM (BEM) results

## Gold sphere (R = 15.874 nm) vs exact Mie, Johnson-Christy

| case | gap | median abs err Fp_z | max | median abs err T_z | median abs err Fp_x | median abs err T_x | Fp_z peak BEM / Mie |
|---|---|---|---|---|---|---|---|
| sph_n1444_air | 5 | 0.91% | 4.22% | 1.36% | 0.71% | 1.00% | 802 / 771 |
| sph_n1444_air | 10 | 1.51% | 3.82% | 1.31% | 0.52% | 1.14% | 99 / 95 |
| sph_n1444_air | 20 | 0.85% | 3.26% | 1.26% | 0.09% | 1.19% | 11 / 10 |
| sph_n400_air | 5 | 2.36% | 6.53% | 1.83% | 2.09% | 0.97% | 781 / 771 |
| sph_n400_air | 10 | 1.92% | 4.81% | 1.48% | 0.49% | 1.11% | 99 / 95 |
| sph_n400_air | 20 | 1.04% | 4.39% | 1.33% | 0.08% | 1.19% | 11 / 10 |
| sph_n784_air | 5 | 0.96% | 4.37% | 1.37% | 0.69% | 0.86% | 800 / 771 |
| sph_n784_air | 10 | 1.83% | 3.90% | 1.33% | 0.53% | 1.11% | 99 / 95 |
| sph_n784_air | 20 | 0.88% | 3.30% | 1.28% | 0.08% | 1.19% | 11 / 10 |
| sph_n784_water | 5 | 0.61% | 4.42% | 1.42% | 0.68% | 0.77% | 777 / 769 |
| sph_n784_water | 10 | 0.66% | 3.01% | 1.38% | 0.50% | 1.10% | 104 / 103 |
| sph_n784_water | 20 | 0.40% | 2.88% | 1.30% | 0.07% | 1.18% | 12 / 12 |

## Rod L = 60 nm, axial dipole, mesh convergence (element size h)

| h (nm) | gap | Fp max | lambda_Fp | T max | lambda_T | eta at T peak |
|---|---|---|---|---|---|---|
| 3 | 3 | 3672 | 508 | 209.8 | 608 | 6.5% |
| 2 | 3 | 3768 | 508 | 213.9 | 608 | 6.6% |
| 1.5 | 3 | 3782 | 508 | 214.1 | 608 | 6.6% |
| 3 | 5 | 1649 | 604 | 117.7 | 608 | 7.3% |
| 2 | 5 | 1643 | 604 | 117.0 | 608 | 7.3% |
| 1.5 | 5 | 1638 | 604 | 116.5 | 608 | 7.3% |
| 3 | 7 | 933 | 604 | 69.9 | 608 | 7.7% |
| 2 | 7 | 930 | 604 | 69.4 | 608 | 7.6% |
| 1.5 | 7 | 928 | 604 | 69.2 | 612 | 8.3% |
| 3 | 10 | 455 | 604 | 36.3 | 612 | 9.0% |
| 2 | 10 | 454 | 604 | 36.2 | 612 | 8.9% |
| 1.5 | 10 | 453 | 604 | 36.1 | 612 | 8.9% |
| 3 | 15 | 172 | 604 | 15.6 | 612 | 10.1% |
| 2 | 15 | 172 | 604 | 15.5 | 612 | 10.1% |
| 1.5 | 15 | 172 | 604 | 15.5 | 612 | 10.0% |
| 3 | 20 | 78 | 604 | 8.3 | 612 | 11.7% |
| 2 | 20 | 78 | 604 | 8.3 | 612 | 11.6% |
| 1.5 | 20 | 78 | 604 | 8.2 | 612 | 11.6% |

Change between the two finest meshes (5 nm gap): Fp 0.3%, T 0.4%, eta 0.3%

## Finest rod mesh (h = 1.5 nm): orientation ratios and gap dependence

- gap 3 nm: Fp_z max 3782 @ 508 nm, T_z max 214.1 @ 608 nm, eta(q0=1) 6.6%; Fp ratio z/x max 19 @ 608 nm; T ratio max 1410
- gap 5 nm: Fp_z max 1638 @ 604 nm, T_z max 116.5 @ 608 nm, eta(q0=1) 7.3%; Fp ratio z/x max 49 @ 608 nm; T ratio max 329
- gap 7 nm: Fp_z max 928 @ 604 nm, T_z max 69.2 @ 612 nm, eta(q0=1) 8.3%; Fp ratio z/x max 88 @ 608 nm; T ratio max 135
- gap 10 nm: Fp_z max 453 @ 604 nm, T_z max 36.1 @ 612 nm, eta(q0=1) 8.9%; Fp ratio z/x max 136 @ 608 nm; T ratio max 54
- gap 15 nm: Fp_z max 172 @ 604 nm, T_z max 15.5 @ 612 nm, eta(q0=1) 10.0%; Fp ratio z/x max 128 @ 608 nm; T ratio max 19
- gap 20 nm: Fp_z max 78 @ 604 nm, T_z max 8.2 @ 612 nm, eta(q0=1) 11.6%; Fp ratio z/x max 75 @ 604 nm; T ratio max 9
- orientation average at 608 nm, 5 nm gap: <Fp> 555, <T> 39.1, <eta> 7.0%

## Aspect-ratio sweep (h = 2 nm) and water

| case | gap | lambda_T | T max | Fp at T peak | eta |
|---|---|---|---|---|---|
| rod_L100_h2_air | 5 | 760 | 1006.5 | 4477 | 22.5% |
| rod_L100_h2_air | 10 | 760 | 315.4 | 1389 | 22.7% |
| rod_L100_h2_air | 20 | 760 | 64.5 | 277 | 23.3% |
| rod_L40_h2_air | 5 | 560 | 18.3 | 719 | 2.5% |
| rod_L40_h2_air | 10 | 565 | 6.6 | 131 | 5.1% |
| rod_L40_h2_air | 20 | 570 | 2.4 | 17 | 14.5% |
| rod_L50_h2_air | 5 | 585 | 47.0 | 979 | 4.8% |
| rod_L50_h2_air | 10 | 585 | 15.3 | 246 | 6.2% |
| rod_L50_h2_air | 20 | 590 | 4.2 | 34 | 12.3% |
| rod_L60_h2_air | 3 | 608 | 213.9 | 3260 | 6.6% |
| rod_L60_h2_air | 5 | 608 | 117.0 | 1603 | 7.3% |
| rod_L60_h2_air | 7 | 608 | 69.4 | 909 | 7.6% |
| rod_L60_h2_air | 10 | 612 | 36.2 | 406 | 8.9% |
| rod_L60_h2_air | 15 | 612 | 15.5 | 155 | 10.1% |
| rod_L60_h2_air | 20 | 612 | 8.3 | 71 | 11.6% |
| rod_L60_h2_water | 5 | 715 | 457.3 | 2309 | 19.8% |
| rod_L60_h2_water | 10 | 715 | 134.3 | 664 | 20.2% |
| rod_L60_h2_water | 20 | 715 | 25.1 | 118 | 21.3% |
| rod_L80_h2_air | 5 | 680 | 638.2 | 3454 | 18.5% |
| rod_L80_h2_air | 10 | 680 | 196.0 | 1039 | 18.9% |
| rod_L80_h2_air | 20 | 680 | 39.2 | 197 | 19.9% |
