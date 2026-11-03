"""
validate.py - verification of the drift-diffusion solver.

 V1  Silicon p-n homojunction in the dark vs. the analytic Shockley diode
     (diffusion current J01 + Sah-Noyce-Shockley depletion current J02).
 V2  Mesh-independence of the MAGeI3 reference cell (coarse/normal/fine).
 V3  Consistency Jsc (J-V) vs. integral of EQE x AM1.5G photon flux
     and Mott-Schottky doping vs. input doping  (taken from run_all results).

writes ../results/Validation_*.csv
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dd1d import Device, Layer, defect, Simulation, Q, KB  # noqa: E402
import dd1d  # noqa: E402
import params as P  # noqa: E402

RES = os.path.join(HERE, "..", "results")
os.makedirs(RES, exist_ok=True)


def v1_shockley():
    T = 300.0
    Vt = KB * T
    Eg, chi, Nc, Nv = 1.12, 4.05, 2.8e19, 1.04e19
    mun, mup = 1000.0, 400.0
    NA, ND = 1e17, 1e17
    Nt, sig, vth = 1e15, 1e-15, 1e7
    tau = 1 / (sig * vth * Nt)
    mk = lambda name, nd, na: Layer(name, 50000.0, Eg, chi, 11.9, Nc, Nv, mun, mup, nd, na,
                                    defects=[defect("neutral", Nt, Eg / 2, sig, sig)])
    # back (p side) work function for flat band
    wf = chi + Eg - Vt * np.log(Nv / NA)
    dev = Device([mk("n-Si", ND, 0.0), mk("p-Si", 0.0, NA)], T=T, back_wf=wf,
                 front_Sn=1e7, front_Sp=1e7, back_Sn=1e7, back_Sp=1e7,
                 te_velocity=1e9, scale_dos_with_T=False)
    X = dev.solve_equilibrium()
    G0 = np.zeros(dev.N)
    ni = np.sqrt(Nc * Nv) * np.exp(-Eg / (2 * Vt))
    Dn, Dp = mun * Vt, mup * Vt
    Ln, Lp = np.sqrt(Dn * tau), np.sqrt(Dp * tau)
    J01 = Q * ni ** 2 * (Dn / (NA * Ln) + Dp / (ND * Lp))
    Vbi = Vt * np.log(NA * ND / ni ** 2)
    rows = []
    Vp = 0.0
    for V in np.arange(0.30, 0.701, 0.05):
        X = dev.solve_bias(X, Vp, V, G0, dV=0.05); Vp = V
        Jnum = -dev.terminal_current(X, V)
        eps = 11.9 * 8.8541878128e-14
        W = np.sqrt(2 * eps * (Vbi - V) / Q * (NA + ND) / (NA * ND))
        J02 = Q * ni * W / (2 * tau) * Vt / (Vbi - V) * np.pi * np.exp(V / (2 * Vt)) / 2  # Sah-Noyce-Shockley (symmetric)
        Jan = J01 * (np.exp(V / Vt) - 1) + J02
        rows.append([V, Jnum, J01 * (np.exp(V / Vt) - 1), J02, Jan, 100 * (Jnum - Jan) / Jan])
    path = os.path.join(RES, "Validation_V1_Shockley.csv")
    np.savetxt(path, rows, delimiter=",", fmt="%.6g",
               header="V,J_numerical_Acm2,J_diffusion_analytic,J_SNS_analytic,J_total_analytic,deviation_pct",
               comments="")
    return rows


def v2_mesh():
    out = []
    orig = Device._layer_mesh
    for name, hmin, ratio, frac in [("coarse", 3e-8, 1.25, 1 / 20), ("normal", 1e-8, 1.12, 1 / 40),
                                    ("fine", 3e-9, 1.06, 1 / 80)]:
        Device._layer_mesh = staticmethod(lambda d, hmin=hmin, ratio=ratio, nmax_frac=frac:
                                          orig(d, hmin, ratio, nmax_frac))
        dev = P.build_device(d_abs=600, d_etl=100, d_htl=100)
        sim = Simulation(dev)
        V, J, _ = sim.jv(dV=0.02)
        from run_all import jv_params
        r = jv_params(V, J)
        out.append([name, dev.N, r["Voc"], r["Jsc"], r["FF"], r["PCE"]])
    Device._layer_mesh = orig
    path = os.path.join(RES, "Validation_V2_mesh.csv")
    with open(path, "w") as fh:
        fh.write("mesh,nodes,Voc_V,Jsc_mAcm2,FF_pct,PCE_pct\n")
        for r in out:
            fh.write(",".join(str(x) if isinstance(x, str) else f"{x:.6g}" for x in r) + "\n")
    return out


if __name__ == "__main__":
    r1 = v1_shockley()
    for r in r1:
        print("V1 V=%.2f num=%.4e an=%.4e dev=%.2f%%" % (r[0], r[1], r[4], r[5]))
    r2 = v2_mesh()
    for r in r2:
        print("V2", r)
