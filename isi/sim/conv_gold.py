import sys, json, time, numpy as np; sys.path.insert(0, '.')
import meep as mp
from nanorod import simulate, save_csv
from mie import radial_dipole
res = float(sys.argv[1]); t = time.time()
o = simulate('sphere', 'z', 5.0, res=res)
if mp.am_master():
    save_csv(f'conv_gold_sphere_res{res}.csv', o, f'res={res}')
    P = json.load(open('gold_jc_params.json'))
    f = 1000 / o['lam']
    eps = lambda l, f=None: (lambda f: P['einf'] - P['s0']*P['f0']**2/(f**2+1j*f*P['g0']) + P['s1']*P['f1']**2/(P['f1']**2-f**2-1j*f*P['g1']) + P['s2']*P['f2']**2/(P['f2']**2-f**2-1j*f*P['g2']))(1000/np.asarray(l,float))
    Fm, Tm = radial_dipole(o['lam'], 15.874, 5.0, eps)
    e = 100 * (o['Fp'] / Fm - 1); et = 100 * (o['T'] / Tm - 1)
    print(f"RESULT grid {1/res:.2f} nm: Fp median err {np.median(abs(e)):.1f}% max {abs(e).max():.1f}% | peak {o['Fp'].max():.0f}@{o['lam'][o['Fp'].argmax()]:.0f} vs Mie {Fm.max():.0f}@{o['lam'][Fm.argmax()]:.0f} | T median err {np.median(abs(et)):.1f}% | {time.time()-t:.0f}s", flush=True)
