"""FDTD (Ansys Lumerical) cross-check of the gold-nanorod dimer/trimer, run through lumapi.

Geometry as in the BEM jobs: capsule rods (cylinder + two hemispheres), D = 60 nm, gap 40 nm, rods along x in the plane
z = 0, optional horizontal R3 (length L3, centre (0, Y3)); host index n = 1.5; gold = "Au (Gold) - Johnson and Christy".
Emitter: electric dipole along x at the gap centre.
Outputs per wavelength (1300-1700 nm, 41 points):
  Fp     = dipolepower / sourcepower                        (total decay rate / rate in the host = LDOS)
  T      = net power out of a box enclosing all rods / sourcepower     (radiative enhancement)
  eta    = T / Fp
  f_py, f_my : fractions of the box power through its +y and -y faces (in-plane directionality)
  with --params '{"waveguide": true}': Si3N4 ridge (n = 2.0, 600 x 300 nm) along y, 20 nm below the rods;
  beta_py, beta_my = power through the waveguide cross-section at y = +-2.5 um / total emitted power.
usage: python lumerical_fdtd.py --lumapi <dir of lumapi.py> --name NAME --params JSON --out file.csv --work DIR
"""
import argparse, glob, json, os, re, sys, threading, time

ap = argparse.ArgumentParser()
ap.add_argument('--lumapi', required=True); ap.add_argument('--name', required=True); ap.add_argument('--params', default='{}')
ap.add_argument('--out', required=True); ap.add_argument('--work', required=True); ap.add_argument('--dry', action='store_true',
                                                                                                 help='only write the .lsf script')
a = ap.parse_args()
P = {'L': 285, 'L3': 0, 'Y3': 160, 'dx': 1.0, 'waveguide': False, 'n': 1.5, 'D': 60, 'g': 40, 'coarse': False}
P.update(json.loads(a.params))
os.makedirs(a.work, exist_ok=True)
nm = 1e-9


def capsule(name, xc, yc, L, D):
    """rod along x: cylinder (addcircle, axis z rotated about y) + two spheres"""
    s = [f'addcircle; set("name","{name}_c"); set("x",{xc*nm}); set("y",{yc*nm}); set("z",0); set("radius",{D/2*nm});',
         f'set("z span",{(L-D)*nm}); set("first axis","y"); set("rotation 1",90); set("material",mat);']
    for k, sx in enumerate((-1, 1)):
        s.append(f'addsphere; set("name","{name}_s{k}"); set("x",{(xc+sx*(L-D)/2)*nm}); set("y",{yc*nm}); set("z",0); '
                 f'set("radius",{D/2*nm}); set("material",mat);')
    return '\n'.join(s)


def lsf():
    L, L3, Y3, D, g, n, dx = P['L'], P['L3'], P['Y3'], P['D'], P['g'], P['n'], P['dx']
    xc = g / 2 + L / 2; xmax = xc + L / 2
    ytop = (Y3 + D / 2) if L3 else D / 2
    pad = 700; m = 100                                            # nm: free space around the structure, monitor margin
    rmesh = 6 if P['coarse'] else 2; acc = 1 if P['coarse'] else 3; tsim = 300 if P['coarse'] else 1000
    S = ['switchtolayout; deleteall;', 'mat = "Au (Gold) - Johnson and Christy";',
         capsule('R1', -xc, 0, L, D), capsule('R2', xc, 0, L, D)]
    if L3: S.append(capsule('R3', 0, Y3, L3, D))
    ylo, yhi = -D / 2 - pad, ytop + pad
    zlo = -D / 2 - pad
    if P['waveguide']:
        ylo, yhi = -3000, 3000; zlo = -D / 2 - 20 - 300 - 400
        S.append(f'addrect; set("name","wg"); set("x",0); set("x span",{600*nm}); set("y",0); set("y span",{20000*nm}); '
                 f'set("z",{(-D/2-20-150)*nm}); set("z span",{300*nm}); set("material","<Object defined dielectric>"); set("index",2.0);')
    S += [f'addfdtd; set("dimension","3D"); set("x",0); set("x span",{2*(xmax+pad)*nm}); set("y min",{ylo*nm}); set("y max",{yhi*nm});',
          f'set("z min",{zlo*nm}); set("z max",{(D/2+pad)*nm}); set("index",{n}); set("mesh accuracy",{acc});',
          f'set("simulation time",{tsim}e-15); set("auto shutoff min",1e-5);',
          # 2 nm mesh over all rods, dx in the gap
          f'addmesh; set("name","rods"); set("x",0); set("x span",{2*(xmax+10)*nm}); set("y min",{(-D/2-10)*nm}); set("y max",{(ytop+10)*nm});',
          f'set("z",0); set("z span",{(D+20)*nm}); set("override x mesh",1); set("override y mesh",1); set("override z mesh",1);',
          f'set("dx",{rmesh*nm}); set("dy",{rmesh*nm}); set("dz",{rmesh*nm});',
          f'addmesh; set("name","gap"); set("x",0); set("x span",{(g+10)*nm}); set("y",0); set("y span",{(D+10)*nm}); set("z",0); set("z span",{(D+10)*nm});',
          f'set("override x mesh",1); set("override y mesh",1); set("override z mesh",1); set("dx",{dx*nm}); set("dy",{dx*nm}); set("dz",{dx*nm});',
          'adddipole; set("name","dip"); set("x",0); set("y",0); set("z",0); set("theta",90); set("phi",0);',
          'setglobalsource("wavelength start",1.3e-6); setglobalsource("wavelength stop",1.7e-6); setglobalmonitor("frequency points",41);']
    bx, by0, by1, bz = xmax + m, -D / 2 - m, ytop + m, D / 2 + m
    if P['waveguide']: bz0 = -D / 2 - 20 - 300 - m
    else: bz0 = -bz
    mons = [('bx1', 'X', -bx, None), ('bx2', 'X', bx, None), ('by1', 'Y', by0, None), ('by2', 'Y', by1, None),
            ('bz1', 'Z', bz0, None), ('bz2', 'Z', bz, None)]
    for nme, ax, pos, _ in mons:
        s = f'addpower; set("name","{nme}"); set("monitor type","2D {ax}-normal"); '
        if ax == 'X': s += f'set("x",{pos*nm}); set("y min",{by0*nm}); set("y max",{by1*nm}); set("z min",{bz0*nm}); set("z max",{bz*nm});'
        if ax == 'Y': s += f'set("y",{pos*nm}); set("x min",{-bx*nm}); set("x max",{bx*nm}); set("z min",{bz0*nm}); set("z max",{bz*nm});'
        if ax == 'Z': s += f'set("z",{pos*nm}); set("x min",{-bx*nm}); set("x max",{bx*nm}); set("y min",{by0*nm}); set("y max",{by1*nm});'
        S.append(s)
    if P['waveguide']:
        for nme, y in (('wgm', -2500), ('wgp', 2500)):
            S.append(f'addpower; set("name","{nme}"); set("monitor type","2D Y-normal"); set("y",{y*nm}); set("x",0); set("x span",{1200*nm}); '
                     f'set("z",{(-D/2-20-150)*nm}); set("z span",{1000*nm});')
    return '\n'.join(S)


ANALYSIS = '''f = getdata("bx2","f"); lam = c/f;
P0 = sourcepower(f); Pd = dipolepower(f); Fp = Pd/P0;
T = transmission("bx2") - transmission("bx1") + transmission("by2") - transmission("by1") + transmission("bz2") - transmission("bz1");
fpy = transmission("by2")/T; fmy = -transmission("by1")/T;'''
ANALYSIS_WG = '''bpy = transmission("wgp")/Fp; bmy = -transmission("wgm")/Fp;'''

script = lsf()
open(os.path.join(a.work, a.name + '.lsf'), 'w').write(script + '\n')
if a.dry:
    print('script written'); sys.exit(0)

sys.path.append(a.lumapi)
import lumapi  # noqa: E402
import numpy as np  # noqa: E402

fdtd = lumapi.FDTD(hide=True)
fdtd.eval(script)
proj = os.path.join(a.work, a.name + '.fsp')
fdtd.save(proj)
print(f'project saved: {proj}', flush=True)

done = threading.Event()


def tail_logs():
    """print the engine's '% complete' lines so that the lab-kit runner can estimate the remaining time"""
    seen = 0.0
    while not done.is_set():
        for lg in glob.glob(os.path.join(a.work, a.name + '*_p0.log')) + glob.glob(os.path.join(a.work, a.name + '*.log')):
            try:
                m = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*complete', open(lg, errors='replace').read()[-20000:])
                if m and float(m[-1]) > seen: seen = float(m[-1]); print(f'{seen:.1f}% complete', flush=True)
            except OSError:
                pass
        done.wait(30)


th = threading.Thread(target=tail_logs, daemon=True); th.start()
t0 = time.time()
fdtd.run()
done.set()
print(f'FDTD finished in {(time.time()-t0)/60:.1f} min', flush=True)
fdtd.eval(ANALYSIS + ('\n' + ANALYSIS_WG if P['waveguide'] else ''))
g = lambda k: np.real(np.asarray(fdtd.getv(k))).ravel()
cols = {'lambda_nm': g('lam') * 1e9, 'Fp': g('Fp'), 'T': g('T')}
cols['eta'] = cols['T'] / cols['Fp']; cols['f_py'] = g('fpy'); cols['f_my'] = g('fmy')
if P['waveguide']: cols['beta_py'] = g('bpy'); cols['beta_my'] = g('bmy')
order = np.argsort(cols['lambda_nm'])
with open(a.out, 'w') as f:
    f.write(f'# Lumerical FDTD {a.name}: {json.dumps(P)}\n' + ','.join(cols) + '\n')
    for i in order: f.write(','.join(f'{cols[k][i]:.6g}' for k in cols) + '\n')
fdtd.close()
print('LABKIT_DONE', flush=True)
