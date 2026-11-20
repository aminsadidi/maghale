"""Random island silver film matching the AFM statistics of the device (Rossini et al., Fig S1 and text):
grain diameter 50 +- 18 nm, area fraction of voids 14.4 %, nominal thickness 33 nm, Rms roughness 8.7 nm.
Grains are vertical cylinders (columnar evaporated grains) with rounded tops (a cylinder + an oblate cap), placed by random sequential
deposition in a periodic P x P cell until the covered area reaches 1 - void. Heights are drawn so that the mean metal thickness
(volume / area) equals the nominal thickness and the height Rms of the surface (including the voids at height 0) is close to the
AFM value. Deterministic for a given seed. Units: um.
usage: python tamm/meep/islands.py  (prints the statistics of a few realisations)"""
import numpy as np


def make(P=0.3, seed=1, d_mean=0.050, d_sd=0.018, void=0.144, t_nom=0.033, rms=0.0087, grid=300):
    rng = np.random.default_rng(seed)
    x = (np.arange(grid) + 0.5) * P / grid; X, Y = np.meshgrid(x, x, indexing='ij')
    cov = np.zeros((grid, grid), bool); grains = []
    for _ in range(5000):
        if cov.mean() >= 1 - void: break
        d = float(np.clip(rng.normal(d_mean, d_sd), 0.02, 0.1)); cx, cy = rng.uniform(0, P, 2)
        dx = np.abs(X - cx); dx = np.minimum(dx, P - dx); dy = np.abs(Y - cy); dy = np.minimum(dy, P - dy)
        m = dx ** 2 + dy ** 2 <= (d / 2) ** 2
        if cov[m].mean() > 0.6: continue                       # avoid fully buried grains
        grains.append([cx, cy, d]); cov |= m
    grains = np.array(grains)
    # height map: the highest grain wins at each pixel; grain i has top height h_i
    hz = rng.normal(1.0, 0.12, len(grains)).clip(0.6, 1.4)
    def hmap(scale):
        H = np.zeros((grid, grid))
        for (cx, cy, d), h in zip(grains, hz * scale):
            dx = np.abs(X - cx); dx = np.minimum(dx, P - dx); dy = np.abs(Y - cy); dy = np.minimum(dy, P - dy)
            r2 = (dx ** 2 + dy ** 2) / (d / 2) ** 2
            prof = np.where(r2 <= 1, 0.8 * h + 0.2 * h * np.sqrt(np.clip(1 - r2, 0, 1)), 0)        # same shape as geometry(): cylinder + cap
            H = np.maximum(H, prof)
        return H
    s = t_nom / hmap(1.0).mean(); H = hmap(s)
    return dict(P=P, grains=grains, heights=hz * s, Hmap=H, coverage=float((H > 0).mean()), t_mean=float(H.mean()),
                rms=float(H.std()), grid=grid, seed=seed)


def geometry_shell(f, z0, material, t):
    """shell of thickness t (um) around every grain (drawn before the grains, which then override the inside)"""
    import meep as mp
    P = f['P']; objs = []
    for (cx, cy, d), h in zip(f['grains'], f['heights']):
        for sx in (-P, 0, P):
            for sy in (-P, 0, P):
                x, y = cx + sx - P / 2, cy + sy - P / 2
                if abs(x) > P / 2 + d + t or abs(y) > P / 2 + d + t: continue
                hc = 0.8 * h
                objs.append(mp.Cylinder(radius=d / 2 + t, height=hc, center=mp.Vector3(x, y, z0 + hc / 2), material=material))
                objs.append(mp.Ellipsoid(size=mp.Vector3(d + 2 * t, d + 2 * t, 2 * (0.2 * h + t)), center=mp.Vector3(x, y, z0 + hc), material=material))
    return objs


def geometry(f, z0, material):
    """Meep objects for island film f with the film bottom at z = z0 (periodic images included). Each grain: cylinder of
    height 0.8 h plus an ellipsoid cap reaching h."""
    import meep as mp
    P = f['P']; objs = []
    for (cx, cy, d), h in zip(f['grains'], f['heights']):
        for sx in (-P, 0, P):
            for sy in (-P, 0, P):
                x, y = cx + sx - P / 2, cy + sy - P / 2
                if abs(x) > P / 2 + d or abs(y) > P / 2 + d: continue
                hc = 0.8 * h
                objs.append(mp.Cylinder(radius=d / 2, height=hc, center=mp.Vector3(x, y, z0 + hc / 2), material=material))
                objs.append(mp.Ellipsoid(size=mp.Vector3(d, d, 2 * 0.2 * h), center=mp.Vector3(x, y, z0 + hc), material=material))
    return objs


if __name__ == '__main__':
    for P in (0.3, 0.4):
        for s in (1, 2, 3, 4):
            f = make(P, s)
            print(f'P {P} seed {s}: grains {len(f["grains"])}, coverage {f["coverage"]:.3f}, mean thickness {1000*f["t_mean"]:.1f} nm, '
                  f'Rms {1000*f["rms"]:.1f} nm, max height {1000*f["Hmap"].max():.0f} nm')
