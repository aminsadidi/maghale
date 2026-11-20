"""1D EMA (TMM) sweep: which single change of the silver film moves the Tamm dip by ~90 nm? usage: cd tamm/analysis && python tmm_sweep.py"""
import json, numpy as np, sys
sys.path.insert(0,'.'); import tmm
B=json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'..','results','baseline.json'))); d=B['dbr']; t=B['td']
lam=np.arange(500,900,1.0)
AgCl=lambda l: np.full(len(l),2.07+0j)
def dev(dAg=t['dAg'],void=t['void'],dg=t['dgamma'],pre=[],post=[]):
    sio=tmm.porous(tmm.SiO2,tmm.AIR,d['pS']); tio=tmm.porous(tmm.TiO2,tmm.AIR,d['pT'])
    ag=tmm.silver(t['ag'],dg,1.0,void,tmm.AIR,t['L'])
    L=list(post)+([(ag,dAg)] if dAg>0 else [])+list(pre)+[(tio,d['dT']*t['scale']),(sio,d['dS']*t['scale'])]*5
    R,T=tmm.device(lam,L,side=t['side']); m=(lam>590)&(lam<860); i=np.argmin(np.where(m,R,9)); return lam[i],100*R[i]
l0,R0=dev(); print(f'base dip {l0:.0f} R {R0:.1f}')
def show(name,**k):
    l,R=dev(**k); print(f'{name:40s} dip {l:.0f}  dlam {l-l0:+5.0f}  dR {R-R0:+5.1f}')
for x in (25,20,15,10): show(f'Ag thinner {x} nm',dAg=x)
for v in (0.3,0.4,0.5): show(f'void {v}',void=v)
for x in (5,10,20): show(f'AgCl {x} nm UNDER Ag (Ag -{x/2:.0f})',dAg=t['dAg']-x/2,pre=[(AgCl,x)])
for x in (5,10,20): show(f'AgCl {x} nm ON TOP (Ag -{x/2:.0f})',dAg=t['dAg']-x/2,post=[(AgCl,x)])
for g in (0.5,1.0): show(f'damping {g} eV',dg=g)
