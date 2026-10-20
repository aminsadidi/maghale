"""Gold particle trapped in a gold nanohole, 3D Meep FDTD at 785 nm.

Geometry from Huang et al., Nat. Commun. 10, 5321 (2019) and J.-A. Huang (email, 19 Oct 2026):
  hole diameter 200 nm through 100 nm Au on 100 nm Si3N4, Au particle diameter 50 nm,
  water n = 1.33, SiN n = 2.0, excitation 785 nm from the gold side, polarisation along x.
The nanourchin is replaced by a sphere (see README). The particle sits at mid-height of the
gold layer, displaced along +x so that its surface is `gap` nm from the hole wall.

Only the response at 785 nm is needed, so gold is a single Drude pole fitted exactly to the
Rakic (1998) permittivity at 785 nm (meep.materials.Au gives -19.25+2.03i). The DFT at 785 nm
is then the exact frequency-domain solution for that permittivity, with a much smaller memory
footprint than the 6-pole model. Mirror symmetry y -> -y halves the cell.
The cell is one period of the hole array (default pitch 400 nm). Units: 1 = 1 um.
"""
import argparse
import numpy as np
import meep as mp
from meep.materials import Au

p = argparse.ArgumentParser()
p.add_argument("--gap", type=float, default=5, help="particle-wall gap (nm)")
p.add_argument("--mode", choices=["full", "hole", "empty"], default="full",
               help="hole = no particle; empty = water only (incident-field reference)")
p.add_argument("--res", type=int, default=500)
p.add_argument("--pitch", type=float, default=400, help="hole-array period (nm)")
p.add_argument("--out", default="pip.npz")
a = p.parse_args()

nm = 1e-3
lam0 = 0.785
f0 = 1 / lam0
# single Drude pole with eps(f0) = Rakic value: eps = 1 - fp^2/(f^2 + i*g*f)  (Meep convention)
e = complex(Au.epsilon(f0)[0, 0])
X = 1 - e                                        # = fp^2 / (f0^2 + i g f0)
g = f0 * (1 / X).imag / (1 / X).real            # from Im/Re of 1/X
fp2 = (f0 ** 2) / (1 / X).real
gold = mp.Medium(epsilon=1, E_susceptibilities=[mp.DrudeSusceptibility(frequency=1, gamma=g, sigma=fp2)])
assert abs(gold.epsilon(f0)[0, 0] - e) < 1e-6 * abs(e)
water, sin_ = mp.Medium(index=1.33), mp.Medium(index=2.0)

Rh, tAu, tSiN, Rp = 100 * nm, 100 * nm, 100 * nm, 25 * nm
dpml, mzb, mzt = 0.2, 0.08, 0.12
sx = a.pitch * nm
z_lo, z_hi = -tSiN - mzb - dpml, tAu + mzt + dpml     # Au/SiN interface at z = 0
sz = z_hi - z_lo
zc = 0.5 * (z_lo + z_hi)
V = lambda x, y, z: mp.Vector3(x, y, z - zc)

geom = [mp.Block(center=V(0, 0, -tSiN / 2), size=mp.Vector3(mp.inf, mp.inf, tSiN), material=sin_),
        mp.Block(center=V(0, 0, tAu / 2), size=mp.Vector3(mp.inf, mp.inf, tAu), material=gold),
        mp.Cylinder(radius=Rh, height=tAu + tSiN, center=V(0, 0, (tAu - tSiN) / 2), material=water)]
if a.mode == "empty":
    geom = []
xp = Rh - a.gap * nm - Rp
zp = tAu / 2
if a.mode == "full":
    geom.append(mp.Sphere(radius=Rp, center=V(xp, 0, zp), material=gold))

z_src = tAu + mzt - 0.03
src = mp.Source(mp.GaussianSource(f0, fwidth=0.4 * f0, is_integrated=True), component=mp.Ex,
                center=V(0, 0, z_src), size=mp.Vector3(sx, sx, 0))
# The device is a hole array: a periodic cell keeps the incident wave a clean plane wave and
# avoids a PML through the dispersive Au film (unstable). PML only along z (water on both sides).
sim = mp.Simulation(cell_size=mp.Vector3(sx, sx, sz), resolution=a.res, boundary_layers=[mp.PML(dpml, direction=mp.Z)],
                    geometry=geom, default_material=water, sources=[src],
                    symmetries=[mp.Mirror(mp.Y)], k_point=mp.Vector3())

L = sx / 2
xz = mp.Volume(center=V(0, 0, 0.5 * (tAu - tSiN)), size=mp.Vector3(2 * L, 0, tAu + tSiN + 0.08))
xy = mp.Volume(center=V(0, 0, zp), size=mp.Vector3(2 * L, 2 * L, 0))
comps = [mp.Ex, mp.Ey, mp.Ez]
d_xz = sim.add_dft_fields(comps, [f0], where=xz)
d_xy = sim.add_dft_fields(comps, [f0], where=xy)
sim.run(until_after_sources=mp.stop_when_dft_decayed(1e-4, 0))

out = {}
for tag, d, vol in (("xz", d_xz, xz), ("xy", d_xy, xy)):
    I = sum(np.abs(sim.get_dft_array(d, c, 0)) ** 2 for c in comps)
    x, y, z, w = sim.get_array_metadata(vol=vol)
    out[f"I_{tag}"] = I
    x, y, z = np.asarray(x), np.asarray(y), np.asarray(z) + zc
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    lab = np.zeros(X.shape, int)                 # 0 water, 1 gold, 2 SiN
    if a.mode != "empty":
        lab[(Z >= 0) & (Z <= tAu)] = 1
        lab[(Z >= -tSiN) & (Z < 0)] = 2
        lab[np.hypot(X, Y) < Rh] = 0
        if a.mode == "full":
            lab[np.sqrt((X - xp) ** 2 + Y ** 2 + (Z - zp) ** 2) < Rp] = 1
    out[f"eps_{tag}"] = lab
    out[f"x_{tag}"], out[f"y_{tag}"], out[f"z_{tag}"] = x, y, z
if mp.am_master():   # every MPI rank holds the gathered arrays
    np.savez_compressed(a.out, gap=a.gap, mode=a.mode, res=a.res, xp=xp, zp=zp, Rp=Rp, **out)
print("saved", a.out)
