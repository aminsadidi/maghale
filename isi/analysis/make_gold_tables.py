"""Gold permittivity tables for the MNPBEM sensitivity runs (isi/bem/extra/gold_*.dat, format 'eV n k').
 - olmon / mcpeak : evaporated-film data (Olmon et al. PRB 2012, McPeak et al. ACS Photonics 2015) from the
                    refractiveindex.info database (CC0), resampled on 0.6-4.0 eV.
 - cold1, cold2   : Johnson-Christy with the Drude damping of the Drude-Lorentz fit (SI S3, hbar*gamma = 0.061 eV)
                    replaced by 0.039 eV (room-temperature phonon contribution, 0.022 eV from the dc resistivity,
                    removed) and by 0.020 eV (one third), i.e. eps_cold = eps_JC + D(gamma_cold) - D(gamma_JC).
 - surf           : JC plus surface (Kreibig) damping A*hbar*v_F/L_eff, A = 0.33, v_F = 1.40e6 m/s,
                    L_eff = 4V/S = 17.8 nm for the 60 x 20 nm rod: +0.017 eV.
"""
import numpy as np, re, os
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', 'bem', 'extra')
HC = 1239.84193  # eV nm

def read_yml(fn):
    txt = open(fn).read()
    blk = txt.split('data: |')[1]
    rows = []
    for l in blk.splitlines():
        v = l.split()
        if len(v) == 3:
            try: rows.append([float(x) for x in v])
            except ValueError: break
        elif rows: break
    a = np.array(rows); return a[:, 0] * 1e3, a[:, 1], a[:, 2]   # nm, n, k

def read_dat(fn):
    a = np.loadtxt(fn, comments='%'); return HC / a[:, 0], a[:, 1], a[:, 2]

def write(name, lam, n, k, note):
    E = HC / lam; o = np.argsort(E); E, n, k = E[o], n[o], k[o]
    with open(os.path.join(out, f'gold_{name}.dat'), 'w') as f:
        f.write(f'% {note}\n%  Energy (eV)  n   k\n')
        for e, a, b in zip(E, n, k): f.write(f'{e:.4f}\t{a:.5f}\t{b:.5f}\n')

def eps_of(n, k): return (n + 1j * k) ** 2
def nk_of(eps):
    m = np.sqrt(eps.astype(complex)); m = np.where(m.imag < 0, -m, m); return m.real, m.imag

Egrid = np.linspace(0.6, 4.0, 171)
for name, fn, note in [('olmon', 'Olmon-ev.yml', 'Olmon et al. PRB 86, 235147 (2012), evaporated'),
                       ('mcpeak', 'McPeak.yml', 'McPeak et al. ACS Photonics 2, 326 (2015)')]:
    lam, n, k = read_yml(os.path.join(here, '..', 'sim', fn))
    E = HC / lam; o = np.argsort(E)
    e = np.interp(Egrid, E[o], eps_of(n, k)[o].real) + 1j * np.interp(Egrid, E[o], eps_of(n, k)[o].imag)
    nn, kk = nk_of(e); write(name, HC / Egrid, nn, kk, note)

# JC (MNPBEM gold.dat copy shipped in isi/sim/jc_au.yml is the same data); Drude term of the SI S3 fit
lam, n, k = read_yml(os.path.join(here, '..', 'sim', 'jc_au.yml')) if os.path.exists(os.path.join(here, '..', 'sim', 'jc_au.yml')) else None
wp = 10.26 * np.sqrt(0.701)            # eV, effective plasma energy of the fitted Drude term
g_jc = 0.049 * 1.23984                # eV
def drude(E, g): return -wp ** 2 / (E ** 2 + 1j * g * E)
E = HC / lam; ej = eps_of(n, k)
for name, g in [('cold1', 0.039), ('cold2', 0.020), ('surf', g_jc + 0.017)]:
    e = ej + drude(E, g) - drude(E, g_jc)
    nn, kk = nk_of(e)
    write(name, lam, nn, kk, f'Johnson-Christy with Drude damping {g_jc:.3f} -> {g:.3f} eV (hbar*omega_p = {wp:.2f} eV)')
