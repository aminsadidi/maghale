"""Gold sphere, radial dipole 5 nm: Fp from LDOS vs Fp from power balance (P_rad + P_abs)/P0."""
import meep as mp, numpy as np, sys, json, time
sys.path.insert(0,'.')
from gold_jc import Au_JC
from mie import radial_dipole
res=float(sys.argv[1]); R=0.015874; d=float(sys.argv[2])/1000 if len(sys.argv)>2 else 0.005; zd=R+d
BANDS=[(0.46,0.61),(0.54,0.76),(0.63,0.99)]; KEEP=[(0.49,0.57),(0.57,0.70),(0.70,0.90)]
dpml=float(sys.argv[3]) if len(sys.argv)>3 else 0.3; TR=float(sys.argv[4]) if len(sys.argv)>4 else 60; pad=0.04; rbox=R+pad; hz=zd+pad
cell=mp.Vector3(rbox+0.04+dpml,0,2*(hz+0.04)+2*dpml)
ra=R+0.003; zt=R+d/2; zb=-(R+0.003)          # absorption box: encloses sphere, top disk at mid-gap
L=[];FL=[];FF=[];TT=[]
t0=time.time()
for (lo,hi),(ka,kb) in zip(BANDS,KEEP):
    fcen=0.5*(1/lo+1/hi); df=1/lo-1/hi; nf=31
    out={}
    for tag,geo in (('s',[mp.Sphere(radius=R,material=Au_JC)]),('f',[])):
        sim=mp.Simulation(cell_size=cell,dimensions=mp.CYLINDRICAL,m=0,resolution=res*1000,boundary_layers=[mp.PML(dpml)],geometry=geo,
            sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=mp.Vector3(0,0,zd))])
        rad=sim.add_flux(fcen,df,nf,mp.FluxRegion(center=mp.Vector3(rbox/2,0,hz),size=mp.Vector3(rbox,0,0),weight=1),
                         mp.FluxRegion(center=mp.Vector3(rbox/2,0,-hz),size=mp.Vector3(rbox,0,0),weight=-1),
                         mp.FluxRegion(center=mp.Vector3(rbox,0,0),size=mp.Vector3(0,0,2*hz),weight=1))
        ab=sim.add_flux(fcen,df,nf,mp.FluxRegion(center=mp.Vector3(ra/2,0,zt),size=mp.Vector3(ra,0,0),weight=1),
                         mp.FluxRegion(center=mp.Vector3(ra/2,0,zb),size=mp.Vector3(ra,0,0),weight=-1),
                         mp.FluxRegion(center=mp.Vector3(ra,0,(zt+zb)/2),size=mp.Vector3(0,0,zt-zb),weight=1))
        sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=TR)
        out[tag]=(np.array(sim.ldos_data),np.array(mp.get_fluxes(rad)),np.array(mp.get_fluxes(ab)))
        sim.reset_meep()
    lam=1000/np.linspace(fcen-df/2,fcen+df/2,nf); m=(lam>=1000*ka)&(lam<=1000*kb)
    Prad=out['s'][1]; Pabs=-out['s'][2]; P0=out['f'][1]
    L+=list(lam[m]); FL+=list((out['s'][0]/out['f'][0])[m]); FF+=list(((Prad+Pabs)/P0)[m]); TT+=list((Prad/P0)[m])
o=np.argsort(L); L,FL,FF,TT=[np.array(x)[o] for x in (L,FL,FF,TT)]
P=json.load(open('gold_jc_params.json'))
def eps(l):
    f=1000/np.asarray(l,float); return P['einf']-P['s0']*P['f0']**2/(f**2+1j*f*P['g0'])+P['s1']*P['f1']**2/(P['f1']**2-f**2-1j*f*P['g1'])+P['s2']*P['f2']**2/(P['f2']**2-f**2-1j*f*P['g2'])
Fm,Tm=radial_dipole(L,15.874,d*1000,eps)
if mp.am_master():
    for j in range(0,len(L),5): print(f"{L[j]:.0f}  Mie {Fm[j]:.0f} | LDOS {FL[j]:.0f} | flux {FF[j]:.0f} | T {TT[j]:.2f} vs {Tm[j]:.2f}")
    e1=100*(FL/Fm-1); e2=100*(FF/Fm-1)
    print(f"RESULT grid {1/res:.2f} nm: median err LDOS {np.median(abs(e1)):.0f}%  flux {np.median(abs(e2)):.0f}%  ({time.time()-t0:.0f}s)")
