import meep as mp, numpy as np, sys
res=250; R=0.015874; d=0.005; pt=mp.Vector3(0,0,R+d)
lmin,lmax=0.48,0.92; fcen=0.5*(1/lmin+1/lmax); df=1/lmin-1/lmax; nf=12
f=np.linspace(fcen-df/2,fcen+df/2,nf)
def run(sr,sz,dpml,T):
    sim=mp.Simulation(cell_size=mp.Vector3(sr+dpml,0,sz+2*dpml),dimensions=mp.CYLINDRICAL,m=0,boundary_layers=[mp.PML(dpml)],
        sources=[mp.Source(mp.GaussianSource(fcen,fwidth=df),component=mp.Ez,center=pt)],resolution=res)
    sim.run(mp.dft_ldos(fcen,df,nf),until_after_sources=T)
    return np.array(sim.ldos_data)
for (sr,sz,dp,T) in [(0.3,0.6,0.5,50),(0.5,1.0,0.5,50),(0.3,0.6,0.5,150)]:
    a=run(sr,sz,dp,T); print(sr,sz,dp,T,'ldos/f^2 normalized:',np.round(a/f**2/(a[-1]/f[-1]**2),3))
