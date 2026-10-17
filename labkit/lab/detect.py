"""Detect what this machine offers: CPU, RAM, disk, MATLAB (+ licence test), Lumerical (lumapi + licence test), COMSOL.
Standard library only. Results go to labkit/output/system.json.
usage: python -m lab.detect [--quick]   (--quick skips the licence tests)"""
import glob, json, os, platform, re, shutil, subprocess, sys, time

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(KIT, 'output')
IS_WIN = os.name == 'nt'
DRIVES = [f'{d}:\\' for d in 'CDEFG'] if IS_WIN else ['/']


def ram_gb():
    if IS_WIN:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong), ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong), ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong), ('sullAvailExtendedVirtual', ctypes.c_ulonglong)]
        m = MS(); m.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys / 2 ** 30, m.ullAvailPhys / 2 ** 30
    try:
        info = dict(l.split(':', 1) for l in open('/proc/meminfo'))
        kb = lambda k: float(info[k].split()[0])
        return kb('MemTotal') / 2 ** 20, kb('MemAvailable') / 2 ** 20
    except Exception:
        return 0.0, 0.0


def cpu_name():
    if IS_WIN:
        return platform.processor() or os.environ.get('PROCESSOR_IDENTIFIER', '?')
    try:
        for l in open('/proc/cpuinfo'):
            if l.startswith('model name'): return l.split(':', 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or '?'


def physical_cores():
    if IS_WIN:
        try:
            r = subprocess.run(['powershell', '-NoProfile', '-Command', '(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum'],
                               capture_output=True, text=True, timeout=60)
            return int(r.stdout.strip())
        except Exception:
            pass
    return max(1, (os.cpu_count() or 2) // 2)


def run(cmd, timeout, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        return -9, 'timeout'
    except Exception as e:
        return -1, str(e)


def find_matlab():
    env = os.environ.get('LABKIT_MATLAB')                 # override (also used by the mock test)
    if env: return [env]
    hits = []
    w = shutil.which('matlab')
    if w: hits.append(w)
    pats = ([d + r'Program Files\MATLAB\R*\bin\matlab.exe' for d in DRIVES] + [d + r'MATLAB\R*\bin\matlab.exe' for d in DRIVES]) if IS_WIN \
        else ['/usr/local/MATLAB/R*/bin/matlab', '/opt/MATLAB/R*/bin/matlab']
    for p in pats: hits += sorted(glob.glob(p), reverse=True)        # newest release first
    seen = []
    for h in hits:
        if h not in seen: seen.append(h)
    return seen


def find_lumerical():
    """returns list of dicts {root, lumapi_dir, python}; newest first"""
    env = os.environ.get('LABKIT_LUMAPI')
    if env: return [{'root': os.path.dirname(os.path.dirname(env)), 'lumapi_dir': env, 'python': os.environ.get('LABKIT_LUMPY', sys.executable)}]
    pats = []
    for d in DRIVES:
        pats += [d + r'Program Files\Lumerical\v*\api\python\lumapi.py', d + r'Program Files\Lumerical\*\api\python\lumapi.py',
                 d + r'Program Files\ANSYS Inc\v*\Lumerical\api\python\lumapi.py', d + r'Program Files\Ansys Inc\v*\Lumerical\api\python\lumapi.py',
                 d + r'Program Files\ANSYS Inc\v*\optics\api\python\lumapi.py']
    if not IS_WIN: pats += ['/opt/lumerical/v*/api/python/lumapi.py', '/opt/ansys_inc/v*/Lumerical/api/python/lumapi.py']
    out = []
    for p in pats:
        for f in sorted(glob.glob(p), reverse=True):
            api = os.path.dirname(f); root = os.path.dirname(os.path.dirname(api))
            py = None
            for c in (os.path.join(root, 'python', 'python.exe'), os.path.join(root, 'python', 'bin', 'python.exe'),
                      os.path.join(root, 'python', 'bin', 'python3')):
                if os.path.exists(c): py = c; break
            if not any(o['lumapi_dir'] == api for o in out): out.append({'root': root, 'lumapi_dir': api, 'python': py})
    return out


def find_comsol():
    pats = [d + r'Program Files\COMSOL\COMSOL*\Multiphysics\bin\win64\comsol*.exe' for d in DRIVES] if IS_WIN else ['/usr/local/comsol*/multiphysics/bin/comsol']
    hits = []
    for p in pats: hits += sorted(glob.glob(p), reverse=True)
    return hits


def test_matlab(exe):
    t = time.time(); code, out = run([exe, '-batch', "disp(['LABKIT_OK ' version]); disp(maxNumCompThreads)"], timeout=600)
    ok = code == 0 and 'LABKIT_OK' in out
    ver = re.search(r'LABKIT_OK (\S+)', out)
    return {'ok': ok, 'version': ver.group(1) if ver else None, 'seconds': round(time.time() - t, 1), 'message': out.strip()[-400:]}


def test_lumerical(info, py_fallback):
    py = info['python'] or py_fallback
    code_s = ("import sys; sys.path.append(r'%s'); import lumapi; f = lumapi.FDTD(hide=True); "
              "print('LABKIT_OK', f.version() if hasattr(f, 'version') else ''); f.close()") % info['lumapi_dir']
    t = time.time(); code, out = run([py, '-c', code_s], timeout=900)
    return {'ok': code == 0 and 'LABKIT_OK' in out, 'python': py, 'seconds': round(time.time() - t, 1), 'message': out.strip()[-400:]}


def detect(quick=False):
    tot, avail = ram_gb()
    du = shutil.disk_usage(KIT)
    S = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'os': platform.platform(), 'python': sys.version.split()[0],
         'cpu': cpu_name(), 'logical_cpus': os.cpu_count(), 'physical_cores': physical_cores(),
         'ram_gb': round(tot, 1), 'ram_free_gb': round(avail, 1), 'disk_free_gb': round(du.free / 2 ** 30, 1),
         'matlab': None, 'lumerical': None, 'comsol': None}
    for exe in find_matlab():
        r = {'exe': exe}
        if not quick: r.update(test_matlab(exe))
        S['matlab'] = r
        if quick or r.get('ok'): break
    for info in find_lumerical():
        r = dict(info)
        if not quick: r.update(test_lumerical(info, sys.executable))
        S['lumerical'] = r
        if quick or r.get('ok'): break
    c = find_comsol()
    if c: S['comsol'] = {'exe': c[0], 'note': 'detected; the FEM cross-check is not automated (needs LiveLink) - see README'}
    os.makedirs(OUT, exist_ok=True)
    json.dump(S, open(os.path.join(OUT, 'system.json'), 'w'), indent=2)
    return S


def summary(S):
    L = [f"CPU      : {S['cpu']}  ({S['physical_cores']} cores / {S['logical_cpus']} threads)",
         f"RAM      : {S['ram_gb']} GB (free {S['ram_free_gb']} GB);  disk free {S['disk_free_gb']} GB"]
    m = S['matlab']; l = S['lumerical']; c = S['comsol']
    L.append('MATLAB   : ' + ('not found' if not m else f"{m['exe']}  ->  " + ('licence OK ' + str(m.get('version')) if m.get('ok') else
                                                                          ('not tested' if 'ok' not in m else 'NOT WORKING: ' + m.get('message', '')[-150:]))))
    L.append('Lumerical: ' + ('not found' if not l else f"{l['lumapi_dir']}  ->  " + ('licence OK' if l.get('ok') else
                                                                             ('not tested' if 'ok' not in l else 'NOT WORKING: ' + l.get('message', '')[-150:]))))
    L.append('COMSOL   : ' + ('not found' if not c else c['exe'] + '  (detected; not automated)'))
    return '\n'.join(L)


if __name__ == '__main__':
    S = detect(quick='--quick' in sys.argv)
    print(summary(S))
