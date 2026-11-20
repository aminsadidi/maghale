"""Drude + Lorentz fit of the silver permittivity for Meep (time-domain), and the same model for the TMM code.

Meep convention (frequency f = 1/lambda in 1/um, exp(-i omega t)):
    eps(f) = eps_inf - sD fD^2 / (f^2 + i f gD) + sum_k s_k f_k^2 / (f_k^2 - f^2 - i f g_k)
Fitted to the Ciesielski 2017 data (20 nm Ag film evaporated on SiO2, the closest data set to the device film) over 0.35-1.0 um.
usage: python tamm/analysis/ldfit.py -> tamm/results/ag_ld.json (parameters) and a check table"""
import json, os, sys
import numpy as np
from scipy.optimize import least_squares
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); ROOT = os.path.join(HERE, '..')
import tmm  # noqa: E402


def eps_ld(P, f):
    e = P['eps_inf'] - P['sD'] * P['fD'] ** 2 / (f ** 2 + 1j * f * P['gD'])
    for s, f0, g in P['L']: e = e + s * f0 ** 2 / (f0 ** 2 - f ** 2 - 1j * f * g)
    return e


def unpack(x):
    return dict(eps_inf=x[0], sD=1.0, fD=x[1], gD=x[2], L=[(x[3], x[4], x[5]), (x[6], x[7], x[8])])


def fit(model='Ciesielski', lo=0.35, hi=1.0):
    lam = np.linspace(lo * 1000, hi * 1000, 200); f = 1000 / lam
    e = tmm.AG[model](lam) ** 2
    x0 = [3.0, 7.2, 0.03, 0.8, 3.3, 0.5, 0.5, 2.5, 1.0]          # fD ~ wp / h c = 9 eV -> 7.26 /um
    lo_b = [1, 5, 0.0, 0, 2.6, 0.01, 0, 0.5, 0.01]; hi_b = [8, 9, 0.5, 5, 6, 3, 5, 5, 5]
    w = 1 / np.maximum(np.abs(e), 1)
    r = least_squares(lambda x: np.r_[((eps_ld(unpack(x), f) - e) * w).real, ((eps_ld(unpack(x), f) - e) * w).imag], x0, bounds=(lo_b, hi_b))
    P = unpack(r.x); em = eps_ld(P, f)
    err = np.abs(em - e) / np.abs(e)
    return P, dict(max_rel=float(err.max()), rms_rel=float(np.sqrt(np.mean(err ** 2))), model=model, range_um=[lo, hi])


def tmm_material(P):
    """TMM material function (lam in nm) for the fitted model, so that TMM and Meep use exactly the same silver"""
    return lambda l: np.sqrt(eps_ld(P, 1000 / np.asarray(l, float)) + 0j)


if __name__ == '__main__':
    P, q = fit()
    print('fit quality', q)
    for l in (400, 500, 600, 700, 850):
        print(l, np.round(tmm.AG['Ciesielski'](np.array([l]))[0] ** 2, 2), np.round(eps_ld(P, 1000 / l), 2))
    json.dump(dict(params=P, quality=q), open(os.path.join(ROOT, 'results', 'ag_ld.json'), 'w'), indent=1)
