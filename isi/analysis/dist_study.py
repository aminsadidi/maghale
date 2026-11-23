"""Supervisor's distance study (2026-11-22): emitter-antenna distance for three structures, Green-function quantities only.
  single rod  S_L275_E_H4            emitter on the axis facing the tip, h = 4 ... 40 nm (columns *_h<h>)
  dimer       L275_G<g>_H4           emitter at the gap centre (column *_c), h = g/2, g = 10 ... 80 nm
  trimer      L275_R295_A0_Y160_G<g>_H4 (g = 40: L275_R295_A0_Y160_H4, the final design)
x dipole (along the rod axis), host n = 1.5, gold JC, mesh 4 nm, BEM (MNPBEM17, retarded), lambda 1100:20:1900 nm.
Derived quantities (model_green_final): Gamma(w)/Gamma0(w) = Fp = 1 + ImG;  J(w) = Gamma0(w) Fp(w) / 2pi;
  kappa = FWHM (energy) of the Fp peak;  regime ratio R_sc = 4 Gamma_peak / kappa (>1: strong coupling, single-Lorentzian picture);
  memory time tau_mem = 2 hbar / kappa;  Lamb shift hbar*delta = -(hbar Gamma0 / 2) ReG;  eta = T / Fp.
hbar Gamma0 at 1550 nm from tau0 = 1.5 ns, scaled as (1550 / lambda)^3.
usage: python isi/analysis/dist_study.py -> isi/results/dist_study.json, isi/figures/fig_g2..g4_*.png"""
import os, re, glob, json
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.size': 10.5, 'savefig.bbox': 'tight', 'savefig.dpi': 170, 'axes.grid': True, 'grid.alpha': 0.3})
HC = 1239.842; HBAR_UEV_NS = 0.6582119569   # hbar in ueV*ns
TAU0 = 1.5; HG0 = HBAR_UEV_NS / TAU0        # hbar*Gamma0 at 1550 nm (ueV)
HS = [4, 6, 8, 10, 12, 15, 20, 25, 30, 40]; GAPS = [10, 20, 30, 40, 60, 80]
COL = dict(single='#1f4e9c', dimer='#b8892a', trimer='#9a3412')


def load(f):
    return np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1, deletechars=''))


def series(stem):
    fs = [f for f in glob.glob(os.path.join(EX, f'tri2_{stem}_c*.csv')) if re.fullmatch(rf'tri2_{re.escape(stem)}_c\d+(_k\d)?\.csv', os.path.basename(f))]
    if not fs: return None
    d = np.concatenate([load(f) for f in fs]); d = d[np.argsort(d['lambda_nm'])]
    _, i = np.unique(d['lambda_nm'], return_index=True); return d[i]


def g0(lam):
    return HG0 * (1550.0 / lam) ** 3


def fwhm_E(lam, y):
    """FWHM in energy (meV) of the main peak of y(lambda), linear interpolation on the half-maximum crossings; nan if not closed"""
    E = HC / lam[::-1]; yy = y[::-1]; i = int(np.argmax(yy)); h = yy[i] / 2
    l = i
    while l > 0 and yy[l] > h: l -= 1
    r = i
    while r < len(yy) - 1 and yy[r] > h: r += 1
    okl, okr = yy[l] <= h, yy[r] <= h
    El = E[l] + (h - yy[l]) * (E[l + 1] - E[l]) / (yy[l + 1] - yy[l]) if okl else None
    Er = E[r - 1] + (h - yy[r - 1]) * (E[r] - E[r - 1]) / (yy[r] - yy[r - 1]) if okr else None
    if okl and okr: return 1e3 * (Er - El), True
    Ep = E[i]
    if okl: return 2e3 * (Ep - El), False        # one-sided: 2 x HWHM of the closed (low-energy) side
    if okr: return 2e3 * (Er - Ep), False        # one-sided: 2 x HWHM of the closed (high-energy) side
    return np.nan, False


def peak(lam, y):
    i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]; s = 0.5 * (a - c) / (a - 2 * b + c); return lam[i] + s * (lam[1] - lam[0]), b - 0.25 * (a - c) * s
    return lam[i], y[i]


def at(lam, y, l0=1550.0):
    return float(np.interp(l0, lam, y))


def quantities(lam, d, s):
    Fp, T = d[f'Fp_x_{s}'], d[f'T_x_{s}']
    lp, Fpk = peak(lam, Fp); kap, closed = fwhm_E(lam, Fp)
    Gpk = Fpk * g0(lp) * 1e-3                          # meV
    q = dict(lam_peak=float(lp), Fp_peak=float(Fpk), kappa_meV=float(kap), kappa_closed=closed, Q=float(HC / lp * 1e3 / kap) if np.isfinite(kap) else None,
             hGamma_peak_ueV=float(Gpk * 1e3), R_sc=float(4 * Gpk / kap) if np.isfinite(kap) else None, tau_mem_fs=float(2 * 658.2119569 / kap) if np.isfinite(kap) else None,
             Fp1550=at(lam, Fp), T1550=at(lam, T), eta1550=at(lam, T / Fp), ImG1550=at(lam, d[f'ImG_x_{s}']), ReG1550=at(lam, d[f'ReG_x_{s}']),
             hGamma1550_ueV=float(at(lam, Fp) * HG0), hdelta1550_ueV=float(-HG0 / 2 * at(lam, d[f'ReG_x_{s}'])),
             na09_1550=at(lam, d[f'f_zNA0.9_x_{s}']), na13_1550=at(lam, d[f'f_zNA1.3_x_{s}']), dir1550=at(lam, d[f'f_py60_x_{s}'] / d[f'f_my60_x_{s}']),
             eta_peak=float(np.interp(lp, lam, T / Fp)))
    q['lifetime1550_ps'] = float(1e3 * TAU0 / q['Fp1550']); q['bright1550'] = q['eta1550'] * q['na09_1550']
    return q


def main():
    out = dict(single={}, dimer={}, trimer={}, notes={})
    sp = {}
    d = series('S_L275_E_H4'); lam = d['lambda_nm']
    for h in HS: out['single'][h] = quantities(lam, d, f'h{h}'); sp[('single', h)] = (lam, d[f'Fp_x_h{h}'], d[f'T_x_h{h}'] / d[f'Fp_x_h{h}'])
    for kind, fmt in (('dimer', 'L275_G{g}_H4'), ('trimer', 'L275_R295_A0_Y160_G{g}_H4')):
        for g in GAPS:
            stem = fmt.format(g=g) if not (kind == 'trimer' and g == 40) else 'L275_R295_A0_Y160_H4'
            d = series(stem)
            if d is None: continue
            lam = d['lambda_nm']; out[kind][g // 2] = quantities(lam, d, 'c'); out[kind][g // 2]['n_lambda'] = int(len(lam)); out[kind][g // 2]['gap'] = g
            sp[(kind, g // 2)] = (lam, d['Fp_x_c'], d['T_x_c'] / d['Fp_x_c'])
    json.dump(out, open(os.path.join(RES, 'dist_study.json'), 'w'), indent=1)

    # Fig g2: Fp spectra
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    cm = plt.get_cmap('viridis')
    for a, kind in zip(ax, ('single', 'dimer', 'trimer')):
        keys = sorted(k for (kk, k) in sp if kk == kind)
        for j, h in enumerate(keys):
            lam, Fp, _ = sp[(kind, h)]
            lab = f'h = {h} nm' if kind == 'single' else f'g = {2*h} nm (h = {h})'
            a.semilogy(lam, Fp, '-o', ms=2.5, lw=1.5, c=cm(j / max(1, len(keys) - 1)), label=lab)
        a.axvline(1550, c='0.4', ls=':', lw=1); a.set_xlabel('wavelength (nm)')
        a.set_title({'single': '(a) single rod, emitter facing the tip', 'dimer': '(b) tip-to-tip dimer, gap centre', 'trimer': '(c) trimer (dimer + R3), gap centre'}[kind], fontsize=11)
        a.legend(fontsize=7.5, ncol=2)
    ax[0].set_ylabel('Purcell factor Fp = Gamma / Gamma0  (x dipole)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_g2_spectra.png')); plt.close(fig)

    # Fig g3: versus distance
    fig, ax = plt.subplots(2, 3, figsize=(15, 8.4)); ax = ax.ravel()
    def line(a, key, f=lambda v: v, logy=False, only_closed=False):
        for kind in ('single', 'dimer', 'trimer'):
            hs = sorted(out[kind]); ys = []
            for h in hs:
                q = out[kind][h]; v = q[key]
                ys.append(np.nan if v is None or (False) else f(v))
            (a.semilogy if logy else a.plot)(hs, ys, '-o', c=COL[kind], lw=2, ms=5, label={'single': 'single rod (h = tip distance)', 'dimer': 'dimer (h = g/2)', 'trimer': 'trimer (h = g/2)'}[kind])
        a.set_xlabel('emitter - tip distance h (nm)')
    line(ax[0], 'Fp1550', logy=True); ax[0].set_ylabel('Fp at 1550 nm'); ax[0].set_title('(a) Purcell factor at 1550 nm'); ax[0].legend(fontsize=9)
    line(ax[1], 'Fp_peak', logy=True); ax[1].set_ylabel('Fp at its spectral peak'); ax[1].set_title('(b) peak Purcell factor')
    line(ax[2], 'lam_peak'); ax[2].axhline(1550, c='0.4', ls=':'); ax[2].set_ylabel('peak wavelength (nm)'); ax[2].set_title('(c) wavelength of the Fp peak')
    line(ax[3], 'eta1550', f=lambda v: 100 * v); ax[3].set_ylabel('antenna efficiency T/Fp at 1550 nm (%)'); ax[3].set_title('(d) radiative efficiency (rest: absorbed in gold)')
    line(ax[4], 'R_sc', logy=True, only_closed=True); ax[4].axhline(1, c='r', ls='--', lw=1.2); ax[4].text(ax[4].get_xlim()[1] * 0.98, 1.15, 'strong coupling above this line', ha='right', color='r', fontsize=9)
    ax[4].set_ylabel('4 Gamma_peak / kappa'); ax[4].set_title('(e) coupling regime (tau0 = 1.5 ns)')
    line(ax[5], 'bright1550', f=lambda v: 100 * v); ax[5].set_ylabel('eta x fraction into NA 0.9 (%)'); ax[5].set_title('(f) photons collected per emission at 1550 nm')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_g3_vs_distance.png')); plt.close(fig)

    # Fig g4: efficiency spectra (radiative efficiency vs wavelength) for the three structures at matched distances
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    for a, h in zip(ax, (5, 10, 20)):
        for kind in ('single', 'dimer', 'trimer'):
            if (kind, h) in sp:
                lam, _, eta = sp[(kind, h)]; a.plot(lam, 100 * eta, '-o', ms=2.5, c=COL[kind], lw=1.8, label=kind)
        a.axvline(1550, c='0.4', ls=':'); a.set_title('(' + 'abc'[(5, 10, 20).index(h)] + f') h = {h} nm' + ('  (single rod: h = 4 nm)' if h == 5 else ''), fontsize=10.5)
        a.set_xlabel('wavelength (nm)')
        if h == 5 and ('single', 4) in sp:
            lam, _, eta = sp[('single', 4)]; a.plot(lam, 100 * eta, '-o', ms=2.5, c=COL['single'], lw=1.8, label='single (h = 4)')
        a.legend(fontsize=8.5)
    ax[0].set_ylabel('antenna efficiency T / Fp (%)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_g4_efficiency.png')); plt.close(fig)

    for kind in ('single', 'dimer', 'trimer'):
        print(f'--- {kind}')
        print(' h   lam_pk  Fp_pk   kappa  Q    R_sc   Fp1550  eta1550 NA09  dir   hG1550(ueV) hd1550  tau_mem(fs)')
        for h in sorted(out[kind]):
            q = out[kind][h]
            print(f"{h:3d} {q['lam_peak']:7.0f} {q['Fp_peak']:7.0f} {q['kappa_meV']:6.0f} {q['Q'] or float('nan'):4.1f} {q['R_sc'] or float('nan'):6.3f} {q['Fp1550']:7.0f} {q['eta1550']:6.2f} {q['na09_1550']:5.2f} {q['dir1550']:5.2f} {q['hGamma1550_ueV']:8.1f} {q['hdelta1550_ueV']:8.1f} {q['tau_mem_fs'] or float('nan'):6.1f}")


if __name__ == '__main__':
    main()
