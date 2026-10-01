import meep as mp, numpy as np
res=250; R=0.015874; d=0.005; pt=mp.Vector3(0,0,R+d)
lmin,lmax=0.48,0.92; fcen=0.5*(1/lmin+1/lmax); df=1/lmin-1/lmax; nf=12
def run(sr,sz,dpml,geo,decay=1e-9):
    sim=mp.Simulation(cell_size=mp.Vector3(sr+dpml,0,sz+2*dpml),dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],geometry=geo,
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=mp.stop_when_fields_decayed(20,mp.Ez,pt,decay))
    return np.array(sim.ldos_data)
a=run(0.3,0.6,0.15,[]); b=run(0.5,1.0,0.3,[])
np.set_printoptions(precision=4,suppress=False)
print('free small',a); print('free big  ',b); print('ratio',a/b)
