"""Retarded mode decomposition by pole fitting.
Fp_z(w) - 1 = Im[C / (w_t - w)] + a0 + a1 w + a2 w^2   (w in eV, C and w_t complex)
The pole term is the contribution of the longitudinal dipolar mode (quasinormal-mode form), the polynomial the
smooth non-resonant background. Validated on the quasistatic BEM spectra, for which the exact dipolar-mode
contribution is known from the eigenmode expansion (isi/results/bem_extra/modes_*.csv).
usage: python isi/analysis/pole_fit.py   (run from repo root) -> isi/results/pole_fit.md"""
import re, glob, numpy as np
from scipy.optimize import least_squares
HC = 1239.84

def load(p):
    L = open(p).read().splitlines(); i = 0
    while L[i].startswith('#'): i += 1
    h = L[i].split(','); d = np.loadtxt(p, delimiter=',', skiprows=i + 1, ndmin=2)
    return {k: d[:, j] for j, k in enumerate(h)}

def fit(lam, F, lo, hi):
    m = (lam >= lo) & (lam <= hi); w = HC / lam[m]; y = F[m] - 1
    k = np.argmax(y); w0 = w[k]
    def model(p, w):
        C = p[0] + 1j * p[1]; wt = p[2] - 1j * abs(p[3])
        return np.imag(C / (wt - w)) + p[4] + p[5] * (w - w0) + p[6] * (w - w0)**2
    p0 = [y[k] * 0.08, 0, w0, 0.08, 0, 0, 0]
    r = least_squares(lambda p: (model(p, w) - y) / np.maximum(y, 1), p0, max_nfev=20000)
    C = r.x[0] + 1j * r.x[1]; wt = r.x[2] - 1j * abs(r.x[3])
    pole = lambda lam_: np.imag(C / (wt - HC / np.asarray(lam_)))
    rms = np.sqrt(np.mean(((model(r.x, w) - y) / np.maximum(y, 1))**2))
    return pole, HC / r.x[2], 2 * abs(r.x[3]), rms

out = ['# Retarded mode decomposition by pole fitting', '',
       '## Validation on the quasistatic spectra (exact dipolar-mode term known)', '',
       '| particle | gap | lambda_L | exact mode share | fitted mode share | fit rms |', '|---|---|---|---|---|---|']
WIN = {'rodL40': (520, 900), 'rodL60': (540, 900), 'rodL80': (580, 950), 'rodL100': (620, 950)}
for s, (lo, hi) in WIN.items():
    d = load(f'isi/results/bem_extra/modes_{s}.csv')
    for g in (3, 5, 10, 20):
        m = d['gap'] == g; lam = d['lambda_nm'][m]; F = d['Fp_z'][m]; dL = d['dFz_L'][m]
        pole, lr, gam, rms = fit(lam, F, lo, hi)
        i = np.argmax(dL)
        out.append(f'| {s} | {g} | {lam[i]:.0f} | {100*dL[i]/(F[i]-1):.1f}% | {100*pole(lam[i])/(F[i]-1):.1f}% | {100*rms:.1f}% |')
out += ['', '## Retarded BEM spectra', '',
        'mode share = pole term / (Fp_z - 1) at the pole wavelength; background ratio = (Fp_z - pole term) / Fp_x;'
        ' total ratio = Fp_z / Fp_x; all at the pole wavelength.', '',
        '| rod | gap | pole lambda (nm) | width (meV) | Fp_z | mode share | background ratio | total ratio | fit rms |',
        '|---|---|---|---|---|---|---|---|---|']
RET = {'rod_L60_h1.5_air': (540, 900), 'rod_L40_h2_air': (520, 900), 'rod_L50_h2_air': (530, 900),
       'rod_L80_h2_air': (580, 1100), 'rod_L100_h2_air': (620, 1100)}
for s, (lo, hi) in RET.items():
    d = load(f'isi/results/bem_raw/{s}.csv'); lam = d['lambda_nm']
    gaps = sorted({int(k.split('_g')[1]) for k in d if k.startswith('Fp_z_g')})
    for g in gaps:
        F, Fx = d[f'Fp_z_g{g}'], d[f'Fp_x_g{g}']
        pole, lr, gam, rms = fit(lam, F, lo, hi)
        i = np.argmin(abs(lam - lr))
        bg = F[i] - pole(lam[i])
        out.append(f'| {s} | {g} | {lr:.0f} | {1000*gam:.0f} | {F[i]:.0f} | {100*pole(lam[i])/(F[i]-1):.1f}% | {bg/Fx[i]:.2f} | {F[i]/Fx[i]:.0f} | {100*rms:.1f}% |')
open('isi/results/pole_fit.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
