"""All 3D Meep cases of the Tamm-device study (one entry = one film3d.py run). Names are unique and become the result file names.
Groups: V validation (flat film vs analytic), I island film baseline (4 realisations, both incidences, both polarisations),
C convergence (resolution, cell size), M silver modifications (extra Drude damping, thinning), W water on top,
S particles (VLP n = 1.48 and PS n = 1.59, 100 nm) on the film, D full device (film + DBR + glass) for the cascade check."""
DBR = [[1.93, 0.0752 * 0.97], [1.435, 0.1006 * 0.97]] * 5          # film-side first: TiO2 / SiO2 (fit of Fig. 1, TD thickness scale)


def cases():
    C = []
    add = lambda name, **k: C.append((name, k))
    for res in (300,):
        for inc in ('top', 'bottom'):
            add(f'V_flat_r{res}_{inc}', film='flat', P=0.02, res=res, inc=inc)
    for seed in (1, 2, 3, 4):
        for inc in ('top', 'bottom'):
            for pol in ('x', 'y'):
                add(f'I_s{seed}_{inc}_{pol}', film='islands', seed=seed, P=0.3, res=200, inc=inc, pol=pol)
    for inc in ('top', 'bottom'):
        add(f'C_s1_r300_{inc}_x', film='islands', seed=1, P=0.3, res=300, inc=inc, pol='x')
        for pol in ('x', 'y'):
            add(f'C_s1_P45_{inc}_{pol}', film='islands', seed=1, P=0.45, res=200, inc=inc, pol=pol)
    for seed in (1, 2):
        for inc in ('top', 'bottom'):
            for tag, k in (('dg05', dict(dg_extra=0.05 / 1.23984)), ('dg10', dict(dg_extra=0.10 / 1.23984)), ('dg20', dict(dg_extra=0.20 / 1.23984)),
                           ('thin85', dict(t_scale=0.85)), ('thin70', dict(t_scale=0.70))):
                add(f'M_{tag}_s{seed}_{inc}_x', film='islands', seed=seed, P=0.3, res=200, inc=inc, pol='x', **k)
    for inc in ('top', 'bottom'):
        add(f'W_s1_{inc}_x', film='islands', seed=1, P=0.3, res=200, inc=inc, pol='x', n_top=1.333)
    for tag, sph in (('ref', None), ('vlp', dict(d=0.1, n=1.48)), ('ps', dict(d=0.1, n=1.59))):
        for inc in ('top', 'bottom'):
            for pol in ('x', 'y'):
                add(f'S_{tag}_P40_{inc}_{pol}', film='islands', seed=1, P=0.4, res=200, inc=inc, pol=pol, zref=0.18, sphere=sph)
    for inc in ('top', 'bottom'):
        add(f'D_s1_{inc}_x', film='islands', seed=1, P=0.3, res=200, inc=inc, pol='x', stack=DBR, nsub=1.52, nb=1.93)
    # ---- round 2: what the PBS / VLP exposure does to the silver. Ag on glass (compare with Fig. S3c,d) and in the device.
    for seed in (1, 2):
        for inc in ('top', 'bottom'):
            base = dict(film='islands', seed=seed, P=0.3, res=200, inc=inc, pol='x')
            mods = (('base', {}), ('agcl3', dict(shell=dict(t=0.003, n=2.07))), ('agcl6', dict(shell=dict(t=0.006, n=2.07))),
                    ('prot5', dict(shell=dict(t=0.005, n=1.45))), ('cov75', dict(void=0.25)), ('cov65', dict(void=0.35)),
                    ('shrink90', dict(d_scale=0.9, t_scale=0.9)), ('dg10', dict(dg_extra=0.10 / 1.23984)))
            for tag, k in mods:
                if tag in ('agcl3', 'agcl6', 'prot5', 'cov75', 'cov65', 'shrink90'):
                    add(f'M2_{tag}_s{seed}_{inc}_x', **dict(base, **k))                       # in the device (film on TiO2)
                add(f'G_{tag}_s{seed}_{inc}_x', **dict(base, nb=1.52, **k))                    # on glass, as in Fig. S3c,d
    # ---- round 3: everything as the FULL device (film + DBR + glass, light from the glass side as in the experiment), because the
    # zeroth-order cascade misses the coupling of the film's diffraction orders and near field to the DBR (cascade check, D runs).
    dev = dict(film='islands', P=0.3, res=200, inc='bottom', pol='x', stack=DBR, nsub=1.52, nb=1.93)
    mods = (('base', {}), ('agcl3', dict(shell=dict(t=0.003, n=2.07))), ('agcl6', dict(shell=dict(t=0.006, n=2.07))),
            ('prot5', dict(shell=dict(t=0.005, n=1.45))), ('cov75', dict(void=0.25)), ('cov65', dict(void=0.35)),
            ('shrink90', dict(d_scale=0.9, t_scale=0.9)), ('thin85', dict(t_scale=0.85)), ('dg10', dict(dg_extra=0.10 / 1.23984)),
            ('dg20', dict(dg_extra=0.20 / 1.23984)))
    for seed in (1, 2):
        for tag, k in mods:
            if seed == 1 and tag == 'base': continue                                      # = D_s1_bottom_x
            add(f'DV_{tag}_s{seed}_x', **dict(dev, seed=seed, **k))
    for seed in (3, 4):
        add(f'DV_base_s{seed}_x', **dict(dev, seed=seed))
    add('DV_base_s1_y', **dict(dev, seed=1, pol='y'))
    for tag, sph in (('ref', None), ('vlp', dict(d=0.1, n=1.48)), ('ps', dict(d=0.1, n=1.59))):
        add(f'DV_{tag}_P40_s1_x', **dict(dev, seed=1, P=0.4, zref=0.18, sphere=sph))
    # ---- round 4: large cells (P = 0.8 um, ~280 grains) to remove the lattice artefacts of the small periodic cells (P = 0.3 um behaves
    # like a grating: Rayleigh anomalies at n P = 0.3-0.58 um) and the realisation scatter. Film on glass (Fig. S3c,d) and on TiO2 (Tamm side).
    big = dict(film='islands', P=0.8, res=200, pol='x')
    mods4 = (('base', {}), ('agcl3', dict(shell=dict(t=0.003, n=2.07))), ('agcl6', dict(shell=dict(t=0.006, n=2.07))),
             ('prot5', dict(shell=dict(t=0.005, n=1.45))), ('cov75', dict(void=0.25)), ('cov65', dict(void=0.35)),
             ('shrink90', dict(d_scale=0.9, t_scale=0.9)), ('thin85', dict(t_scale=0.85)), ('dg10', dict(dg_extra=0.10 / 1.23984)),
             ('dg20', dict(dg_extra=0.20 / 1.23984)))
    for seed in (1, 2):
        add(f'LG_base_s{seed}_top_x', **dict(big, seed=seed, nb=1.52, inc='top'))
        for tag, k in mods4:
            add(f'LG_{tag}_s{seed}_bottom_x', **dict(big, seed=seed, nb=1.52, inc='bottom', **k))
            add(f'LT_{tag}_s{seed}_bottom_x', **dict(big, seed=seed, nb=1.93, inc='bottom', **k))
    # ---- round 5: fine sweep of the silver loss (round 4: only dissolution reproduces the sign of the Ag-on-glass change and gives a
    # large red shift, but coverage 75 % overshoots, +185 nm vs +90 nm measured). Same seed -> the remaining grains are a subset of the
    # as-deposited ones (random sequential deposition stops earlier), i.e. a paired comparison. Three realisations.
    mods5 = (('v17', dict(void=0.17)), ('v19', dict(void=0.19)), ('v21', dict(void=0.21)), ('v23', dict(void=0.23)),
             ('sh97', dict(d_scale=0.97, t_scale=0.97)), ('sh94', dict(d_scale=0.94, t_scale=0.94)))
    for seed in (1, 2, 3):
        for tag, k in mods5 + ((('base', {}),) if seed == 3 else ()):
            add(f'LG_{tag}_s{seed}_bottom_x', **dict(big, seed=seed, nb=1.52, inc='bottom', **k))
            add(f'LT_{tag}_s{seed}_bottom_x', **dict(big, seed=seed, nb=1.93, inc='bottom', **k))
    # ---- round 6: FULL device with large cells (film + DBR + glass, P = 0.8 um, light from the glass side). Round 5 (zeroth-order
    # cascade) shows the Tamm dip filling and a broad minimum near 800 nm taking over; this checks it without the cascade approximation
    # (diffracted light in the DBR and the near-field coupling included).
    fv = dict(film='islands', P=0.8, res=200, inc='bottom', pol='x', stack=DBR, nsub=1.52, nb=1.93)
    for seed in (1, 2):
        for tag, k in (('base', {}), ('v21', dict(void=0.21)), ('cov65', dict(void=0.35)), ('sh94', dict(d_scale=0.94, t_scale=0.94)),
                       ('shrink90', dict(d_scale=0.9, t_scale=0.9))):
            add(f'FV_{tag}_s{seed}_x', **dict(fv, seed=seed, **k))
    # ---- round 7: silver changes alone (rounds 5, 6) switch the minimum to ~780 nm instead of moving the Tamm dip continuously; in 1D
    # only a layer at the Ag / TiO2 interface (delamination gap, hydrated or AgCl interlayer) gives the measured continuous red shift with
    # the old dip filling up. Full device with such an interlayer under the as-deposited island film.
    for seed in (1, 2):
        for tag, n, g in (('g133_40', 1.333, 0.040), ('g133_80', 1.333, 0.080), ('g207_20', 2.07, 0.020), ('g207_40', 2.07, 0.040)):
            add(f'FG_{tag}_s{seed}_x', **dict(fv, seed=seed, stack=[[n, g]] + DBR))
    return C


if __name__ == '__main__':
    c = cases(); print(len(c), 'cases'); [print(n) for n, k in c]
