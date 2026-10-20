"""Bowl-shaped (and conventional) gold nanopore, Meep FDTD in cylindrical coordinates.

Reproduces the optical model of Zhao et al., Nano Lett. 23, 4830 (2023), SI Note 2:
  Au bowl layer h1 = 100 nm on Si3N4 h2 = 30 nm, bowl opening D = 250 nm,
  metal thickness at the pore h3, pore radius R, water n = 1.33, SiN n = 2.0,
  gold from Rakic et al. (1998) Lorentz-Drude (= meep.materials.Au).

The structure is axisymmetric and the illumination is normal, so a linearly
polarised beam is the sum of the m = +1 and m = -1 angular orders, which are
mirror images of each other. One 2D (r, z) run with m = +1 and source
Er = 1, Ep = i therefore gives the full 3D field of an x-polarised beam:
  |E|^2(r, phi, z) = (|Er|^2 + |Ez|^2) cos^2(phi) + |Ep|^2 sin^2(phi)
(phi = 0 is the polarisation plane). Units: 1 = 1 um.
"""
import argparse
import numpy as np
import meep as mp
from meep.materials import Au, Au_JC_visible

p = argparse.ArgumentParser()
p.add_argument("--R", type=float, default=10, help="pore radius (nm)")
p.add_argument("--h3", type=float, default=5, help="Au thickness at the pore (nm)")
p.add_argument("--shape", choices=["bowl", "conv", "sphere", "empty"], default="bowl")
p.add_argument("--res", type=int, default=1000, help="pixels per um (1000 = 1 nm)")
p.add_argument("--gold", choices=["rakicfit", "rakic", "jc"], default="rakicfit")
p.add_argument("--w0", type=float, default=0, help="Gaussian waist (nm); 0 = plane wave")
p.add_argument("--courant", type=float, default=0.5,
               help="0.25 keeps the 6-pole Rakic gold stable on <= 1 nm grids with a 5 nm lip")
p.add_argument("--out", default="out.npz")
a = p.parse_args()

nm = 1e-3
# Rakic (1998) gold refitted over 500-1050 nm with Drude + 2 Lorentz poles (max error 0.19 %).
# The 6-pole meep.materials.Au has poles up to 10.7 um^-1 and goes unstable (NaN) on <= 1 nm grids
# when the Au lip is 5 nm or thinner; the low-frequency poles of the refit do not.
au_fit = mp.Medium(epsilon=3.86539, E_susceptibilities=[
    mp.DrudeSusceptibility(frequency=1, gamma=0.05919, sigma=42.64695),
    mp.LorentzianSusceptibility(frequency=2.68573, gamma=1.10225, sigma=2.51656),
    mp.LorentzianSusceptibility(frequency=1.5959, gamma=0.75444, sigma=0.03578)])
assert abs(au_fit.epsilon(1 / 0.785)[0, 0] - Au.epsilon(1 / 0.785)[0, 0]) < 0.01 * abs(Au.epsilon(1 / 0.785)[0, 0])
gold = {"rakicfit": au_fit, "rakic": Au, "jc": Au_JC_visible}[a.gold]
water = mp.Medium(index=1.33)
sin_ = mp.Medium(index=2.0)
h1, h2, D = 100 * nm, 30 * nm, 250 * nm
R, h3 = a.R * nm, a.h3 * nm

dpml = 0.25
r_phys, z_below, z_above = 0.5, 0.1, 0.15
sr = r_phys + dpml
z_lo = -h2 - z_below - dpml           # Au/SiN interface at z = 0
z_hi = h1 + z_above + dpml
sz = z_hi - z_lo
zc = 0.5 * (z_lo + z_hi)
cell = mp.Vector3(sr, 0, sz)


def blk(r0, r1, z0, z1, mat):
    return mp.Block(center=mp.Vector3(0.5 * (r0 + r1), 0, 0.5 * (z0 + z1) - zc),
                    size=mp.Vector3(r1 - r0, mp.inf, z1 - z0), material=mat)


geom = []
if a.shape == "bowl":
    # spherical bowl through (D/2, h1) and (R, h3), centre on the axis
    H = h1 - h3
    u = ((D / 2) ** 2 - R ** 2 - H ** 2) / (2 * H)
    Rs = np.hypot(D / 2, u)
    geom = [blk(0, sr, -h2, 0, sin_), blk(0, sr, 0, h1, gold),
            mp.Sphere(center=mp.Vector3(0, 0, h1 + u - zc), radius=Rs, material=water),
            blk(0, sr, h1, z_hi, water),   # sphere cap above the film is water anyway
            blk(0, R, -h2, h1, water)]
elif a.shape == "conv":
    geom = [blk(0, sr, -h2, 0, sin_), blk(0, sr, 0, h3, gold), blk(0, R, -h2, h3, water)]
elif a.shape == "sphere":   # validation against Mie theory: Au sphere of radius R at z = 0
    geom = [mp.Sphere(center=mp.Vector3(0, 0, -zc), radius=R, material=gold)]

lam = np.linspace(0.55, 1.0, 46)
freqs = 1 / lam
fcen, df = 0.5 * (freqs.max() + freqs.min()), 1.2 * (freqs.max() - freqs.min())
z_src = h1 + z_above - 0.05
w0 = a.w0 * nm
amp = (lambda v: np.exp(-(v.x / w0) ** 2)) if w0 > 0 else (lambda v: 1.0)
src_kw = dict(center=mp.Vector3(0.5 * sr, 0, z_src - zc), size=mp.Vector3(sr), amp_func=amp)
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df, is_integrated=True), component=mp.Er, **src_kw),
           mp.Source(mp.GaussianSource(fcen, fwidth=df, is_integrated=True), component=mp.Ep,
                     amplitude=1j, **src_kw)]

sim = mp.Simulation(cell_size=cell, resolution=a.res, dimensions=mp.CYLINDRICAL, m=1,
                    boundary_layers=[mp.PML(dpml)], geometry=geom, default_material=water,
                    sources=sources, force_complex_fields=True, Courant=a.courant)

# hot-spot region (all wavelengths) and wide map (785 nm only)
zt = h3 if a.shape in ("bowl", "conv") else 0
small = mp.Volume(center=mp.Vector3(0.5 * (R + 25 * nm), 0, zt - zc),
                  size=mp.Vector3(R + 25 * nm, 0, 50 * nm))
wide = mp.Volume(center=mp.Vector3(0.16, 0, 0.5 * (-h2 - 0.05 + h1 + 0.08) - zc),
                 size=mp.Vector3(0.32, 0, h1 + 0.08 + h2 + 0.05))
comps = [mp.Er, mp.Ep, mp.Ez]
d_small = sim.add_dft_fields(comps, freqs, where=small)
d_wide = sim.add_dft_fields(comps, [1 / 0.785], where=wide)

sim.run(until_after_sources=mp.stop_when_dft_decayed(1e-6, 0))


def grab(d, vol, nf):
    # Meep returns cylindrical DFT arrays as (z, r); store them as (r, z)
    F = {c: np.array([sim.get_dft_array(d, c, i).T for i in range(nf)]) for c in comps}
    nr, nz = F[mp.Er].shape[1:]   # get_array_metadata is not available in cylindrical
    c, s = vol.center, vol.size
    return (F, np.linspace(c.x - s.x / 2, c.x + s.x / 2, nr),
            np.linspace(c.z - s.z / 2, c.z + s.z / 2, nz) + zc)


Fs, rs, zs = grab(d_small, small, len(freqs))
Fw, rw, zw = grab(d_wide, wide, 1)


def label(r, z):
    """0 water, 1 gold, 2 SiN on the output grid (get_array(Dielectric) is unreliable here)."""
    r, z = np.meshgrid(r, z, indexing="ij")
    lab = np.zeros(r.shape, int)
    if a.shape == "sphere":
        lab[np.hypot(r, z) < R] = 1
    elif a.shape in ("bowl", "conv"):
        top = h1 if a.shape == "bowl" else h3
        lab[(z >= 0) & (z <= top)] = 1
        lab[(z >= -h2) & (z < 0)] = 2
        if a.shape == "bowl":
            lab[(lab == 1) & (np.hypot(r, z - h1 - u) < Rs)] = 0
        lab[(r < R) & (z >= -h2) & (z <= top)] = 0
    return lab


eps, epw = label(rs, zs), label(rw, zw)
if mp.am_master():   # every MPI rank holds the gathered arrays
    np.savez_compressed(a.out, lam=lam, rs=rs, zs=zs, Er=Fs[mp.Er], Ep=Fs[mp.Ep], Ez=Fs[mp.Ez],
                    rw=rw, zw=zw, Erw=Fw[mp.Er][0], Epw=Fw[mp.Ep][0], Ezw=Fw[mp.Ez][0],
                    eps=eps, epw=epw, args=str(vars(a)))
print("saved", a.out)
