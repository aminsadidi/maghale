# Benchmark: Au sphere R=15.874 nm, radial (z) dipole 5 nm from surface, cylindrical m=0. Compare with Mie (772 @ 506 nm).
import meep as mp, numpy as np, sys
from meep.materials import Au
res=float(sys.argv[1]); R=0.015874; d=0.005
dpml=0.10; sr=0.20; sz=0.40
cell=mp.Vector3(sr+dpml,0,sz+2*dpml)
lmin,lmax=0.48,0.92; fcen=0.5*(1/lmin+1/lmax); df=1/lmin-1/lmax; nf=45
pt=mp.Vector3(0,0,R+d)
def run(geo):
    sim=mp.Simulation(cell_size=cell,dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],geometry=geo,
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res*1000)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=mp.stop_when_fields_decayed(20,mp.Ez,pt,1e-7))
    return np.array(sim.ldos_data)
l1=run([mp.Sphere(radius=R,material=Au)]); l0=run([])
f=np.linspace(fcen-df/2,fcen+df/2,nf); lam=1000/f; Fp=l1/l0
o=np.argsort(lam)
for i in o[::4]: print(f"{lam[i]:.0f} nm  Fp={Fp[i]:.1f}")
i=Fp.argmax(); print(f"RESULT res={res}/nm: Fp max {Fp[i]:.0f} at {lam[i]:.0f} nm")
