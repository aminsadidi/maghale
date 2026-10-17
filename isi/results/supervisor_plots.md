# Supervisor-requested plots: maps, LDOS vs distance, host-index tuning

## Field and LDOS maps (z = 0 plane, n = 1.5)

| case | max E2/E0^2 (x-pol) | E2 at gap centre | Fp_x at centre | max Fp_x in map (x, y) | min Fp_x in map | Fp_x at (0, +-20) |
|---|---|---|---|---|---|---|
| L270_w1550 | 600 | 282 | 272 | 682 (16, 2) | 49 | 160 / 160 |
| L270_R300_A0_Y160_w1550 | 327 | 153 | 212 | 554 (16, -2) | 37 | 124 / 125 |
| L270_R300_A0_Y160_w1520 | 316 | 148 | 238 | 610 (16, -2) | 42 | 139 / 142 |

## LDOS vs emitter-tip distance h (x dipole on the dimer axis)

| structure | lambda | h = 3 | h = 5 | h = 10 | h = 20 | h = 30 |
|---|---|---|---|---|---|---|
| dimer, gap 10 nm | 1310 | 1208 | 1056 | -- | -- | -- |
| dimer, gap 10 nm | 1480 | 3287 | 3051 | -- | -- | -- |
| dimer, gap 10 nm | 1550 | 4638 | 4349 | -- | -- | -- |
| dimer, gap 10 nm | 1660 | 5771 | 5428 | -- | -- | -- |
| dimer, gap 20 nm | 1310 | 618 | 424 | 331 | -- | -- |
| dimer, gap 20 nm | 1480 | 1487 | 1176 | 971 | -- | -- |
| dimer, gap 20 nm | 1550 | 1832 | 1472 | 1222 | -- | -- |
| dimer, gap 20 nm | 1660 | 1832 | 1454 | 1204 | -- | -- |
| dimer, gap 40 nm | 1310 | -- | 291 | 155 | 101 | -- |
| dimer, gap 40 nm | 1480 | -- | 578 | 354 | 258 | -- |
| dimer, gap 40 nm | 1550 | -- | 614 | 378 | 276 | -- |
| dimer, gap 40 nm | 1660 | -- | 534 | 319 | 233 | -- |
| dimer, gap 60 nm | 1310 | -- | 299 | 149 | 65 | 47 |
| dimer, gap 60 nm | 1480 | -- | 423 | 234 | 128 | 105 |
| dimer, gap 60 nm | 1550 | -- | 416 | 228 | 126 | 104 |
| dimer, gap 60 nm | 1660 | -- | 354 | 185 | 102 | 85 |
| trimer (R3 parallel), gap 40 | 1310 | -- | 282 | 152 | 100 | -- |
| trimer (R3 parallel), gap 40 | 1480 | -- | 674 | 425 | 311 | -- |
| trimer (R3 parallel), gap 40 | 1550 | -- | 481 | 291 | 212 | -- |
| trimer (R3 parallel), gap 40 | 1660 | -- | 407 | 237 | 171 | -- |

(h < 4 nm is below the 4-5 nm mesh resolution: indicative only)

## Tuning with the host index (dimer L = 270 nm, gap 40 nm)

| n | lambda_T | T max | Fp | eta | T(1310) | T(1550) |
|---|---|---|---|---|---|---|
| 1.33 | 1367 | 248 | 282 | 88% | 227 | 165 |
| 1.45 | 1483 | 242 | 276 | 88% | 123 | 225 |
| 1.5 | 1532 | 239 | 273 | 87% | 89 | 237 |
| 1.6 | 1628 | 232 | 268 | 87% | 47 | 208 |
| 1.7 | 1725 | 226 | 263 | 86% | 26 | 139 |

Linear fit: lambda_T = 967 n + 82 nm  ->  n(1310) = 1.27, n(1550) = 1.52

