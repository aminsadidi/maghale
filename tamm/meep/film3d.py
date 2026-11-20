"""3D FDTD (Meep) of the silver film of the Tamm device: zeroth-order (specular) complex scattering parameters.

Periodic P x P cell (random island film or flat film), normal incidence, x or y polarisation, Gaussian pulse 0.38-0.95 um.
Layout along z (um): PML | lower medium (n_b, optionally a stack of layers + substrate) | film (bottom at z = 0) | air (or water) | PML.
The zeroth diffraction order is obtained exactly by averaging the DFT field over a full period; the incident field and the phase
propagation are taken from normalisation runs in homogeneous 1D cells with the same grid, so no analytic phase convention enters.
Outputs (complex, E-field amplitudes, reference planes z = 0 (film bottom) and z = zref (top of the film zone)):
    incidence 'top'    : r_top (in air, at zref), t_down (into the lower medium, at z = 0)
    incidence 'bottom' : r_bot (in the lower medium, at z = 0), t_up (into air, at zref)
plus flux-based R, T (power) as a check, and with a stack below (full device) the device R and T from fluxes.
usage: python tamm/meep/film3d.py '<json case>' out.npz"""
import json, os, sys, time
import numpy as np
import meep as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import islands  # noqa: E402

LAM_MIN, LAM_MAX, NF = 0.38, 0.95, 58
FMIN, FMAX = 1 / LAM_MAX, 1 / LAM_MIN
FCEN, DF = 0.5 * (FMIN + FMAX), 1.15 * (FMAX - FMIN)


def ag_medium(P):
    s = [mp.DrudeSusceptibility(frequency=P['fD'], gamma=P['gD'] + P.get('dg_extra', 0.0), sigma=P['sD'])]
    s += [mp.LorentzianSusceptibility(frequency=f0, gamma=g, sigma=sg) for sg, f0, g in P['L']]
    return mp.Medium(epsilon=P['eps_inf'], E_susceptibilities=s)


def run(case):
    c = dict(dict(P=0.3, res=200, seed=1, film='islands', pol='x', inc='top', nb=1.93, n_top=1.0, zref=0.07, stack=[], dpml=0.4,
                  pad=0.35, sphere=None, t_scale=1.0, tol=1e-6, tmax=200), **case)
    agP = json.load(open(os.path.join(HERE, '..', 'results', 'ag_ld.json')))['params']
    if c.get('dg_extra'): agP = dict(agP, dg_extra=c['dg_extra'])
    Ag = ag_medium(agP)
    res, P, dpml, pad, zref = c['res'], c['P'], c['dpml'], c['pad'], c['zref']
    stack = c['stack']                                       # list of [n, d] from the film downwards; substrate n = c['nsub']
    dstack = sum(d for n, d in stack)
    nsub = c.get('nsub', c['nb'])
    zlo = -(dstack + pad + dpml); zhi = zref + pad + dpml
    Lz = zhi - zlo; zc = 0.5 * (zhi + zlo)
    Z = lambda z: z - zc                                    # absolute -> cell coordinates
    zsrc_top, zsrc_bot = zref + 0.6 * pad, -(dstack + 0.6 * pad)
    zmon_top, zmon_bot = zref + 0.3 * pad, -(dstack + 0.3 * pad)
    comp = mp.Ex if c['pol'] == 'x' else mp.Ey
    # ---- geometry
    def geom(full):
        g = []
        if not full: return g
        # lower medium: substrate everywhere below 0, then the stack layers
        g.append(mp.Block(size=mp.Vector3(mp.inf, mp.inf, (0 - zlo)), center=mp.Vector3(0, 0, Z(0.5 * zlo)), material=mp.Medium(index=nsub)))
        z = 0.0
        for n, d in stack:
            g.append(mp.Block(size=mp.Vector3(mp.inf, mp.inf, d), center=mp.Vector3(0, 0, Z(z - d / 2)), material=mp.Medium(index=n))); z -= d
        if c['n_top'] != 1.0:
            g.append(mp.Block(size=mp.Vector3(mp.inf, mp.inf, zhi), center=mp.Vector3(0, 0, Z(zhi / 2)), material=mp.Medium(index=c['n_top'])))
        if c['film'] == 'none':
            pass
        elif c['film'] == 'flat':
            t = c.get('t_flat', 0.033)
            g.append(mp.Block(size=mp.Vector3(mp.inf, mp.inf, t), center=mp.Vector3(0, 0, Z(t / 2)), material=Ag))
        elif c['film'] == 'islands':
            f = islands.make(P, c['seed'], void=c.get('void', 0.144))
            if c['t_scale'] != 1.0: f['heights'] = f['heights'] * c['t_scale']
            if c.get('d_scale', 1.0) != 1.0: f['grains'] = f['grains'] * [1, 1, c['d_scale']]       # lateral shrinking of every grain
            if c.get('shell'):
                g += islands.geometry_shell(f, Z(0), mp.Medium(index=c['shell']['n']), c['shell']['t'])
            g += islands.geometry(f, Z(0), Ag)
            if c.get('sphere'):
                s = c['sphere']; R = s['d'] / 2
                ix = iy = int(f['grid'] / 2)
                ztop = float(f['Hmap'][ix - 3:ix + 3, iy - 3:iy + 3].max()) * c['t_scale']
                g.append(mp.Sphere(radius=R, center=mp.Vector3(0, 0, Z(ztop + R)), material=mp.Medium(index=s['n'])))
        return g
    def sim_for(full, inc, n_hom=None):
        three_d = full
        cell = mp.Vector3(P if three_d else 2.0 / res, P if three_d else 2.0 / res, Lz)
        src_z = zsrc_top if inc == 'top' else zsrc_bot
        src = [mp.Source(mp.GaussianSource(FCEN, fwidth=DF, is_integrated=True), component=comp, center=mp.Vector3(0, 0, Z(src_z)),
                         size=mp.Vector3(cell.x, cell.y, 0))]
        geo = geom(full) if full else [mp.Block(size=mp.Vector3(mp.inf, mp.inf, mp.inf), material=mp.Medium(index=n_hom))]
        return mp.Simulation(cell_size=cell, resolution=res, boundary_layers=[mp.PML(dpml, direction=mp.Z)], sources=src,
                             geometry=geo, k_point=mp.Vector3(), dimensions=3, eps_averaging=True)
    planes = dict(top=zmon_top, ref=zref, bot=0.0, low=zmon_bot)
    def measure(sim, cell_xy, full):
        dfts = {k: sim.add_dft_fields([comp], 0.5 * (FMIN + FMAX), FMAX - FMIN, NF, center=mp.Vector3(0, 0, Z(z)), size=mp.Vector3(cell_xy, cell_xy, 0))
                for k, z in planes.items()}
        fl = {k: sim.add_flux(0.5 * (FMIN + FMAX), FMAX - FMIN, NF, mp.FluxRegion(center=mp.Vector3(0, 0, Z(z)), size=mp.Vector3(cell_xy, cell_xy, 0)))
              for k, z in (('top', zmon_top), ('low', zmon_bot))}
        return dfts, fl
    def stopper(inc):
        """minimum time (three transits of the cell after the source) and then field decay at the far monitor"""
        zf = zmon_bot if inc == 'top' else zmon_top
        dec = mp.stop_when_fields_decayed(2.0, comp, mp.Vector3(0, 0, Z(zf)), c['tol'])
        tmin = 3 * Lz * max(nsub, c['n_top'])
        state = dict(t0=None)
        def f(sim):
            if state['t0'] is None: state['t0'] = sim.meep_time()
            done = dec(sim)                                     # always called, so that it tracks the field maximum from the start
            if sim.meep_time() - state['t0'] < tmin: return False
            return done or sim.meep_time() - state['t0'] > c['tmax']
        return f
    def avg(sim, d):
        return np.array([np.mean(sim.get_dft_array(d, comp, i)) for i in range(NF)])
    out = {}
    freqs = np.linspace(FMIN, FMAX, NF)
    # ---- normalisation: homogeneous medium of the incidence side
    n_inc = 1.0 * c['n_top'] if c['inc'] == 'top' else nsub
    t0 = time.time()
    s0 = sim_for(False, c['inc'], n_inc); d0, f0 = measure(s0, 2.0 / res, False)
    s0.run(until_after_sources=stopper(c['inc']))
    E0 = {k: avg(s0, d) for k, d in d0.items()}
    inc_flux = np.array(mp.get_fluxes(f0['top' if c['inc'] == 'top' else 'low']))
    if c['inc'] == 'top': inc_flux = -inc_flux                    # downward
    # phase propagation in the far medium (for the transmitted wave): homogeneous run of the other medium
    n_far = nsub if c['inc'] == 'top' else c['n_top']
    s1 = sim_for(False, c['inc'], n_far); d1, _ = measure(s1, 2.0 / res, False)
    s1.run(until_after_sources=stopper(c['inc']))
    E1 = {k: avg(s1, d) for k, d in d1.items()}
    t_norm = time.time() - t0
    # ---- structure
    s = sim_for(True, c['inc']); d, fl = measure(s, P, True)
    near = 'top' if c['inc'] == 'top' else 'low'
    inc_flux = inc_flux * (P * res / 2.0) ** 2                  # normalisation cell is 2 x 2 pixels wide
    t1 = time.time()
    s.run(until_after_sources=stopper(c['inc']))
    E = {k: avg(s, dd) for k, dd in d.items()}
    t_run = time.time() - t1
    Rflux = np.array(mp.get_fluxes(fl[near])); Tflux = np.array(mp.get_fluxes(fl['low' if near == 'top' else 'top']))
    # net flux at the near monitor = incident - reflected (counter-propagating cross terms cancel): R = 1 - net / incident
    if c['inc'] == 'top':
        R = 1 + Rflux / inc_flux; T = -Tflux / inc_flux
        Eref_n = E['top'] - E0['top']                                      # reflected wave at the near monitor
        r = Eref_n * E0['top'] / E0['ref'] ** 2                            # referenced to z = zref
        if not stack:
            t = E['low'] / (E0['ref'] * (E1['low'] / E1['bot']))         # referenced: incident at zref -> transmitted at z = 0
        else:
            t = np.full(NF, np.nan + 0j)
    else:
        R = 1 - Rflux / inc_flux; T = Tflux / inc_flux
        Eref_n = E['low'] - E0['low']
        r = Eref_n * E0['low'] / E0['bot'] ** 2                            # referenced to z = 0
        t = E['top'] / (E0['bot'] * (E1['top'] / E1['ref']))             # incident at z = 0 -> transmitted at zref
    out = dict(freq=freqs, lam=1 / freqs, r=r, t=t, R=R, T=T, case=json.dumps(c), t_norm=t_norm, t_run=t_run,
               voxels=float((P * res) ** 2 * Lz * res), timesteps=float(s.timestep()))
    return out


if __name__ == '__main__':
    case = json.loads(sys.argv[1]); out = sys.argv[2]
    o = run(case)
    np.savez(out, **o)
    print(f"done: {o['t_run']/60:.1f} min (+ norm {o['t_norm']/60:.1f} min), {o['voxels']:.2e} voxels, {o['timesteps']:.0f} steps; "
          f"R(600nm) {np.interp(0.6, o['lam'][::-1], o['R'][::-1]):.3f} T {np.interp(0.6, o['lam'][::-1], o['T'][::-1]):.3f}")
