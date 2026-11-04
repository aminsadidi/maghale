# FDTD (Lumerical) versus BEM (MNPBEM): final telecom design

FDTD input: `data/lab_20261104b/lumerical`

## 1. Peak, Purcell factor and efficiency

| structure | method | peak of T (nm) | T max | eta at T peak | peak of Fp (nm) | Fp max | Fp(1550) | T(1550) | eta(1550) |
|---|---|---|---|---|---|---|---|---|---|
| dimer | FDTD (gap 1 nm) | 1658 | 283 | 87.2% | 1657 | 324 | 270 | 235 | 87.0% |
| dimer | BEM h = 4 nm | 1604 | 262 | 86.1% | 1605 | 304 | 288 | 248 | 86.1% |
| dimer | BEM h = 2 nm | 1625 | 269 | 86.0% | 1626 | 312 | 283 | 243 | 86.1% |
| dimer | **FDTD - BEM (h = 4)** | **+53 nm** | **+8.0%** | | | | **-6.4%** | **-5.4%** | **+0.9 pp** |
| dimer | FDTD - BEM h = 2 nm | +33 nm | +5.2% | | | | -4.6% | -3.6% | +0.9 pp |
| trimer | FDTD (gap 1 nm) | 1532 | 313 | 58.9% | 1533 | 533 | 502 | 296 | 58.9% |
| trimer | BEM h = 4 nm | 1489 | 275 | 59.1% | 1488 | 467 | 313 | 204 | 65.1% |
| trimer | BEM h = 2.5 nm (sym.) | 1505 | 292 | 58.4% | 1506 | 501 | 373 | 227 | 60.8% |
| trimer | **FDTD - BEM (h = 4)** | **+43 nm** | **+13.8%** | | | | **+60.3%** | **+44.9%** | **-6.3 pp** |
| trimer | FDTD - BEM h = 2.5 nm (sym.) | +27 nm | +7.3% | | | | +34.6% | +30.4% | -1.9 pp |

## 2. FDTD mesh convergence (dimer, mesh override in the gap; 2 nm on the rods)

| gap mesh (nm) | peak of T (nm) | T max | Fp(1550) | T(1550) | eta(1550) |
|---|---|---|---|---|---|
| 2 | 1658 | 281 | 269 | 234 | 86.9% |
| 1 | 1658 | 283 | 270 | 235 | 87.0% |
| 0.5 | 1663 | 277 | 263 | 227 | 86.5% |

Last refinement (1 -> 0.5 nm): peak +5.4 nm, Fp(1550) -2.6%, T(1550) -3.1%. The rods themselves stay at a 2 nm mesh in all three runs.

## 3. In-plane directionality (trimer)

FDTD: power through the +y / -y faces of the monitor box; BEM: far-field power in 60 deg cones about +y / -y. Different quantities:
only the sign of the asymmetry and the wavelength where it switches are compared.

| | +y/-y at 1550 nm | maximum (at nm) | switch from -y to +y (nm) |
|---|---|---|---|
| FDTD box faces | 0.93 | 2.37 (1649) | 1554 |
| BEM 60 deg cones (h = 4) | 4.81 | 5.75 (1580) | 1468 |

## 4. Coupling into a Si3N4 waveguide along y (FDTD only)

beta = guided power through y = +-2.5 um / total power emitted by the dipole (radiated + absorbed).

| structure | beta(+y) 1550 | beta(-y) 1550 | beta(+y)+beta(-y) 1550 | +y/-y 1550 | max +y/-y (nm) | max beta total (nm) | Fp(1550) with / without waveguide |
|---|---|---|---|---|---|---|---|
| trimer | 0.080 | 0.121 | 0.202 | 0.66 | 6.20 (1700) | 0.206 (1454) | 469 / 502 |

The dimer is mirror-symmetric about y = 0, so its +y/-y ratio must be 1: any deviation measures the numerical noise of this quantity.

