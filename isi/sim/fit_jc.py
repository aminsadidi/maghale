"""Fit Johnson-Christy Au to Drude + 2 Lorentz poles in Meep's convention (frequency f = 1/lambda[um]).
chi_Drude = -s0 f0^2/(f^2 + i f g0) ; chi_Lor = s f_n^2/(f_n^2 - f^2 - i f g)."""
import numpy as np, re, json
from scipy.optimize import least_squares
txt=open('jc_au.yml').read()
d=np.array([list(map(float,l.split())) for l in txt.split('data: |')[1].strip().split('\n') if re.match(r'\s*[\d.]',l)])
lam,n,k=d.T; m=(lam>=0.44)&(lam<=1.0); lam,n,k=lam[m],n[m],k[m]
eps=(n+1j*k)**2; f=1/lam
def model(p,f):
    einf,f0,g0,s0,f1,g1,s1,f2,g2,s2=p
    return einf - s0*f0**2/(f**2+1j*f*g0) + s1*f1**2/(f1**2-f**2-1j*f*g1) + s2*f2**2/(f2**2-f**2-1j*f*g2)
def res(p):
    r=(model(p,f)-eps)/abs(eps)**0.5
    return np.concatenate([r.real,r.imag])
p0=[2,7,0.06,1,2.2,0.5,1,3.2,1,1]
lb=[1,1,0,0.01,1.5,0.01,0.01,2.3,0.01,0.01]; ub=[12,15,2,10,2.3,3,20,6,6,20]
best=None
for s in range(40):
    q=np.array(p0)*np.exp(np.random.default_rng(s).normal(0,0.3,10)); q=np.clip(q,lb,ub)
    r=least_squares(res,q,bounds=(lb,ub),max_nfev=20000)
    if best is None or r.cost<best.cost: best=r
p=best.x; e=model(p,f)
rel=abs(e-eps)/abs(eps)
print('params',np.round(p,4).tolist()); print('max rel err %.1f%%, rms %.1f%%'%(100*rel.max(),100*np.sqrt((rel**2).mean())))
for L in [0.5,0.52,0.6,0.7,0.8,0.9]:
    i=abs(lam-L).argmin(); print(f"{1000*lam[i]:.0f} nm  JC {eps[i]:.2f}  fit {e[i]:.2f}")
json.dump(dict(zip('einf f0 g0 s0 f1 g1 s1 f2 g2 s2'.split(),p.tolist())),open('gold_jc_params.json','w'),indent=1)
