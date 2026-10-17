"""Lab kit runner: plans the simulations that fit this machine, runs them one after another (each simulation already
uses all cores), resumes after an interruption, predicts the remaining time and writes a status page.
Standard library only.

usage (from the labkit folder):
  python -m lab.runner plan   [--tiers 1,2,3,4] [--max-days D]     show what would run and the predicted time
  python -m lab.runner run    [--tiers ...] [--max-days D] [--only mnpbem|lumerical]
  python -m lab.runner status                                        print the current status
  python -m lab.runner pack                                          zip the results for transfer
"""
import argparse, json, math, os, re, shutil, socket, subprocess, sys, threading, time, zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import detect, tasks as T  # noqa: E402

KIT = detect.KIT
REPO = os.path.dirname(KIT)
OUT = detect.OUT
LOGS = os.path.join(OUT, 'logs')
EXTRA = os.path.join(REPO, 'isi', 'bem', 'extra')
MNPBEM = os.environ.get('LABKIT_MNPBEM') or os.path.join(KIT, 'vendor', 'MNPBEM')
CAL = os.path.join(OUT, 'calibration.json')
STATUS_EVERY = int(os.environ.get('LABKIT_STATUS_EVERY', 30))   # s; the monitor thread only reads small log files

DEFAULT_CAL = {'mnpbem': {'a': 2.2, 'p': 2.6, 'samples': []},          # s per step per unit (Xeon E5-1650 guess)
               'lumerical': {'a': 2.0e-4, 'samples': []}}              # s per unit (rough guess, refined after 1 run)


def now():
    return time.time()


def fmt_dt(s):
    if s is None or not math.isfinite(s): return '?'
    s = max(0, int(s)); d, s = divmod(s, 86400); h, s = divmod(s, 3600); m = s // 60
    return (f'{d} d ' if d else '') + (f'{h} h ' if h or d else '') + f'{m} min'


def load_cal():
    try: c = json.load(open(CAL))
    except Exception: c = json.loads(json.dumps(DEFAULT_CAL))
    for k, v in DEFAULT_CAL.items(): c.setdefault(k, json.loads(json.dumps(v)))
    return c


def save_cal(c):
    json.dump(c, open(CAL, 'w'), indent=1)


def refit(c):
    m = c['mnpbem']; S = m['samples']
    if S:
        Ns = {round(s[0], 3) for s in S}
        if len(Ns) >= 2 and len(S) >= 4:                     # fit t = a * u^p  with u = nblocks*(N/1000)^2.6 rescaled
            xs = [math.log(s[0]) for s in S]; ys = [math.log(s[1]) for s in S]
            n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
            sxx = sum((x - mx) ** 2 for x in xs)
            if sxx > 1e-6:
                k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx      # exponent relative to units^1
                k = min(max(k, 0.6), 1.4); m['p'] = 2.6 * k
                m['a'] = math.exp(my - k * mx)
                m['k'] = k
                return
        m['k'] = 1.0
        m['a'] = sorted(s[1] / s[0] for s in S)[len(S) // 2]
    l = c['lumerical']
    if l['samples']: l['a'] = sorted(s[1] / s[0] for s in l['samples'])[len(l['samples']) // 2]


def step_seconds(task, cal):
    if task['backend'] == 'mnpbem':
        m = cal['mnpbem']; return m['a'] * task['units_per_step'] ** m.get('k', 1.0)
    return cal['lumerical']['a'] * task['units_per_step']


def out_path(task):
    return os.path.join(OUT, task['backend'], task['output'])


def is_done(task):
    p = out_path(task)
    try: return os.path.getsize(p) > 0 and sum(1 for _ in open(p)) >= 3
    except OSError: return False


def plan(S, tiers, only=None, max_days=None, cal=None, quiet=False):
    cal = cal or load_cal()
    have = {'mnpbem': bool(S.get('matlab') and S['matlab'].get('ok', True) and os.path.isdir(MNPBEM)),
            'lumerical': bool(S.get('lumerical') and S['lumerical'].get('ok', True))}
    ram = float(os.environ.get('LABKIT_RAM_GB') or S.get('ram_gb') or 0)
    P = []
    for t in T.catalogue():
        if t['tier'] not in tiers or (only and t['backend'] != only): continue
        t = dict(t)
        if not have[t['backend']]:
            t['state'] = 'skip: ' + ('MATLAB/MNPBEM not available' if t['backend'] == 'mnpbem' else 'Lumerical not available')
        elif t['mem_gb'] > 0.9 * ram:
            t['state'] = f"skip: needs ~{t['mem_gb']:.0f} GB RAM (this machine {ram:.0f} GB)"
        elif is_done(t):
            t['state'] = 'done'
        else:
            t['state'] = 'todo'
        t['eta_s'] = step_seconds(t, cal) * t['nsteps']
        P.append(t)
    if max_days:                                        # drop the most expensive pending tasks of the highest tiers
        budget = max_days * 86400
        todo = [t for t in P if t['state'] == 'todo']
        tot = sum(t['eta_s'] for t in todo)
        for t in sorted(todo, key=lambda t: (-t['tier'], -t['eta_s'])):
            if tot <= budget: break
            t['state'] = f"skip: over the --max-days {max_days:g} budget"; tot -= t['eta_s']
    return P


def plan_text(P, S):
    L = ['', detect.summary(S), '', f"{'state':<14} {'tier':<4} {'RAM':>6} {'predicted':>12}  task"]
    for t in P:
        st = t['state'] if not t['state'].startswith('skip') else 'skip'
        L.append(f"{st:<14} {t['tier']:<4} {t['mem_gb']:>5.0f}G {fmt_dt(t['eta_s']) if t['state'] == 'todo' else '':>12}  {t['id']}  - {t['desc']}"
                 + (f"   [{t['state'][6:]}]" if t['state'].startswith('skip') else ''))
    todo = [t for t in P if t['state'] == 'todo']
    L += ['', f"to run: {len(todo)} tasks, predicted {fmt_dt(sum(t['eta_s'] for t in todo))} (rough until the first steps have been timed)"]
    return '\n'.join(L)


class Monitor(threading.Thread):
    """reads the log of the running task every STATUS_EVERY s, updates the step timing, writes status.json/html"""

    def __init__(self, runner):
        super().__init__(daemon=True); self.r = runner; self.stop = False; self.advised = False

    def run(self):
        while not self.stop:
            try: self.r.update_status()
            except Exception as e: print('[monitor]', e)
            for _ in range(STATUS_EVERY):
                if self.stop: break
                time.sleep(1)


class Runner:
    def __init__(self, S, P, args):
        self.S, self.P, self.args = S, P, args
        self.cal = load_cal(); self.current = None; self.t_start = now(); self.lock = threading.Lock()
        self.cur_steps = []; self.cur_t0 = None; self.log_pos = 0; self.advice = None

    # ---------- execution ----------
    def command(self, t):
        od = os.path.join(OUT, t['backend']); os.makedirs(od, exist_ok=True)
        if t['backend'] == 'mnpbem':
            q = lambda p: p.replace('\\', '/')
            mcmd = (f"addpath(genpath('{q(MNPBEM)}')); addpath('{q(EXTRA)}'); tic; job_{t['job']}('{t['spec']}', '{q(od)}'); "
                    f"fprintf('LABKIT_DONE %.1f min\\n', toc/60)")
            return [self.S['matlab']['exe'], '-batch', mcmd], od
        lum = self.S['lumerical']
        py = lum.get('python') or sys.executable
        return [py, os.path.join(KIT, 'lab', 'lumerical_fdtd.py'), '--lumapi', lum['lumapi_dir'], '--name', t['name'],
                '--params', json.dumps(t['params']), '--out', os.path.join(od, t['output']), '--work', os.path.join(OUT, 'fdtd_work')], od

    def run_task(self, t):
        cmd, od = self.command(t)
        log = os.path.join(LOGS, t['id'].replace(':', '_') + '.log')
        with self.lock:
            self.current, self.cur_steps, self.cur_t0, self.log_pos, self.cur_log = t, [], now(), 0, log
        t['state'] = 'running'; t['t0'] = now(); self.update_status()
        print(f"\n=== [{time.strftime('%H:%M')}] {t['id']}  ({t['desc']})", flush=True)
        with open(log, 'w', encoding='utf-8', errors='replace') as f:
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=od)
            code = p.wait()
        with self.lock:
            self.read_progress()                             # last steps
        dt = now() - t['t0']
        ok = code == 0 and is_done(t)
        with self.lock:
            if ok and not self.cur_steps:                    # no per-step lines: use the whole run as one sample
                self.record(t, dt / t['nsteps'])
            self.current = None
        t['state'] = 'done' if ok else f'failed (exit {code}, see logs/{os.path.basename(log)})'
        t['elapsed'] = dt
        print(f"    -> {t['state']} after {fmt_dt(dt)}", flush=True)
        self.update_status()
        return ok

    def record(self, t, sec_per_step):
        key = t['backend']
        self.cal[key]['samples'].append([t['units_per_step'], sec_per_step])
        self.cal[key]['samples'] = self.cal[key]['samples'][-60:]
        refit(self.cal); save_cal(self.cal)

    def read_progress(self):
        """parse new lines of the running task's log: MNPBEM prints one line per wavelength, Lumerical '% complete'"""
        t = self.current
        if not t: return
        try:
            with open(self.cur_log, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(self.log_pos); new = f.read(); self.log_pos = f.tell()
        except OSError:
            return
        if t['backend'] == 'mnpbem':
            k = len(re.findall(r'lambda\s+\d+(?:\.\d+)?(?:\s+done|:)', new))
            if k:
                tnow = now(); first = not self.cur_steps
                last = self.cur_steps[-1] if self.cur_steps else t['t0'] + 45     # ~45 s MATLAB start-up before step 1
                each = max((tnow - last) / k, 1e-3)                              # several lines in one read: share the time
                self.cur_steps += [tnow] * k
                if tnow - t['t0'] > 60 or not first:
                    for _ in range(k): self.record(t, each)
        else:
            m = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*complete', new)
            if m: t['progress'] = float(m[-1]) / 100.0

    # ---------- status / ETA ----------
    def remaining(self):
        rem = 0.0; cur = None
        for t in self.P:
            if t['state'] == 'todo': rem += step_seconds(t, self.cal) * t['nsteps']
            elif t['state'] == 'running':
                st = step_seconds(t, self.cal); el = now() - t['t0']
                if t['backend'] == 'mnpbem':
                    done = len(self.cur_steps); cur = max(st * (t['nsteps'] - done) - (now() - (self.cur_steps[-1] if self.cur_steps else t['t0'])), 0)
                else:
                    pr = t.get('progress')
                    cur = el * (1 - pr) / pr if pr and pr > 0.02 else max(st - el, 0)
                rem += cur
        return rem, cur

    def update_status(self):
        with self.lock:
            self.read_progress()
            rem, cur = self.remaining()
        done = [t for t in self.P if t['state'] == 'done']; todo = [t for t in self.P if t['state'] in ('todo', 'running')]
        fin = time.strftime('%Y-%m-%d %H:%M', time.localtime(now() + rem)) if todo else '-'
        measured = len(self.cal['mnpbem']['samples']) + len(self.cal['lumerical']['samples'])
        st = {'updated': time.strftime('%Y-%m-%d %H:%M:%S'), 'host': socket.gethostname(), 'running_for': fmt_dt(now() - self.t_start),
              'done': len(done), 'remaining_tasks': len(todo), 'remaining_time': fmt_dt(rem), 'expected_finish': fin,
              'eta_quality': 'measured' if measured else 'initial guess', 'current': self.current['id'] if self.current else None,
              'current_remaining': fmt_dt(cur) if cur is not None else None,
              'tasks': [{k: t.get(k) for k in ('id', 'tier', 'state', 'desc', 'mem_gb')} | {'elapsed': fmt_dt(t.get('elapsed')) if t.get('elapsed') else ''}
                        for t in self.P]}
        if measured >= 2 and not self.advice: self.advice = self.make_advice(rem)
        st['advice'] = self.advice
        json.dump(st, open(os.path.join(OUT, 'status.json'), 'w'), indent=1)
        write_html(st)
        if self.advice and not getattr(self, 'advice_printed', False):
            self.advice_printed = True
            print('\n' + '#' * 70 + '\n' + self.advice + '\n' + '#' * 70 + '\n', flush=True)
            open(os.path.join(OUT, 'ADVICE.txt'), 'w', encoding='utf-8').write(self.advice + '\n')

    def make_advice(self, rem):
        per_tier = {}
        for t in self.P:
            if t['state'] in ('todo', 'running'): per_tier[t['tier']] = per_tier.get(t['tier'], 0) + step_seconds(t, self.cal) * t['nsteps']
        L = ['ADVICE (from the first measured steps):',
             f'  predicted remaining time for everything planned: {fmt_dt(rem)}']
        for k in sorted(per_tier): L.append(f'    tier {k} ({T.TIER_NAMES.get(k, "")}): {fmt_dt(per_tier[k])}')
        days = rem / 86400
        if days <= 3: L.append('  -> fine: let it run, nothing to change.')
        elif days <= 10: L.append('  -> long but feasible. To shorten: stop (Ctrl+C) and restart with  RUN.bat --tiers 1,2  (finished tasks are kept).')
        else: L.append('  -> too long for this machine: restart with  RUN.bat --tiers 1,2 --max-days 5  and run the rest on a stronger system.')
        skipped = [t for t in self.P if t['state'].startswith('skip: needs')]
        if skipped: L.append(f'  {len(skipped)} task(s) were skipped for lack of RAM; they need a machine with >= '
                             f"{max(t['mem_gb'] for t in skipped) / 0.9:.0f} GB.")
        return '\n'.join(L)

    def go(self):
        os.makedirs(LOGS, exist_ok=True)
        prevent_sleep(True)
        mon = Monitor(self); mon.start()
        try:
            order = sorted([t for t in self.P if t['state'] == 'todo'], key=lambda t: (not t.get('smoke'), t['tier']))
            for t in order:
                if t['state'] != 'todo': continue
                ok = self.run_task(t)
                if t.get('smoke') and not ok:                 # broken installation: do not waste hours on this backend
                    for u in self.P:
                        if u['backend'] == t['backend'] and u['state'] == 'todo':
                            u['state'] = f"skip: smoke test failed (see logs/{t['id'].replace(':', '_')}.log)"
                    print(f"!!! {t['backend']} smoke test failed - its other tasks are skipped. Send me the log file.", flush=True)
        except KeyboardInterrupt:
            print('\nstopped by the user; finished tasks are kept, run RUN.bat again to continue.')
            if self.current: self.current['state'] = 'todo'
        finally:
            mon.stop = True; self.update_status(); prevent_sleep(False)
        z = pack()
        print(f'\nresults packed into {z}')


def prevent_sleep(on):
    if os.name != 'nt': return
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if on else 0))
    except Exception:
        pass


def write_html(st):
    rows = ''.join(f"<tr class='{'ok' if t['state'] == 'done' else 'run' if t['state'] == 'running' else 'skip' if t['state'].startswith('skip') else 'bad' if t['state'].startswith('failed') else ''}'>"
                   f"<td>{t['id']}</td><td>{t['tier']}</td><td>{t['state']}</td><td>{t['elapsed']}</td><td>{t['desc']}</td></tr>" for t in st['tasks'])
    adv = f"<pre>{st['advice']}</pre>" if st.get('advice') else ''
    html = f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="30"><title>Lab kit status</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:20px;background:#f6f5f1;color:#1d2330}} table{{border-collapse:collapse;width:100%;font-size:13px}}
td,th{{border-bottom:1px solid #ddd;padding:4px 6px;text-align:left}} tr.ok td{{color:#2a7a4b}} tr.run td{{font-weight:bold;color:#1f4e9c}}
tr.skip td{{color:#999}} tr.bad td{{color:#b03030}} .box{{background:#fff;border:1px solid #ddd;border-radius:8px;padding:12px 16px;margin-bottom:14px}}
pre{{background:#fff8e6;border:1px solid #e6d29a;padding:10px;border-radius:6px}}</style></head><body>
<div class="box"><b>{st['host']}</b> &mdash; updated {st['updated']} (page refreshes every 30 s)<br>
running for {st['running_for']} &nbsp;|&nbsp; done {st['done']} &nbsp;|&nbsp; remaining {st['remaining_tasks']} tasks, <b>{st['remaining_time']}</b>
&nbsp;|&nbsp; expected finish <b>{st['expected_finish']}</b> ({st['eta_quality']})<br>current: {st['current'] or '-'} {('(' + st['current_remaining'] + ' left)') if st.get('current_remaining') else ''}</div>
{adv}<table><tr><th>task</th><th>tier</th><th>state</th><th>time</th><th>description</th></tr>{rows}</table></body></html>"""
    open(os.path.join(OUT, 'status.html'), 'w', encoding='utf-8').write(html)


def pack():
    name = os.path.join(KIT, f"results_{socket.gethostname()}_{time.strftime('%Y%m%d_%H%M')}.zip")
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            if 'fdtd_work' in root: continue                 # large project files stay local
            for f in files: z.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), KIT))
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['plan', 'run', 'status', 'pack'])
    ap.add_argument('--tiers', default='1,2,3,4'); ap.add_argument('--max-days', type=float); ap.add_argument('--only', choices=['mnpbem', 'lumerical'])
    ap.add_argument('--redetect', action='store_true', help='repeat the software detection (licence tests)')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == 'status':
        try: st = json.load(open(os.path.join(OUT, 'status.json')))
        except Exception: print('no status yet'); return
        print(json.dumps({k: v for k, v in st.items() if k != 'tasks'}, indent=1)); return
    if a.cmd == 'pack':
        print(pack()); return
    sp = os.path.join(OUT, 'system.json')
    if a.redetect or not os.path.exists(sp):
        print('detecting software (licence tests can take a few minutes) ...', flush=True); S = detect.detect()
    else:
        S = json.load(open(sp))
    tiers = [int(x) for x in a.tiers.split(',') if x.strip()]
    P = plan(S, tiers, a.only, a.max_days)
    print(plan_text(P, S), flush=True)
    if a.cmd == 'run':
        if not any(t['state'] == 'todo' for t in P): print('\nnothing to run.'); pack(); return
        Runner(S, P, a).go()


if __name__ == '__main__':
    main()
