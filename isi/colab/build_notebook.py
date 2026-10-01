"""Generate a self-contained Colab notebook from the simulation sources in isi/sim.
Run: python isi/colab/build_notebook.py   -> isi/colab/meep_nanorod.ipynb

Design (robust on any Colab Python version):
  * Meep is installed with micromamba into its own environment (/content/mm/envs/meep);
    the Colab kernel is never replaced or restarted.
  * Every simulation runs as a subprocess: <env>/bin/mpirun -np N <env>/bin/python runner.py ...
  * Analysis cells in the kernel need only numpy/scipy/matplotlib (pre-installed on Colab).
  * The notebook also runs outside Colab (env NB_BASE=<dir>, NB_QUICK=1) for automated testing."""
import json, os
SIM = os.path.join(os.path.dirname(__file__), '..', 'sim')
src = lambda f: open(os.path.join(SIM, f), encoding='utf-8').read()
cells = []
md = lambda t: cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': t})
code = lambda t: cells.append({'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': t})

md("""# شبیه‌سازی سنگین نانومیله‌ی طلا (Meep، مختصات استوانه‌ای — فیزیک کاملاً سه‌بعدی)

**فقط سلول‌ها را به ترتیب از بالا به پایین اجرا کنید** (یا منوی Runtime → Run all). نیازی به ری‌استارت نیست.

- سلول ۱ Meep را در یک محیط جدا نصب می‌کند (حدود ۳ تا ۶ دقیقه، فقط یک‌بار در هر نشست).
- سلول ۲ از شما اجازه‌ی Google Drive می‌خواهد؛ نتایج در `MyDrive/maghale_meep` ذخیره می‌شوند. اگر کولب قطع شد، دوباره Run all بزنید: اجراهای تمام‌شده تکرار نمی‌شوند.
- سلول آخر فایل `results.zip` را می‌سازد و دانلود می‌کند؛ آن را برای Claude بفرستید.
- اگر خطایی دیدید، **متن کامل خطا** (آخرین ۲۰ خط خروجی همان سلول) را برای Claude بفرستید.
""")
code(r'''# 1) Install Meep into a separate micromamba environment (kernel is NOT restarted)
import os, subprocess, sys, time
BASE = os.environ.get('NB_BASE', '/content')
MM = f'{BASE}/mm'; ENV = f'{MM}/envs/meep'; PY = f'{ENV}/bin/python'; MPIRUN = f'{ENV}/bin/mpirun'
# clean environment for the Meep subprocesses: Jupyter/Colab variables (MPLBACKEND, PYTHONPATH, ...) break the separate env
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'MPL', 'JPY', 'CONDA', 'MAMBA'))}
CLEAN_ENV['MPLBACKEND'] = 'Agg'
def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=CLEAN_ENV)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:]); raise RuntimeError('command failed: ' + cmd)
    return r.stdout
if not os.path.exists(PY):
    t = time.time()
    sh(f'mkdir -p {BASE}/mmbin && curl -sSL https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C {BASE}/mmbin bin/micromamba')
    sh(f'MAMBA_ROOT_PREFIX={MM} {BASE}/mmbin/bin/micromamba create -y -q -n meep -c conda-forge '
       f'python=3.11 "pymeep=*=mpi_mpich_*" numpy scipy h5py')
    print(f'installed in {(time.time()-t)/60:.1f} min')
print(sh(f'{PY} -c "import meep; print(\'Meep\', meep.__version__)"').strip())''')
code(r'''# 2) Results folder: Google Drive on Colab (survives disconnects), local folder otherwise
try:
    from google.colab import drive
    drive.mount('/content/drive')
    OUT = '/content/drive/MyDrive/maghale_meep'
except ImportError:
    OUT = f'{BASE}/results'
SIMDIR = f'{BASE}/sim'
os.makedirs(OUT, exist_ok=True); os.makedirs(SIMDIR, exist_ok=True)
QUICK = os.environ.get('NB_QUICK') == '1'      # automated test mode: tiny grids only
print('results ->', OUT, '| quick test' if QUICK else '')''')
for f in ['gold_jc_params.json', 'gold_jc.py', 'mie.py', 'nanorod.py']:
    body = src(f).replace('\\', '\\\\').replace("'''", "\\'\\'\\'")
    code(f"# write {f}\nopen(f'{{SIMDIR}}/{f}', 'w').write('''{body}''')\nprint('wrote {f}')")
code(r'''# 3) Job runner: each job runs on all CPU cores via MPI and writes one CSV into OUT
import json, multiprocessing
NP = multiprocessing.cpu_count(); print('CPU cores:', NP)
open(f'{SIMDIR}/runner.py', 'w').write(
    "import sys, json\n"
    f"sys.path.insert(0, {SIMDIR!r})\n"
    "import meep as mp\n"
    "from nanorod import simulate, save_csv\n"
    "a = json.loads(sys.argv[1]); out = a.pop('out')\n"
    "o = simulate(**a)\n"
    "if mp.am_master(): save_csv(out, o, json.dumps(a))\n")
def job(name, **kw):
    path = f'{OUT}/{name}.csv'
    if os.path.exists(path):
        print(f'[skip] {name} (already done)'); return
    kw['out'] = path
    t = time.time(); print(f'[run ] {name}  {kw}', flush=True)
    r = subprocess.run([MPIRUN, '-np', str(NP), PY, f'{SIMDIR}/runner.py', json.dumps(kw)],
                       capture_output=True, text=True, cwd=SIMDIR, env=CLEAN_ENV)
    if r.returncode != 0 or not os.path.exists(path):
        print(r.stdout[-2000:]); print(r.stderr[-3000:]); raise RuntimeError('job failed: ' + name)
    print(f'[done] {name} in {(time.time()-t)/60:.1f} min', flush=True)
# kernel-side helpers (numpy/scipy only)
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
print('runner ready')''')
md("""## مرحله‌ی A — کالیبراسیون: کره‌ی طلا در برابر حل دقیق می
اگر خطای میانه زیر حدود ۳٪ باشد، روش برای نانومیله قابل اعتماد است.""")
code(r'''RES_A = [0.25] if QUICK else [1.0, 2.0]
for res in RES_A:
    job(f'bench_sphere_res{res}', shape='sphere', orient='z', gap=5.0, res=res)
for res in RES_A:
    d = load(f'bench_sphere_res{res}')
    Fm, Tm = radial_dipole(d['lam'], 15.874, 5.0, eps_fit)
    e = 100 * (d['Fp'] / Fm - 1)
    print(f"grid {1/res:.2f} nm: median |err Fp| {np.median(abs(e)):.1f}%  max {abs(e).max():.1f}%   "
          f"peak Meep {d['Fp'].max():.0f} @ {d['lam'][d['Fp'].argmax()]:.0f} nm vs Mie {Fm.max():.0f} @ {d['lam'][Fm.argmax()]:.0f} nm")''')
md("""## مرحله‌ی B — همگرایی مش برای حالت اصلی (میله، دوقطبی طولی، گاف ۵ nm) و حالت‌های عرضی
شبکه‌ی ۱، ۰٫۶۷ و ۰٫۵ نانومتر. این همان آزمونی است که عدم‌قطعیت ±۴۰٪ مقاله را جایگزین می‌کند.""")
code(r'''RES_B = [0.25] if QUICK else [1.0, 1.5, 2.0]
for res in RES_B:
    job(f'rodA_z_gap5_res{res}', shape='rod', orient='z', gap=5.0, res=res, na_list=[0.5, 0.9, 1.3])
for res in ([0.25] if QUICK else [1.0, 2.0]):
    job(f'rodC_x_gap5_res{res}', shape='rod', orient='x', gap=5.0, res=res)
    job(f'sphereDp_x_gap5_res{res}', shape='sphere', orient='x', gap=5.0, res=res)''')
code(r'''import matplotlib; import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
for res in RES_B:
    if not os.path.exists(f'{OUT}/rodA_z_gap5_res{res}.csv'): continue
    d = load(f'rodA_z_gap5_res{res}')
    for a, k, s in zip(ax, ['Fp', 'T', 'eta'], [1, 1, 100]): a.plot(d['lam'], s * d[k], label=f'grid {1/res:.2f} nm')
    i, k = d['Fp'].argmax(), d['T'].argmax()
    print(f"grid {1/res:.2f} nm: Fp {d['Fp'][i]:.0f} @ {d['lam'][i]:.0f} nm | T {d['T'][k]:.1f} @ {d['lam'][k]:.0f} nm | eta@T {100*d['eta'][k]:.1f}%")
for a, t in zip(ax, ['Fp', 'T', 'eta (%)']): a.set_title(t); a.set_xlabel('nm'); a.legend()
plt.show()''')
md("""## مرحله‌ی C — نقشه‌های طراحی (سهم علمی تازه‌ی مقاله)
گاف × نسبت ابعاد، در هوا و آب. این مرحله طولانی است؛ هر زمان قطع شد، دوباره Run all بزنید تا از همان‌جا ادامه دهد.""")
code(r'''RES = 0.25 if QUICK else 1.0
GAPS = [5] if QUICK else [3, 5, 7, 10, 15, 20]
LENGTHS = [60] if QUICK else [40, 50, 60, 80, 100]       # D = 20 nm -> aspect ratio 2 ... 5
ENVS = [(1.0, 'air')] if QUICK else [(1.0, 'air'), (1.33, 'water')]
for n_host, tag in ENVS:
    for L in LENGTHS:
        for g in GAPS:
            job(f'map_{tag}_L{L}_gap{g}_res{RES}', shape='rod', orient='z', gap=float(g), L=float(L), D=20.0,
                res=RES, n_host=n_host, na_list=[0.9, 1.2])''')
code(r'''# 4) Package all results
import shutil
zp = shutil.make_archive(f'{BASE}/results', 'zip', OUT)
print('zip:', zp, os.path.getsize(zp) // 1024, 'KB')
try:
    from google.colab import files
    files.download(zp)
except ImportError:
    pass''')
nb = {'cells': cells, 'metadata': {'colab': {'provenance': []}, 'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
                                   'language_info': {'name': 'python'}}, 'nbformat': 4, 'nbformat_minor': 0}
out = os.path.join(os.path.dirname(__file__), 'meep_nanorod.ipynb')
json.dump(nb, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', out, len(cells), 'cells')
