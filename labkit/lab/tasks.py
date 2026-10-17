"""Catalogue of the simulations the lab kit can run, with memory and cost estimates used for planning and ETA.

MNPBEM (MATLAB) tasks reuse the job files of the repository (isi/bem/extra/job_*.m), exactly as on GitHub Actions.
Memory model (calibrated on the GitHub runs, 16 GB):  mem_GB ~ 1.5 + 0.093 * nblocks * (N/1000)^2
  N = boundary elements of the meshed part, nblocks = number of mirror-symmetry blocks (1, 2 for 'x', 4 for 'xy').
Cost model per wavelength:  t ~ a * nblocks * (N/1000)^p  (p ~ 2.6; a is re-fitted from the measured run times).
Lumerical tasks: cost units ~ (FDTD cells) / (smallest mesh step in nm); calibrated after the first FDTD run.
"""
import math

TIER_NAMES = {1: 'mesh convergence (supervisor request)', 2: 'Lumerical FDTD cross-check', 3: 'final design, high accuracy',
              4: 'waveguide coupling (Q1, experimental)'}


def rod_faces(D, L, h):
    """faces of bemx_rod(D, L, h) (checked: D60 L300 h5 -> 3182)"""
    nphi = math.ceil(math.pi * D / h); nth = 2 * math.ceil(math.pi * D / (4 * h)); nz = math.ceil((L - D) / h) + 1
    return (nphi - 1) * (nz - 1) + 2 * (nphi - 1) * (nth - 1)


def mem_gb(N, nblocks=1):
    return 1.5 + 0.093 * nblocks * (N / 1000.0) ** 2


def mnpbem(job, spec, nlam, N, nblocks, tier, desc):
    return {'id': f'{job}:{spec}', 'backend': 'mnpbem', 'job': job, 'spec': spec, 'output': f'{job}_{spec}.csv',
            'nsteps': nlam, 'N': N, 'nblocks': nblocks, 'mem_gb': round(mem_gb(N, nblocks), 1),
            'units_per_step': nblocks * (N / 1000.0) ** 2.6, 'tier': tier, 'desc': desc}


def lumerical(name, params, cells, dxmin_nm, tier, desc, mem=None):
    return {'id': f'fdtd:{name}', 'backend': 'lumerical', 'name': name, 'params': params, 'output': f'fdtd_{name}.csv',
            'nsteps': 1, 'cells': cells, 'mem_gb': mem or round(1.0 + cells * 3e-7, 1),
            'units_per_step': cells / dxmin_nm, 'tier': tier, 'desc': desc}


def catalogue():
    T = []
    D = 60
    # --- smoke tests (a few minutes): if one fails, the other tasks of that backend are skipped ---------------------------
    sm = mnpbem('meshsym', 'D_L285_H8', 4, rod_faces(D, 285, 8) // 2, 4, 1, 'SMOKE TEST: MATLAB + MNPBEM (dimer, 8 nm mesh, 4 wavelengths)')
    sm['smoke'] = True; T.append(sm)
    sm = lumerical('smoke', {'L': 285, 'L3': 0, 'dx': 4.0, 'coarse': True}, 3e5, 4.0, 2, 'SMOKE TEST: Lumerical FDTD (coarse dimer, a few minutes)')
    sm['smoke'] = True; T.append(sm)
    # --- tier 1: fine end of the mesh-convergence study (spectra 1300-1700 nm, 6 chunks of 7 wavelengths) -------------
    for h in (3.5, 3.0):                                     # trimer, symmetry 'x': R2 + half R3 meshed
        N = rod_faces(D, 285, h) + rod_faces(D, 315, h) // 2
        for c in range(1, 7):
            T.append(mnpbem('meshsym', f'T_L285_R315_Y160_H{h:g}_c{c}', 7, N, 2, 1, f'trimer mesh h = {h:g} nm, spectrum chunk {c}/6'))
    for h in (2.5, 2.0):                                     # dimer, symmetry 'xy': half of R2 meshed
        N = rod_faces(D, 285, h) // 2
        for c in range(1, 7):
            T.append(mnpbem('meshsym', f'D_L285_H{h:g}_c{c}', 7, N, 4, 1, f'dimer mesh h = {h:g} nm, spectrum chunk {c}/6'))
    # --- tier 3: final design at a 4 nm mesh, full outputs (Green function, collection, all dipoles) ----------------------
    N = 2 * rod_faces(D, 285, 4) + rod_faces(D, 315, 5.6)
    for c in range(1, 7):
        T.append(mnpbem('tri2', f'L285_R315_A0_Y160_H4_c{c}', 7, N, 1, 3, f'final trimer, 4 nm mesh, chunk {c}/6 (1100-1900 nm)'))
    # --- tier 2: Lumerical FDTD cross-check of the BEM results (independent method) ---------------------------------------
    T.append(lumerical('dimer_L285', {'L': 285, 'L3': 0, 'dx': 1.0}, 6e6, 1.0, 2, 'FDTD dimer L = 285 nm: Purcell, T, efficiency (1300-1700 nm)'))
    T.append(lumerical('trimer_L285_R315', {'L': 285, 'L3': 315, 'Y3': 160, 'dx': 1.0}, 8e6, 1.0, 2,
                       'FDTD final trimer: Purcell, T, +y/-y power split (1300-1700 nm)'))
    for dx in (2.0, 0.5):
        T.append(lumerical(f'dimer_L285_dx{dx:g}', {'L': 285, 'L3': 0, 'dx': dx}, 6e6 / dx ** 1.5, dx, 2,
                           f'FDTD mesh convergence: gap override {dx:g} nm'))
    # --- tier 4: waveguide coupling of the directional emission (experimental) --------------------------------------------
    T.append(lumerical('wg_trimer_L285_R315', {'L': 285, 'L3': 315, 'Y3': 160, 'dx': 1.0, 'waveguide': True}, 2.5e7, 1.0, 4,
                       'FDTD trimer above a Si3N4 waveguide along y: power coupled into +y / -y'))
    T.append(lumerical('wg_dimer_L285', {'L': 285, 'L3': 0, 'dx': 1.0, 'waveguide': True}, 2.2e7, 1.0, 4,
                       'FDTD dimer above the same waveguide (reference, symmetric coupling)'))
    return T
