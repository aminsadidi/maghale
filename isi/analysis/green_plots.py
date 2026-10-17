"""Green-function figures requested by the supervisor (Hughes-style), from the BEM runs (n = 1.5):
  fig_green.png  : Re and Im of the scattered Green function G_xx(r0, r0; w) at the emitter vs photon energy for the
                   single rod, the dimer and the parallel-R3 trimer; dashed: cross-polarised component (y dipole) x 50
  fig_drude.png  : gold permittivity, Johnson-Christy data and the Drude fit used beyond 1937 nm
Normalisation: G~ = d*.E_ind(r0) / (0.5 n (4/3) k0^3), so that Fp = LDOS/LDOS_0 = 1 + Im G~ and dw/Gamma0 = -Re G~ / 2."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tri2, trimer
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures'); HC = 1239.84
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True, 'legend.frameon': False, 'savefig.bbox': 'tight'})


def green():
    rows = [('single rod (L = 300 nm), 20 nm from the tip', trimer.geometry('single')[0], '0.3'),
            ('dimer (L = 270 nm, gap 40 nm), gap centre', tri2.series('L270')[0], '#1f4e9c'),
            (r'trimer, R3 parallel ($L_3$ = 300 nm, $Y_3$ = 160 nm)', tri2.series('L270_R300_A0_Y160')[0], '#c0392b')]
    fig, ax = plt.subplots(3, 2, figsize=(7.6, 7.4), sharex=True)
    for i, (lab, d, c) in enumerate(rows):
        w = HC / d['lambda_nm']
        a = ax[i, 0]; a.plot(w, d['ReG_x_c'], c=c, lw=1.2, label=r'Re $\tilde G_{xx}$')
        a.axhline(0, c='0.7', lw=0.6); a.set_ylabel(r'Re $\tilde G$'); a.legend(fontsize=6.5, loc='upper right')
        a.set_title(f'({"ace"[i]}) {lab}', loc='left', fontsize=8)
        a = ax[i, 1]; a.semilogy(w, d['ImG_x_c'], c=c, lw=1.2, label=r'Im $\tilde G_{xx}$ = $\rho_{xx}/\rho_0 - 1$')
        a.semilogy(w, 50 * d['Fp_y_c'], c=c, lw=0.9, ls='--', label=r'$\rho_{yy}/\rho_0 \times 50$')
        a.set_ylabel(r'Im $\tilde G$,  LDOS'); a.legend(fontsize=6.5, loc='lower right')
        a.set_title(f'({"bdf"[i]})', loc='left', fontsize=8)
    for a in ax.flat:
        for le in (1310, 1550): a.axvline(HC / le, c='0.6', lw=0.8, ls=':')
    for a in ax[2]: a.set_xlabel(r'$\hbar\omega$ (eV)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_green.png'), dpi=150); fig.savefig(os.path.join(FIG, 'fig_green.pdf'))


def drude():
    d = np.loadtxt(os.path.join(HERE, 'gold_jc.dat'), comments='%'); E, n, k = d.T; eps = (n + 1j * k) ** 2
    einf, wp, g = 9.71, 8.967, 0.0736
    w = np.linspace(0.45, 2.0, 300); ed = einf - wp ** 2 / (w ** 2 + 1j * g * w)
    m = E <= 2.0
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    ax[0].plot(E[m], -eps[m].real, 'o', ms=3.5, c='#b8892a', label='Johnson-Christy'); ax[0].plot(w, -ed.real, c='#1f4e9c', lw=1.1, label='Drude fit')
    ax[0].set_yscale('log'); ax[0].set_ylabel(r"$-\varepsilon'$"); ax[0].legend(fontsize=7)
    ax[1].plot(E[m], eps[m].imag, 'o', ms=3.5, c='#b8892a'); ax[1].plot(w, ed.imag, c='#1f4e9c', lw=1.1)
    ax[1].set_yscale('log'); ax[1].set_ylabel(r"$\varepsilon''$")
    for a, t in zip(ax, 'ab'):
        a.set_xlabel(r'$\hbar\omega$ (eV)'); a.set_title(f'({t})', loc='left', fontsize=9)
        for le in (1310, 1550): a.axvline(HC / le, c='0.6', lw=0.8, ls=':')
    fig.suptitle(rf'Drude: $\varepsilon_\infty$ = {einf}, $\hbar\omega_p$ = {wp} eV, $\hbar\gamma$ = {g} eV (fit to JC at 0.64-1.6 eV)', fontsize=8, y=1.02)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig_drude.png'), dpi=150)


if __name__ == '__main__':
    green(); drude()
