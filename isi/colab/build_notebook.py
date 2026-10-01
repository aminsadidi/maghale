"""Generate a self-contained Colab notebook from the simulation sources in isi/sim.
Run: python isi/colab/build_notebook.py   -> isi/colab/meep_nanorod.ipynb"""
import json, os
SIM = os.path.join(os.path.dirname(__file__), '..', 'sim')
src = lambda f: open(os.path.join(SIM, f), encoding='utf-8').read()
cells = []
md = lambda t: cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': t})
code = lambda t: cells.append({'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': t})

md("""# شبیه‌سازی سنگین نانومیله‌ی طلا (Meep، مختصات استوانه‌ای — فیزیک کاملاً سه‌بعدی)

**ترتیب اجرا:** سلول‌ها را از بالا به پایین اجرا کنید. سلول ۱ کرنل را یک‌بار ری‌استارت می‌کند (طبیعی است)؛ بعد از ری‌استارت از سلول ۲ ادامه دهید.

- نتایج مستقیم در Google Drive در پوشه‌ی `MyDrive/maghale_meep` ذخیره می‌شوند. اگر کولب قطع شد، فقط دوباره از بالا اجرا کنید: اجراهای تمام‌شده دوباره انجام نمی‌شوند.
- در پایان، سلول آخر یک فایل `results.zip` می‌سازد؛ آن را دانلود و در گفتگو برای Claude بفرستید (یا در مخزن در `isi/results/` بگذارید).
- **کولب رایگان** (۲ هسته): مراحل A و B حدود ۲ تا ۴ ساعت. مرحله‌ی C (نقشه‌ها) طولانی‌تر است و می‌توانید آن را در چند نشست اجرا کنید.
""")
code("""# 1) نصب conda در کولب (کرنل یک‌بار ری‌استارت می‌شود)
!pip install -q condacolab
import condacolab
condacolab.install()""")
code("""# 2) نصب Meep (حدود ۳ تا ۵ دقیقه)
!mamba install -q -y -c conda-forge "pymeep=*=mpi_mpich_*" h5py > /dev/null && echo "Meep installed"
import meep as mp; print('Meep', mp.__version__)""")
code("""# 3) اتصال Google Drive برای ذخیره‌ی پایدار نتایج
from google.colab import drive
drive.mount('/content/drive')
import os
OUT = '/content/drive/MyDrive/maghale_meep'; os.makedirs(OUT, exist_ok=True)
os.makedirs('/content/sim', exist_ok=True); os.chdir('/content/sim'); print('results ->', OUT)""")
for f in ['gold_jc_params.json', 'gold_jc.py', 'mie.py', 'nanorod.py']:
    code(f"%%writefile /content/sim/{f}\n" + src(f))
code(r'''# 4) ابزار اجرای موازی: هر کار با mpirun روی همه‌ی هسته‌ها اجرا و نتیجه در Drive ذخیره می‌شود
import subprocess, os, sys, time, json, multiprocessing
NP = multiprocessing.cpu_count(); print('cores:', NP)
RUNNER = """
import sys, json; sys.path.insert(0, '/content/sim')
import meep as mp
from nanorod import simulate, save_csv
a = json.loads(sys.argv[1]); out = a.pop('out')
o = simulate(**a)
if mp.am_master(): save_csv(out, o, json.dumps(a))
"""
open('/content/sim/runner.py', 'w').write(RUNNER)
def job(name, **kw):
    path = f'{OUT}/{name}.csv'
    if os.path.exists(path):
        print(f'[skip] {name} (already done)'); return
    kw['out'] = path
    t = time.time(); print(f'[run ] {name} {kw}', flush=True)
    r = subprocess.run(['mpirun', '-np', str(NP), sys.executable, '/content/sim/runner.py', json.dumps(kw)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(path):
        print(r.stdout[-1500:], r.stderr[-1500:]); raise RuntimeError(name)
    print(f'[done] {name} in {(time.time()-t)/60:.1f} min', flush=True)''')
md("""## مرحله‌ی A — کالیبراسیون: کره‌ی طلا در برابر حل دقیق می
اگر خطای میانه زیر حدود ۳٪ باشد، روش برای نانومیله قابل اعتماد است.""")
code(r'''import numpy as np
from mie import radial_dipole
from gold_jc import eps_jc
for res in [1.0, 2.0]:
    job(f'bench_sphere_res{res}', shape='sphere', orient='z', gap=5.0, res=res)
for res in [1.0, 2.0]:
    d = np.loadtxt(f'{OUT}/bench_sphere_res{res}.csv', delimiter=',')
    Fm, Tm = radial_dipole(d[:, 0], 15.874, 5.0, eps_jc)
    e = 100 * (d[:, 1] / Fm - 1)
    print(f'res {res}/nm: median |err Fp| {np.median(abs(e)):.1f}%  max {abs(e).max():.1f}%   peak Meep {d[:,1].max():.0f} vs Mie {Fm.max():.0f}')''')
md("""## مرحله‌ی B — همگرایی مش برای حالت اصلی (میله، دوقطبی طولی، گاف ۵ nm) و حالت عرضی
شبکه‌ی ۱، ۰٫۶۷ و ۰٫۵ نانومتر. این همان آزمونی است که عدم‌قطعیت ±۴۰٪ مقاله را جایگزین می‌کند.""")
code(r'''for res in [1.0, 1.5, 2.0]:
    job(f'rodA_z_gap5_res{res}', shape='rod', orient='z', gap=5.0, res=res, na_list=[0.5, 0.9, 1.3])
for res in [1.0, 2.0]:
    job(f'rodC_x_gap5_res{res}', shape='rod', orient='x', gap=5.0, res=res)
    job(f'sphereDp_x_gap5_res{res}', shape='sphere', orient='x', gap=5.0, res=res)''')
code(r'''import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
for res in [1.0, 1.5, 2.0]:
    p = f'{OUT}/rodA_z_gap5_res{res}.csv'
    if not os.path.exists(p): continue
    d = np.loadtxt(p, delimiter=','); g = 1/res
    for j, a in enumerate(ax): a.plot(d[:, 0], d[:, j+1] * (100 if j == 2 else 1), label=f'grid {g:.2f} nm')
    i = d[:, 1].argmax(); k = d[:, 2].argmax()
    print(f'grid {g:.2f} nm: Fp {d[i,1]:.0f} @ {d[i,0]:.0f} nm | T {d[k,2]:.1f} @ {d[k,0]:.0f} nm | eta@T {100*d[k,3]:.1f}%')
for a, t in zip(ax, ['Fp', 'T', 'eta (%)']): a.set_title(t); a.set_xlabel('nm'); a.legend()
plt.show()''')
md("""## مرحله‌ی C — نقشه‌های طراحی (سهم علمی تازه‌ی مقاله)
گاف × نسبت ابعاد، در هوا و آب، با شبکه‌ی ۱ نانومتر (`RES` را بعد از دیدن نتیجه‌ی مرحله‌ی B تنظیم کنید).
این مرحله طولانی است؛ هر زمان قطع شد، دوباره اجرا کنید تا از همان‌جا ادامه دهد.""")
code(r'''RES = 1.0
GAPS = [3, 5, 7, 10, 15, 20]
LENGTHS = [40, 50, 60, 80, 100]          # D = 20 nm  ->  aspect ratio 2, 2.5, 3, 4, 5
for n_host, tag in [(1.0, 'air'), (1.33, 'water')]:
    for L in LENGTHS:
        for g in GAPS:
            job(f'map_{tag}_L{L}_gap{g}_res{RES}', shape='rod', orient='z', gap=float(g), L=float(L), D=20.0,
                res=RES, n_host=n_host, na_list=[0.9, 1.2])''')
code(r'''# 5) بسته‌بندی همه‌ی نتایج برای ارسال
import shutil
shutil.make_archive('/content/results', 'zip', OUT)
from google.colab import files
files.download('/content/results.zip')''')
nb = {'cells': cells, 'metadata': {'colab': {'provenance': []}, 'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
                                   'language_info': {'name': 'python'}}, 'nbformat': 4, 'nbformat_minor': 0}
out = os.path.join(os.path.dirname(__file__), 'meep_nanorod.ipynb')
json.dump(nb, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', out, len(cells), 'cells')
