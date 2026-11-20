"""Tamm-device spectra from the 3D island-film S-parameters (Meep, tamm/results/meep/*.npz) cascaded with the planar DBR and the
thick glass substrate, compared with the measurements; validation of the cascade against the full-device 3D runs (D_*).

Film S-parameters: r_top, t_down from incidence from air ('top' runs), r_bot, t_up from incidence from below ('bottom' runs); the x
and y polarisations are averaged (random film). Reference planes: z = zref (air side) and z = 0 (film bottom, in n_b = 1.93).
usage: python tamm/analysis/meep_device.py"""
import glob, json, os, sys
import numpy as np, matplotlib
from scipy.optimize import least_squares
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); ROOT = os.path.join(HERE, '..')
import tmm, cascade as C  # noqa: E402
MEEP = os.path.join(ROOT, 'results', 'meep')
plt.rcParams.update({'font.size': 11, 'axes.linewidth': 0.9, 'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.dpi': 200, 'axes.grid': True, 'grid.color': '#ecebe6'})
NB = 1.93


def load(name):
    o = np.load(os.path.join(MEEP, name + '.npz')); lam = o['lam'] * 1000; s = np.argsort(lam)
    return dict(lam=lam[s], r=o['r'][s], t=o['t'][s], R=o['R'][s], T=o['T'][s], case=json.loads(str(o['case'])))


def have(name): return os.path.exists(os.path.join(MEEP, name + '.npz'))


def film(prefix, pols=('x', 'y')):
    """S-parameters of one film: prefix like 'I_s1' or 'M_dg10_s1' (expects <prefix>_top_<pol>, <prefix>_bottom_<pol>)"""
    tops = [load(f'{prefix}_top_{p}') for p in pols if have(f'{prefix}_top_{p}')]
    bots = [load(f'{prefix}_bottom_{p}') for p in pols if have(f'{prefix}_bottom_{p}')]
    if not tops or not bots: return None
    m = lambda L, k: np.mean([x[k] for x in L], axis=0)
    c = tops[0]['case']
    return dict(lam=tops[0]['lam'], r12=m(tops, 'r'), t12=m(tops, 't'), r21=m(bots, 'r'), t21=m(bots, 't'),
                R_top=m(tops, 'R'), T_top=m(tops, 'T'), R_bot=m(bots, 'R'), T_bot=m(bots, 'T'), n_top=c.get('n_top', 1.0), nb=c.get('nb', NB),
                diffuse_top=m(tops, 'R') - np.abs(m(tops, 'r')) ** 2)


def dbr_sections(lam, B, scale, n_first_const=None):
    """planar DBR below the film: from the film side TiO2 / SiO2 x 5 (fit of Fig. 1), then glass. Returns the S-section list."""
    d = B['dbr']; sio = tmm.porous(tmm.SiO2, tmm.AIR, d['pS'])(lam); tio = tmm.porous(tmm.TiO2, tmm.AIR, d['pT'])(lam)
    top_first = 'TiO2' if d['first'] == 'SiO2' else 'SiO2'
    pair = [(tio, d['dT'] * scale), (sio, d['dS'] * scale)] if top_first == 'TiO2' else [(sio, d['dS'] * scale), (tio, d['dT'] * scale)]
    layers = pair * 5
    S = []; n_prev = np.full(len(lam), NB + 0j)
    for n, t in layers:
        S += [C.interface(n_prev, n), C.layer(n, t, lam)]; n_prev = n
    S.append(C.interface(n_prev, tmm.BK7(lam)))
    return S


def device(F, lam, B, scale, side='glass'):
    """coherent air|film|DBR|glass amplitudes + incoherent glass back face; returns R, T (fractions)"""
    fl = (F['r12'], F['t12'], F['r21'], F['t21'], np.full(len(lam), F['n_top'] + 0j), np.full(len(lam), NB + 0j))
    S = C.chain(fl, *dbr_sections(lam, B, scale))
    r12, t12, r21, t21, n1, n2 = S
    ng = tmm.BK7(lam).real
    Rf, Tf = np.abs(r12) ** 2, ng / F['n_top'] * np.abs(t12) ** 2            # from air (film side) into glass
    Rg = np.abs(r21) ** 2; Tg = F['n_top'] / ng * np.abs(t21) ** 2           # from glass into air
    rb = ((ng - 1) / (ng + 1)) ** 2
    if side == 'film':
        R = Rf + Tf * rb * Tf / (1 - rb * Rg); T = Tf * (1 - rb) / (1 - rb * Rg)
    else:
        R = rb + (1 - rb) ** 2 * Rg / (1 - rb * Rg); T = (1 - rb) * Tg / (1 - rb * Rg)
    return R, T


def interp_film(F, lam):
    out = dict(F); out['lam'] = lam
    for k in ('r12', 't12', 'r21', 't21'):
        out[k] = np.interp(lam, F['lam'], F[k].real) + 1j * np.interp(lam, F['lam'], F[k].imag)
    return out


def main():
    B = json.load(open(os.path.join(ROOT, 'results', 'baseline.json')))
    meas = np.genfromtxt(os.path.join(ROOT, 'data', 'fig1_td.csv'), delimiter=',', names=True); meas = meas[np.argsort(meas['lambda_nm'])]
    lam = np.arange(400, 851, 2.0)
    out = {}
    # ---- 1. cascade check against the full-device 3D runs (glass not incoherent there: compare the coherent stack with a glass half-space)
    if have('D_s1_top_x') and have('I_s1_top_x') and have('I_s1_bottom_x'):
        F = film('I_s1', pols=('x',)); D = load('D_s1_top_x'); Db = load('D_s1_bottom_x') if have('D_s1_bottom_x') else None
        fl = (F['r12'], F['t12'], F['r21'], F['t21'], np.full(len(F['lam']), 1.0 + 0j), np.full(len(F['lam']), NB + 0j))
        stack = json.loads(json.dumps(D['case']['stack']))
        S = [fl]; n_prev = np.full(len(F['lam']), NB + 0j)
        for n, t in stack:
            S += [C.interface(n_prev, n + 0j), C.layer(n + 0j, t * 1000, F['lam'])]; n_prev = np.full(len(F['lam']), n + 0j)
        S.append(C.interface(n_prev, np.full(len(F['lam']), 1.52 + 0j)))
        Sx = C.chain(*S)
        Rc, Tc = np.abs(Sx[0]) ** 2, 1.52 * np.abs(Sx[1]) ** 2
        out['cascade_check'] = dict(lam=F['lam'].tolist(), R_3D=D['R'].tolist(), R_cascade=Rc.tolist(), T_3D=D['T'].tolist(), T_cascade=Tc.tolist(),
                                    max_dR=float(np.max(np.abs(D['R'] - Rc))), max_dT=float(np.max(np.abs(D['T'] - Tc))))
        print(f"cascade vs full 3D device (from air): max |dR| {out['cascade_check']['max_dR']:.3f}, max |dT| {out['cascade_check']['max_dT']:.3f}")
    # ---- 2. island-film device vs measurement: fit only the DBR thickness scale and the two calibration factors
    films = {p: film(p) for p in ('I_s1', 'I_s2', 'I_s3', 'I_s4')}
    films = {k: v for k, v in films.items() if v is not None}
    if films:
        Fm = {k: interp_film(v, lam) for k, v in films.items()}
        mR = np.interp(lam, meas['lambda_nm'], meas['R_pct']) / 100; mT = np.interp(lam, meas['lambda_nm'], meas['T_pct']) / 100
        res = {}
        for side in ('glass', 'film'):
            def model(x):
                RT = [device(F, lam, B, x[0], side) for F in Fm.values()]
                return x[1] * np.mean([r for r, t in RT], 0), x[2] * np.mean([t for r, t in RT], 0)
            r = least_squares(lambda x: np.r_[model(x)[0] - mR, model(x)[1] - mT], [1.0, 1.1, 1.0], bounds=([0.85, 0.85, 0.7], [1.15, 1.3, 1.3]))
            res[side] = (np.sqrt(np.mean(r.fun ** 2)), r.x, model(r.x))
            print(f'island film (3D, {len(Fm)} realisations) + DBR, light from the {side} side: rms {res[side][0]*100:.2f} %, scale {r.x[0]:.3f}, calR {r.x[1]:.3f}, calT {r.x[2]:.3f}')
        side = min(res, key=lambda k: res[k][0]); rms, x, (Rm, Tm) = res[side]
        out['device_fit'] = dict(side=side, rms=rms, scale=x[0], calR=x[1], calT=x[2], n_films=len(Fm))
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.4))
        ax[0].plot(meas['lambda_nm'], meas['R_pct'], c='#1f4e9c', lw=1.2, alpha=0.6, label='R measured')
        ax[0].plot(lam, 100 * Rm, c='#1f4e9c', lw=2.2, ls='--', label='R: 3D island film + DBR')
        ax[0].plot(meas['lambda_nm'], meas['T_pct'], c='#9a3412', lw=1.2, alpha=0.6, label='T measured')
        ax[0].plot(lam, 100 * Tm, c='#9a3412', lw=2.2, ls='--', label='T: 3D island film + DBR')
        ax[0].set_xlim(400, 850); ax[0].set_ylim(0, 100); ax[0].set_xlabel('wavelength (nm)'); ax[0].set_ylabel('%'); ax[0].legend(fontsize=9)
        ax[0].set_title(f'(a) Tamm device: measured vs 3D model (light from the {side} side)')
        for k, F in films.items():
            ax[1].plot(F['lam'], 100 * F['R_top'], lw=1.2, label=f'{k}: R (from air)')
            ax[1].plot(F['lam'], 100 * F['diffuse_top'], lw=1.0, ls=':', label=f'{k}: diffuse part')
        ax[1].set_xlim(400, 850); ax[1].set_xlabel('wavelength (nm)'); ax[1].set_ylabel('%'); ax[1].legend(fontsize=7.5, ncol=2)
        ax[1].set_title('(b) island film on TiO$_2$ alone (4 random realisations)')
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'figures', 'fig_t2_device3d.png')); plt.close(fig)
    json.dump(out, open(os.path.join(ROOT, 'results', 'meep_device.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
