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
    return C


if __name__ == '__main__':
    c = cases(); print(len(c), 'cases'); [print(n) for n, k in c]
