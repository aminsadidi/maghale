"""Catalogue of the simulations the lab kit can run, with memory and cost estimates used for planning and ETA.

MNPBEM (MATLAB) tasks reuse the job files of the repository (isi/bem/extra/job_*.m), exactly as on GitHub Actions.
Memory model (calibrated on the GitHub runs, 16 GB):  mem_GB ~ 1.5 + 0.093 * nblocks * (N/1000)^2
  N = boundary elements of the meshed part, nblocks = number of mirror-symmetry blocks (1, 2 for 'x', 4 for 'xy').
Cost model per wavelength:  t ~ a * nblocks * (N/1000)^p  (p ~ 2.6; a is re-fitted from the measured run times).
Lumerical tasks: cost units ~ (FDTD cells) / (smallest mesh step in nm); calibrated after the first FDTD run.
"""
import math

TIER_NAMES = {1: 'BEM mesh convergence', 2: 'FDTD cross-check and retuning sweep (far field)', 3: 'BEM of the selected design',
              4: 'FDTD of the selected design: waveguide, material, mesh, tolerance'}
SWEEP = [(L, L + dL) for L in (265, 270, 275, 280) for dL in (20, 30, 40)]     # (R1 = R2 length, R3 length) of the FDTD retuning sweep
PLACEHOLDER = {'L': 275, 'L3': 305}                                          # only for the time / memory estimate before the selection


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
    for h in (3.0, 2.75, 2.5):                               # trimer rotated into the xz plane, symmetry 'xy' (1/4 problem)
        N = rod_faces(D, 285, h) // 2 + rod_faces(D, 315, h) // 4
        for c in range(1, 7):
            T.append(mnpbem('meshsym', f'Q_L285_R315_Y160_H{h:g}_c{c}', 7, N, 4, 1, f'trimer mesh h = {h:g} nm, spectrum chunk {c}/6'))
    for h in (2.5, 2.25, 2.0):                               # dimer, symmetry 'xy': half of R2 meshed
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
    # ================= campaign 2: retuning to 1550 nm with far field, then everything for the selected design ==================
    sm = lumerical('smoke_ff', {'L': 285, 'L3': 315, 'dx': 4.0, 'coarse': True, 'ff_strict': True}, 3e5, 4.0, 2,
                   'SMOKE TEST: FDTD with far-field projection (coarse trimer, a few minutes)')
    sm['smoke'] = True; T.append(sm)
    T.append(lumerical('ff_L285_R315', {'L': 285, 'L3': 315, 'Y3': 160, 'dx': 1.0}, 8e6, 1.0, 2,
                       'FDTD earlier trimer with far field: directionality in the BEM definition (60 deg cones)'))
    for L in (265, 270, 275, 280):
        T.append(lumerical(f'sw_L{L}', {'L': L, 'L3': 0, 'dx': 1.0}, 6e6, 1.0, 2, f'FDTD sweep: dimer L = {L} nm'))
        for L3 in [b for a, b in SWEEP if a == L]:
            T.append(lumerical(f'sw_L{L}_R{L3}', {'L': L, 'L3': L3, 'Y3': 160, 'dx': 1.0}, 8e6, 1.0, 2,
                               f'FDTD sweep: trimer L = {L}, R3 = {L3} nm (far field)'))
    # tier 4: the selected design (L, L3 inserted at run time from selected.json)
    for name, params, cells, dxm, desc, geo in (
            ('sel_wg_trimer', {'waveguide': True}, 2.5e7, 1.0, 'selected trimer above the Si3N4 waveguide: guided power +y / -y', 'trimer'),
            ('sel_wg_dimer', {'waveguide': True}, 2.2e7, 1.0, 'selected dimer above the Si3N4 waveguide (symmetric reference)', 'dimer'),
            ('sel_palik', {'mat': 'Au (Gold) - Palik'}, 8e6, 1.0, 'selected trimer, gold = Palik', 'trimer'),
            ('sel_crc', {'mat': 'Au (Gold) - CRC'}, 8e6, 1.0, 'selected trimer, gold = CRC', 'trimer'),
            ('sel_conformal', {'conformal': True}, 8e6, 1.0, 'selected trimer, conformal mesh on the gold', 'trimer'),
            ('sel_gap05', {'dx': 0.5}, 2.3e7, 0.5, 'selected trimer, gap mesh 0.5 nm', 'trimer'),
            ('sel_rod1', {'rmesh': 1.0}, 3.2e7, 1.0, 'selected trimer, rod mesh 1 nm (finest FDTD)', 'trimer'),
            ('sel_Y150', {'Y3': 150}, 8e6, 1.0, 'selected trimer, R3 moved to y = 150 nm (tolerance)', 'trimer'),
            ('sel_Y170', {'Y3': 170}, 8e6, 1.0, 'selected trimer, R3 moved to y = 170 nm (tolerance)', 'trimer')):
        t = lumerical(name, dict({'Y3': 160, 'dx': 1.0}, **params), cells, dxm, 4, desc)
        t['auto'] = geo; T.append(t)
    # tier 3: BEM of the selected design at h = 4 and 3 nm (full outputs, job_tri2)
    for h in (4.0, 3.0):
        for c in range(1, 7):
            T.append({'id': f'tri2:AUTO_H{h:g}_c{c}', 'backend': 'mnpbem', 'auto': 'trimer', 'h': h, 'chunk': c, 'tier': 3,
                      'output': f'tri2_AUTO_H{h:g}_c{c}.csv', 'nsteps': 7, 'desc': f'BEM selected trimer, h = {h:g} nm, chunk {c}/6'})
    T += campaign3()
    return [resolve(t, PLACEHOLDER, placeholder=True) if t.get('auto') else t for t in T]


# ================= campaign 3 (supervisor, 2026-11-15): R3 brought close to the dimer (edge spacing 20-80 nm), then rotated ===========
C3_L, C3_L3 = 275, 295                                   # selected design of campaign 2


def _segdist(p1, p2, q1, q2):
    """minimum distance between segments p1p2 and q1q2 (2D), by dense sampling (exact enough for nm geometry)"""
    best = 1e9
    for i in range(201):
        t = i / 200; x = p1[0] + t * (p2[0] - p1[0]); y = p1[1] + t * (p2[1] - p1[1])
        dx, dy = q2[0] - q1[0], q2[1] - q1[1]; u = max(0.0, min(1.0, ((x - q1[0]) * dx + (y - q1[1]) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - q1[0] - u * dx, y - q1[1] - u * dy))
    return best


def r3_spacing(Y3, A3, L=C3_L, L3=C3_L3, D=60, g=40):
    """smallest gold-to-gold distance (nm) between R3 (centre (0, Y3), angle A3) and the dimer"""
    h = (L3 - D) / 2; c, s = math.cos(math.radians(A3)), math.sin(math.radians(A3))
    r3 = ((-h * c, Y3 - h * s), (h * c, Y3 + h * s))
    a, b = g / 2 + D / 2, g / 2 + L - D / 2
    return min(_segdist(*r3, (-b, 0), (-a, 0)), _segdist(*r3, (a, 0), (b, 0))) - D


def y3_for(spacing, A3):
    lo, hi = 30.0, 400.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if r3_spacing(mid, A3) < spacing: lo = mid
        else: hi = mid
    return round(hi, 1)


def campaign3():
    sm = lumerical('smoke_c3', {'L': C3_L, 'L3': C3_L3, 'Y3': y3_for(30, 45), 'A3': 45, 'dx': 4.0, 'coarse': True, 'ff_strict': True},
                   3e5, 4.0, 5, 'SMOKE TEST: rotated third rod (coarse, a few minutes)')
    sm['smoke'] = True; T = [sm]
    for s in (20, 30, 40, 50, 60, 70, 80):               # (a) distance sweep, R3 parallel (A3 = 0); 90-110 nm exist (Y3 = 150-170)
        T.append(lumerical(f'c3_s{s}_a0', {'L': C3_L, 'L3': C3_L3, 'Y3': y3_for(s, 0), 'A3': 0, 'dx': 1.0}, 8e6, 1.0, 5,
                           f'campaign 3: R3 parallel, spacing {s} nm to the dimer'))
    for s in (30, 20):                                   # (b) rotation at a fixed smallest spacing
        for A in (15, 30, 45, 60, 90):
            T.append(lumerical(f'c3_s{s}_a{A}', {'L': C3_L, 'L3': C3_L3, 'Y3': y3_for(s, A), 'A3': A, 'dx': 1.0}, 9e6, 1.0, 5,
                               f'campaign 3: R3 rotated {A} deg, smallest spacing {s} nm'))
    return T


def resolve(t, sel, placeholder=False):
    """insert the selected geometry (L, L3) into an 'auto' task"""
    t = dict(t); L, L3 = int(sel['L']), int(sel['L3'])
    if t['backend'] == 'lumerical':
        t['params'] = dict(t['params'], L=L, L3=L3 if t['auto'] == 'trimer' else 0)
    else:
        h = t['h']; spec = f"L{L}_R{L3}_A0_Y160_H{h:g}_c{t['chunk']}"
        N = 2 * rod_faces(60, L, h) + rod_faces(60, L3, 1.4 * h)
        new = mnpbem('tri2', spec, 7, N, 1, t['tier'], t['desc'] + ('' if placeholder else f' (L = {L}, R3 = {L3})'))
        for k in ('id', 'output', 'desc'): new.pop(k) if placeholder else None
        t.update(new)
    t['pending_sel'] = placeholder
    if not placeholder: t['desc'] = t['desc'].split(' (L =')[0] + f' (L = {L}, R3 = {L3})'
    return t
