"""Benchmark: split band into sub-bands (each with own Gaussian) to remove band-edge errors.
usage: python bench2.py RES_PER_NM diel|au TRUN DPML"""
import meep as mp, numpy as np, sys, time
sys.path.insert(0,'.'); from mie import radial_dipole
res=float(sys.argv[1]); which=sys.argv[2]; TRUN=float(sys.argv[3]); dpml=float(sys.argv[4])
R=0.015874; d=0.005; pt=mp.Vector3(0,0,R+d)
if which=='diel': mat=mp.Medium(epsilon=4.0); eps=lambda l:4.0+0j
else:
    from gold_jc import Au_JC, eps_jc; mat=Au_JC; eps=eps_jc
sr=0.15; sz=0.30
BANDS=[(0.47,0.59),(0.55,0.73),(0.68,0.95)]; KEEP=[(0.49,0.57),(0.57,0.70),(0.70,0.91)]
def run(geo,fcen,df,nf):
    sim=mp.Simulation(cell_size=mp.Vector3(sr+dpml,0,sz+2*dpml),dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],geometry=geo,
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res*1000)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=TRUN)
    return np.array(sim.ldos_data)
t=time.time(); L=[];F=[]
for (a,b),(ka,kb) in zip(BANDS,KEEP):
    fcen=0.5*(1/a+1/b); df=1/a-1/b; nf=31; f=np.linspace(fcen-df/2,fcen+df/2,nf); lam=1/f
    Fp=run([mp.Sphere(radius=R,material=mat)],fcen,df,nf)/run([],fcen,df,nf)
    m=(lam>=ka)&(lam<=kb); L+=list(1000*lam[m]); F+=list(Fp[m])
t=time.time()-t; L=np.array(L); F=np.array(F); o=np.argsort(L); L,F=L[o],F[o]
Fm,_=radial_dipole(L,R*1000,d*1000,eps); err=100*(F/Fm-1)
for i in range(0,len(L),5): print(f"{L[i]:.0f} meep {F[i]:.2f} mie {Fm[i]:.2f} err {err[i]:+.1f}%")
print(f"SUMMARY {which} res={res}/nm T={TRUN} pml={dpml}: max|err| {abs(err).max():.1f}% median {np.median(abs(err)):.1f}% peak meep {F.max():.0f}@{L[F.argmax()]:.0f} mie {Fm.max():.0f}@{L[Fm.argmax()]:.0f} time {t:.0f}s")
