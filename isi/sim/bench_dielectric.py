import meep as mp, numpy as np, sys
sys.path.insert(0,'.'); from mie import radial_dipole
res=float(sys.argv[1]); R=0.015874; d=0.005; EPS=-4+1j*1.0  # placeholder replaced below
mat=mp.Medium(epsilon=4.0)
dpml=0.15; sr=0.30; sz=0.60
cell=mp.Vector3(sr+dpml,0,sz+2*dpml)
lmin,lmax=0.48,0.92; fcen=0.5*(1/lmin+1/lmax); df=1/lmin-1/lmax; nf=23
pt=mp.Vector3(0,0,R+d)
def run(geo):
    sim=mp.Simulation(cell_size=cell,dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],geometry=geo,
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res*1000)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=mp.stop_when_fields_decayed(20,mp.Ez,pt,1e-9))
    return np.array(sim.ldos_data)
Fp=run([mp.Sphere(radius=R,material=mat)])/run([])
lam=1000/np.linspace(fcen-df/2,fcen+df/2,nf)
Fm,_=radial_dipole(lam,R*1000,d*1000,lambda l:4.0)
for i in range(0,nf,4): print(f"{lam[i]:.0f} meep {Fp[i]:.3f}  mie {Fm[i]:.3f}  err {100*(Fp[i]/Fm[i]-1):+.1f}%")
