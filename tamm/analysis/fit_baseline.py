"""Step 2: fit of the measured DBR and Tamm-device spectra (Fig 1, Zenodo) with the transfer-matrix model.

DBR: glass / 5 x (SiO2-NP / TiO2-NP) / air. Free: pore fractions pS, pT, thicknesses dS, dT, the material of the first layer on the
glass, the illuminated side, and one calibration factor each for R and T (the measured R + T exceeds 1 by up to 12 % in the stop band,
so the absolute scales of the two integrating-sphere measurements are not both exact).
Tamm device: the fitted DBR + Ag film (thickness, void fraction, Ag data set, extra Drude damping), same calibration factors.
usage: python tamm/analysis/fit_baseline.py -> tamm/results/baseline.json, tamm/figures/fig_t1_baseline.png"""
import json, os, sys, itertools
import numpy as np, matplotlib
from scipy.optimize import least_squares
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); ROOT = os.path.join(HERE, '..')
import tmm  # noqa: E402
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
LO, HI = 400, 850


def data(name):
    d = np.genfromtxt(os.path.join(ROOT, 'data', name), delimiter=',', names=True); d = d[np.argsort(d['lambda_nm'])]
    m = (d['lambda_nm'] >= LO) & (d['lambda_nm'] <= HI); return d[m]


def dbr_params(x, first, side):
    pS, pT, dS, dT = x[:4]
    # first layer on the glass = `first`; from the ambient side the stack starts with the other material
    return dict(pS=pS, pT=pT, dS=dS, dT=dT, N=5, top=('TiO2' if first == 'SiO2' else 'SiO2'), dAg=0), side


GH_X, GH_W = np.polynomial.hermite_e.hermegauss(7); GH_W = GH_W / GH_W.sum()


def avg(lam, p, side, sig):
    """R, T averaged over a Gaussian spread (relative sigma `sig`) of all DBR thicknesses inside the light spot"""
    R = T = 0.0
    for x, w in zip(GH_X, GH_W):
        q = dict(p, dS=p['dS'] * (1 + sig * x), dT=p['dT'] * (1 + sig * x))
        r, t = tmm.device(lam, tmm.tamm_layers(q), side=side); R = R + w * r; T = T + w * t
    return R, T


SEM = (110.0, 90.0, 8.0)          # SEM thicknesses of SiO2 / TiO2 (Fig 1a) and the prior width (nm)


def model_dbr(x, lam, first, side):
    p, side = dbr_params(x, first, side)
    R, T = avg(lam, p, side, x[6])
    return x[4] * R, x[5] * T


def fit_dbr(d):
    lam = d['lambda_nm']; R, T = d['R_pct'] / 100, d['T_pct'] / 100
    best = None
    for first, side in itertools.product(('SiO2', 'TiO2'), ('film', 'glass')):
        for x0 in ([0.35, 0.35, 110, 90, 1.0, 1.0, 0.03], [0.2, 0.5, 105, 95, 1.0, 1.0, 0.05], [0.45, 0.25, 115, 85, 1.0, 1.0, 0.02]):
            def res(x):
                mR, mT = model_dbr(x, lam, first, side)
                return np.r_[mR - R, mT - T, 0.02 * (x[2] - SEM[0]) / SEM[2], 0.02 * (x[3] - SEM[1]) / SEM[2]]
            r = least_squares(res, x0, bounds=([0, 0, 80, 60, 0.85, 0.85, 0.0], [0.7, 0.7, 140, 120, 1.2, 1.2, 0.12]))
            rms = np.sqrt(np.mean(r.fun[:-2] ** 2))
            if best is None or rms < best[0]: best = (rms, r.x, first, side)
    return best


def model_td(y, xd, lam, first, side, ag):
    """Ag film = sub-wavelength island film (EMA: void fraction, depolarisation L, extra damping) covering a fraction 1 - a of the
    spot; the fraction a is bare DBR (large uncovered patches, added incoherently). a = 0: pure EMA film."""
    dAg, void, dgam, sc, L, a = y
    p, _ = dbr_params(xd, first, side); p.update(dAg=dAg, void=void, dgamma=dgam, ag=ag, dS=xd[2] * sc, dT=xd[3] * sc, L=L)
    R, T = avg(lam, p, side, xd[6])
    if a > 0:
        q = dict(p, dAg=0); R0, T0 = avg(lam, q, side, xd[6]); R, T = (1 - a) * R + a * R0, (1 - a) * T + a * T0
    return xd[4] * R, xd[5] * T


def fit_td(d, xd, first, side):
    lam = d['lambda_nm']; R, T = d['R_pct'] / 100, d['T_pct'] / 100
    out = {}
    for ag in ('JC', 'Yang', 'Ciesielski'):
        for sd in (side, 'film' if side == 'glass' else 'glass'):
            best = None
            for y0 in ([38, 0.34, 0.0, 1.0, 0.6, 0.0], [33, 0.25, 0.05, 0.97, 0.45, 0.05], [40, 0.4, 0.02, 1.0, 0.33, 0.0]):
                r = least_squares(lambda y: np.r_[model_td(y, xd, lam, first, sd, ag)[0] - R, model_td(y, xd, lam, first, sd, ag)[1] - T], y0,
                                  bounds=([10, 0, 0, 0.85, 0.05, 0.0], [60, 0.7, 0.3, 1.15, 0.75, 0.6]))
                rms = np.sqrt(np.mean(r.fun ** 2))
                if best is None or rms < best[0]: best = (rms, r.x)
            out[(ag, sd)] = best
    return out


def dip(lam, R, lo=520, hi=780):
    m = (lam > lo) & (lam < hi); i = np.argmin(np.where(m, R, 9)); return lam[i], R[i]


def main():
    dd, dt = data('fig1_dbr.csv'), data('fig1_td.csv')
    rms, xd, first, side = fit_dbr(dd)
    print(f'DBR fit: rms {rms*100:.2f} %  first layer on glass {first}, light from the {side} side')
    print(f'   SiO2: porosity {xd[0]:.3f} d {xd[2]:.1f} nm | TiO2: porosity {xd[1]:.3f} d {xd[3]:.1f} nm | calibration R x{xd[4]:.3f} T x{xd[5]:.3f} | thickness spread {100*xd[6]:.1f} %')
    for l in (500, 600, 700):
        print(f'   n_SiO2({l}) = {tmm.porous(tmm.SiO2, tmm.AIR, xd[0])(np.array([l]))[0].real:.3f}  n_TiO2({l}) = {tmm.porous(tmm.TiO2, tmm.AIR, xd[1])(np.array([l]))[0]:.3f}')
    td = fit_td(dt, xd, first, side)
    for k, (r, y) in sorted(td.items(), key=lambda kv: kv[1][0]):
        print(f'TD fit {k}: rms {r*100:.2f} %  dAg {y[0]:.1f} nm, void {y[1]:.3f}, extra damping {y[2]*1e3:.0f} meV, DBR thickness x{y[3]:.3f}, L {y[4]:.3f}, bare area {y[5]:.3f}')
    (ag, sd), (r, y) = min(td.items(), key=lambda kv: kv[1][0])
    lam = np.linspace(LO, HI, 451)
    Rd, Td = model_dbr(xd, lam, first, side); Rt, Tt = model_td(y, xd, lam, first, sd, ag)
    ld, Rmin = dip(lam, Rt); le, Re_ = dip(dt['lambda_nm'], dt['R_pct'] / 100)
    print(f'Tamm dip: model {ld:.0f} nm R = {Rmin*100:.1f} %, measured {le:.0f} nm R = {Re_*100:.1f} %')
    res = dict(dbr=dict(rms=rms, pS=xd[0], pT=xd[1], dS=xd[2], dT=xd[3], calR=xd[4], calT=xd[5], spread=xd[6], first=first, side=side),
               td=dict(rms=r, ag=ag, side=sd, dAg=y[0], void=y[1], dgamma=y[2], scale=y[3], L=y[4], bare=y[5], dip_model=ld, Rdip_model=Rmin, dip_exp=le, Rdip_exp=Re_),
               td_all={f'{k[0]}|{k[1]}': dict(rms=v[0], dAg=v[1][0], void=v[1][1], dgamma=v[1][2], scale=v[1][3], L=v[1][4], bare=v[1][5]) for k, v in td.items()})
    json.dump(res, open(os.path.join(ROOT, 'results', 'baseline.json'), 'w'), indent=1, default=float)
    S = np.genfromtxt(os.path.join(ROOT, 'data', 'figS6_tmm.csv'), delimiter=',', names=True)
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.4))
    ax[0].plot(dd['lambda_nm'], dd['R_pct'], c='#1f4e9c', lw=1.2, alpha=0.6, label='R measured'); ax[0].plot(lam, 100 * Rd, c='#1f4e9c', lw=2.2, ls='--', label='R model')
    ax[0].plot(dd['lambda_nm'], dd['T_pct'], c='#9a3412', lw=1.2, alpha=0.6, label='T measured'); ax[0].plot(lam, 100 * Td, c='#9a3412', lw=2.2, ls='--', label='T model')
    ax[0].set_title('(a) DBR: 5 x (SiO$_2$/TiO$_2$ nanoparticle films)'); ax[0].legend(fontsize=9)
    ax[1].plot(dt['lambda_nm'], dt['R_pct'], c='#1f4e9c', lw=1.2, alpha=0.6, label='R measured'); ax[1].plot(lam, 100 * Rt, c='#1f4e9c', lw=2.2, ls='--', label='R model (this work)')
    ax[1].plot(dt['lambda_nm'], dt['T_pct'], c='#9a3412', lw=1.2, alpha=0.6, label='T measured'); ax[1].plot(lam, 100 * Tt, c='#9a3412', lw=2.2, ls='--', label='T model')
    ax[1].plot(S['lambda_nm'], 100 * S['TD_TMM'], c='0.6', lw=1, ls=':', label='R, TMM of Fig. S6')
    ax[1].set_title(f'(b) Tamm device: + Ag {y[0]:.0f} nm ({ag}), {100*y[5]:.0f} % bare area'); ax[1].legend(fontsize=9)
    for a in ax: a.set_xlabel('wavelength (nm)'); a.set_ylabel('%'); a.set_xlim(LO, HI); a.set_ylim(0, 110)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t1_baseline.png')); print('figure written')


if __name__ == '__main__':
    main()
