# Mesh convergence of the full spectra (1300-1700 nm, mirror symmetry), gap centre, x dipole

## dimer (L = 285 nm)

| h (nm) | faces (full) | peak lambda (nm) | peak Fp | T at peak | eta at peak | Fp(1550) | T(1550) |
|---|---|---|---|---|---|---|---|
| 8 | 2448 | 1578.3 | 293.1 | 254.6 | 86.9% | 288.9 | 250.9 |
| 5 | 6308 | 1596.1 | 300.4 | 258.9 | 86.2% | 289.2 | 249.3 |
| 4 | 9888 | 1605.1 | 303.9 | 261.6 | 86.1% | 288.0 | 248.0 |
| 3 | 17536 | 1614.9 | 307.8 | 264.7 | 86.0% | 285.9 | 246.1 |
| 2.5 | 24928 | 1620.3 | 309.9 | 266.6 | 86.0% | 284.5 | 244.9 |
| 2.25 | 30576 | 1623.1 | 311.0 | 267.5 | 86.0% | 283.7 | 244.2 |
| 2 | 39744 | 1626.3 | 312.3 | 268.6 | 86.0% | 282.6 | 243.4 |

Richardson (h^2 -> 0, h <= 5 nm): peak lambda = 1629.6 nm, peak Fp = 313.6, Fp(1550) = 282.4
Change from the finest computed mesh to the extrapolated limit: peak lambda +3.3 nm, peak Fp +0.4%, Fp(1550) -0.1%
Observed order (fit y0 + b h^p on h <= 4 nm): peak lambda (nm): p = 0.55, limit 1671.7 (finest mesh h = 2 nm: 1626.3; h^2-Richardson above: 1629.6)
Observed order (fit y0 + b h^p on h <= 4 nm): peak Fp: p = 0.51, limit 332.0 (finest mesh h = 2 nm: 312.3; h^2-Richardson above: 313.6)
-> p < 2: the h^2 extrapolation underestimates the remaining shift; the limit lies between the h^2 and the fitted-p value.

## trimer (L = 285, R3 = 315 nm horizontal)

| h (nm) | faces (full) | peak lambda (nm) | peak Fp | T at peak | eta at peak | Fp(1550) | T(1550) |
|---|---|---|---|---|---|---|---|
| 8 | 3588 | 1473.8 | 457.7 | 267.3 | 58.4% | 275.3 | 184.3 |
| 6 | 6448 | 1482.3 | 468.5 | 272.1 | 58.1% | 294.0 | 190.7 |
| 5 | 9398 | 1487.8 | 475.4 | 275.7 | 58.0% | 308.1 | 196.3 |
| 4.5 | 11562 | 1490.9 | 479.9 | 278.7 | 58.1% | 317.5 | 200.4 |
| 4 | 14852 | 1494.6 | 485.0 | 280.8 | 57.9% | 329.7 | 205.9 |
| 3.5 | 19656 | 1498.3 | 489.6 | 284.3 | 58.1% | 342.0 | 211.6 |
| 3 | 26880 | 1502.1 | 495.4 | 287.8 | 58.1% | 356.9 | 218.8 |
| 2.75 | 32620 | 1504.1 | 498.3 | 289.2 | 58.0% | 365.4 | 223.0 |
| 2.5 | 38304 | 1506.0 | 500.7 | 290.9 | 58.1% | 372.9 | 226.7 |

Richardson (h^2 -> 0, h <= 5 nm): peak lambda = 1511.1 nm, peak Fp = 507.9, Fp(1550) = 389.4
Change from the finest computed mesh to the extrapolated limit: peak lambda +5.1 nm, peak Fp +1.4%, Fp(1550) +4.4%
Observed order (fit y0 + b h^p on h <= 4 nm): peak lambda (nm): p = 0.85, limit 1529.2 (finest mesh h = 2.5 nm: 1506.0; h^2-Richardson above: 1511.1)
Observed order (fit y0 + b h^p on h <= 4 nm): peak Fp: p = 0.64, limit 546.8 (finest mesh h = 2.5 nm: 500.7; h^2-Richardson above: 507.9)
-> p < 2: the h^2 extrapolation underestimates the remaining shift; the limit lies between the h^2 and the fitted-p value.

