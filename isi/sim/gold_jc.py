"""Johnson-Christy gold as a Meep Drude-Lorentz medium (fit 440-1000 nm, rms 1.6 %, see fit_jc.py).
Meep units: length 1 um, frequency f = 1/lambda[um]."""
import json, os, numpy as np
import meep as mp
_p = json.load(open(os.path.join(os.path.dirname(__file__), 'gold_jc_params.json')))

def eps_jc(lam_nm):
    """Permittivity of the fitted model (same as the Meep medium), lam in nm."""
    f = 1000.0 / np.asarray(lam_nm, float)
    p = _p
    return (p['einf'] - p['s0'] * p['f0']**2 / (f**2 + 1j * f * p['g0'])
            + p['s1'] * p['f1']**2 / (p['f1']**2 - f**2 - 1j * f * p['g1'])
            + p['s2'] * p['f2']**2 / (p['f2']**2 - f**2 - 1j * f * p['g2']))

Au_JC = mp.Medium(epsilon=_p['einf'], E_susceptibilities=[
    mp.DrudeSusceptibility(frequency=_p['f0'], gamma=_p['g0'], sigma=_p['s0']),
    mp.LorentzianSusceptibility(frequency=_p['f1'], gamma=_p['g1'], sigma=_p['s1']),
    mp.LorentzianSusceptibility(frequency=_p['f2'], gamma=_p['g2'], sigma=_p['s2']),
])
