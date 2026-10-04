"""Combine downloaded task files (any sub-folders of argv[1]) into one CSV per complete case in isi/results/ci."""
import glob, json, os, sys
sys.path.insert(0, 'isi/sim'); sys.path.insert(0, os.path.dirname(__file__))
from cases import STAGES
from nanorod import combine_tasks, save_csv
files = {os.path.basename(f)[:-4]: f for f in glob.glob(os.path.join(sys.argv[1], '**', '*.npz'), recursive=True)}
os.makedirs('isi/results/ci', exist_ok=True)
for st in STAGES.values():
    for name, p in st:
        if os.environ.get('CI_QUICK'): p = dict(p, res=0.2)
        keys = [f'{name}__{b}_{t}' for b in range(3) for t in ('struct', 'free')]
        if all(k in files for k in keys) and not os.path.exists(f'isi/results/ci/{name}.csv'):
            paths = {(b, t): files[f'{name}__{b}_{t}'] for b in range(3) for t in ('struct', 'free')}
            save_csv(f'isi/results/ci/{name}.csv', combine_tasks(p, paths), json.dumps(p))
            print('combined', name)
        elif not os.path.exists(f'isi/results/ci/{name}.csv'):
            print('incomplete', name, sum(k in files for k in keys), '/ 6')
