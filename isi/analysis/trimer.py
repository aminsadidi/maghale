"""Emitter in the gap of a gold-nanorod trimer for 1550 nm (supervisor's model M4; job_trimer.m, host n = 1.5).
Geometries: single rod (R1), dimer (R1 + R2, 40 nm gap), trimer (R3 at 35 deg), T shape (R3 at 90 deg).
Merges the wavelength chunks, checks Fp = 1 + Im G, and writes the table and the Green-function figure.
usage: python isi/analysis/trimer.py -> isi/results/trimer.md, isi/figures/fig_trimer.pdf"""
import os, re, glob
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results'); FIG = os.path.join(HERE, '..', 'figures')
EX = os.path.join(RES, 'bem_extra')
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})
GEO = [('single', 'single rod', '0.5'), ('dimer', 'dimer', '#1f4e9c'), ('trimer', r'trimer ($\theta_3$ = 35$^\circ$)', '#c0392b'),
       ('tri90', r'T shape ($\theta_3$ = 90$^\circ$)', '#2a9d5c')]
HC = 1239.84


def geometry(g):
    fs = sorted(glob.glob(os.path.join(EX, f'trimer_{g}_c*.csv')), key=lambda f: int(re.search(r'_c(\d+)\.csv', f).group(1)))
    if not fs: return None, 0
    d = np.concatenate([np.atleast_1d(np.genfromtxt(f, delimiter=',', names=True, skip_header=1)) for f in fs])
    return d[np.argsort(d['lambda_nm'])], len(fs)


def at(d, key, lam0):
    return np.interp(lam0, d['lambda_nm'], d[key])


def main():
    D = {}
    out = ['# Emitter in the gap of a gold-nanorod trimer (model M4), host n = 1.5', '',
           'Rods D = 60 nm; R1, R2: L = 300 nm, gap 40 nm; R3: L = 240 nm centred at (0, 160) nm. Emitter at the gap centre,',
           'dipole along x unless stated. Rates in units of the rate in the host. Lamb shift dw/Gamma0 = -Re G / 2.', '',
           '| geometry | chunks | lambda_T | T max | Fp at lambda_T | eta | T(1550) | Fp(1550) | eta(1550) | -ReG/2 (1550) | f NA1.3 (1550) | f +y / -y (1550) | max abs(Fp-1-ImG) |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for g, lab, _ in GEO:
        d, nc = geometry(g)
        if d is None: out.append(f'| {g} | 0 | (pending) |'); continue
        D[g] = d; lam = d['lambda_nm']; T = d['T_x_c']; F = d['Fp_x_c']; i = np.argmax(T)
        chk = np.max(np.abs(F - 1 - d['ImG_x_c']) / F)
        row = f"| {g} | {nc}/8 | {lam[i]:.0f} | {T[i]:.0f} | {F[i]:.0f} | {100*T[i]/F[i]:.0f}% |"
        if lam.min() <= 1550 <= lam.max():
            t, f = at(d, 'T_x_c', 1550), at(d, 'Fp_x_c', 1550)
            row += (f" {t:.0f} | {f:.0f} | {100*t/f:.0f}% | {-at(d, 'ReG_x_c', 1550)/2:.0f} | {at(d, 'f_zNA13_x_c', 1550):.2f} |"
                    f" {at(d, 'f_py60_x_c', 1550):.2f} / {at(d, 'f_my60_x_c', 1550):.2f} | {100*chk:.2g}% |")
        else:
            row += f' -- | -- | -- | -- | -- | -- | {100*chk:.2g}% |'
        out.append(row)
    out += ['', '## Position and orientation at 1550 nm (T / Fp)', '', '| geometry | x, centre | y, centre | z, centre | x, 5 nm to R2 | x, 10 nm to R3 |', '|---|---|---|---|---|---|']
    for g in D:
        d = D[g]
        if not (d['lambda_nm'].min() <= 1550 <= d['lambda_nm'].max()): continue
        cells = [f"{at(d, 'T_'+k, 1550):.3g} / {at(d, 'Fp_'+k, 1550):.3g}" for k in ('x_c', 'y_c', 'z_c', 'x_px5', 'x_py10')]
        out.append(f'| {g} | ' + ' | '.join(cells) + ' |')
    open(os.path.join(RES, 'trimer.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
    if not D: return

    fig, ax = plt.subplots(2, 3, figsize=(9.6, 5.2))
    for g, lab, c in GEO:
        if g not in D: continue
        d = D[g]; lam = d['lambda_nm']; w = HC / lam
        ax[0, 0].plot(w, d['ReG_x_c'], c=c, lw=1.1, label=lab)
        ax[0, 1].semilogy(w, d['ImG_x_c'], c=c, lw=1.1)
        ax[0, 2].semilogy(w, d['T_x_c'], c=c, lw=1.1)
        ax[1, 0].plot(w, 100 * d['T_x_c'] / d['Fp_x_c'], c=c, lw=1.1)
        ax[1, 1].plot(w, d['f_zNA13_x_c'], c=c, lw=1.1)
        ax[1, 2].semilogy(w, d['ext_x'] / 1e3, c=c, lw=1.1)
        if g in ('trimer', 'tri90'): ax[1, 2].semilogy(w, d['ext_y'] / 1e3, c=c, lw=0.9, ls='--')
    labs = [r'Re $\tilde G_{xx}$ (scattered)', r'Im $\tilde G_{xx}$ = LDOS $-$ 1', r'radiative enhancement $T$',
            r'antenna efficiency $\eta_a$ (%)', 'fraction into NA 1.3 (+z)', r'extinction ($10^3$ nm$^2$); dashed: $y$-pol.']
    for a, l, t in zip(ax.flat, labs, 'abcdef'):
        a.set_xlabel(r'$\hbar\omega$ (eV)'); a.set_ylabel(l); a.set_title(f'({t})', loc='left', fontsize=9)
        for le in (1310, 1550): a.axvline(HC / le, c='0.6', lw=0.8, ls=':')
    ax[0, 0].axhline(0, c='0.7', lw=0.6); ax[0, 0].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_trimer.pdf')); fig.savefig(os.path.join(FIG, 'fig_trimer.png'), dpi=130)


if __name__ == '__main__':
    main()
