"""Run the cases of one job in parallel processes (one per core) -> task_out/<case>.npz"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cases import cases
K = dict(cases()); names = sys.argv[1].split(',')
os.makedirs('task_out', exist_ok=True)
procs = []
for n in names:
    log = open(f'task_out/{n}.log', 'w')
    procs.append((n, subprocess.Popen([sys.executable, os.path.join(HERE, '..', 'meep', 'film3d.py'), json.dumps(K[n]), f'task_out/{n}.npz'],
                                      stdout=log, stderr=subprocess.STDOUT, env=dict(os.environ, OMP_NUM_THREADS='1')), time.time()))
bad = 0
for n, p, t in procs:
    p.wait(); ok = p.returncode == 0 and os.path.exists(f'task_out/{n}.npz'); bad += not ok
    print(f'{n}: {"ok" if ok else "FAILED"} ({(time.time()-t)/60:.1f} min)'); print(open(f'task_out/{n}.log').read()[-600:])
sys.exit(1 if bad == len(procs) else 0)
