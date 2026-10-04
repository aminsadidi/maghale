"""Body-of-revolution FDTD (Meep, cylindrical coordinates) for a dipole near a gold nanorod or sphere.

Physics is fully 3D: the field is expanded as exp(i m phi); a dipole on the symmetry axis couples only to
m = 0 (axial / longitudinal dipole, Ez source) or m = +-1 (transverse dipole, Er source).
Outputs per wavelength:
    Fp   = P_tot / P_0         (total decay-rate enhancement, from power balance P_rad + P_abs; Fp_ldos = LDOS cross-check)
    T    = P_rad / P_0         (radiated power through a closed box, normalised by the same box in free space)
    eta  = T / Fp              (apparent quantum efficiency for intrinsic yield q0 = 1)
    coll = fraction of radiated power inside a cone of numerical aperture NA around +z (optional)
Units: lengths in nm at the interface, Meep length unit = 1 um.
"""
import numpy as np
import meep as mp
from gold_jc import Au_JC

# Sub-bands: each gets its own Gaussian pulse; only the central part of each band is kept (band edges are noisy).
BANDS = [(0.46, 0.61), (0.54, 0.76), (0.63, 0.99)]
KEEP = [(0.49, 0.57), (0.57, 0.70), (0.70, 0.90)]


def geometry(shape, L=60.0, D=20.0, R_sph=15.874, material=Au_JC):
    """Rod: cylinder + two hemispherical caps, axis z, centre at origin. Returns (objects, z_top_apex)."""
    if shape == 'rod':
        r = D / 2000.0
        h = (L - D) / 1000.0
        objs = [mp.Cylinder(radius=r, height=h, center=mp.Vector3(), material=material),
                mp.Sphere(radius=r, center=mp.Vector3(0, 0, +h / 2), material=material),
                mp.Sphere(radius=r, center=mp.Vector3(0, 0, -h / 2), material=material)]
        return objs, L / 2000.0, r
    if shape == 'sphere':
        return [mp.Sphere(radius=R_sph / 1000.0, material=material)], R_sph / 1000.0, R_sph / 1000.0
    raise ValueError(shape)


def _setup(z_top, gap, pad):
    zdip = z_top + gap / 1000.0
    half_z = max(abs(zdip), z_top) + pad          # flux box half-height
    rbox = max(z_top, 0.02) + pad                  # flux box radius (encloses rod or sphere)
    return zdip, half_z, rbox


def _run_one(objs, z_top, r_part, gap, orient, res, n_host, band, nf, trun, dpml, pad, na_list, tag):
    """One independent FDTD run: tag 'struct' (with particle) or 'free' (reference). Returns raw spectra."""
    lo, hi = band
    fcen, df = 0.5 * (1 / lo + 1 / hi), 1 / lo - 1 / hi
    m = 0 if orient == 'z' else 1
    comp = mp.Ez if orient == 'z' else mp.Er
    zdip, half_z, rbox = _setup(z_top, gap, pad)
    cell = mp.Vector3(rbox + 0.04 + dpml, 0, 2 * (half_z + 0.04) + 2 * dpml)
    sim = mp.Simulation(cell_size=cell, dimensions=mp.CYLINDRICAL, m=m, resolution=res * 1000,
                        boundary_layers=[mp.PML(dpml)], geometry=objs if tag == 'struct' else [],
                        default_material=mp.Medium(index=n_host),
                        sources=[mp.Source(mp.GaussianSource(fcen, fwidth=df), component=comp,
                                           center=mp.Vector3(0, 0, zdip))])
    regs = [mp.FluxRegion(center=mp.Vector3(rbox / 2, 0, +half_z), size=mp.Vector3(rbox, 0, 0), weight=+1),
            mp.FluxRegion(center=mp.Vector3(rbox / 2, 0, -half_z), size=mp.Vector3(rbox, 0, 0), weight=-1),
            mp.FluxRegion(center=mp.Vector3(rbox, 0, 0), size=mp.Vector3(0, 0, 2 * half_z), weight=+1)]
    flux = sim.add_flux(fcen, df, nf, *regs)
    # closed surface around the particle only (top disk at mid-gap): net inflow = power absorbed in the metal
    ra, zt, zb = r_part + 0.003, z_top + gap / 2000.0, -(z_top + 0.003)
    absf = sim.add_flux(fcen, df, nf,
                        mp.FluxRegion(center=mp.Vector3(ra / 2, 0, zt), size=mp.Vector3(ra, 0, 0), weight=+1),
                        mp.FluxRegion(center=mp.Vector3(ra / 2, 0, zb), size=mp.Vector3(ra, 0, 0), weight=-1),
                        mp.FluxRegion(center=mp.Vector3(ra, 0, (zt + zb) / 2), size=mp.Vector3(0, 0, zt - zb), weight=+1))
    # far field is only needed for the structure run (the free-space pattern is never used)
    n2f = (sim.add_near2far(fcen, df, nf, *[mp.Near2FarRegion(center=r.center, size=r.size, weight=r.weight) for r in regs])
           if (na_list and tag == 'struct') else None)
    sim.run(mp.dft_ldos(fcen, df, nf), until_after_sources=trun)
    rec = {'ldos': np.array(sim.ldos_data), 'flux': np.array(mp.get_fluxes(flux)), 'abs': -np.array(mp.get_fluxes(absf))}
    if n2f is not None:
        # far-field power density on a large circle in the r-z half plane; theta from +z axis
        th = np.linspace(0, np.pi, 181)
        Rff = 1000.0  # um, far zone
        S = []
        for t in th:
            ff = sim.get_farfield(n2f, mp.Vector3(Rff * np.sin(t), 0, Rff * np.cos(t)))
            E = np.array(ff).reshape(nf, 6)  # per frequency: (Er, Ep, Ez, Hr, Hp, Hz)
            e, h = E[:, :3], E[:, 3:]
            Sr = np.real(np.conj(e[:, 1]) * h[:, 2] - np.conj(e[:, 2]) * h[:, 1]) * np.sin(t) \
                 + np.real(np.conj(e[:, 0]) * h[:, 1] - np.conj(e[:, 1]) * h[:, 0]) * np.cos(t)
            S.append(Sr)
        rec['ff_th'] = th
        rec['ff_S'] = np.array(S)  # shape (n_theta, nf)
    sim.reset_meep()
    return rec


def _combine_band(struct, free, band, nf, n_host, na_list):
    lo, hi = band
    fcen, df = 0.5 * (1 / lo + 1 / hi), 1 / lo - 1 / hi
    lam = 1000.0 / np.linspace(fcen - df / 2, fcen + df / 2, nf)
    P0 = free['flux']
    res_ = {'lam': lam,
            'Fp': (struct['flux'] + struct['abs']) / P0,   # power balance: (P_rad + P_abs) / P_0
            'Fp_ldos': struct['ldos'] / free['ldos'],      # LDOS at the source (cross-check)
            'T': struct['flux'] / P0}
    if na_list:
        th, S = struct['ff_th'], struct['ff_S']
        w = np.sin(th)[:, None] * S                     # power per d(theta), axially symmetric
        tot = np.trapezoid(w, th, axis=0)
        for na in na_list:
            cut = np.arcsin(min(na / n_host, 1.0))
            msk = th <= cut
            res_[f'coll_NA{na}'] = np.trapezoid(w[msk], th[msk], axis=0) / tot
    return res_


def _assemble(per_band):
    acc = {}
    for r, keep in zip(per_band, KEEP):
        msk = (r['lam'] >= 1000 * keep[0]) & (r['lam'] <= 1000 * keep[1])
        for k, v in r.items():
            acc.setdefault(k, []).extend(list(np.asarray(v)[msk]))
    o = np.argsort(acc['lam'])
    out = {k: np.asarray(v)[o] for k, v in acc.items()}
    out['eta'] = out['T'] / out['Fp']
    return out


# ---- task API: every (band, struct/free) run is independent -> run them in parallel, one core each ----
TASKS = [(b, tag) for b in range(len(BANDS)) for tag in ('struct', 'free')]


def run_task(params, band_idx, tag, path):
    """Run one independent task and save its raw spectra to `path` (.npz)."""
    p = dict(DEFAULTS, **params)
    objs, z_top, r_part = geometry(p['shape'], p['L'], p['D'], p['R_sph'])
    rec = _run_one(objs, z_top, r_part, p['gap'], p['orient'], p['res'], p['n_host'], BANDS[band_idx], p['nf'],
                   p['trun'], p['dpml'], p['pad'], tuple(p['na_list']), tag)
    if mp.am_master():
        np.savez(path, **rec)


def combine_tasks(params, paths):
    """paths[(band_idx, tag)] -> .npz files; returns the same dict as simulate()."""
    p = dict(DEFAULTS, **params)
    per_band = []
    for b, band in enumerate(BANDS):
        st, fr = (dict(np.load(paths[(b, t)])) for t in ('struct', 'free'))
        per_band.append(_combine_band(st, fr, band, p['nf'], p['n_host'], tuple(p['na_list'])))
    return _assemble(per_band)


DEFAULTS = dict(shape='rod', orient='z', gap=5.0, res=1.0, n_host=1.0, L=60.0, D=20.0, R_sph=15.874,
                nf=31, trun=30, dpml=0.15, pad=0.04, na_list=())


def simulate(shape='rod', orient='z', gap=5.0, res=1.0, n_host=1.0, L=60.0, D=20.0, R_sph=15.874,
             nf=31, trun=30, dpml=0.15, pad=0.04, na_list=()):
    """Return dict of arrays over 490-900 nm. res = grid points per nm (1 -> 1 nm grid). Serial version."""
    objs, z_top, r_part = geometry(shape, L, D, R_sph)
    per_band = []
    for band in BANDS:
        st, fr = (_run_one(objs, z_top, r_part, gap, orient, res, n_host, band, nf, trun, dpml, pad, tuple(na_list), t)
                  for t in ('struct', 'free'))
        per_band.append(_combine_band(st, fr, band, nf, n_host, tuple(na_list)))
    return _assemble(per_band)


def save_csv(path, out, meta=''):
    keys = ['lam', 'Fp', 'Fp_ldos', 'T', 'eta'] + sorted(k for k in out if k.startswith('coll'))
    np.savetxt(path, np.column_stack([out[k] for k in keys]), delimiter=',', header=','.join(keys),
               comments='# ' + meta + '\n')
