"""g2(0), indistinguishability, brightness and directionality of the single-photon source versus the trimer geometry:
spacing between the third rod R3 and the dimer (R3 parallel), and R3 angle at a fixed smallest spacing (campaign 3).

Antenna (Lumerical FDTD, emitter = x dipole at the gap centre, host n = 1.5, Johnson-Christy gold), all at 1550 nm:
  Fp (total rate / rate in the host), T (radiated power / host), eta = T / Fp, directionality ff_py60 / ff_my60.
Emitter (two-level, resonant 200 fs pi pulse, QuTiP master equation, pulsed_tls.run): intrinsic lifetime tau0 = 2 ns,
intrinsic quantum yield 1 (InAs/InP QD at 4 K), Gamma = Fp / tau0, pure dephasing gamma* = 1 and 10 ueV.
The geometry enters the quantum figures of merit only through Fp (rate) and, for the photon numbers, eta and ff_py60.
Data: isi/data/lab_20261111/lumerical (campaign 2) and every isi/data/lab_*/lumerical/fdtd_c3_*.csv (campaign 3).
usage: python isi/analysis/geom_quantum.py -> isi/figures/fig_geom_quantum.png, isi/results/geom_quantum.md/.json"""
import glob, json, os, re, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '..', 'labkit'))
from pulsed_tls import run as tls  # noqa: E402
from lab.tasks import r3_spacing  # noqa: E402
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HB = 6.582119569e-16; TAU0 = 2e-9; TP = 200e-15; DEPH = (1e-6, 10e-6)


def load(path):
    head = open(path).readline(); P = json.loads(re.search(r'\{.*?\}', head).group(0))
    d = np.genfromtxt(path, delimiter=',', names=True, skip_header=1); d = d[np.argsort(d['lambda_nm'])]
    at = lambda k: float(np.interp(1550, d['lambda_nm'], d[k]))
    r = dict(name=os.path.basename(path)[5:-4], L=P['L'], L3=P['L3'], Y3=P['Y3'], A3=float(P.get('A3', 0) or 0),
             Fp=at('Fp'), T=at('T'), eta=at('T') / at('Fp'), ratio=at('ff_py60') / at('ff_my60'), fpy=at('ff_py60'))
    r['s'] = round(r3_spacing(r['Y3'], r['A3'], L=r['L'], L3=r['L3']), 1)
    return r


def quantum(r):
    G = r['Fp'] / TAU0
    for ge in DEPH:
        N, g2, I = tls(TP * G, ge / HB / G)
        r[f'g2_{ge*1e6:.0f}'], r[f'I_{ge*1e6:.0f}'] = g2, I
    r['tau_ps'] = 1e12 / G; r['ph_ff'] = r['eta']; r['ph_py'] = r['eta'] * r['fpy']
    return r


def main():
    files = [f for f in glob.glob(os.path.join(ROOT, 'data', 'lab_20261111', 'lumerical', 'fdtd_*.csv'))
             if re.search(r'fdtd_(sw_L275_R295|sel_Y1[57]0)\.csv$', f)]
    files += sorted(glob.glob(os.path.join(ROOT, 'data', 'lab_*', 'lumerical', 'fdtd_c3_*.csv')))
    R = [quantum(load(f)) for f in files if not f.endswith('_pattern.csv')]
    par = sorted([r for r in R if r['A3'] == 0], key=lambda r: r['s'])
    rot = sorted([r for r in R if r['A3'] != 0], key=lambda r: (r['s'], r['A3']))
    # ---- table
    out = ['# Single-photon figures of merit vs trimer geometry (L = 275, R3 = 295 nm, 1550 nm)', '',
           f'Emitter: two-level, tau0 = {TAU0*1e9:g} ns, q0 = 1, resonant {TP*1e15:.0f} fs pi pulse; antenna from Lumerical FDTD (x dipole, gap centre, n = 1.5).', '',
           '| R3 angle | spacing (nm) | Y3 (nm) | Fp | T | eta | +y/-y | lifetime (ps) | g2(0) | I (1 ueV) | I (10 ueV) | photons/pulse far field | into +y cone |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in par + rot:
        out.append(f"| {r['A3']:g} | {r['s']:g} | {r['Y3']:g} | {r['Fp']:.0f} | {r['T']:.0f} | {r['eta']:.0%} | {r['ratio']:.2f} | {r['tau_ps']:.1f} | "
                   f"{r['g2_1']:.3f} | {r['I_1']:.3f} | {r['I_10']:.3f} | {r['ph_ff']:.2f} | {r['ph_py']:.2f} |")
    if not any(r['name'].startswith('c3_') for r in R):
        out += ['', 'Campaign 3 (spacing 20-80 nm, rotation) not yet run: only the campaign-2 points (spacing 90, 100, 110 nm) are shown.']
    open(os.path.join(ROOT, 'results', 'geom_quantum.md'), 'w').write('\n'.join(out) + '\n')
    json.dump(R, open(os.path.join(ROOT, 'results', 'geom_quantum.json'), 'w'), indent=1)
    print('\n'.join(out))
    # ---- figure
    fig, ax = plt.subplots(2, 2, figsize=(13, 8.6)); ax = ax.ravel()
    s = [r['s'] for r in par]
    ax[0].plot(s, [r['ratio'] for r in par], 'o-', c='#1f4e9c', lw=2, ms=7)
    ax[0].set_xlabel('فاصله‌ی لبه‌به‌لبه‌ی میله‌ی سوم تا دیمر (nm)'); ax[0].set_ylabel('نسبت +y/−y در ۱۵۵۰ nm', color='#1f4e9c')
    a2 = ax[0].twinx(); a2.plot(s, [r['Fp'] for r in par], 's--', c='#9a3412', lw=1.6, ms=6); a2.set_ylabel('ضریب پورسل Fp', color='#9a3412'); a2.grid(False)
    ax[0].set_title('(الف) جهت‌دهی و پورسل بر حسب فاصله (میله‌ی سوم موازی)', fontsize=12)
    ax[1].plot(s, [r['I_1'] for r in par], 'o-', c='#2a7a4b', lw=2, ms=7, label='تمیزناپذیری، $\\gamma^*$ = 1 µeV')
    ax[1].plot(s, [r['I_10'] for r in par], 'o--', c='#2a7a4b', lw=1.6, ms=6, label='تمیزناپذیری، $\\gamma^*$ = 10 µeV')
    ax[1].plot(s, [r['g2_1'] for r in par], 'D-', c='#b8892a', lw=2, ms=6, label='g2(0)')
    ax[1].set_ylim(0, 1.02); ax[1].set_xlabel('فاصله‌ی لبه‌به‌لبه‌ی میله‌ی سوم تا دیمر (nm)'); ax[1].legend(fontsize=10, loc='center right')
    ax[1].set_title('(ب) g2(0) و تمیزناپذیری بر حسب فاصله', fontsize=12)
    for sp, mk in ((20, 'o'), (30, 's')):
        rr = [r for r in R if abs(r['s'] - sp) < 1.5 and (r['A3'] != 0 or r['name'].startswith('c3_'))]
        rr = sorted(rr, key=lambda r: r['A3'])
        if not rr: continue
        A = [r['A3'] for r in rr]
        ax[2].plot(A, [r['ratio'] for r in rr], mk + '-', lw=2, ms=7, label=f'فاصله {sp} nm')
        ax[3].plot(A, [r['I_1'] for r in rr], mk + '-', c='#2a7a4b', lw=2, ms=7, label=f'I ($\\gamma^*$ = 1 µeV)، فاصله {sp} nm')
        ax[3].plot(A, [r['g2_1'] for r in rr], mk + '--', c='#b8892a', lw=1.6, ms=6, label=f'g2(0)، فاصله {sp} nm')
    for k, t in ((2, '(ج) جهت‌دهی بر حسب زاویه‌ی میله‌ی سوم'), (3, '(د) g2(0) و تمیزناپذیری بر حسب زاویه')):
        ax[k].set_xlabel('زاویه‌ی میله‌ی سوم نسبت به دیمر (درجه)'); ax[k].set_title(t, fontsize=12)
        if ax[k].lines: ax[k].legend(fontsize=9.5)
        else: ax[k].text(0.5, 0.5, 'در انتظار نتایج اجرای ۳\n(کامپیوتر استاد)', ha='center', va='center', transform=ax[k].transAxes, fontsize=13, color='0.45')
    ax[2].set_ylabel('نسبت +y/−y'); ax[3].set_ylim(0, 1.02)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_geom_quantum.png')); print('figure written')


if __name__ == '__main__':
    main()
