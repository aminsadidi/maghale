"""Chapter-4 figures from results_v2 (SCAPS re-simulation with sourced parameters)."""
import os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["MG_RESULTS"] = os.path.join(HERE, "..", "results_v2")
os.environ["MG_FIGURES"] = os.path.join(HERE, "..", "figures_v2")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rerun", "full"))
import rerun_params as R  # noqa: F401  (overrides layer parameters)
import params as P
import numpy as np
import make_figures as M
from make_figures import plt, tag, save, four_panel, COL, MK
RES, FIG = os.environ["MG_RESULTS"], os.environ["MG_FIGURES"]
LB = {"None": "No buffer", "none": "No buffer", "NiOx": r"NiO$_x$", "V2O5": r"V$_2$O$_5$", "WOx": r"WO$_x$"}
C = {"None": COL["No buffer"], "none": COL["No buffer"], "NiOx": COL["NiOx"], "V2O5": COL["V2O5"], "WOx": COL["WOx"]}
Mk = {"None": "o", "none": "o", "NiOx": "^", "V2O5": "D", "WOx": "s"}

def rd(n):
    rows = list(csv.DictReader(open(os.path.join(RES, n), encoding="utf-8")))
    out = []
    for r in rows:
        o = {}
        for k, v in r.items():
            try: o[k] = float(v)
            except ValueError: o[k] = v
        out.append(o)
    return out
K = {"Voc": "Voc_V", "Jsc": "Jsc_mAcm2", "FF": "FF_pct", "PCE": "PCE_pct"}

def simple(name, xcol, xlabel, out, logx=False):
    d = rd(name); x = [r[xcol] for r in d]
    four_panel(x, {k: [r[v] for r in d] for k, v in K.items()}, xlabel, out, logx=logx)

def series(name, scol, xcol, xlabel, out, logx=False, keys=None):
    d = rd(name); keys = keys or list(dict.fromkeys(r[scol] for r in d))
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6))
    for ax, (k, yl), t in zip(axs.flat, [("Voc", r"$V_{oc}$ (V)"), ("Jsc", r"$J_{sc}$ (mA cm$^{-2}$)"),
                                          ("FF", "FF (%)"), ("PCE", "PCE (%)")], "abcd"):
        for s in keys:
            rr = [r for r in d if r[scol] == s and r[K[k]] == r[K[k]]]
            ax.plot([r[xcol] for r in rr], [r[K[k]] for r in rr], marker=Mk.get(s, "o"), color=C.get(s), label=LB.get(s, s), mfc="white", mew=1.3)
        ax.set_xlabel(xlabel); ax.set_ylabel(yl); ax.grid(alpha=.25, lw=.5); tag(ax, t)
        if logx: ax.set_xscale("log")
    axs[0, 0].legend(frameon=False); save(fig, out)

def fig_absorption():
    lam = np.linspace(300, 900, 601); E = 1239.84 / lam
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for L, c in ((P.ITO(), "#888"), (P.TiO2(), "#c9a400"), (P.MAGeI3(), "#e8743b"), (P.WOx(), COL["WOx"]),
                 (P.NiOx(), COL["NiOx"]), (P.V2O5(), COL["V2O5"]), (P.Spiro(), "#8e44ad")):
        a = 1e5 * np.sqrt(np.clip(E - L.Eg, 0, None)); m = a > 0
        ax.semilogy(lam[m], a[m], color=c, label=f"{L.name.replace('Spiro-OMeTAD','Spiro-OMeTAD')} (Eg = {L.Eg:.2f} eV)")
    ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel(r"Absorption coefficient $\alpha$ (cm$^{-1}$)")
    ax.set_ylim(1e3, 3e5); ax.set_xlim(300, 900); ax.legend(frameon=False, fontsize=7.5); ax.grid(alpha=.25, lw=.5)
    save(fig, "Fig4_00_absorption.png")

def fig_structure():
    layers = [P.ITO(), P.TiO2(), P.MAGeI3(), P.NiOx(), P.WOx(), P.V2O5(), P.Spiro()]
    names = ["ITO", r"TiO$_2$", r"MAGeI$_3$", r"NiO$_x$", r"WO$_x$", r"V$_2$O$_5$", "Spiro-\nOMeTAD"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.9), gridspec_kw=dict(width_ratios=[1, 1.9]))
    stack = [("Glass", "#c8e6c9"), ("ITO (front contact)", "#9e9e9e"), (r"TiO$_2$ (ETL, n-type)", "#f5e663"),
             (r"MAGeI$_3$ (absorber)", "#e8743b"), (r"Buffer: V$_2$O$_5$ / WO$_x$ / NiO$_x$", "#9ad0ec"),
             ("Spiro-OMeTAD (HTL, p-type)", "#c9a0dc"), ("Au (back contact)", "#d4af37")]
    for i, (t, c) in enumerate(stack):
        a.add_patch(plt.Rectangle((0, i), 1, 0.9, color=c, ec="k", lw=0.7)); a.text(0.5, i + 0.45, t, ha="center", va="center", fontsize=8.3)
    for xx in (0.2, 0.5, 0.8):
        a.annotate("", xy=(xx, -0.05), xytext=(xx, -0.9), arrowprops=dict(arrowstyle="-|>", color="#e0a800", lw=2))
    a.text(0.5, -1.25, "AM1.5G light, 100 mW cm$^{-2}$ (through glass/ITO)", ha="center", fontsize=8.0)
    a.text(1.08, 3.0, "n-i-p", rotation=90, va="center", fontsize=9, fontweight="bold")
    a.set_xlim(-0.05, 1.15); a.set_ylim(-1.5, 8.0); a.axis("off"); tag(a, "a")
    for i, (L, n) in enumerate(zip(layers, names)):
        Ec, Ev = -L.chi, -(L.chi + L.Eg)
        b.add_patch(plt.Rectangle((i, Ev), 0.8, Ec - Ev, fc="#e8eef8", ec="#1f3b73", lw=1))
        b.text(i + 0.4, Ec + 0.08, f"{Ec:.2f}", ha="center", fontsize=7.5); b.text(i + 0.4, Ev - 0.22, f"{Ev:.2f}", ha="center", fontsize=7.5)
        b.text(i + 0.4, (Ec + Ev) / 2, n, ha="center", va="center", fontsize=8, rotation=90)
    b.axhline(-5.1, color="#d4af37", ls="--", lw=1.2); b.text(6.95, -5.03, "Au  -5.10", fontsize=7.5, ha="right")
    b.axhline(-5.88, color="#e8743b", ls=":", lw=1.0)
    b.set_xlim(-0.3, 7.1); b.set_ylim(-8.2, -1.0); b.set_xticks([]); b.set_ylabel("Energy relative to vacuum (eV)"); tag(b, "b")
    save(fig, "Fig4_01_structure_bands.png")

def fig_buffer():
    d = rd("Step4_buffer.csv"); base = [r for r in d if r["buffer"] == "None"][0]
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.6))
    for ax, (k, yl), t in zip(axs.flat, [("Voc", r"$V_{oc}$ (V)"), ("Jsc", r"$J_{sc}$ (mA cm$^{-2}$)"), ("FF", "FF (%)"), ("PCE", "PCE (%)")], "abcd"):
        for b in ("NiOx", "V2O5"):
            rr = [base] + [r for r in d if r["buffer"] == b]
            ax.plot([r["d_nm"] for r in rr], [r[K[k]] for r in rr], marker=Mk[b], color=C[b], label=LB[b], mfc="white", mew=1.3)
        ax.axhline(base[K[k]], color="#222", ls="--", lw=0.9, label="No buffer")
        ax.set_xlabel("Buffer thickness (nm)"); ax.set_ylabel(yl); ax.grid(alpha=.25, lw=.5); tag(ax, t)
    axs[0, 0].legend(frameon=False, fontsize=8)
    fig.text(0.5, 0.005, r"WO$_x$ (parameters of Coatings 2023): no converged solution at any thickness", ha="center", fontsize=8.5, color=COL["WOx"])
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(FIG, "Fig4_07_step4_buffer.png"), dpi=300); plt.close(fig)

def fig_jv():
    d = rd("Step56_JV.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for s, dd in (("None", 0), ("NiOx", 10), ("V2O5", 10)):
        rr = [r for r in d if r["buffer"] == s and r["d_nm"] == dd and r["J_mAcm2"] > -2]
        lab = LB[s] + ("" if s == "None" else " (10 nm)")
        a.plot([r["V"] for r in rr], [r["J_mAcm2"] for r in rr], color=C[s], label=lab)
        b.plot([r["V"] for r in rr], [r["P_mWcm2"] for r in rr], color=C[s], label=lab)
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"$J$ (mA cm$^{-2}$)"); a.set_ylim(0, 15); a.set_xlim(0, 1.75)
    b.set_xlabel("Voltage (V)"); b.set_ylabel(r"$P$ (mW cm$^{-2}$)"); b.set_ylim(0, 14); b.set_xlim(0, 1.75)
    for ax, t in ((a, "a"), (b, "b")): ax.grid(alpha=.25, lw=.5); tag(ax, t); ax.legend(frameon=False, fontsize=8)
    save(fig, "Fig4_08_JV_PV.png")

def fig_bars():
    d = rd("Step56_structures.csv"); names = [("None", 0), ("NiOx", 10), ("V2O5", 10), ("WOx", 10)]
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4))
    for ax, (k, yl), t in zip(axs.flat, [("Voc", r"$V_{oc}$ (V)"), ("Jsc", r"$J_{sc}$ (mA cm$^{-2}$)"), ("FF", "FF (%)"), ("PCE", "PCE (%)")], "abcd"):
        for i, (s, dd) in enumerate(names):
            r = [x for x in d if x["buffer"] == s and x["d_nm"] == dd][0]; v = r[K[k]]
            if v == v:
                ax.bar(i, v, color=C[s], width=0.62); ax.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5)
            else:
                ax.text(i, 0.02 * ax.get_ylim()[1] + 0.01, "n.c.", ha="center", fontsize=8, color=C[s])
        ax.set_xticks(range(4)); ax.set_xticklabels([LB[s] for s, _ in names]); ax.set_ylabel(yl); tag(ax, t)
    save(fig, "Fig4_09_bars.png")

def fig_qe():
    d = rd("Step7_QE.csv"); fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for s in ("none", "NiOx"):
        rr = [r for r in d if r["structure"] == s]
        ax.plot([r["lambda_nm"] for r in rr], [r["QE_pct"] for r in rr], marker=Mk[s], ms=3.5, mfc="white", color=C[s], label=LB[s])
    ax.set_xlabel("Wavelength (nm)"); ax.set_ylabel("EQE (%)"); ax.set_xlim(300, 900); ax.set_ylim(0, 100)
    ax.grid(alpha=.25, lw=.5); ax.legend(frameon=False); save(fig, "Fig4_10_EQE.png")

def fig_rec():
    d = rd("Recombination.csv"); cases = [("None", 0), ("NiOx", 10), ("V2O5", 10)]
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.4))
    for ax, V, t in ((axs[0], 0.0, "a"), (axs[1], 1.0, "b")):
        x = np.arange(len(cases)); w = 0.25
        for j, (col, lab, c) in enumerate((("Jbulk", "Bulk SRH", "#555"), ("Jifr", "Interfaces", "#c0392b"), ("Jminor_front", "Front contact (minority)", "#95a5a6"))):
            vals = [[r for r in d if r["buffer"] == s and r["d_nm"] == dd and abs(r["V"] - V) < 1e-3][0][col] for s, dd in cases]
            ax.bar(x + (j - 1) * w, vals, w, color=c, label=lab)
        ax.set_xticks(x); ax.set_xticklabels([LB[s] for s, _ in cases]); ax.set_yscale("log"); ax.set_ylim(1e-3, 30)
        ax.set_ylabel(r"Recombination current (mA cm$^{-2}$)"); ax.set_title(f"V = {V:.1f} V", fontsize=9.5); tag(ax, t)
    axs[0].legend(frameon=False, fontsize=7.5); save(fig, "Fig4_11_recombination.png")

def fig_cv():
    d = rd("CV.csv"); fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for s in ("none", "NiOx"):
        rr = [r for r in d if r["structure"] == s]; V = np.array([r["V"] for r in rr]); Cc = np.array([r["C_nFcm2"] for r in rr])
        a.plot(V, Cc, marker=Mk[s], mfc="white", color=C[s], label=LB[s])
        b.plot(V, 1e-9 * 0 + 8.854e-14 * 10 / (Cc * 1e-9) * 1e7, marker=Mk[s], mfc="white", color=C[s], label=LB[s])
    a.set_xlabel("Voltage (V)"); a.set_ylabel(r"$C$ (nF cm$^{-2}$)"); b.set_xlabel("Voltage (V)")
    b.set_ylabel(r"$W = \varepsilon_0\varepsilon_r/C$ (nm)"); b.axhline(300, color="#e8743b", ls=":", lw=1); b.text(0.02, 305, "absorber thickness", fontsize=7.5)
    for ax, t in ((a, "a"), (b, "b")): ax.grid(alpha=.25, lw=.5); tag(ax, t); ax.legend(frameon=False, fontsize=8)
    save(fig, "Fig4_12_CV.png")

def fig_chi():
    v, wx = rd("V2O5_chi.csv"), rd("WOx_chi.csv")
    base = rd("Step56_structures.csv")[0]["PCE_pct"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    rr = [r for r in v if r["PCE_pct"] == r["PCE_pct"]]
    a.plot([r["VBO_eV"] for r in rr], [r["PCE_pct"] for r in rr], "D-", color=C["V2O5"], mfc="white", label=LB["V2O5"])
    rr = [r for r in wx if r["PCE_pct"] == r["PCE_pct"]]
    a.plot([r["VBO_eV"] for r in rr], [r["PCE_pct"] for r in rr], "s-", color=C["WOx"], mfc="white", label=LB["WOx"])
    a.axhline(base, color="#222", ls="--", lw=.9, label="No buffer"); a.axvline(0, color="#888", ls=":", lw=.8)
    a.set_xlabel(r"VBO = $E_V^{MAGeI_3}-E_V^{buffer}$ (eV)"); a.set_ylabel("PCE (%)"); a.legend(frameon=False, fontsize=8)
    rr = [r for r in v if r["FF_pct"] == r["FF_pct"]]
    b.plot([r["VBO_eV"] for r in rr], [r["FF_pct"] for r in rr], "D-", color=C["V2O5"], mfc="white", label="FF")
    rr2 = [r for r in v if r["Voc_V"] == r["Voc_V"]]
    b2 = b.twinx(); b2.plot([r["VBO_eV"] for r in rr2], [r["Voc_V"] for r in rr2], "o--", color="#555", mfc="white", label=r"$V_{oc}$")
    b.set_xlabel(r"VBO (eV), V$_2$O$_5$"); b.set_ylabel("FF (%)"); b2.set_ylabel(r"$V_{oc}$ (V)")
    for ax, t in ((a, "a"), (b, "b")): ax.grid(alpha=.25, lw=.5); tag(ax, t)
    save(fig, "Fig4_15_VBO.png")

if __name__ == "__main__":
    fig_absorption(); fig_structure()
    simple("Step1_absorber.csv", "d_abs_nm", r"MAGeI$_3$ thickness (nm)", "Fig4_04_step1_absorber.png")
    simple("Step2_TiO2.csv", "d_TiO2_nm", r"TiO$_2$ thickness (nm)", "Fig4_05_step2_TiO2.png", logx=True)
    simple("Step3_Spiro.csv", "d_Spiro_nm", "Spiro-OMeTAD thickness (nm)", "Fig4_06_step3_Spiro.png", logx=True)
    fig_buffer(); fig_jv(); fig_bars(); fig_qe(); fig_rec(); fig_cv()
    series("Temperature.csv", "structure", "T_K", "Temperature (K)", "Fig4_13_temperature.png", keys=["none", "NiOx"])
    series("Absorber_Nt.csv", "structure", "Nt_cm3", r"MAGeI$_3$ defect density $N_t$ (cm$^{-3}$)", "Fig4_14_absorber_Nt.png", logx=True)
    fig_chi()
    series("HTL_doping.csv", "structure", "NA_cm3", r"Spiro-OMeTAD acceptor density $N_A$ (cm$^{-3}$)", "Fig4_16_HTL_doping.png", logx=True)
    simple("NiOx_doping.csv", "NA_cm3", r"NiO$_x$ acceptor density $N_A$ (cm$^{-3}$)", "Fig4_17_NiOx_doping.png", logx=True)
    simple("NiOx_eps.csv", "eps", r"NiO$_x$ relative permittivity $\varepsilon_r$", "Fig4_18_NiOx_eps.png")
    print("ok", sorted(os.listdir(FIG)))
