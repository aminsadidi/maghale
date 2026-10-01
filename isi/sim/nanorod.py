"""Body-of-revolution FDTD (Meep, cylindrical coordinates) for a dipole near a gold nanorod or sphere.

Physics is fully 3D: the field is expanded as exp(i m phi); a dipole on the symmetry axis couples only to
m = 0 (axial / longitudinal dipole, Ez source) or m = +-1 (transverse dipole, Er source).
Outputs per wavelength:
    Fp   = P_tot / P_0         (total decay-rate enhancement, from the LDOS at the dipole)
    T    = P_rad / P_0         (radiated power through a closed box, normalised by the same box in free space)
    eta  = T / Fp              (apparent quantum efficiency for intrinsic yield q0 = 1)
    coll = fraction of radiated power inside a cone of numerical aperture NA around +z (optional)
Units: lengths in nm at the interface, Meep length unit = 1 um.
"""
import numpy as np
import meep as mp
from gold_jc import Au_JC

# Sub-bands: each gets its own Gaussian pulse; only the central part of each band is kept (band edges are noisy).
BANDS = [(0.47, 0.59), (0.55, 0.73), (0.68, 0.95)]
KEEP = [(0.49, 0.57), (0.57, 0.70), (0.70, 0.91)]


def geometry(shape, L=60.0, D=20.0, R_sph=15.874, material=Au_JC):
    """Rod: cylinder + two hemispherical caps, axis z, centre at origin. Returns (objects, z_top_apex)."""
    if shape == 'rod':
        r = D / 2000.0
        h = (L - D) / 1000.0
        objs = [mp.Cylinder(radius=r, height=h, center=mp.Vector3(), material=material),
                mp.Sphere(radius=r, center=mp.Vector3(0, 0, +h / 2), material=material),
                mp.Sphere(radius=r, center=mp.Vector3(0, 0, -h / 2), material=material)]
        return objs, L / 2000.0
    if shape == 'sphere':
        return [mp.Sphere(radius=R_sph / 1000.0, material=material)], R_sph / 1000.0
    raise ValueError(shape)


def _run_band(objs, z_top, gap, orient, res, n_host, band, nf, trun, dpml, pad, na_list):
    lo, hi = band
    fcen, df = 0.5 * (1 / lo + 1 / hi), 1 / lo - 1 / hi
    m = 0 if orient == 'z' else 1
    comp = mp.Ez if orient == 'z' else mp.Er
    zdip = z_top + gap / 1000.0
    half_z = max(abs(zdip), z_top) + pad          # flux box half-height
    rbox = max(z_top, 0.02) + pad                  # flux box radius (encloses rod or sphere)
    sr = rbox + 0.04
    sz = 2 * (half_z + 0.04)
    cell = mp.Vector3(sr + dpml, 0, sz + 2 * dpml)
    host = mp.Medium(index=n_host)
    out = {}
    for tag, geo in (('struct', objs), ('free', [])):
        sim = mp.Simulation(cell_size=cell, dimensions=mp.CYLINDRICAL, m=m, resolution=res * 1000,
                            boundary_layers=[mp.PML(dpml)], geometry=geo, default_material=host,
                            sources=[mp.Source(mp.GaussianSource(fcen, fwidth=df), component=comp,
                                               center=mp.Vector3(0, 0, zdip))])
        regs = [mp.FluxRegion(center=mp.Vector3(rbox / 2, 0, +half_z), size=mp.Vector3(rbox, 0, 0), weight=+1),
                mp.FluxRegion(center=mp.Vector3(rbox / 2, 0, -half_z), size=mp.Vector3(rbox, 0, 0), weight=-1),
                mp.FluxRegion(center=mp.Vector3(rbox, 0, 0), size=mp.Vector3(0, 0, 2 * half_z), weight=+1)]
        flux = sim.add_flux(fcen, df, nf, *regs)
        n2f = sim.add_near2far(fcen, df, nf, *[mp.Near2FarRegion(center=r.center, size=r.size, weight=r.weight) for r in regs]) if na_list else None
        sim.run(mp.dft_ldos(fcen, df, nf), until_after_sources=trun)
        rec = {'ldos': np.array(sim.ldos_data), 'flux': np.array(mp.get_fluxes(flux))}
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
            rec['ff'] = (th, np.array(S))  # shape (n_theta, nf)
        out[tag] = rec
        sim.reset_meep()
    f = np.linspace(fcen - df / 2, fcen + df / 2, nf)
    lam = 1000.0 / f
    res_ = {'lam': lam, 'Fp': out['struct']['ldos'] / out['free']['ldos'],
            'T': out['struct']['flux'] / out['free']['flux']}
    if na_list:
        th, S = out['struct']['ff']
        w = np.sin(th)[:, None] * S                     # power per d(theta), axially symmetric
        tot = np.trapezoid(w, th, axis=0)
        for na in na_list:
            cut = np.arcsin(min(na / n_host, 1.0))
            msk = th <= cut
            res_[f'coll_NA{na}'] = np.trapezoid(w[msk], th[msk], axis=0) / tot
    return res_


def simulate(shape='rod', orient='z', gap=5.0, res=1.0, n_host=1.0, L=60.0, D=20.0, R_sph=15.874,
             nf=31, trun=60, dpml=0.3, pad=0.04, na_list=()):
    """Return dict of arrays over 490-910 nm. res = grid points per nm (1 -> 1 nm grid)."""
    objs, z_top = geometry(shape, L, D, R_sph)
    acc = {}
    for band, keep in zip(BANDS, KEEP):
        r = _run_band(objs, z_top, gap, orient, res, n_host, band, nf, trun, dpml, pad, na_list)
        m = (r['lam'] >= 1000 * keep[0]) & (r['lam'] <= 1000 * keep[1])
        for k, v in r.items():
            acc.setdefault(k, []).extend(list(np.asarray(v)[m]))
    o = np.argsort(acc['lam'])
    out = {k: np.asarray(v)[o] for k, v in acc.items()}
    out['eta'] = out['T'] / out['Fp']
    return out


def save_csv(path, out, meta=''):
    keys = ['lam', 'Fp', 'T', 'eta'] + sorted(k for k in out if k.startswith('coll'))
    np.savetxt(path, np.column_stack([out[k] for k in keys]), delimiter=',', header=','.join(keys),
               comments='# ' + meta + '\n')
