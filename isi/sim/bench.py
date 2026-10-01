"""Benchmark Meep cylindrical LDOS against exact Mie for a radial dipole near a sphere.
usage: python bench.py RES_PER_NM MATERIAL(diel|au)"""
import meep as mp, numpy as np, sys, time
sys.path.insert(0,'.'); from mie import radial_dipole
res=float(sys.argv[1]); which=sys.argv[2]; TRUN=float(sys.argv[3]) if len(sys.argv)>3 else 150
R=0.015874; d=0.005; pt=mp.Vector3(0,0,R+d)
if which=='diel':
    mat=mp.Medium(epsilon=4.0); eps=lambda l:4.0+0j
else:
    from gold_jc import Au_JC, eps_jc; mat=Au_JC; eps=eps_jc
dpml=0.5; sr=0.3; sz=0.6
lmin,lmax=0.48,0.92; fcen=0.5*(1/lmin+1/lmax); df=1/lmin-1/lmax; nf=23
f=np.linspace(fcen-df/2,fcen+df/2,nf); lam=1000/f
def run(geo):
    sim=mp.Simulation(cell_size=mp.Vector3(sr+dpml,0,sz+2*dpml),dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],geometry=geo,
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res*1000)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=TRUN)
    return np.array(sim.ldos_data)
t=time.time(); Fp=run([mp.Sphere(radius=R,material=mat)])/run([]); t=time.time()-t
Fm,_=radial_dipole(lam,R*1000,d*1000,eps)
err=100*(Fp/Fm-1)
for i in range(0,nf,3): print(f"{lam[i]:.0f} meep {Fp[i]:.3f} mie {Fm[i]:.3f} err {err[i]:+.1f}%")
print(f"SUMMARY {which} res={res}/nm  max|err| {abs(err).max():.1f}%  median {np.median(abs(err)):.1f}%  time {t:.0f}s")
