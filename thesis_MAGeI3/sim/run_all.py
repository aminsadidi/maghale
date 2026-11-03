"""
run_all.py - complete simulation campaign for Chapter 4.

Runs the 7-step protocol of Chapter 3 plus extended analyses, writes every
data set to ../results/*.csv (+ one Excel workbook for Origin) and
every figure to ../figures/*.png (300 dpi).

usage:  python run_all.py            (full run, ~10-30 min)
        python run_all.py --quick    (coarse, for testing)
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
_trapz = getattr(np, "trapezoid", None) or np.trapz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dd1d import Simulation, Device, Layer, defect, Q, EPS0  # noqa: E402
import params as P  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

QUICK = "--quick" in sys.argv
DV = 0.04 if QUICK else 0.02
BUFS = ["WOx", "NiOx", "V2O5"]
LABEL = {None: "No buffer", "WOx": "WOx", "NiOx": "NiOx", "V2O5": "V2O5"}


# --------------------------------------------------------------------- helpers
def jv_params(V, J):
    from scipy.interpolate import PchipInterpolator
    Jsc = float(np.interp(0.0, V, J))
    idx = np.where(J <= 0)[0]
    if Jsc <= 1e-3 or len(idx) == 0:
        Vf = np.linspace(0, V[-1], 4000)
        P_ = Vf * np.interp(Vf, V, J)
        return dict(Voc=float("nan"), Jsc=Jsc, FF=float("nan"), PCE=float(max(P_.max(), 0)))
    i = idx[0]
    Voc = float(V[i - 1] + (V[i] - V[i - 1]) * J[i - 1] / (J[i - 1] - J[i]))
    f = PchipInterpolator(V, J)
    Vf = np.linspace(0, Voc, 4000)
    P_ = Vf * f(Vf)
    k = int(np.argmax(P_))
    PCE = float(P_[k])
    return dict(Voc=Voc, Jsc=Jsc, FF=100 * PCE / (Voc * Jsc), PCE=PCE,
                Vmp=float(Vf[k]), Jmp=float(f(Vf[k])))


def run_jv(kw, dV=None, keep_curve=False):
    """kw -> build_device kwargs. Returns params (+curve)."""
    dV = dV or DV
    t = time.time()
    kw = dict(kw)
    suns = kw.pop("suns", 1.0)
    try:
        sim = Simulation(P.build_device(**kw))
        if suns != 1.0:
            sim.G = sim.G * suns; sim.Gl = sim.Gl * suns
        V, J, X = sim.jv(dV=dV, Vmax=1.8)
        out = jv_params(V, J)
        out["PCE"] = out["PCE"] / suns
        out["ok"] = True
    except Exception as exc:  # pragma: no cover
        out = dict(Voc=np.nan, Jsc=np.nan, FF=np.nan, PCE=np.nan, ok=False, err=str(exc))
        V, J = np.array([]), np.array([])
    out["suns"] = suns
    out.update({k: (v if v is not None else "none") for k, v in kw.items()
                if not isinstance(v, dict)})
    out["time_s"] = time.time() - t
    if keep_curve:
        out["V"] = V.tolist(); out["J"] = J.tolist()
    return out


def pmap(func, items, procs=4):
    with Pool(procs) as pool:
        return pool.map(func, items)


def save_csv(name, header, rows):
    path = os.path.join(RES, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(",".join(header) + "\n")
        for r in rows:
            fh.write(",".join(f"{x:.6g}" if isinstance(x, (float, np.floating)) else str(x)
                              for x in r) + "\n")
    return path


def best(rows, key="d"):
    ok = [r for r in rows if r.get("ok") and r["PCE"] == r["PCE"]]
    return max(ok, key=lambda r: r["PCE"])


def _jv_curve(kw):
    return run_jv(kw, dV=0.01 if not QUICK else 0.04, keep_curve=True)


# --------------------------------------------------------------------- steps
def step_sweep(var, values, base, extra=None):
    items = []
    for v in values:
        kw = dict(base); kw[var] = v
        if extra:
            kw.update(extra)
        items.append(kw)
    return pmap(run_jv, items)


def profiles_for(kw, V=0.0, light=True):
    sim = Simulation(P.build_device(**kw))
    dev = sim.dev
    G = sim.G if light else np.zeros(dev.N)
    X = sim.Xeq.copy()
    if light:
        X = dev.ramp_light(X, 0.0, G)
    if V != 0:
        X = dev.solve_bias(X, 0.0, V, G, dV=0.05)
    pr = sim.profiles(X, G)
    pr["layers"] = [L.name for L in dev.layers]
    pr["bounds_nm"] = list(np.cumsum([0] + [L.d_nm for L in dev.layers]))
    return pr


def eqe_for(kw):
    sim = Simulation(P.build_device(**kw), dlam=10.0)
    sim.Xsc = sim.dev.ramp_light(sim.Xeq.copy(), 0.0, sim.G)
    lam, qe = sim.qe()
    # integrated Jsc (mA/cm2)
    from dd1d import load_am15g
    l2, fl = load_am15g(300, 900, 10.0)
    qe = np.clip(np.asarray(qe), 0.0, None) + 0.0
    Jint = np.concatenate([[0], np.cumsum(Q * fl[1:] * qe[1:] / 100 * 10.0)]) * 1e3
    Jsc_direct = sim.dev.terminal_current(sim.Xsc, 0.0) * 1e3
    return dict(lam=lam.tolist(), qe=qe.tolist(), Jint=Jint.tolist(), Jsc=float(Jsc_direct))


def cv_for(kw):
    """Dark C-V at 1 kHz and Mott-Schottky analysis."""
    sim = Simulation(P.build_device(**kw))
    dev = sim.dev
    G0 = np.zeros(dev.N)
    X = sim.Xeq.copy()
    Vs = np.round(np.arange(-0.4, 1.31, 0.05), 3)
    out_V, out_C = [], []
    # start at 0 then go negative and positive
    Xs = {}
    Xc = X.copy()
    for V in [v for v in Vs if v >= 0]:
        Xc = dev.solve_bias(Xc, out_V[-1] if out_V else 0.0, V, G0, dV=0.05) if V != 0 else Xc
        Y = sim.admittance(Xc, V, G0, [1e3])[0]
        out_V.append(V); out_C.append(Y.imag / (2 * np.pi * 1e3))
    Xc = X.copy(); Vp = 0.0
    neg_V, neg_C = [], []
    for V in sorted([v for v in Vs if v < 0], reverse=True):
        Xc = dev.solve_bias(Xc, Vp, V, G0, dV=0.05); Vp = V
        Y = sim.admittance(Xc, V, G0, [1e3])[0]
        neg_V.append(V); neg_C.append(Y.imag / (2 * np.pi * 1e3))
    V = np.array(neg_V[::-1] + out_V); C = np.array(neg_C[::-1] + out_C)   # F/cm2
    inv = 1 / C ** 2
    # linear fit in reverse / low forward bias region
    m = (V >= -0.4) & (V <= 0.6)
    k, c0 = np.polyfit(V[m], inv[m], 1)
    Vbi = -c0 / k
    eps = P.MAGeI3().eps
    Ndop = 2 / (Q * eps * EPS0 * abs(k))
    return dict(V=V.tolist(), C=C.tolist(), invC2=inv.tolist(), Vbi=float(Vbi),
                N=float(Ndop), slope=float(k))


def impedance_for(kw):
    """Impedance spectrum under 1 sun at open circuit (approx. Vmp..Voc)."""
    sim = Simulation(P.build_device(**kw))
    V, J, Xs = sim.jv(dV=0.02, Vmax=1.8)
    pr = jv_params(V, J)
    Vb = pr["Voc"] if pr["Voc"] == pr["Voc"] else 1.0
    # nearest computed bias state below Voc
    i = int(np.argmin(np.abs(V - Vb)))
    X = sim.dev.solve_bias(Xs[i], V[i], Vb, sim.G, dV=0.005)
    f = np.logspace(0, 8, 49)
    Y = sim.admittance(X, Vb, sim.G, f)
    Z = 1 / Y
    return dict(f=f.tolist(), Zre=Z.real.tolist(), Zim=Z.imag.tolist(), Vbias=float(Vb))


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    summary = {}

    # ---------------- Step 1: absorber thickness
    d_abs_vals = [100, 200, 300, 400, 500, 600, 700, 800]
    s1 = step_sweep("d_abs", d_abs_vals, dict(d_etl=100, d_htl=100))
    save_csv("Step1_MAGeI3_thickness.csv", ["d_MAGeI3_nm", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[r["d_abs"], r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for r in s1])
    # optimum: the thickness after which PCE gains < 1% relative (saturation) or max
    pces = np.array([r["PCE"] for r in s1])
    d_abs_opt = d_abs_vals[int(np.nanargmax(pces))]
    summary["d_abs_opt"] = d_abs_opt
    print("step1 done", d_abs_opt, time.time() - t0, flush=True)

    # ---------------- Step 2: ETL thickness
    d_etl_vals = [1, 50, 100, 150, 200, 250, 300, 350, 400]
    s2 = step_sweep("d_etl", d_etl_vals, dict(d_abs=d_abs_opt, d_htl=100))
    save_csv("Step2_TiO2_thickness.csv", ["d_TiO2_nm", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[r["d_etl"], r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for r in s2])
    d_etl_opt = best(s2)["d_etl"]
    summary["d_etl_opt"] = d_etl_opt
    print("step2 done", d_etl_opt, time.time() - t0, flush=True)

    # ---------------- Step 3: HTL thickness
    d_htl_vals = [1, 50, 100, 150, 200]
    s3 = step_sweep("d_htl", d_htl_vals, dict(d_abs=d_abs_opt, d_etl=d_etl_opt))
    save_csv("Step3_Spiro_thickness.csv", ["d_Spiro_nm", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[r["d_htl"], r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for r in s3])
    d_htl_opt = best(s3)["d_htl"]
    summary["d_htl_opt"] = d_htl_opt
    print("step3 done", d_htl_opt, time.time() - t0, flush=True)

    base = dict(d_abs=d_abs_opt, d_etl=d_etl_opt, d_htl=d_htl_opt)

    # ---------------- Step 4: buffer thickness
    d_buf_vals = [0, 10, 20, 30, 40, 50]
    items = []
    for b in BUFS:
        for d in d_buf_vals:
            kw = dict(base); kw.update(buffer=(b if d > 0 else None), d_buf=d)
            items.append((b, d, kw))
    res = pmap(run_jv, [it[2] for it in items])
    rows4 = []
    s4 = {b: [] for b in BUFS}
    for (b, d, _), r in zip(items, res):
        s4[b].append(dict(r, d_buf=d))
        rows4.append([b, d, r["Voc"], r["Jsc"], r["FF"], r["PCE"]])
    save_csv("Step4_buffer_thickness.csv", ["buffer", "d_buffer_nm", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"], rows4)
    d_buf_opt = {}
    for b in BUFS:
        cand = [r for r in s4[b] if r["d_buf"] > 0 and r.get("ok") and r["PCE"] == r["PCE"]]
        d_buf_opt[b] = max(cand, key=lambda r: r["PCE"])["d_buf"] if cand else 10
    summary["d_buf_opt"] = d_buf_opt
    print("step4 done", d_buf_opt, time.time() - t0, flush=True)

    # ---------------- Steps 5-6: J-V / P-V of optimum structures
    structs = {"No buffer": dict(base)}
    for b in BUFS:
        kw = dict(base); kw.update(buffer=b, d_buf=d_buf_opt[b]); structs[b] = kw
    curves = pmap(_jv_curve, list(structs.values()))
    jv = dict(zip(structs.keys(), curves))
    save_csv("Step5_6_optimum_structures.csv", ["structure", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct", "Vmp_V", "Jmp_mAcm2"],
             [[k, v["Voc"], v["Jsc"], v["FF"], v["PCE"], v.get("Vmp", np.nan), v.get("Jmp", np.nan)] for k, v in jv.items()])
    Vg = np.round(np.arange(0, 1.8001, 0.01), 3)
    rows = []
    for V in Vg:
        row = [V]
        for k in structs:
            Vk, Jk = np.array(jv[k]["V"]), np.array(jv[k]["J"])
            row.append(float(np.interp(V, Vk, Jk, right=np.nan)) if len(Vk) else np.nan)
        for k in structs:
            Vk, Jk = np.array(jv[k]["V"]), np.array(jv[k]["J"])
            row.append(float(V * np.interp(V, Vk, Jk, right=np.nan)) if len(Vk) else np.nan)
        rows.append(row)
    save_csv("Step5_6_JV_PV_curves.csv", ["V"] + [f"J_{k}" for k in structs] + [f"P_{k}" for k in structs], rows)
    print("step5-6 done", time.time() - t0, flush=True)

    # ---------------- Step 7: EQE
    eq = pmap(eqe_for, list(structs.values()))
    eqd = dict(zip(structs.keys(), eq))
    lam = eq[0]["lam"]
    save_csv("Step7_EQE.csv", ["lambda_nm"] + [f"EQE_{k}" for k in structs] + [f"Jint_{k}" for k in structs],
             [[lam[i]] + [eqd[k]["qe"][i] for k in structs] + [eqd[k]["Jint"][i] for k in structs]
              for i in range(len(lam))])
    print("step7 done", time.time() - t0, flush=True)

    # ---------------- Bands, field, recombination
    prof = {}
    for k, kw in structs.items():
        prof[k] = {"eq": profiles_for(kw, light=False), "sc": profiles_for(kw, light=True)}
        p = prof[k]["eq"]; s = prof[k]["sc"]
        save_csv(f"Bands_{k.replace(' ', '')}.csv",
                 ["x_nm", "layer", "Ec_eq", "Ev_eq", "EF_eq", "E_field_eq_Vcm",
                  "Ec_sc", "Ev_sc", "Fn_sc", "Fp_sc", "n_sc", "p_sc", "G_sc", "R_sc"],
                 [[p["x_nm"][i], p["layers"][p["layer"][i]], p["Ec"][i], p["Ev"][i], p["Fn"][i],
                   p["E_Vcm"][i], s["Ec"][i], s["Ev"][i], s["Fn"][i], s["Fp"][i],
                   s["n"][i], s["p"][i], s["G"][i], s["R"][i]] for i in range(len(p["x_nm"]))])
    print("profiles done", time.time() - t0, flush=True)

    # ---------------- C-V / Mott-Schottky
    cvs = pmap(cv_for, list(structs.values()))
    cvd = dict(zip(structs.keys(), cvs))
    Vc = cvs[0]["V"]
    save_csv("CV_MottSchottky_1kHz.csv", ["V"] + [f"C_{k}_nFcm2" for k in structs] + [f"invC2_{k}" for k in structs],
             [[Vc[i]] + [cvd[k]["C"][i] * 1e9 for k in structs] + [cvd[k]["invC2"][i] for k in structs]
              for i in range(len(Vc))])
    save_csv("MottSchottky_fit.csv", ["structure", "Vbi_V", "N_cm3", "slope"],
             [[k, cvd[k]["Vbi"], cvd[k]["N"], cvd[k]["slope"]] for k in structs])
    print("cv done", time.time() - t0, flush=True)

    # ---------------- Impedance (Nyquist)
    zs = pmap(impedance_for, [structs[k] for k in structs if k != "V2O5"])
    zd = dict(zip([k for k in structs if k != "V2O5"], zs))
    f = zs[0]["f"]
    save_csv("Impedance_Nyquist_Voc.csv", ["f_Hz"] + sum([[f"Zre_{k}", f"Zim_{k}"] for k in zd], []),
             [[f[i]] + sum([[zd[k]["Zre"][i], zd[k]["Zim"][i]] for k in zd], []) for i in range(len(f))])
    print("impedance done", time.time() - t0, flush=True)

    # ---------------- Temperature
    Ts = [280, 300, 320, 340, 360]
    items = [(k, T, dict(kw, T=T)) for k, kw in structs.items() for T in Ts]
    res = pmap(run_jv, [it[2] for it in items])
    save_csv("Temperature.csv", ["structure", "T_K", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[k, T, r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (k, T, _), r in zip(items, res)])
    print("temperature done", time.time() - t0, flush=True)

    # ---------------- Interface defect density
    Nits = [1.1e5, 1e9, 1e10, 1e11, 1e12, 1e13]
    items = [(k, N, dict(kw, Nit=N)) for k, kw in structs.items() if k != "V2O5" for N in Nits]
    res = pmap(run_jv, [it[2] for it in items])
    save_csv("Interface_Nit.csv", ["structure", "Nit_cm2", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[k, N, r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (k, N, _), r in zip(items, res)])
    print("Nit done", time.time() - t0, flush=True)

    # ---------------- Absorber bulk defect density
    Nts = [1e14, 1e15, 1e16, 1e17, 1e18]
    items = [(k, N, dict(kw, Nt_abs=N)) for k, kw in structs.items() if k in ("No buffer", "NiOx") for N in Nts]
    res = pmap(run_jv, [it[2] for it in items])
    save_csv("Absorber_Nt.csv", ["structure", "Nt_cm3", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[k, N, r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (k, N, _), r in zip(items, res)])
    print("Nt done", time.time() - t0, flush=True)

    # ---------------- Valence-band offset of the V2O5 buffer
    # VBO = Ev(MAGeI3) - Ev(buffer) = (chi_b + Eg_b) - (chi_abs + Eg_abs)
    chis = [1.20, 1.40, 1.60, 1.70, 1.80, 1.90, 2.00, 2.10, 2.30]
    items = []
    for c in chis:
        kw = dict(base); kw.update(buffer="V2O5", d_buf=10, buffer_overrides=dict(chi=c))
        items.append((c, kw))
    res = pmap(run_jv, [it[1] for it in items])
    save_csv("V2O5_band_offset.csv", ["chi_V2O5_eV", "VBO_eV", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[c, (c + 3.99) - (3.7 + 1.9), r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (c, _), r in zip(items, res)])
    print("VBO done", time.time() - t0, flush=True)

    summary["optimum"] = {k: {kk: v[kk] for kk in ("Voc", "Jsc", "FF", "PCE")} for k, v in jv.items()}
    summary["eqe_Jsc"] = {k: dict(Jint=eqd[k]["Jint"][-1], Jsc=eqd[k]["Jsc"]) for k in eqd}
    summary["mott_schottky"] = {k: dict(Vbi=cvd[k]["Vbi"], N=cvd[k]["N"]) for k in cvd}
    summary["runtime_min"] = (time.time() - t0) / 60
    with open(os.path.join(RES, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2, default=float)
    print("ALL DONE in %.1f min" % summary["runtime_min"], flush=True)


def _dark(kw):
    sim = Simulation(P.build_device(**kw))
    V, J, X = sim.jv(dV=0.02, Vmax=1.6, light=False)
    return dict(V=V.tolist(), J=(-J).tolist())


def extras(base, structs):
    t0 = time.time()
    # back-contact work function
    wfs = [4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.6]
    items = [(k, wf, dict(structs[k], back_wf=wf)) for k in ("No buffer", "WOx") for wf in wfs]
    res = pmap(run_jv, [it[2] for it in items])
    save_csv("Back_contact_workfunction.csv", ["structure", "WF_eV", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[k, wf, r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (k, wf, _), r in zip(items, res)])
    print("WF done", time.time() - t0, flush=True)
    # light intensity
    suns = [0.01, 0.03, 0.1, 0.3, 1.0, 2.0]
    items = [(k, s, dict(structs[k], suns=s)) for k in ("No buffer", "WOx", "NiOx") for s in suns]
    res = pmap(run_jv, [it[2] for it in items])
    save_csv("Light_intensity.csv", ["structure", "suns", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"],
             [[k, s, r["Voc"], r["Jsc"], r["FF"], r["PCE"]] for (k, s, _), r in zip(items, res)])
    print("intensity done", time.time() - t0, flush=True)
    # dark J-V
    ks = ["No buffer", "WOx", "NiOx"]
    dk = pmap(_dark, [structs[k] for k in ks])
    Vd = dk[0]["V"]
    save_csv("Dark_JV.csv", ["V"] + [f"Jdark_{k}_mAcm2" for k in ks],
             [[Vd[i]] + [dk[j]["J"][i] if i < len(dk[j]["J"]) else float("nan") for j in range(len(ks))] for i in range(len(Vd))])
    print("dark done", time.time() - t0, flush=True)


def load_structs():
    s = json.load(open(os.path.join(RES, "summary.json")))
    base = dict(d_abs=s["d_abs_opt"], d_etl=s["d_etl_opt"], d_htl=s["d_htl_opt"])
    structs = {"No buffer": dict(base)}
    for b in BUFS:
        kw = dict(base); kw.update(buffer=b, d_buf=s["d_buf_opt"][b]); structs[b] = kw
    return base, structs


if __name__ == "__main__":
    if "--extra-only" in sys.argv:
        extras(*load_structs())
    else:
        main()
        extras(*load_structs())

