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
  far field (homogeneous host only, i.e. not with the waveguide): a second, spatially down-sampled box of DFT monitors 20 nm outside
  the power box; near-to-far transformation of its six faces (lab/farfield.py, equal-area directions); the sign convention is
  checked against Lumerical's own farfield3d of the top face. Columns ff_py60, ff_my60 = far-field power fraction in 60 deg
  cones about +y / -y (same definition as the BEM f_py60 / f_my60), ff_zNA13, ff_zNA09 = fraction collected along +z by NA 1.3 / 0.9,
  ff_check = far-field power / box power (should be 1). In-plane patterns at 1450, 1550, 1650 nm -> <out>_pattern.csv.
  params: L, L3, Y3, D, g, n, dx (gap mesh), rmesh (rod mesh, 2 nm), mat (Lumerical material name), conformal (metal conformal mesh),
  waveguide, farfield, ff_strict (abort if the far field fails; smoke test), coarse.
usage: python lumerical_fdtd.py --lumapi <dir of lumapi.py> --name NAME --params JSON --out file.csv --work DIR
"""
import argparse, glob, json, os, re, sys, threading, time

ap = argparse.ArgumentParser()
ap.add_argument('--lumapi', required=True); ap.add_argument('--name', required=True); ap.add_argument('--params', default='{}')
ap.add_argument('--out', required=True); ap.add_argument('--work', required=True); ap.add_argument('--dry', action='store_true',
                                                                                                 help='only write the .lsf script')
a = ap.parse_args()
P = {'L': 285, 'L3': 0, 'Y3': 160, 'dx': 1.0, 'waveguide': False, 'n': 1.5, 'D': 60, 'g': 40, 'coarse': False, 'rmesh': 2.0,
     'mat': 'Au (Gold) - Johnson and Christy', 'conformal': False, 'farfield': True, 'ff_strict': False}
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
    rmesh = 6 if P['coarse'] else P['rmesh']; acc = 1 if P['coarse'] else 3; tsim = 300 if P['coarse'] else 1000
    S = ['switchtolayout; deleteall;', f'mat = "{P["mat"]}";',
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
          'set("mesh refinement","conformal variant 1");' if P['conformal'] else '',
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
    if FF_ON:                                                     # far-field box: 20 nm outside the power box
        e = 20; fx, fy0, fy1, fz, fz0 = bx + e, by0 - e, by1 + e, bz + e, bz0 - e
        for nme, ax, pos in (('ffx1', 'X', -fx), ('ffx2', 'X', fx), ('ffy1', 'Y', fy0), ('ffy2', 'Y', fy1), ('ffz1', 'Z', fz0), ('ffz2', 'Z', fz)):
            s = f'addpower; set("name","{nme}"); set("monitor type","2D {ax}-normal"); '
            if ax == 'X': s += f'set("x",{pos*nm}); set("y min",{fy0*nm}); set("y max",{fy1*nm}); set("z min",{fz0*nm}); set("z max",{fz*nm});'
            if ax == 'Y': s += f'set("y",{pos*nm}); set("x min",{-fx*nm}); set("x max",{fx*nm}); set("z min",{fz0*nm}); set("z max",{fz*nm});'
            if ax == 'Z': s += f'set("z",{pos*nm}); set("x min",{-fx*nm}); set("x max",{fx*nm}); set("y min",{fy0*nm}); set("y max",{fy1*nm});'
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

FF_ON = bool(P['farfield']) and not P['waveguide']
FF_MONS = ['ffx1', 'ffx2', 'ffy1', 'ffy2', 'ffz1', 'ffz2'] if FF_ON else []
script = lsf()
open(os.path.join(a.work, a.name + '.lsf'), 'w').write(script + '\n')
if a.dry:
    print('script written'); sys.exit(0)

# older lumapi versions do not register their DLL folders (needed with Python >= 3.8 on Windows)
_root = os.path.dirname(os.path.dirname(os.path.abspath(a.lumapi)))
for _d in (a.lumapi, os.path.join(_root, 'bin'), os.path.join(_root, 'api', 'c')):
    if os.path.isdir(_d):
        os.environ['PATH'] = _d + os.pathsep + os.environ.get('PATH', '')
        if hasattr(os, 'add_dll_directory'):
            try: os.add_dll_directory(_d)
            except OSError: pass
sys.path.append(a.lumapi)
import lumapi  # noqa: E402
import numpy as np  # noqa: E402

try:
    fdtd = lumapi.FDTD(hide=True)
except TypeError:                                    # very old lumapi without the hide option
    fdtd = lumapi.FDTD()
fdtd.eval(script)

# Spectral range, set explicitly on the dipole and on every monitor. In Lumerical 2024 a new dipole overrides the global
# source settings with its own 400-700 nm default, so setglobalsource alone gave 400-700 nm spectra (first lab run).
WL0, WL1, NPTS = 1.3e-6, 1.7e-6, 41


def tryset(obj, prop, val):
    try: fdtd.setnamed(obj, prop, val); return True
    except Exception as e: print(f'  note: {obj}.{prop} not set ({str(e)[:80]})', flush=True); return False


tryset('dip', 'override global source settings', 1)
tryset('dip', 'wavelength start', WL0); tryset('dip', 'wavelength stop', WL1)
mons = ['bx1', 'bx2', 'by1', 'by2', 'bz1', 'bz2'] + (['wgm', 'wgp'] if P['waveguide'] else []) + FF_MONS
for mo in mons:
    tryset(mo, 'override global monitor settings', 1); tryset(mo, 'use source limits', 0)
    tryset(mo, 'minimum wavelength', WL0); tryset(mo, 'maximum wavelength', WL1); tryset(mo, 'frequency points', NPTS)
for mo in FF_MONS:                                   # far-field faces: every 2nd mesh point is enough at >= 120 nm from the gold
    for ax in 'XYZ': tryset(mo, f'down sample {ax}', 2)


def check_range(lo, hi, what):
    ok = abs(lo - WL0) < 0.02 * WL0 and abs(hi - WL1) < 0.02 * WL1
    print(f'  {what}: {lo*1e9:.0f} - {hi*1e9:.0f} nm  ->  {"OK" if ok else "WRONG"}', flush=True)
    if not ok:
        print('LABKIT_ERROR wrong wavelength range: the simulation is NOT run. Send this log.', flush=True)
        sys.exit(3)


print('checking the wavelength range before the run:', flush=True)
for obj, a0, a1 in (('dip', 'wavelength start', 'wavelength stop'), ('bx2', 'minimum wavelength', 'maximum wavelength')):
    try: lo, hi = float(fdtd.getnamed(obj, a0)), float(fdtd.getnamed(obj, a1))
    except Exception as e: print(f'  {obj}: range not readable ({str(e)[:60]}), checked after the run', flush=True); continue
    check_range(lo, hi, obj)
proj =os.path.join(a.work, a.name + '.fsp')
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
check_range(cols['lambda_nm'].min() * 1e-9, cols['lambda_nm'].max() * 1e-9, 'computed spectrum')   # no CSV if wrong


def far_field():
    """near-to-far transformation of the ff box; returns extra columns (aligned with cols['lambda_nm']) and writes the patterns"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import farfield as FFm
    t1 = time.time(); faces = []; lam_ff = None
    for mo, axis, nrm in (('ffx1', 0, -1), ('ffx2', 0, 1), ('ffy1', 1, -1), ('ffy2', 1, 1), ('ffz1', 2, -1), ('ffz2', 2, 1)):
        rE, rH = fdtd.getresult(mo, 'E'), fdtd.getresult(mo, 'H')
        xyz = [np.real(np.asarray(rE[c])).ravel() for c in 'xyz']
        f = np.real(np.asarray(rE['f'])).ravel(); nf = len(f)
        E = np.asarray(rE['E']).reshape(len(xyz[0]), len(xyz[1]), len(xyz[2]), nf, 3)
        H = np.asarray(rH['H']).reshape(len(xyz[0]), len(xyz[1]), len(xyz[2]), nf, 3)
        faces.append(FFm.face(axis, nrm, xyz, E, H)); lam_ff = 2.99792458e8 / f
    print(f'  far field: {sum(len(F["w"]) for F in faces)} surface points, {len(lam_ff)} wavelengths', flush=True)
    # sign convention: compare the projection of the top face alone with Lumerical's farfield3d of the same face
    fi = int(np.argmin(abs(lam_ff - 1.55e-6)))
    fdtd.eval(f'ffE2 = farfield3d("ffz2", {fi + 1}); ffux = farfieldux("ffz2", {fi + 1}); ffuy = farfielduy("ffz2", {fi + 1});')
    E2 = np.real(np.asarray(fdtd.getv('ffE2'))); ux = np.real(np.asarray(fdtd.getv('ffux'))).ravel(); uy = np.real(np.asarray(fdtd.getv('ffuy'))).ravel()
    E2 = E2.reshape(len(ux), len(uy)); UX, UY = np.meshgrid(ux, uy, indexing='ij'); ok = UX ** 2 + UY ** 2 < 0.95
    sub = np.flatnonzero(ok.ravel())[::max(1, ok.sum() // 1500)]
    dirs = np.stack([UX.ravel()[sub], UY.ravel()[sub], np.sqrt(1 - UX.ravel()[sub] ** 2 - UY.ravel()[sub] ** 2)], 1)
    corr = {}
    for sg in (1, -1):
        _, U1, _, _ = FFm.project([faces[5]], lam_ff[fi:fi + 1], P['n'], sign=sg, dirs=dirs)
        corr[sg] = float(np.corrcoef(U1[0], E2.ravel()[sub])[0, 1])
    sign = 1 if corr[1] >= corr[-1] else -1
    print(f'  sign check vs farfield3d: corr(+1) = {corr[1]:.4f}, corr(-1) = {corr[-1]:.4f} -> sign {sign:+d}', flush=True)
    d, U, Pb, ratio = FFm.project(faces, lam_ff, P['n'], ndir=4000, sign=sign)
    th13, th09 = np.arcsin(1.3 / P['n']), np.arcsin(0.9 / P['n'])
    ex = {'ff_py60': FFm.cone_fraction(d, U, [0, 1, 0], np.pi / 3), 'ff_my60': FFm.cone_fraction(d, U, [0, -1, 0], np.pi / 3),
          'ff_zNA13': FFm.cone_fraction(d, U, [0, 0, 1], th13), 'ff_zNA09': FFm.cone_fraction(d, U, [0, 0, 1], th09), 'ff_check': ratio}
    ex = {k: np.interp(cols['lambda_nm'], lam_ff[::-1] * 1e9, v[::-1]) if lam_ff[0] > lam_ff[-1] else np.interp(cols['lambda_nm'], lam_ff * 1e9, v)
          for k, v in ex.items()}
    # in-plane (xy) and xz patterns at three wavelengths
    phi = np.radians(np.arange(0, 360, 2.0)); pat = {'angle_deg': np.degrees(phi)}
    for l0 in (1450, 1550, 1650):
        j = int(np.argmin(abs(lam_ff * 1e9 - l0)))
        for pl, dv in (('xy', np.stack([np.cos(phi), np.sin(phi), 0 * phi], 1)), ('xz', np.stack([np.cos(phi), 0 * phi, np.sin(phi)], 1))):
            _, Up, _, _ = FFm.project(faces, lam_ff[j:j + 1], P['n'], sign=sign, dirs=dv); pat[f'U_{pl}_{l0}'] = Up[0] / Up[0].max()
    with open(a.out[:-4] + '_pattern.csv', 'w') as fo:
        fo.write(f'# far-field patterns (normalised), {a.name}, sign {sign:+d}\n' + ','.join(pat) + '\n')
        for i in range(len(phi)): fo.write(','.join(f'{pat[k][i]:.5g}' for k in pat) + '\n')
    print(f'  far field done in {(time.time()-t1)/60:.1f} min; P_ff/P_box = {ex["ff_check"].min():.3f} ... {ex["ff_check"].max():.3f}', flush=True)
    return ex, sign, corr


ff_note = ''
if FF_ON:
    try:
        ex, sign, corr = far_field(); cols.update(ex); ff_note = f' farfield sign {sign:+d} corr {corr[sign]:.4f}'
        if np.any(abs(ex['ff_check'] - 1) > 0.1): print('  WARNING: far-field power differs from the box power by more than 10%', flush=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f'  far field FAILED: {e}', flush=True)
        if P['ff_strict']: print('LABKIT_ERROR far field failed (strict mode)', flush=True); sys.exit(4)
order = np.argsort(cols['lambda_nm'])
with open(a.out, 'w') as f:
    f.write(f'# Lumerical FDTD {a.name}: {json.dumps(P)}{ff_note}\n' + ','.join(cols) + '\n')
    for i in order: f.write(','.join(f'{cols[k][i]:.6g}' for k in cols) + '\n')
fdtd.close()
print('LABKIT_DONE', flush=True)
