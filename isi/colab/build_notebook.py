"""Generate the Colab notebook (2 code cells) -> isi/colab/meep_nanorod.ipynb
Cell 1: install Meep (separate micromamba env, no kernel restart), Drive, download sources, helpers.
Cell 2: run stages A, B, C in sequence, print results, zip + download.
Simulation sources are fetched from GitHub (public repo); locally (NB_BASE set) they are copied from isi/sim.
Test outside Colab:  NB_BASE=<dir> NB_QUICK=1 (tiny grids)."""
import json, os
BRANCH = 'claude/sleepy-rubin-e80q4k'
cells = []
md = lambda t: cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': t})
code = lambda t: cells.append({'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': t})

md("""# شبیه‌سازی نانومیله‌ی طلا با Meep — فقط دو سلول

۱. **سلول ۱** را اجرا کنید (نصب، حدود ۵ دقیقه؛ یک‌بار اجازه‌ی Google Drive می‌خواهد).
۲. **سلول ۲** را اجرا کنید و کولب را باز بگذارید. همه‌ی مراحل پشت‌سرهم اجرا می‌شوند و نتیجه‌ی هر مرحله چاپ می‌شود.

یا ساده‌تر: منوی **Runtime → Run all** (یا `Ctrl+F9`).

- نتایج در `MyDrive/maghale_meep` ذخیره می‌شوند. اگر کولب قطع شد، دوباره **Run all** بزنید؛ کارهای تمام‌شده تکرار نمی‌شوند.
- بعد از هر مرحله فایل `results.zip` به‌روز می‌شود و در پایان دانلود می‌شود؛ آن را برای Claude بفرستید.
- اگر خطا دیدید، ۲۰ خط آخر خروجی را برای Claude بفرستید.
""")
code(r'''# ===== CELL 1: setup (install Meep, Drive, sources, helpers) =====
import os, subprocess, sys, time, json, multiprocessing, urllib.request
BASE = os.environ.get('NB_BASE', '/content')
MM = f'{BASE}/mm'; ENV = f'{MM}/envs/meep'; PY = f'{ENV}/bin/python'; MPIRUN = f'{ENV}/bin/mpirun'
SIMDIR = f'{BASE}/sim'; os.makedirs(SIMDIR, exist_ok=True)
QUICK = os.environ.get('NB_QUICK') == '1'
# Jupyter/Colab variables (MPLBACKEND, PYTHONPATH, ...) must not leak into the separate Meep environment
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'MPL', 'JPY', 'CONDA', 'MAMBA'))}
CLEAN_ENV['MPLBACKEND'] = 'Agg'
def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=CLEAN_ENV)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:]); raise RuntimeError('command failed: ' + cmd)
    return r.stdout
# 1) Meep in its own environment
if not os.path.exists(PY):
    print('installing Meep (about 5 min) ...', flush=True); t = time.time()
    sh(f'mkdir -p {BASE}/mmbin && curl -sSL https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C {BASE}/mmbin bin/micromamba')
    sh(f'MAMBA_ROOT_PREFIX={MM} {BASE}/mmbin/bin/micromamba create -y -q -n meep -c conda-forge '
       f'python=3.11 "pymeep=*=mpi_mpich_*" numpy scipy h5py')
    print(f'installed in {(time.time()-t)/60:.1f} min')
print(sh(f"{PY} -c \"import meep; print('Meep', meep.__version__)\"").strip().splitlines()[-1])
# 2) results folder
try:
    from google.colab import drive
    drive.mount('/content/drive'); OUT = '/content/drive/MyDrive/maghale_meep'
except ImportError:
    OUT = f'{BASE}/results'
os.makedirs(OUT, exist_ok=True)
# 3) simulation sources
FILES = ['gold_jc_params.json', 'gold_jc.py', 'mie.py', 'nanorod.py']
LOCAL_SRC = os.environ.get('NB_SRC')
for f in FILES:
    if LOCAL_SRC:
        open(f'{SIMDIR}/{f}', 'w').write(open(f'{LOCAL_SRC}/{f}').read())
    else:
        urllib.request.urlretrieve(f'https://raw.githubusercontent.com/aminsadidi/maghale/__BRANCH__/isi/sim/{f}', f'{SIMDIR}/{f}')
open(f'{SIMDIR}/runner.py', 'w').write(
    "import sys, json\n"
    f"sys.path.insert(0, {SIMDIR!r})\n"
    "import meep as mp\n"
    "from nanorod import simulate, save_csv\n"
    "a = json.loads(sys.argv[1]); out = a.pop('out')\n"
    "o = simulate(**a)\n"
    "if mp.am_master(): save_csv(out, o, json.dumps(a))\n")
# 4) helpers
NP = multiprocessing.cpu_count()
def job(name, **kw):
    path = f'{OUT}/{name}.csv'
    if os.path.exists(path):
        print(f'  [skip] {name} (already done)'); return
    kw['out'] = path; t = time.time(); print(f'  [run ] {name} ...', flush=True)
    r = subprocess.run([MPIRUN, '-np', str(NP), PY, f'{SIMDIR}/runner.py', json.dumps(kw)],
                       capture_output=True, text=True, cwd=SIMDIR, env=CLEAN_ENV)
    if r.returncode != 0 or not os.path.exists(path):
        print(r.stdout[-2000:]); print(r.stderr[-3000:]); raise RuntimeError('job failed: ' + name)
    print(f'  [done] {name} in {(time.time()-t)/60:.1f} min', flush=True)
sys.path.insert(0, SIMDIR)
import numpy as np
from mie import radial_dipole
P = json.load(open(f'{SIMDIR}/gold_jc_params.json'))
def eps_fit(lam):
    f = 1000.0 / np.asarray(lam, float)
    return (P['einf'] - P['s0']*P['f0']**2/(f**2 + 1j*f*P['g0'])
            + P['s1']*P['f1']**2/(P['f1']**2 - f**2 - 1j*f*P['g1'])
            + P['s2']*P['f2']**2/(P['f2']**2 - f**2 - 1j*f*P['g2']))
def load(name):
    p = f'{OUT}/{name}.csv'
    L = open(p).read().splitlines(); i = next(n for n, l in enumerate(L) if l.lstrip('# ').startswith('lam'))
    d = np.loadtxt(p, delimiter=',', skiprows=i + 1, ndmin=2)
    return {k: d[:, j] for j, k in enumerate(L[i].lstrip('# ').split(','))}
import shutil
def pack():
    zp = shutil.make_archive(f'{BASE}/results', 'zip', OUT); return zp
print(f'READY: {NP} CPU cores, results -> {OUT}' + ('  [quick test mode]' if QUICK else ''))'''.replace('__BRANCH__', BRANCH))
code(r'''# ===== CELL 2: run everything (A -> B -> C), print results, zip =====
STAGES = 'AB'           # A: calibration, B: convergence. Add 'C' (design maps) only after Claude has checked A and B.
q = lambda full, quick: quick if QUICK else full
T0 = time.time()

if 'A' in STAGES:
    print('\n=== Stage A: gold sphere vs exact Mie ===')
    RES_A = q([0.5, 0.75, 1.0], [0.2, 0.25])          # grids 2, 1.33, 1 nm
    for res in RES_A:
        job(f'bench_sphere_res{res}', shape='sphere', orient='z', gap=5.0, res=res)
    for res in RES_A:
        d = load(f'bench_sphere_res{res}'); Fm, Tm = radial_dipole(d['lam'], 15.874, 5.0, eps_fit)
        e = 100 * (d['Fp'] / Fm - 1)
        et = 100 * (d['T'] / Tm - 1)
        print(f"  grid {1/res:.2f} nm: median |err Fp| {np.median(abs(e)):.1f}%  |err T| {np.median(abs(et)):.1f}%  "
              f"peak Meep {d['Fp'].max():.0f} @ {d['lam'][d['Fp'].argmax()]:.0f} nm vs Mie {Fm.max():.0f} @ {d['lam'][Fm.argmax()]:.0f} nm")
    # Richardson-type extrapolation to zero grid spacing (linear fit in grid spacing), checked against exact Mie
    G = np.array([1 / r for r in RES_A]); S = np.array([load(f'bench_sphere_res{r}')['Fp'] for r in RES_A])
    F0 = np.polyfit(G, S, 1)[1]
    d = load(f'bench_sphere_res{RES_A[-1]}'); Fm, Tm = radial_dipole(d['lam'], 15.874, 5.0, eps_fit)
    e0 = 100 * (F0 / Fm - 1)
    print(f"  extrapolated to 0 nm: median |err Fp| {np.median(abs(e0)):.1f}%  peak {F0.max():.0f} @ {d['lam'][F0.argmax()]:.0f} nm vs Mie {Fm.max():.0f}")
    if not QUICK:   # PML-thickness check on the finest grid
        job('bench_sphere_res1.0_pml0.3', shape='sphere', orient='z', gap=5.0, res=1.0, dpml=0.3)
        a, b = load('bench_sphere_res1.0'), load('bench_sphere_res1.0_pml0.3')
        print(f"  PML 0.15 vs 0.30 um at 1-nm grid: median |dFp| {100*np.median(abs(a['Fp']/b['Fp']-1)):.1f}%, |dT| {100*np.median(abs(a['T']/b['T']-1)):.1f}%")
    pack()

if 'B' in STAGES:
    print('\n=== Stage B: mesh convergence (rod, axial dipole, 5 nm) + transverse cases ===')
    RES_B = q([0.5, 0.75, 1.0], [0.2, 0.25])
    for res in RES_B:
        job(f'rodA_z_gap5_res{res}', shape='rod', orient='z', gap=5.0, res=res, na_list=[0.5, 0.9, 1.3])
    for res in q([1.0], [0.25]):
        job(f'rodC_x_gap5_res{res}', shape='rod', orient='x', gap=5.0, res=res)
        job(f'sphereDp_x_gap5_res{res}', shape='sphere', orient='x', gap=5.0, res=res)
    for res in RES_B:
        d = load(f'rodA_z_gap5_res{res}'); i, k = d['Fp'].argmax(), d['T'].argmax()
        print(f"  grid {1/res:.2f} nm: Fp {d['Fp'][i]:.0f} @ {d['lam'][i]:.0f} nm | T {d['T'][k]:.1f} @ {d['lam'][k]:.0f} nm | eta@T {100*d['eta'][k]:.1f}%")
    G = np.array([1 / r for r in RES_B]); S = np.array([load(f'rodA_z_gap5_res{r}')['Fp'] for r in RES_B])
    F0 = np.polyfit(G, S, 1)[1]; lam = load(f'rodA_z_gap5_res{RES_B[-1]}')['lam']
    print(f"  extrapolated to 0 nm: Fp peak {F0.max():.0f} @ {lam[F0.argmax()]:.0f} nm")
    pack()

if 'C' in STAGES:
    print('\n=== Stage C: design maps (gap x aspect ratio, air and water) ===')
    RES = q(1.0, 0.25)          # Claude will adjust after checking stages A and B
    for n_host, tag in q([(1.0, 'air'), (1.33, 'water')], [(1.0, 'air')]):
        for L in q([40, 50, 60, 80, 100], [60]):
            for g in q([3, 5, 7, 10, 15, 20], [5]):
                job(f'map_{tag}_L{L}_gap{g}_res{RES}', shape='rod', orient='z', gap=float(g), L=float(L), D=20.0,
                    res=RES, n_host=n_host, na_list=[0.9, 1.2])
                pack()

zp = pack()
print(f'\nALL DONE in {(time.time()-T0)/3600:.1f} h -> {zp}')
try:
    from google.colab import files; files.download(zp)
except ImportError:
    pass''')
nb = {'cells': cells, 'metadata': {'colab': {'provenance': []}, 'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
                                   'language_info': {'name': 'python'}}, 'nbformat': 4, 'nbformat_minor': 0}
out = os.path.join(os.path.dirname(__file__), 'meep_nanorod.ipynb')
json.dump(nb, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', out, len(cells), 'cells')
