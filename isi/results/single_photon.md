# Single-photon source at 1550 nm on the final trimer (L = 275, R3 = 295 nm)

## 1. Emitter size for 1550 nm (0.800 eV)

- PbS colloidal QD (Moreels 2009 sizing curve, first exciton): d = 5.93 nm; with a 20-40 meV Stokes shift the emission at 1550 nm needs the absorption at 0.82-0.84 eV, i.e. d = 5.51-5.71 nm.
- GaAs QDs cannot reach 1550 nm: the GaAs gap is 1.42 eV (873 nm); confinement only increases the energy.
- InAs/InP QD (disk, finite wells, Vurgaftman parameters), height h for 0.800 eV: h = 2.9 nm (gap 0.417 eV, diameter 30 nm), h = 2.6 nm (gap 0.417 eV, diameter 50 nm), h = 4.5 nm (gap 0.53 eV, diameter 30 nm), h = 3.8 nm (gap 0.53 eV, diameter 50 nm) -> about 2-4 nm high and 30-50 nm wide, the typical InAs/InP telecom dot; indicative (no 3D strain or piezo field).

## 2. Antenna at 1550 nm

| dipole | Fp | T | eta |
|---|---|---|---|
| x (FDTD) | 286 | 199 | 69% |
| x (BEM h = 3) | 240 | 181 | 75% |
| y (BEM) | 0.76 | 0.34 | |
| z (BEM) | 0.71 | 0.29 | |
| isotropic (mean) | 96 | | |

Collection along +z: NA 1.3 28%, NA 0.9 13%; far-field +y/-y = 6.1. Antenna Q ~ 3 (T FWHM 1380-1820 nm): no spectral tuning of the emitter needed.

## 3. Pulsed single-photon emission (resonant pi pulse, QuTiP)

| emitter | antenna | 1/Gamma | pulse | dephasing | g2(0) | I | I x ZPL^2 | photons/pulse into far field | into NA 1.3 |
|---|---|---|---|---|---|---|---|---|---|
| InAs/InP QD, 4 K | no | 2.0 ns | 2.0 ps | gamma* = 1 ueV (resonant pumping) | 0.000 | 0.143 | 0.12 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | no | 2.0 ns | 2.0 ps | 10 ueV (spectral diffusion) | 0.000 | 0.028 | 0.02 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | no | 2.0 ns | 2.0 ps | 50 ueV (above-band pumping) | 0.000 | 0.009 | 0.01 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | no | 2.0 ns | 20.0 ps | gamma* = 1 ueV (resonant pumping) | 0.004 | 0.142 | 0.12 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | no | 2.0 ns | 20.0 ps | 10 ueV (spectral diffusion) | 0.004 | 0.017 | 0.01 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | no | 2.0 ns | 20.0 ps | 50 ueV (above-band pumping) | 0.005 | 0.003 | 0.00 | 1.00 | 0.25 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 200 fs | gamma* = 1 ueV (resonant pumping) | 0.012 | 0.968 | 0.78 | 0.69 | 0.20 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 200 fs | 10 ueV (spectral diffusion) | 0.012 | 0.816 | 0.66 | 0.69 | 0.20 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 200 fs | 50 ueV (above-band pumping) | 0.012 | 0.480 | 0.39 | 0.69 | 0.20 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 2.0 ps | gamma* = 1 ueV (resonant pumping) | 0.098 | 0.897 | 0.73 | 0.69 | 0.20 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 2.0 ps | 10 ueV (spectral diffusion) | 0.098 | 0.756 | 0.61 | 0.69 | 0.20 |
| InAs/InP QD, 4 K | yes | 7.0 ps | 2.0 ps | 50 ueV (above-band pumping) | 0.100 | 0.446 | 0.36 | 0.69 | 0.20 |
| PbS colloidal QD, 300 K | no | 1.0 us | 2.0 ps | gamma* = 20 meV (room temperature) | nan | 0.000 | - | 0.40 | 0.10 |
| PbS colloidal QD, 300 K | no | 1.0 us | 20.0 ps | gamma* = 20 meV (room temperature) | nan | 0.000 | - | 0.40 | 0.10 |
| PbS colloidal QD, 300 K | yes | 25.7 ns | 200 fs | gamma* = 20 meV (room temperature) | nan | 0.000 | - | 0.68 | 0.19 |
| PbS colloidal QD, 300 K | yes | 25.7 ns | 2.0 ps | gamma* = 20 meV (room temperature) | nan | 0.000 | - | 0.68 | 0.19 |

I = two-photon interference visibility of consecutive photons; I x ZPL^2 includes a 90% zero-phonon-line fraction (InAs QDs, no filter).
PbS: g2(0) of the two-level model only (re-excitation); the real limit of colloidal dots is biexciton emission, g2 ~ QY_XX/QY_X.
