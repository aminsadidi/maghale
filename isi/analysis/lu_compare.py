"""Comparison with Lu et al., ACS Photonics 7, 2498 (2020): NDI-2TEG-3T (q0 = 1.3e-4, emission maximum ~730 nm,
FWHM ~115 nm, detection >= 675 nm) near gold nanorods (D = 25 nm) in toluene, cw excitation at 671 nm.
Measured maximum enhancement: ~6500 for SPR 667 nm with circular polarisation (13000 for polarisation along the rod, as
estimated by the authors) and ~2000 (4000) for SPR 638 nm. Model: xi = E_exc(671) * <eta(q0)>/q0 over the detected
emission band, dipole on the axis and parallel to it (linear polarisation along the rod).
usage: python isi/analysis/lu_compare.py -> isi/results/lu_compare.md"""
import os, re, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
Q0 = 1.3e-4
MEAS = [(667, 13000, 6500), (638, 4000, 2000)]   # SPR, linear-equivalent, measured (circular)


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(RES, 'bem_extra', 'lu_L*.csv')), key=lambda f: int(re.search(r'_L(\d+)', f).group(1))):
        L = int(re.search(r'_L(\d+)', f).group(1)); meta = open(f).readline()
        d = np.genfromtxt(f, delimiter=',', names=True, skip_header=1); lam = d['lambda_nm']
        E671 = [float(x) for x in re.search(r'671 nm: ([\d.e+\- ]+)', meta).group(1).split()]
        spr = lam[np.argmax(d['ext_nm2'])]
        w = np.exp(-0.5 * ((lam - 730) / (115 / 2.355)) ** 2) * (lam >= 675); w /= w.sum()
        for gi, g in enumerate((1.5, 2, 3, 5)):
            names = d.dtype.names; F, T = d[names[2 + 3 * gi]], d[names[3 + 3 * gi]]
            Eem = np.sum(w * T / (F + (1 - Q0) / Q0)) / Q0
            rows.append((L, spr, g, E671[gi], Eem, E671[gi] * Eem, np.sum(w * T)))
    R = np.array(rows)
    out = ['# Comparison with Lu et al. 2020 (q0 = 1.3e-4, 671 nm excitation, D = 25 nm rods in toluene)', '',
           '| L | SPR | gap | E_exc(671) | E_em | xi | <T> band |', '|---|---|---|---|---|---|---|']
    for r in rows:
        out.append(f'| {r[0]} | {r[1]:.0f} | {r[2]:g} | {r[3]:.0f} | {r[4]:.0f} | {r[5]:.3g} | {r[6]:.0f} |')
    out += ['', '## At the measured resonances (interpolated in SPR)', '']
    for spr, lin, circ in MEAS:
        s = []
        for g in (1.5, 2, 3, 5):
            m = R[:, 2] == g; o = np.argsort(R[m, 1])
            xi = np.exp(np.interp(spr, R[m, 1][o], np.log(R[m, 5][o])))
            s.append(f'gap {g:g} nm: {xi:.3g}')
        out.append(f'- SPR {spr} nm: measured {circ} (circular), {lin} (along rod); model ' + ', '.join(s))
    open(os.path.join(RES, 'lu_compare.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__':
    main()
