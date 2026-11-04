"""make_figures.py - all Chapter-4 figures (300 dpi PNG) from ../results/*.csv"""
import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.environ.get("MG_RESULTS", os.path.join(HERE, "..", "results"))
FIG = os.environ.get("MG_FIGURES", os.path.join(HERE, "..", "figures"))
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif", "Times New Roman"],
    "font.size": 10, "axes.labelsize": 10.5, "axes.titlesize": 10.5,
    "legend.fontsize": 8.5, "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True, "axes.linewidth": 0.9,
    "lines.linewidth": 1.6, "lines.markersize": 5, "savefig.dpi": 300,
    "figure.dpi": 100,
})
COL = {"No buffer": "#222222", "WOx": "#1f77b4", "NiOx": "#2ca02c", "V2O5": "#d62728"}
MK = {"No buffer": "o", "WOx": "s", "NiOx": "^", "V2O5": "D"}
STRUCTS = ["No buffer", "WOx", "NiOx", "V2O5"]
LBL = {"No buffer": "No buffer", "WOx": r"WO$_x$", "NiOx": r"NiO$_x$", "V2O5": r"V$_2$O$_5$"}


def read(name):
    import csv
    with open(os.path.join(RES, name), encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head = rows[0]
    data = {h: [] for h in head}
    for r in rows[1:]:
        for h, v in zip(head, r):
            try:
                data[h].append(float(v))
            except ValueError:
                data[h].append(v)
    return data


def tag(ax, s):
    ax.text(0.03, 0.93, f"({s})", transform=ax.transAxes, fontweight="bold", fontsize=11)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name), dpi=300)
    plt.close(fig)


def four_panel(x, ys, xlabel, name, series=None, logx=False, xticks=None, note=None):
    """ys: dict param->(list or dict series->list)"""
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6))
    labels = [("Voc", r"$V_{oc}$ (V)"), ("Jsc", r"$J_{sc}$ (mA cm$^{-2}$)"),
              ("FF", "FF (%)"), ("PCE", "PCE (%)")]
    for ax, (k, yl), t in zip(axs.flat, labels, "abcd"):
        if series is None:
            ax.plot(x, ys[k], "o-", color="#1f3b73", mfc="white", mew=1.4)
        else:
            for s in series:
                xs, yv = ys[k][s]
                ax.plot(xs, yv, marker=MK.get(s, "o"), color=COL.get(s), label=LBL.get(s, s),
                        mfc="white", mew=1.3)
        ax.set_xlabel(xlabel); ax.set_ylabel(yl)
        if logx:
            ax.set_xscale("log")
        if xticks is not None:
            ax.set_xticks(xticks)
        tag(ax, t)
        ax.grid(alpha=0.25, lw=0.5)
    if series is not None:
        axs[0, 0].legend(frameon=False, loc="best")
    if note:
        fig.text(0.5, 0.005, note, ha="center", fontsize=8.5, color=COL["V2O5"])
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(os.path.join(FIG, name), dpi=300); plt.close(fig); return
    save(fig, name)


# --------------------------------------------------------------------------
def fig_structure():
    import params as P
    layers = [P.ITO(), P.TiO2(), P.MAGeI3(), P.NiOx(), P.WOx(), P.V2O5(), P.Spiro()]
    names = ["ITO", r"TiO$_2$", r"MAGeI$_3$", r"NiO$_x$", r"WO$_x$", r"V$_2$O$_5$", "Spiro-\nOMeTAD"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.9), gridspec_kw=dict(width_ratios=[1, 1.9]))
    stack = [("Au (back contact)", "#d4af37"), ("Spiro-OMeTAD (HTL)", "#c9a0dc"),
             (r"Buffer: V$_2$O$_5$ / WO$_x$ / NiO$_x$", "#9ad0ec"),
             (r"MAGeI$_3$ (absorber)", "#e8743b"), (r"TiO$_2$ (ETL)", "#f5e663"),
             ("ITO (front contact)", "#9e9e9e"), ("Glass", "#c8e6c9")]
    for i, (t, c) in enumerate(stack):
        a.add_patch(plt.Rectangle((0, i), 1, 0.9, color=c, ec="k", lw=0.7))
        a.text(0.5, i + 0.45, t, ha="center", va="center", fontsize=8.3)
    for xx in (0.2, 0.5, 0.8):
        a.annotate("", xy=(xx, -0.05), xytext=(xx, -0.9), arrowprops=dict(arrowstyle="-|>", color="#e0a800", lw=2))
    a.text(0.5, -1.25, "AM1.5G, 100 mW cm$^{-2}$", ha="center", fontsize=8.5)
    a.set_xlim(-0.05, 1.05); a.set_ylim(-1.5, 7.1); a.axis("off"); tag(a, "a")
    for i, (L, n) in enumerate(zip(layers, names)):
        Ec, Ev = -L.chi, -(L.chi + L.Eg)
        b.add_patch(plt.Rectangle((i, Ev), 0.8, Ec - Ev, fc="#e8eef8", ec="#1f3b73", lw=1))
        b.text(i + 0.4, Ec + 0.08, f"{Ec:.2f}", ha="center", fontsize=7.5)
        b.text(i + 0.4, Ev - 0.22, f"{Ev:.2f}", ha="center", fontsize=7.5)
        b.text(i + 0.4, (Ec + Ev) / 2, n, ha="center", va="center", fontsize=8, rotation=90)
    b.axhline(-5.1, color="#d4af37", ls="--", lw=1.2); b.text(6.95, -5.05, "Au  -5.10", fontsize=7.5, ha="right")
    b.axhline(-5.6, color="#e8743b", ls=":", lw=1.0)
    b.set_xlim(-0.3, 7.1); b.set_ylim(-8.2, -1.5); b.set_xticks([])
    b.set_ylabel("Energy relative to vacuum (eV)"); tag(b, "b")
    save(fig, "Fig4_01_structure_bands.png")


def fig_validation():
    v = np.loadtxt(os.path.join(RES, "Validation_V1_Shockley.csv"), delimiter=",", skiprows=1)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.2))
    a.semilogy(v[:, 0], v[:, 1], "o", mfc="white", color="#1f3b73", label="This solver")
    a.semilogy(v[:, 0], v[:, 4], "-", color="#d62728", label="Analytic (Shockley + SNS)")
    a.semilogy(v[:, 0], v[:, 2], "--", color="#888", lw=1, label="Diffusion term only")
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"Dark current density (A cm$^{-2}$)")
    a.legend(frameon=False); tag(a, "a")
    b.plot(v[:, 0], v[:, 5], "s-", color="#2ca02c", mfc="white")
    b.axhline(0, color="k", lw=0.6)
    b.set_xlabel("Voltage (V)"); b.set_ylabel("Deviation (%)"); tag(b, "b")
    save(fig, "Fig4_02_validation.png")


def fig_steps(s):
    d = read("Step1_MAGeI3_thickness.csv")
    four_panel(d["d_MAGeI3_nm"], dict(Voc=d["Voc_V"], Jsc=d["Jsc_mAcm2"], FF=d["FF_pct"], PCE=d["PCE_pct"]),
               r"MAGeI$_3$ thickness (nm)", "Fig4_03_step1_absorber.png")
    d = read("Step2_TiO2_thickness.csv")
    four_panel(d["d_TiO2_nm"], dict(Voc=d["Voc_V"], Jsc=d["Jsc_mAcm2"], FF=d["FF_pct"], PCE=d["PCE_pct"]),
               r"TiO$_2$ thickness (nm)", "Fig4_04_step2_ETL.png")
    d = read("Step3_Spiro_thickness.csv")
    four_panel(d["d_Spiro_nm"], dict(Voc=d["Voc_V"], Jsc=d["Jsc_mAcm2"], FF=d["FF_pct"], PCE=d["PCE_pct"]),
               "Spiro-OMeTAD thickness (nm)", "Fig4_05_step3_HTL.png")
    d = read("Step4_buffer_thickness.csv")
    ys = {k: {} for k in ("Voc", "Jsc", "FF", "PCE")}
    keys = dict(Voc="Voc_V", Jsc="Jsc_mAcm2", FF="FF_pct", PCE="PCE_pct")
    for b in ("WOx", "NiOx", "V2O5"):
        m = [i for i, x in enumerate(d["buffer"]) if x == b]
        for k, c in keys.items():
            ys[k][b] = ([d["d_buffer_nm"][i] for i in m], [d[c][i] for i in m])
    for k in ys:
        ys[k].pop("V2O5", None)
    four_panel(None, ys, "Buffer thickness (nm)", "Fig4_06_step4_buffer.png", series=["WOx", "NiOx"],
               note=os.environ.get("MG_NOTE", r"V$_2$O$_5$ (10-50 nm): PCE < 0.01 % (hole blocking)"))


def fig_jv(s):
    d = read("Step5_6_JV_PV_curves.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for k in STRUCTS:
        V = np.array(d["V"]); J = np.array(d[f"J_{k}"], float); P_ = np.array(d[f"P_{k}"], float)
        if not np.any(np.isfinite(J)):
            continue
        m = np.isfinite(J) & (J > -2)
        a.plot(V[m], J[m], color=COL[k], label=LBL[k])
        m2 = np.isfinite(P_) & (P_ > -1)
        b.plot(V[m2], P_[m2], color=COL[k], label=LBL[k])
    a.set_xlim(0, 1.6); a.set_ylim(0, 16); b.set_xlim(0, 1.6); b.set_ylim(0, None)
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"Current density (mA cm$^{-2}$)")
    b.set_xlabel("Voltage (V)"); b.set_ylabel(r"Power density (mW cm$^{-2}$)")
    a.legend(frameon=False, loc="lower left"); tag(a, "a"); tag(b, "b")
    save(fig, "Fig4_07_JV_PV.png")
    o = read("Step5_6_optimum_structures.csv")
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4))
    for ax, (c, yl), t in zip(axs.flat, [("Voc_V", r"$V_{oc}$ (V)"), ("Jsc_mAcm2", r"$J_{sc}$ (mA cm$^{-2}$)"),
                                         ("FF_pct", "FF (%)"), ("PCE_pct", "PCE (%)")], "abcd"):
        vals = [o[c][o["structure"].index(k)] for k in STRUCTS]
        vals = [0 if (not isinstance(v, float) or v != v) else v for v in vals]
        bars = ax.bar(range(4), vals, color=[COL[k] for k in STRUCTS], width=0.6)
        for bb, v in zip(bars, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
        ax.set_xticks(range(4)); ax.set_xticklabels([LBL[k] for k in STRUCTS]); ax.set_ylabel(yl)
        ax.set_ylim(0, max(vals) * 1.18 if max(vals) > 0 else 1); tag(ax, t)
    save(fig, "Fig4_08_comparison_bars.png")


def fig_eqe():
    d = read("Step7_EQE.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for k in [k for k in STRUCTS if f"EQE_{k}" in d]:
        a.plot(d["lambda_nm"], d[f"EQE_{k}"], color=COL[k], label=LBL[k], marker=MK[k], markevery=4, mfc="white")
        b.plot(d["lambda_nm"], d[f"Jint_{k}"], color=COL[k], label=LBL[k])
    a.set_xlabel("Wavelength (nm)"); a.set_ylabel("EQE / IPCE (%)"); a.set_ylim(0, 100); a.set_xlim(300, 900)
    b.set_xlabel("Wavelength (nm)"); b.set_ylabel(r"Integrated $J_{sc}$ (mA cm$^{-2}$)"); b.set_xlim(300, 900)
    a.legend(frameon=False, loc="upper right"); tag(a, "a"); tag(b, "b")
    save(fig, "Fig4_09_EQE.png")


def _bands(k):
    return read(f"Bands_{k.replace(' ', '')}.csv")


def _layer_shade(ax, d):
    lay = d["layer"]; x = d["x_nm"]
    cols = {"ITO": "#eeeeee", "TiO2": "#fff7c2", "MAGeI3": "#fde0cf", "Spiro-OMeTAD": "#efe3f7",
            "WOx": "#dbeefa", "NiOx": "#dcf3dc", "V2O5": "#f9d9d9"}
    start = 0
    for i in range(1, len(lay) + 1):
        if i == len(lay) or lay[i] != lay[start]:
            ax.axvspan(x[start], x[i - 1], color=cols.get(lay[start], "#fff"), lw=0, zorder=0)
            start = i


def fig_bands():
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.8))
    for ax, k, t in zip(axs.flat, STRUCTS, "abcd"):
        d = _bands(k)
        _layer_shade(ax, d)
        ax.plot(d["x_nm"], d["Ec_eq"], color="#1f3b73", label=r"$E_C$")
        ax.plot(d["x_nm"], d["Ev_eq"], color="#d62728", label=r"$E_V$")
        ax.plot(d["x_nm"], d["EF_eq"], "--", color="k", lw=1, label=r"$E_F$")
        ax.set_title(LBL[k]); ax.set_xlabel("Position (nm)"); ax.set_ylabel("Energy (eV)")
        tag(ax, t)
    axs[0, 0].legend(frameon=False, loc="lower left", fontsize=7.5)
    save(fig, "Fig4_10_bands_equilibrium.png")
    # zoom on absorber / buffer / HTL under short circuit
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.8))
    for ax, k, t in zip(axs.flat, STRUCTS, "abcd"):
        d = _bands(k)
        x = np.array(d["x_nm"]); m = x > (x.max() - 220)
        _layer_shade(ax, {kk: [v for v, mm in zip(d[kk], m) if mm] for kk in ("layer", "x_nm")})
        ax.plot(x[m], np.array(d["Ec_sc"])[m], color="#1f3b73", label=r"$E_C$")
        ax.plot(x[m], np.array(d["Ev_sc"])[m], color="#d62728", label=r"$E_V$")
        ax.plot(x[m], np.array(d["Fn_sc"])[m], "--", color="#1f3b73", lw=1, label=r"$E_{Fn}$")
        ax.plot(x[m], np.array(d["Fp_sc"])[m], "--", color="#d62728", lw=1, label=r"$E_{Fp}$")
        ax.set_title(LBL[k]); ax.set_xlabel("Position (nm)"); ax.set_ylabel("Energy (eV)")
        ax.set_ylim(-7.5, -0.5); tag(ax, t)
    axs[0, 0].legend(frameon=False, loc="lower left", fontsize=7.5, ncol=2)
    save(fig, "Fig4_11_bands_HTL_interface_sc.png")


def fig_field_rec():
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.8))
    a, b, c, e = axs.flat
    for k in STRUCTS:
        d = _bands(k)
        x = np.array(d["x_nm"])
        a.plot(x, np.abs(np.array(d["E_field_eq_Vcm"])) / 1e3, color=COL[k], label=LBL[k])
        b.semilogy(x, np.maximum(np.array(d["n_sc"]), 1e0), color=COL[k])
        b.semilogy(x, np.maximum(np.array(d["p_sc"]), 1e0), color=COL[k], ls="--")
        c.semilogy(x, np.maximum(np.array(d["R_sc"]), 1e10), color=COL[k], label=LBL[k])
    d = _bands("No buffer")
    e.semilogy(d["x_nm"], np.maximum(np.array(d["G_sc"]), 1e14), color="#e0a800")
    a.set_ylabel(r"|Electric field| (kV cm$^{-1}$)"); b.set_ylabel(r"$n$ (solid), $p$ (dashed) (cm$^{-3}$)")
    c.set_ylabel(r"SRH recombination (cm$^{-3}$ s$^{-1}$)"); e.set_ylabel(r"Generation (cm$^{-3}$ s$^{-1}$)")
    b.set_ylim(1e2, 1e20)
    for ax, t in zip(axs.flat, "abcd"):
        ax.set_xlabel("Position (nm)"); tag(ax, t)
    a.legend(frameon=False, fontsize=7.5)
    save(fig, "Fig4_12_field_carriers_recombination.png")


def fig_cv():
    d = read("CV_MottSchottky_1kHz.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for k in [k for k in STRUCTS if f"C_{k}_nFcm2" in d]:
        a.plot(d["V"], d[f"C_{k}_nFcm2"], color=COL[k], label=LBL[k], marker=MK[k], markevery=4, mfc="white")
        b.plot(d["V"], np.array(d[f"invC2_{k}"]) / 1e14, color=COL[k], label=LBL[k], marker=MK[k], markevery=4, mfc="white")
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"Capacitance (nF cm$^{-2}$)")
    b.set_xlabel("Voltage (V)"); b.set_ylabel(r"$1/C^2$ ($10^{14}$ cm$^4$ F$^{-2}$)")
    a.legend(frameon=False); tag(a, "a"); tag(b, "b")
    save(fig, "Fig4_13_CV_MottSchottky.png")


def fig_nyquist():
    d = read("Impedance_Nyquist_Voc.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for k in ("No buffer", "WOx", "NiOx"):
        if f"Zre_{k}" not in d:
            continue
        a.plot(d[f"Zre_{k}"], -np.array(d[f"Zim_{k}"]), color=COL[k], marker=MK[k], mfc="white", label=LBL[k], markevery=3)
        b.semilogx(d["f_Hz"], -np.array(d[f"Zim_{k}"]), color=COL[k], label=LBL[k])
    a.set_xlabel(r"Z' ($\Omega$ cm$^2$)"); a.set_ylabel(r"-Z'' ($\Omega$ cm$^2$)"); a.set_aspect("equal", adjustable="datalim")
    b.set_xlabel("Frequency (Hz)"); b.set_ylabel(r"-Z'' ($\Omega$ cm$^2$)")
    a.legend(frameon=False); tag(a, "a"); tag(b, "b")
    save(fig, "Fig4_14_Nyquist.png")


def fig_series(fname, xcol, xlabel, out, structs, logx=False):
    d = read(fname)
    ys = {k: {} for k in ("Voc", "Jsc", "FF", "PCE")}
    keys = dict(Voc="Voc_V", Jsc="Jsc_mAcm2", FF="FF_pct", PCE="PCE_pct")
    for s in structs:
        m = [i for i, x in enumerate(d["structure"]) if x == s]
        if not m:
            continue
        for k, c in keys.items():
            ys[k][s] = ([d[xcol][i] for i in m], [d[c][i] for i in m])
    four_panel(None, ys, xlabel, out, series=[s for s in structs if s in ys["PCE"]], logx=logx)


def fig_vbo():
    d = read("V2O5_band_offset.csv")
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4))
    for ax, (c, yl), t in zip(axs.flat, [("Voc_V", r"$V_{oc}$ (V)"), ("Jsc_mAcm2", r"$J_{sc}$ (mA cm$^{-2}$)"),
                                         ("FF_pct", "FF (%)"), ("PCE_pct", "PCE (%)")], "abcd"):
        ax.plot(d["VBO_eV"], d[c], "D-", color=COL["V2O5"], mfc="white")
        ax.axvline(0, color="k", lw=0.6, ls=":")
        ax.set_xlabel(r"Valence-band offset $E_V^{MAGeI_3}-E_V^{V_2O_5}$ (eV)"); ax.set_ylabel(yl); tag(ax, t)
    save(fig, "Fig4_18_V2O5_band_offset.png")


def fig_wf():
    fig_series("Back_contact_workfunction.csv", "WF_eV", "Back-contact work function (eV)",
               "Fig4_19_back_workfunction.png", ["No buffer", "WOx"])


def fig_dark_intensity():
    d = read("Dark_JV.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    Vt = 0.025852
    for k in ("No buffer", "WOx", "NiOx"):
        V = np.array(d["V"], float); J = np.array(d[f"Jdark_{k}_mAcm2"], float)
        m = np.isfinite(J) & (J > 0)
        a.semilogy(V[m], J[m], color=COL[k], label=LBL[k])
        lnJ = np.log(J[m]); Vm = V[m]
        nid = np.gradient(Vm, lnJ) / Vt
        b.plot(Vm, nid, color=COL[k], label=LBL[k])
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"Dark current density (mA cm$^{-2}$)"); a.set_ylim(1e-2, 1e2); a.set_xlim(1.25, 1.6)
    b.set_xlabel("Voltage (V)"); b.set_ylabel(r"Local ideality factor $n_{id}$"); b.set_ylim(0.5, 3); b.set_xlim(1.25, 1.58)
    a.legend(frameon=False); tag(a, "a"); tag(b, "b")
    save(fig, "Fig4_20_dark_JV_ideality.png")
    d = read("Light_intensity.csv")
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4))
    a, b, c, e = axs.flat
    for k in ("No buffer", "WOx", "NiOx"):
        m = [i for i, x in enumerate(d["structure"]) if x == k]
        S = np.array([d["suns"][i] for i in m]); Voc = np.array([d["Voc_V"][i] for i in m])
        Jsc = np.array([d["Jsc_mAcm2"][i] for i in m]); FF = np.array([d["FF_pct"][i] for i in m])
        PCE = np.array([d["PCE_pct"][i] for i in m])
        sl = np.polyfit(np.log(S), Voc, 1)[0] / Vt
        a.semilogx(S, Voc, marker=MK[k], color=COL[k], mfc="white", label=f"{LBL[k]}  (n = {sl:.2f})")
        b.loglog(S, Jsc, marker=MK[k], color=COL[k], mfc="white", label=LBL[k])
        c.semilogx(S, FF, marker=MK[k], color=COL[k], mfc="white")
        e.semilogx(S, PCE, marker=MK[k], color=COL[k], mfc="white")
    a.set_ylabel(r"$V_{oc}$ (V)"); b.set_ylabel(r"$J_{sc}$ (mA cm$^{-2}$)"); c.set_ylabel("FF (%)"); e.set_ylabel("PCE (%)")
    for ax, t in zip(axs.flat, "abcd"):
        ax.set_xlabel("Light intensity (suns)"); tag(ax, t)
    a.legend(frameon=False, fontsize=7.5, loc="lower right")
    save(fig, "Fig4_21_light_intensity.png")


def fig_recomb():
    d = read("Recombination_vs_V.csv")
    c = read("Recombination_components.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for k in ("No buffer", "WOx", "NiOx"):
        if f"Jbulk_{k}" in d:
            a.semilogy(d["V"], d[f"Jbulk_{k}"], color=COL[k], label=LBL[k])
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"Bulk SRH recombination current (mA cm$^{-2}$)")
    a.legend(frameon=False); tag(a, "a")
    ks = [k for k in ("No buffer", "WOx", "NiOx") if k in c["structure"]]
    idx = [i for i, (s, v) in enumerate(zip(c["structure"], c["V"])) if v == 0]
    x = np.arange(len(idx))
    bulk = [c["Jbulk_mAcm2"][i] for i in idx]; front = [c["Jright_contact_mAcm2"][i] for i in idx]
    other = [c["Jinterface_mAcm2"][i] + c["Jleft_contact_mAcm2"][i] for i in idx]
    b.bar(x, bulk, color=[COL[c["structure"][i]] for i in idx], width=0.55, label="bulk SRH (absorber)")
    b.bar(x, front, bottom=bulk, color="#bbbbbb", width=0.55, label="front contact (minority)")
    for xi, v in zip(x, bulk):
        b.text(xi, v / 2, f"{v:.2f}", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    b.set_xticks(x); b.set_xticklabels([LBL[c["structure"][i]] for i in idx])
    b.set_ylabel(r"Recombination loss at $V=0$ (mA cm$^{-2}$)"); b.legend(frameon=False, fontsize=7.5, loc="upper right")
    b.set_ylim(0, max(bulk) * 1.35); tag(b, "b")
    save(fig, "Fig4_10_recombination_components.png")


def fig_scaps_extra():
    if os.path.exists(os.path.join(RES, "HTL_doping.csv")):
        fig_series("HTL_doping.csv", "NA_cm3", r"Spiro-OMeTAD acceptor density $N_A$ (cm$^{-3}$)",
                   "Fig4_19_HTL_doping.png", ["No buffer", "WOx"], logx=True)
    if os.path.exists(os.path.join(RES, "Buffer_doping.csv")):
        fig_series("Buffer_doping.csv", "NA_cm3", r"WO$_x$ buffer acceptor density $N_A$ (cm$^{-3}$)",
                   "Fig4_20_buffer_doping.png", ["WOx"], logx=True)
    if os.path.exists(os.path.join(RES, "Buffer_permittivity.csv")):
        fig_series("Buffer_permittivity.csv", "eps", r"WO$_x$ buffer relative permittivity $\varepsilon_r$",
                   "Fig4_21_buffer_permittivity.png", ["WOx"])


def main():
    fig_structure()
    if os.path.exists(os.path.join(RES, "Validation_V1_Shockley.csv")):
        fig_validation()
    fig_steps(None)
    fig_jv(None)
    fig_eqe()
    for fn, need in ((fig_bands, "Bands_Nobuffer.csv"), (fig_field_rec, "Bands_Nobuffer.csv"),
                     (fig_recomb, "Recombination_components.csv"), (fig_cv, "CV_MottSchottky_1kHz.csv"),
                     (fig_nyquist, "Impedance_Nyquist_Voc.csv")):
        if os.path.exists(os.path.join(RES, need)):
            fn()
    fig_series("Temperature.csv", "T_K", "Temperature (K)", "Fig4_15_temperature.png", STRUCTS)
    if os.path.exists(os.path.join(RES, "Interface_Nit.csv")):
      fig_series("Interface_Nit.csv", "Nit_cm2", r"Interface defect density $N_{it}$ (cm$^{-2}$)",
               "Fig4_16_interface_Nit.png", ["No buffer", "WOx", "NiOx"], logx=True)
    fig_series("Absorber_Nt.csv", "Nt_cm3", r"MAGeI$_3$ defect density $N_t$ (cm$^{-3}$)",
               "Fig4_17_absorber_Nt.png", ["No buffer", "NiOx"], logx=True)
    fig_vbo()
    fig_scaps_extra()
    if os.path.exists(os.path.join(RES, 'Back_contact_workfunction.csv')):
        fig_wf()
    if os.path.exists(os.path.join(RES, 'Light_intensity.csv')) and os.path.exists(os.path.join(RES, 'Dark_JV.csv')):
        fig_dark_intensity()
    print("figures written to", os.path.abspath(FIG))


if __name__ == "__main__":
    main()
