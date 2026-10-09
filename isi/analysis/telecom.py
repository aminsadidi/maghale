"""Gold nanorods (D = 20 nm) in glass/polymer (n = 1.45) tuned from the visible to the telecom O and C bands (BEM,
job_telecom.m). For each rod: radiative peak, Fp, T, antenna efficiency, anisotropy; resonance-matched rods for
emitters at 810, 1310 and 1550 nm (linear interpolation in the rod length between computed rods); closed-form model
check; quantum figures of merit (coupling g, indistinguishability) for representative telecom emitters.
usage: python isi/analysis/telecom.py -> isi/results/telecom.md, isi/figures/fig_telecom.pdf
"""
import os, re, glob, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
sys.path.insert(0, HERE)
from spheroid_qs import gold_jc
from scaling_law import closed_form
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'lines.linewidth': 1.4,
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
                     'legend.frameon': False, 'savefig.bbox': 'tight', 'figure.dpi': 150})
C = ['#1f4e9c', '#c0392b', '#2a9d5c', '#8a5a00', '#7b3fa0', '#5f6b73']
NB = 1.45; GAPS = (5, 10, 20)
hbar = 6.582e-16


def load(f):
    return np.genfromtxt(f, delimiter=',', names=True, skip_header=1)


def rods():
    out = []
    for f in sorted(glob.glob(os.path.join(RES, 'bem_extra', 'telecom_L*.csv')), key=lambda f: int(re.search(r'_L(\d+)', f).group(1))):
        L = int(re.search(r'_L(\d+)', f).group(1)); d = load(f)
        r = dict(L=L, d=d, spr=d['lambda_nm'][np.argmax(d['ext_nm2'])])
        for g in GAPS:
            Tz, Fz, Fx = d[f'T_z_g{g}'], d[f'Fp_z_g{g}'], d[f'Fp_x_g{g}']
            i = np.argmax(Tz)
            r[g] = dict(lamT=d['lambda_nm'][i], T=Tz[i], Fp=Fz[i], eta=Tz[i] / Fz[i], R=Fz[i] / Fx[i], Rmax=(Fz / Fx).max(),
                        Ez2=d[f'Ez2_g{g}'][i], i=i)
        out.append(r)
    return out


EMITTERS = [  # name, wavelength, q0, radiative lifetime (s), pure dephasing at 4 K (eV)
    ('GaAs/InGaAs QD', 810, 0.9, 1e-9, 1e-6),
    ('InAs/GaAs QD (O band)', 1310, 0.9, 1.5e-9, 2e-6),
    ('G centre in Si', 1278, 0.1, 6e-9, 5e-6),
    ('InAs/InP QD (C band)', 1550, 0.9, 1.5e-9, 2e-6),
    ('PbS/CdS colloidal QD', 1550, 0.3, 1e-6, None),
    ('Er$^{3+}$ in glass', 1535, 0.8, 1e-2, None),
]


def interp_at(R, lam_e, g, key):
    lt = np.array([r[g]['lamT'] for r in R]); v = np.array([r[g][key] for r in R]); o = np.argsort(lt)
    if lam_e < lt.min() or lam_e > lt.max(): return np.nan
    return float(np.exp(np.interp(lam_e, lt[o], np.log(v[o])))) if key != 'lamT' else lam_e


def main():
    R = rods()
    if not R: print('no telecom data'); return
    out = ['# Telecom-band gold nanorods (D = 20 nm, n = 1.45), axial dipole on the axis', '',
           '| L (nm) | AR | SPR (ext) | gap | lambda_T | T | Fp | eta_a | Fp_z/Fp_x at lambda_T | max | Ez2 at lambda_T | closed form Fp / T |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in R:
        for g in GAPS:
            x = r[g]
            e = gold_jc(np.array([x['lamT'] / 1.0]))[0] / NB ** 2      # relative permittivity eps_m/eps_b
            Fm, Tm = closed_form(20, r['L'], 'rod', g, x['lamT'] / NB, e)
            out.append(f"| {r['L']} | {r['L']/20:.1f} | {r['spr']:.0f} | {g} | {x['lamT']:.0f} | {x['T']:.0f} | {x['Fp']:.0f} | "
                       f"{100*x['eta']:.1f}% | {x['R']:.0f} | {x['Rmax']:.0f} | {x['Ez2']:.0f} | {Fm:.0f} / {Tm:.0f} |")
    # resonance-matched designs
    out += ['', '## Resonance-matched rods for telecom emitters (interpolated between computed rods)', '',
            '| emitter | lambda_e | q0 | gap | T | Fp | eta(q0) | speed-up | hbar g (meV) | g/(kappa/4) | I (4 K) |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for name, le, q0, trad, gs in EMITTERS:
        for g in (5, 10, 20):
            T = interp_at(R, le, g, 'T'); F = interp_at(R, le, g, 'Fp')
            if np.isnan(T): continue
            eta = T / (F + (1 - q0) / q0); sp = q0 * F + 1 - q0
            hG0 = hbar / trad
            # linewidth from the radiative-peak width of the nearest rod (FWHM of T_z) in energy
            r = min(R, key=lambda r: abs(r[g]['lamT'] - le)); d = r['d']; Tz = d[f'T_z_g{g}']; lam = d['lambda_nm']
            half = lam[Tz >= Tz.max() / 2]; kap = 1239.84 / half.min() - 1239.84 / half.max()
            hg = 0.5 * np.sqrt(F * hG0 * kap)
            I = f'{100 * sp * hG0 / q0 / (sp * hG0 / q0 + 2 * gs):.0f}%' if gs else '--'
            out.append(f'| {name} | {le} | {q0} | {g} | {T:.0f} | {F:.0f} | {100*eta:.1f}% | {sp:.3g} | {1e3*hg:.3g} | {hg/(kap/4):.2g} | {I} |')
    open(os.path.join(RES, 'telecom.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

    # figure: (a) T spectra of all rods at 10 nm, (b) eta_a and Fp_z/Fp_x at the radiative peak vs lambda_T
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    cm = plt.get_cmap('viridis')
    for k, r in enumerate(R):
        d = r['d']; ax[0].semilogy(d['lambda_nm'], d['T_z_g10'], c=cm(k / max(1, len(R) - 1)), lw=1.1, label=f"L={r['L']}")
    for le in (810, 1310, 1550): ax[0].axvline(le, c='0.6', lw=0.8, ls=':')
    ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel(r'$T$ (axial, 10 nm gap)'); ax[0].legend(fontsize=5.5, ncol=2)
    ax[0].set_title('(a)', loc='left', fontsize=9)
    a2 = ax[1]; b2 = a2.twinx()
    for g, mk in zip(GAPS, 'os^'):
        lt = [r[g]['lamT'] for r in R]
        a2.plot(lt, [100 * r[g]['eta'] for r in R], mk + '-', c=C[0], ms=3.5, lw=1, label=f'{g} nm')
        b2.semilogy(lt, [r[g]['R'] for r in R], mk + '--', c=C[1], ms=3.5, lw=1)
    for le in (810, 1310, 1550): a2.axvline(le, c='0.6', lw=0.8, ls=':')
    a2.set_xlabel(r'radiative peak $\lambda_T$ (nm)'); a2.set_ylabel(r'antenna efficiency $\eta_a$ (%)', color=C[0])
    b2.set_ylabel(r'$F_p^{\parallel}/F_p^{\perp}$ at $\lambda_T$', color=C[1]); a2.legend(fontsize=6, loc='upper left')
    a2.set_title('(b)', loc='left', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_telecom.pdf')); fig.savefig(os.path.join(FIG, 'fig_telecom.png'), dpi=130)


if __name__ == '__main__':
    main()
