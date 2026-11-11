"""Single-photon source at 1550 nm on the final gold-nanorod trimer (L = 275, R3 = 295 nm, gap 40 nm, host n = 1.5).

1. Emitter size for 1550 nm (0.800 eV):
   PbS colloidal quantum dot: empirical sizing curve of Moreels et al., ACS Nano 3, 3023 (2009):
       E(d) = 0.41 + 1 / (0.0252 d^2 + 0.283 d)  [eV, d in nm]   (first-exciton absorption; emission is Stokes-shifted)
   InAs/InP quantum dot: flat disk of height h and diameter Dl; electron and heavy hole in finite wells along z
   (BenDaniel-Duke matching), lateral ground state of a hard disk; band parameters of Vurgaftman et al., J. Appl. Phys. 89, 5815 (2001);
   strain is bracketed by two InAs gaps (unstrained 0.417 eV, compressively strained ~0.53 eV). Indicative only (no 3D strain/piezo field).
2. Antenna: x dipole at the gap centre, Fp and T at 1550 nm from FDTD (Lumerical, 1 nm gap mesh) and BEM (h = 3 nm);
   y and z dipoles from BEM. Collection NA 1.3 / 0.9 along +z from BEM.
3. Dynamics: resonant Gaussian pi pulse on a two-level emitter (QuTiP master equation, pulsed_tls.run), total decay Gamma = Fp Gamma_0
   (for an emitter of intrinsic quantum yield q0: Gamma = Gamma_0 (q0 Fp + 1 - q0)), pure dephasing gamma*.
   Outputs: g2(0), indistinguishability I (two-photon interference visibility), photons per pulse, efficiency into the far field.
usage: python isi/analysis/single_photon.py -> isi/results/single_photon.md, isi/figures/fig_sps_*.png
"""
import os, sys, json
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
sys.path.insert(0, HERE)
import tri2
from pulsed_tls import run as tls
plt.rcParams.update({'font.family': 'Vazirmatn', 'font.size': 12, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
HB = 6.582119569e-16          # eV s
E0 = 1239.842 / 1550.0         # eV
C1, C2, C3, C4 = '#1f4e9c', '#b8892a', '#2a7a4b', '#9a3412'

# ------------------------------------------------------------------ 1. emitter size
pbs_E = lambda d: 0.41 + 1.0 / (0.0252 * d ** 2 + 0.283 * d)


def pbs_size(E):
    lo, hi = 2.0, 15.0
    for _ in range(80):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if pbs_E(m) > E else (lo, m)
    return 0.5 * (lo + hi)


HB2M = 0.0380998          # hbar^2 / (2 m0) in eV nm^2


def well_ground(h, V, mw, mb):
    """ground state of a finite well of width h (nm), depth V (eV), masses mw (inside), mb (barrier), BenDaniel-Duke"""
    f = lambda E: np.sqrt(mb * (V - E)) / mb * 1 - np.sqrt(mw * E) / mw * np.tan(np.sqrt(mw * E / HB2M) * h / 2)
    lo, hi = 1e-9, min(V, HB2M * np.pi ** 2 / (mw * h ** 2)) - 1e-9
    for _ in range(100):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if f(m) > 0 else (lo, m)
    return 0.5 * (lo + hi)


def inas_E(h, Dl=40.0, Eg=0.417):
    me, mh = 0.026, 0.333          # InAs electron, heavy hole along [001]
    meb, mhb = 0.0795, 0.53        # InP
    dEc, dEv = 0.657, 0.35          # unstrained offsets from the Vurgaftman VBO
    lat = lambda m: HB2M * 2.405 ** 2 / (m * (Dl / 2) ** 2)
    return Eg + well_ground(h, dEc, me, meb) + well_ground(h, dEv, mh, mhb) + lat(me) + lat(0.035)   # in-plane hole mass ~0.035


def inas_height(E, **kw):
    lo, hi = 0.8, 20.0
    for _ in range(80):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if inas_E(m, **kw) > E else (lo, m)
    return 0.5 * (lo + hi)


# ------------------------------------------------------------------ 2. antenna
def antenna():
    d, n = tri2.series('L275_R295_A0_Y160_H3'); l = d['lambda_nm']; e = lambda k: float(np.interp(1550, l, d[k]))
    f = np.genfromtxt(os.path.join(HERE, '..', 'data', 'lab_20261109', 'lumerical', 'fdtd_sw_L275_R295.csv'), delimiter=',', names=True, skip_header=1)
    f = f[np.argsort(f['lambda_nm'])]; ef = lambda k: float(np.interp(1550, f['lambda_nm'], f[k]))
    return {'Fp_x_fdtd': ef('Fp'), 'T_x_fdtd': ef('T'), 'Fp_x_bem': e('Fp_x_c'), 'T_x_bem': e('T_x_c'), 'Fp_y': e('Fp_y_c'), 'Fp_z': e('Fp_z_c'),
            'T_y': e('T_y_c'), 'T_z': e('T_z_c'), 'na13': e('f_zNA13_x_c'), 'na09': e('f_zNA09_x_c'),
            'ratio_ff': ef('ff_py60') / ef('ff_my60')}


def main():
    out = ['# Single-photon source at 1550 nm on the final trimer (L = 275, R3 = 295 nm)', '']
    # ---- sizes
    dP = pbs_size(E0)
    out += ['## 1. Emitter size for 1550 nm (0.800 eV)', '',
            f'- PbS colloidal QD (Moreels 2009 sizing curve, first exciton): d = {dP:.2f} nm; with a 20-40 meV Stokes shift the emission at 1550 nm '
            f'needs the absorption at 0.82-0.84 eV, i.e. d = {pbs_size(0.84):.2f}-{pbs_size(0.82):.2f} nm.',
            f'- GaAs QDs cannot reach 1550 nm: the GaAs gap is 1.42 eV (873 nm); confinement only increases the energy.']
    hs = {(Eg, Dl): inas_height(E0, Dl=Dl, Eg=Eg) for Eg in (0.417, 0.53) for Dl in (30.0, 50.0)}
    out += ['- InAs/InP QD (disk, finite wells, Vurgaftman parameters), height h for 0.800 eV: ' +
            ', '.join(f'h = {h:.1f} nm (gap {Eg} eV, diameter {Dl:.0f} nm)' for (Eg, Dl), h in hs.items()) +
            ' -> about 2-4 nm high and 30-50 nm wide, the typical InAs/InP telecom dot; indicative (no 3D strain or piezo field).', '']
    # ---- antenna
    A = antenna(); Fpx = A['Fp_x_fdtd']; etax = A['T_x_fdtd'] / Fpx
    Fiso = (Fpx + A['Fp_y'] + A['Fp_z']) / 3
    out += ['## 2. Antenna at 1550 nm', '',
            f"| dipole | Fp | T | eta |", '|---|---|---|---|',
            f"| x (FDTD) | {Fpx:.0f} | {A['T_x_fdtd']:.0f} | {etax:.0%} |",
            f"| x (BEM h = 3) | {A['Fp_x_bem']:.0f} | {A['T_x_bem']:.0f} | {A['T_x_bem']/A['Fp_x_bem']:.0%} |",
            f"| y (BEM) | {A['Fp_y']:.2f} | {A['T_y']:.2f} | |", f"| z (BEM) | {A['Fp_z']:.2f} | {A['T_z']:.2f} | |",
            f"| isotropic (mean) | {Fiso:.0f} | | |", '',
            f"Collection along +z: NA 1.3 {A['na13']:.0%}, NA 0.9 {A['na09']:.0%}; far-field +y/-y = {A['ratio_ff']:.1f}. "
            'Antenna Q ~ 3 (T FWHM 1380-1820 nm): no spectral tuning of the emitter needed.', '']
    # ---- emitters
    em = [  # name, tau0 in the n = 1.5 host (s), q0, dephasing scenarios (eV), temperature label, dipole factor
        ('InAs/InP QD, 4 K', 2e-9, 1.0, [(1e-6, 'gamma* = 1 ueV (resonant pumping)'), (10e-6, '10 ueV (spectral diffusion)'), (50e-6, '50 ueV (above-band pumping)')], 'x', 0.9),
        ('PbS colloidal QD, 300 K', 1e-6, 0.4, [(20e-3, 'gamma* = 20 meV (room temperature)')], 'iso', None)]
    rows = []
    out += ['## 3. Pulsed single-photon emission (resonant pi pulse, QuTiP)', '',
            '| emitter | antenna | 1/Gamma | pulse | dephasing | g2(0) | I | I x ZPL^2 | photons/pulse into far field | into NA 1.3 |',
            '|---|---|---|---|---|---|---|---|---|---|']
    for name, tau0, q0, deph, dip, zpl in em:
        for ant in (False, True):
            Fp = (Fpx if dip == 'x' else Fiso) if ant else 1.0
            T = (A['T_x_fdtd'] if dip == 'x' else A['T_x_fdtd'] / 3) if ant else 1.0
            G = (q0 * Fp + 1 - q0) / tau0                           # total decay (antenna + intrinsic non-radiative)
            eff = q0 * T / (q0 * Fp + 1 - q0)                       # photons into the far field per excitation
            na = A['na13'] if ant else 0.5 * (1 - np.sqrt(1 - (1.3 / 1.5) ** 2) * 1.0)  # bare in-plane dipole: rough NA 1.3 fraction
            for tp in ((0.2e-12, 2e-12) if ant else (2e-12, 20e-12)):
                for ge, gl in deph:
                    gs = ge / HB
                    x = (tp * G, gs / G)
                    if x[0] > 3 or x[1] > 2000: N, g2, I = 1.0, np.nan, 2 * 0 + (G / (G + 2 * gs))   # far outside the QuTiP grid: I -> Gamma/(Gamma+2gamma*)
                    else: N, g2, I = tls(*x)
                    rows.append(dict(em=name, ant=ant, inv=1 / G, tp=tp, deph=gl, g2=g2, I=I, eff=eff, na=na, Fp=Fp))
                    Iz = I * zpl ** 2 if zpl else np.nan
                    out.append(f"| {name} | {'yes' if ant else 'no'} | {fmt_t(1/G)} | {fmt_t(tp)} | {gl} | {g2:.3f} | {I:.3f} | "
                               + (f'{Iz:.2f}' if zpl else '-') + f' | {eff:.2f} | {eff*na:.2f} |')
                    print(rows[-1])
    out += ['', 'I = two-photon interference visibility of consecutive photons; I x ZPL^2 includes a 90% zero-phonon-line fraction (InAs QDs, no filter).',
            'PbS: g2(0) of the two-level model only (re-excitation); the real limit of colloidal dots is biexciton emission, g2 ~ QY_XX/QY_X.']
    # analytic Gamma/(Gamma + 2 gamma*) curves for the figure
    gam = np.logspace(-7, -1, 200)
    open(os.path.join(RES, 'single_photon.md'), 'w').write('\n'.join(out) + '\n')
    json.dump({'A': A, 'pbs_d': dP, 'inas_h': {f'{k[0]}_{k[1]}': v for k, v in hs.items()}, 'rows': rows}, open(os.path.join(RES, 'single_photon.json'), 'w'),
              indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    figures(A, dP, hs, gam, Fpx)
    print('\n'.join(out))


def fmt_t(t):
    return f'{t*1e15:.0f} fs' if t < 1e-12 else (f'{t*1e12:.1f} ps' if t < 1e-9 else (f'{t*1e9:.1f} ns' if t < 1e-6 else f'{t*1e6:.1f} us'))


def figures(A, dP, hs, gam, Fpx):
    # (a) PbS sizing curve, (b) InAs/InP height
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.9))
    d = np.linspace(3, 10, 200); ax[0].plot(d, 1239.842 / pbs_E(d), c=C1, lw=2.2)
    ax[0].axhline(1550, c=C2, ls='--', lw=1.2); ax[0].plot(dP, 1550, 'o', c=C2, ms=8)
    ax[0].annotate(f'd = {dP:.1f} nm', (dP, 1550), (10, -28), textcoords='offset points', color=C2, fontsize=13)
    ax[0].set_xlabel('قطر نقطه‌ی کوانتومی PbS (نانومتر)'); ax[0].set_ylabel('طول موج اکسیتون (نانومتر)'); ax[0].set_title('(الف) نقطه‌ی کوانتومی کلوییدی PbS', fontsize=12)
    h = np.linspace(1.2, 8, 120)
    for (Eg, Dl), col, ls in (((0.417, 30.0), C1, '-'), ((0.417, 50.0), C1, '--'), ((0.53, 30.0), C3, '-'), ((0.53, 50.0), C3, '--')):
        ax[1].plot(h, [1239.842 / inas_E(x, Dl=Dl, Eg=Eg) for x in h], c=col, ls=ls, lw=2,
                   label=f'Eg = {Eg} eV, D = {Dl:.0f} nm')
    ax[1].axhline(1550, c=C2, ls='--', lw=1.2); ax[1].set_xlabel('ارتفاع نقطه‌ی InAs/InP (نانومتر)'); ax[1].set_ylabel('طول موج (نانومتر)')
    ax[1].set_title('(ب) نقطه‌ی اپیتکسیال InAs/InP (تخمینی)', fontsize=12); ax[1].legend(fontsize=9.5, loc='lower right')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_sps_size.png')); plt.close(fig)
    # indistinguishability vs dephasing, with and without the antenna (InAs/InP, 4 K, tau0 = 2 ns), plus g2 vs pulse length
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.9))
    for F, col, lab in ((1, '#7a8191', 'بدون آنتن'), (Fpx, C1, f'با آنتن (Fp = {Fpx:.0f})')):
        G = F / 2e-9; ax[0].semilogx(gam * 1e6, G / (G + 2 * gam / HB), c=col, lw=2.4, label=lab)
    for ge in (1e-6, 10e-6, 50e-6): ax[0].axvline(ge * 1e6, c='0.75', lw=0.8, ls=':')
    ax[0].set_xlabel('آهنگ ناهمدوسی خالص (میکروالکترون‌ولت)'); ax[0].set_ylabel('تمیزناپذیری I'); ax[0].set_ylim(0, 1.02); ax[0].set_xlim(0.1, 1e5)
    ax[0].set_title('(الف) تمیزناپذیری: آنتن ناهمدوسی را دور می‌زند', fontsize=12); ax[0].legend(fontsize=10.5, loc='lower left')
    tp = np.array([0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]); res = np.array([tls(x, 0.0)[1] for x in tp])
    G = Fpx / 2e-9; ax[1].loglog(tp / G * 1e12, res, 'o-', c=C1, lw=2, ms=6, label=f'با آنتن (طول عمر {1e12/G:.0f} پیکوثانیه)')
    G0 = 1 / 2e-9; ax[1].loglog(tp / G0 * 1e12, res, 's--', c='#7a8191', lw=1.6, ms=5, label='بدون آنتن (طول عمر ۲ نانوثانیه)')
    ax[1].set_xlabel('طول پالس تحریک (پیکوثانیه)'); ax[1].set_ylabel('g2(0)'); ax[1].set_title('(ب) خلوص تک‌فوتون و طول پالس', fontsize=12)
    ax[1].legend(fontsize=10.5, loc='lower right')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_sps_quantum.png')); plt.close(fig)


if __name__ == '__main__':
    main()
