"""Run one task (case, band, tag) -> task_out/<case>__<band>_<tag>.npz"""
import os, sys, time
sys.path.insert(0, 'isi/sim'); sys.path.insert(0, os.path.dirname(__file__))
from cases import STAGES
from nanorod import run_task
case, band, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
params = dict({n: p for st in STAGES.values() for n, p in st}[case])
if os.environ.get('CI_QUICK'): params['res'] = 0.2   # local smoke test only
os.makedirs('task_out', exist_ok=True)
t = time.time()
run_task(params, band, tag, f'task_out/{case}__{band}_{tag}.npz')
print(f'{case} band {band} {tag}: {(time.time()-t)/60:.1f} min')
