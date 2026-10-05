# Gold-permittivity sensitivity (BEM, rod 60 x 20 nm, axial vs transverse dipole)

| data | gap | lambda_T | T max | Fp there | eta_a | max Fp_z/Fp_x (at nm) | T_z/T_x at lambda_T |
|---|---|---|---|---|---|---|---|
| JC (reference) | 5 | 608 | 117.0 | 1603 | 7.3% | 49 (608) | 330 |
| JC (reference) | 10 | 612 | 36.2 | 406 | 8.9% | 136 (608) | 54 |
| JC (reference) | 20 | 612 | 8.3 | 71 | 11.6% | 75 (604) | 9 |
| Palik | 5 | 652 | 193.1 | 2452 | 7.9% | 80 (652) | 551 |
| Palik | 10 | 652 | 58.1 | 688 | 8.5% | 222 (652) | 87 |
| Palik | 20 | 652 | 11.9 | 119 | 10.1% | 116 (652) | 14 |
| Olmon (evap.) | 5 | 604 | 145.6 | 1746 | 8.3% | 62 (604) | 412 |
| Olmon (evap.) | 10 | 604 | 44.2 | 488 | 9.1% | 167 (604) | 66 |
| Olmon (evap.) | 20 | 608 | 9.7 | 77 | 12.6% | 85 (600) | 11 |
| McPeak | 5 | 596 | 144.3 | 1584 | 9.1% | 61 (592) | 406 |
| McPeak | 10 | 596 | 44.3 | 443 | 10.0% | 165 (592) | 66 |
| McPeak | 20 | 600 | 9.6 | 68 | 14.3% | 82 (592) | 11 |
| JC + surface damping | 5 | 612 | 100.5 | 1395 | 7.2% | 42 (608) | 280 |
| JC + surface damping | 10 | 612 | 31.4 | 384 | 8.2% | 117 (608) | 47 |
| JC + surface damping | 20 | 616 | 7.4 | 60 | 12.3% | 68 (608) | 8 |
| JC, cold (0.039 eV) | 5 | 608 | 146.9 | 1762 | 8.3% | 62 (608) | 416 |
| JC, cold (0.039 eV) | 10 | 608 | 44.7 | 492 | 9.1% | 168 (608) | 67 |
| JC, cold (0.039 eV) | 20 | 612 | 9.8 | 77 | 12.8% | 86 (604) | 11 |
| JC, cold (0.020 eV) | 5 | 608 | 183.7 | 1933 | 9.5% | 78 (608) | 521 |
| JC, cold (0.020 eV) | 10 | 608 | 55.6 | 544 | 10.2% | 206 (608) | 83 |
| JC, cold (0.020 eV) | 20 | 612 | 11.6 | 82 | 14.3% | 99 (604) | 13 |

## Relative to JC

- Palik: gap 5: dlam +44 nm, T +65%, Fp +53%, eta 7.9% vs 7.3%, Rmax 80 vs 49; gap 10: dlam +40 nm, T +61%, Fp +69%, eta 8.5% vs 8.9%, Rmax 222 vs 136
- Olmon (evap.): gap 5: dlam -4 nm, T +24%, Fp +9%, eta 8.3% vs 7.3%, Rmax 62 vs 49; gap 10: dlam -8 nm, T +22%, Fp +20%, eta 9.1% vs 8.9%, Rmax 167 vs 136
- McPeak: gap 5: dlam -12 nm, T +23%, Fp -1%, eta 9.1% vs 7.3%, Rmax 61 vs 49; gap 10: dlam -16 nm, T +22%, Fp +9%, eta 10.0% vs 8.9%, Rmax 165 vs 136
- JC + surface damping: gap 5: dlam +4 nm, T -14%, Fp -13%, eta 7.2% vs 7.3%, Rmax 42 vs 49; gap 10: dlam +0 nm, T -13%, Fp -5%, eta 8.2% vs 8.9%, Rmax 117 vs 136
- JC, cold (0.039 eV): gap 5: dlam +0 nm, T +26%, Fp +10%, eta 8.3% vs 7.3%, Rmax 62 vs 49; gap 10: dlam -4 nm, T +23%, Fp +21%, eta 9.1% vs 8.9%, Rmax 168 vs 136
- JC, cold (0.020 eV): gap 5: dlam +0 nm, T +57%, Fp +21%, eta 9.5% vs 7.3%, Rmax 78 vs 49; gap 10: dlam -4 nm, T +54%, Fp +34%, eta 10.2% vs 8.9%, Rmax 206 vs 136

## Indistinguishability I = Fp G0 / (Fp G0 + 2 gamma*) at the radiative peak (q0 = 1, tau_rad = 1 ns)

| data | gap | Fp | eta_a | I (gamma* = 1 ueV) | I (10 ueV) |
|---|---|---|---|---|---|
| JC (reference) | 5 | 1603 | 7.3% | 99.8% | 98.1% |
| JC (reference) | 20 | 71 | 11.6% | 95.9% | 70.0% |
| JC, cold (0.039 eV) | 5 | 1762 | 8.3% | 99.8% | 98.3% |
| JC, cold (0.039 eV) | 20 | 77 | 12.8% | 96.2% | 71.6% |
| JC, cold (0.020 eV) | 5 | 1933 | 9.5% | 99.8% | 98.5% |
| JC, cold (0.020 eV) | 20 | 82 | 14.3% | 96.4% | 72.9% |
