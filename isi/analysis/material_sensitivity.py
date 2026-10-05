"""Sensitivity of the main results to the gold permittivity (BEM, 60 x 20 nm rod, h = 2 nm mesh) and cryogenic estimate.
Inputs: isi/results/bem_extra/material_<spec>.csv (job_material.m), reference JC: isi/results/bem_raw/rod_L60_h2_air.csv.
usage: python isi/analysis/material_sensitivity.py -> isi/results/material_sensitivity.md"""
import os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
SETS = [('JC (reference)', 'bem_raw/rod_L60_h2_air.csv'), ('Palik', 'bem_extra/material_palik.csv'),
        ('Olmon (evap.)', 'bem_extra/material_olmon.csv'), ('McPeak', 'bem_extra/material_mcpeak.csv'),
        ('JC + surface damping', 'bem_extra/material_surf.csv'),
        ('JC, cold (0.039 eV)', 'bem_extra/material_cold1.csv'), ('JC, cold (0.020 eV)', 'bem_extra/material_cold2.csv')]


def load(f):
    p = os.path.join(RES, f)
    return np.genfromtxt(p, delimiter=',', names=True, skip_header=1) if os.path.exists(p) else None


def summary():
    rows = {}
    for lab, f in SETS:
        d = load(f)
        if d is None: continue
        lam = d['lambda_nm']; m = (lam >= 500) & (lam <= 840)
        r = {}
        for g in (5, 10, 20):
            Tz, Fz, Fx = d[f'T_z_g{g}'][m], d[f'Fp_z_g{g}'][m], d[f'Fp_x_g{g}'][m]; l = lam[m]
            i = np.argmax(Tz); R = Fz / Fx
            r[g] = dict(lamT=l[i], T=Tz[i], Fp=Fz[i], eta=Tz[i] / Fz[i], Rmax=R.max(), lamR=l[np.argmax(R)],
                        Fpmax=Fz.max(), RT=(Tz / d[f'T_x_g{g}'][m])[i])
        rows[lab] = r
    return rows


def main():
    rows = summary()
    out = ['# Gold-permittivity sensitivity (BEM, rod 60 x 20 nm, axial vs transverse dipole)', '',
           '| data | gap | lambda_T | T max | Fp there | eta_a | max Fp_z/Fp_x (at nm) | T_z/T_x at lambda_T |', '|---|---|---|---|---|---|---|---|']
    for lab, r in rows.items():
        for g in (5, 10, 20):
            x = r[g]
            out.append(f'| {lab} | {g} | {x["lamT"]:.0f} | {x["T"]:.1f} | {x["Fp"]:.0f} | {100*x["eta"]:.1f}% | {x["Rmax"]:.0f} ({x["lamR"]:.0f}) | {x["RT"]:.0f} |')
    if 'JC (reference)' in rows:
        ref = rows['JC (reference)']
        out += ['', '## Relative to JC', '']
        for lab, r in rows.items():
            if lab.startswith('JC (ref'): continue
            out.append(f'- {lab}: ' + '; '.join(
                f'gap {g}: dlam {r[g]["lamT"]-ref[g]["lamT"]:+.0f} nm, T {100*(r[g]["T"]/ref[g]["T"]-1):+.0f}%, Fp {100*(r[g]["Fp"]/ref[g]["Fp"]-1):+.0f}%, '
                f'eta {100*r[g]["eta"]:.1f}% vs {100*ref[g]["eta"]:.1f}%, Rmax {r[g]["Rmax"]:.0f} vs {ref[g]["Rmax"]:.0f}' for g in (5, 10)))
        # indistinguishability with the cold permittivity (q0 = 1, tau_rad = 1 ns)
        hG0 = 6.582e-16 / 1e-9
        out += ['', '## Indistinguishability I = Fp G0 / (Fp G0 + 2 gamma*) at the radiative peak (q0 = 1, tau_rad = 1 ns)', '',
                '| data | gap | Fp | eta_a | I (gamma* = 1 ueV) | I (10 ueV) |', '|---|---|---|---|---|---|']
        for lab in ('JC (reference)', 'JC, cold (0.039 eV)', 'JC, cold (0.020 eV)'):
            if lab not in rows: continue
            for g in (5, 20):
                F = rows[lab][g]['Fp']; hG = F * hG0
                out.append(f'| {lab} | {g} | {F:.0f} | {100*rows[lab][g]["eta"]:.1f}% | {100*hG/(hG+2e-6):.1f}% | {100*hG/(hG+2e-5):.1f}% |')
    open(os.path.join(RES, 'material_sensitivity.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))


if __name__ == '__main__':
    main()
