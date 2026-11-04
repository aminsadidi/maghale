# Uncertainty budget of the final design (trimer L = 285, R3 = 315 nm horizontal at y = 160 nm)

Reference (BEM, h = 4 nm, x dipole at the gap centre): peak of T at 1489 nm; at 1550 nm Fp = 313, T = 204, eta = 65.1%, f(+y)/f(-y) = 4.81.

Entries are changes relative to the reference (fabrication rows: relative to the same design at h = 5 nm, peak 1483 nm, Fp(1550) 294, ratio 5.10). n/a: quantity not available from that run.

| group | source | peak of T | Fp(1550) | T(1550) | eta(1550) | f(+y)/f(-y) (1550) |
|---|---|---|---|---|---|---|
| numerics | mesh h = 5 -> 4 nm (full geometry) | +7 nm | +6.5% | +4.1% | -1.5 pp | -5.6% |
| numerics | mesh h = 4 -> 2.5 nm (symmetric runs) | +11 nm | +13.1% | +10.1% | -1.7 pp | n/a |
| numerics | remaining, h = 2.5 nm -> 0 (h^2 law ... fitted order p = 0.91) | +7 nm ... +21 nm | +6.7% ... +20.7% | +5.4% ... +17.0% | -0.7 pp ... -1.9 pp | n/a |
| numerics | mirror symmetry (dimer, h = 5 nm, symmetric vs full) | n/a | -1.0 ... +0.5% (1310-1660 nm) | n/a | n/a | n/a |
| fabrication (h = 5 nm) | R3 length 315 -> 305 nm | -14 nm | -8.4% | -0.0% | +6.1 pp | +5.4% |
| fabrication (h = 5 nm) | R3 length 315 -> 325 nm | +14 nm | +16.1% | +5.4% | -6.1 pp | -38.5% |
| fabrication (h = 5 nm) | R3 position y 160 -> 150 nm | -13 nm | -10.5% | -11.7% | -0.9 pp | +30.6% |
| fabrication (h = 5 nm) | R3 position y 160 -> 170 nm | +11 nm | +10.0% | +11.5% | +0.9 pp | -22.1% |
| fabrication (h = 5 nm) | R3 position x 0 -> 10 nm | +0 nm | +0.2% | +0.2% | -0.0 pp | -0.7% |
| fabrication (h = 5 nm) | R3 rotated by 5 deg | +0 nm | +0.1% | +0.3% | +0.2 pp | -2.7% |
| fabrication (h = 5 nm) | R3 rotated by 10 deg | +0 nm | +0.3% | +1.3% | +0.6 pp | -10.1% |
| emitter (h = 4 nm) | emitter 5 nm along x | -0 nm | +8.0% | +7.8% | -0.1 pp | -0.2% |
| emitter (h = 4 nm) | emitter 10 nm along y | -0 nm | -14.0% | -13.8% | +0.1 pp | -0.6% |
| method | FDTD (Lumerical, 1 nm gap mesh) vs BEM | +43 nm | +60.3% | +44.9% | -6.3 pp | different definition |

Notes
- rigid-shift check, h = 2.75 -> 2.5 nm: peak moves +1.7 nm; Fp(1550) predicted 371.7, computed 372.9 (-0.3%).
- Peak of T in the symmetric mesh study: h = 4 nm 1494.3 nm, h = 2.5 nm 1505.3 nm; extrapolated 1512.0 nm (h^2) and 1526.1 nm (fitted order p = 0.91).
- The symmetric runs mesh R3 at h, the full runs at 1.4 h; their absolute values differ by a few per cent, so only changes are used.
- The efficiency eta and the directionality are the least mesh-sensitive figures; Fp(1550) is sensitive because 1550 nm lies on the
  red flank of the resonance, where a few nm of peak shift change Fp by several per cent.
- Not included: gold permittivity (only Johnson-Christy computed for this design), substrate, rounding of the rod ends, nonlocality.
