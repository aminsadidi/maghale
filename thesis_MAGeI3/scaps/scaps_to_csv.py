"""scaps_to_csv.py - convert SCAPS-1D script outputs (MG_*.iv/.qe/.cv/.eb)
into the CSV tables used by make_figures.py / make_excel.py / make_chapter4.py.

usage: python scaps_to_csv.py <folder_with_MG_files> <output_results_folder>
The parser is tolerant: it reads the solar-cell parameters (Voc, Jsc, FF, eta)
from the file header when present and the numeric data table that follows.
"""
import glob
import os
import re
import sys

import numpy as np

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"


def read_text(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


def numeric_table(text, min_cols=2):
    """Return (header_line, ndarray) of the longest block of numeric rows."""
    lines = text.replace("\r", "").split("\n")
    best, cur, cur_head, best_head = [], [], None, None
    prev = ""
    for ln in lines:
        parts = ln.replace(",", " ").split()
        ok = len(parts) >= min_cols and all(re.fullmatch(NUM, p) for p in parts)
        if ok:
            if not cur:
                cur_head = prev
            cur.append([float(p) for p in parts])
        else:
            if len(cur) > len(best):
                best, best_head = cur, cur_head
            cur = []
            if ln.strip():
                prev = ln
    if len(cur) > len(best):
        best, best_head = cur, cur_head
    if not best:
        return None, None
    n = min(len(r) for r in best)
    return best_head, np.array([r[:n] for r in best])


def iv_params(path):
    t = read_text(path)
    out = {}
    for key, pat in (("Voc", r"Voc\s*=\s*(" + NUM + r")"), ("Jsc", r"Jsc\s*=\s*(" + NUM + r")"),
                     ("FF", r"FF\s*=\s*(" + NUM + r")"), ("PCE", r"eta\s*=\s*(" + NUM + r")")):
        m = re.search(pat, t)
        out[key] = float(m.group(1)) if m else float("nan")
    head, tab = numeric_table(t)
    V = J = None
    if tab is not None and tab.shape[1] >= 2:
        V, J = tab[:, 0], tab[:, 1]
        # SCAPS: consumer convention, J<0 under light -> make photocurrent positive
        if np.nanmean(J[: max(2, len(J) // 4)]) < 0:
            J = -J
        if out["Voc"] != out["Voc"] or out["Jsc"] != out["Jsc"]:
            out.update(params_from_curve(V, J))
    if out.get("Jsc") == out.get("Jsc"):
        out["Jsc"] = abs(out["Jsc"])
    return out, V, J


def params_from_curve(V, J):
    Jsc = float(np.interp(0, V, J))
    idx = np.where(J <= 0)[0]
    if len(idx) == 0 or idx[0] == 0:
        Vf = np.linspace(V[0], V[-1], 3000); P = Vf * np.interp(Vf, V, J)
        return dict(Voc=float("nan"), Jsc=Jsc, FF=float("nan"), PCE=float(max(P.max(), 0)))
    i = idx[0]
    Voc = float(V[i - 1] + (V[i] - V[i - 1]) * J[i - 1] / (J[i - 1] - J[i]))
    Vf = np.linspace(0, Voc, 3000); P = Vf * np.interp(Vf, V, J)
    return dict(Voc=Voc, Jsc=Jsc, FF=100 * P.max() / (Voc * Jsc), PCE=float(P.max()))


def w(path, header, rows):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(",".join(header) + "\n")
        for r in rows:
            fh.write(",".join(f"{x:.6g}" if isinstance(x, (float, np.floating)) else str(x) for x in r) + "\n")


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    files = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(src, "**", "MG_*"), recursive=True)}
    print(len(files), "SCAPS output files")
    P = {k: iv_params(p) for k, p in files.items() if p.lower().endswith(".iv")}
    par = lambda k: P[k][0] if k in P else dict(Voc=np.nan, Jsc=np.nan, FF=np.nan, PCE=np.nan)
    row = lambda k: [par(k)["Voc"], par(k)["Jsc"], par(k)["FF"], par(k)["PCE"]]
    H = ["Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"]
    w(os.path.join(dst, "Step1_MAGeI3_thickness.csv"), ["d_MAGeI3_nm"] + H,
      [[d] + row(f"MG_S1_abs{d:03d}") for d in range(100, 900, 100)])
    w(os.path.join(dst, "Step2_TiO2_thickness.csv"), ["d_TiO2_nm"] + H,
      [[d] + row(f"MG_S2_etl{d:03d}") for d in (1, 50, 100, 150, 200, 250, 300, 350, 400)])
    w(os.path.join(dst, "Step3_Spiro_thickness.csv"), ["d_Spiro_nm"] + H,
      [[d] + row(f"MG_S3_htl{d:03d}") for d in (1, 50, 100, 150, 200)])
    rows = []
    for b in ("WOx", "NiOx", "V2O5"):
        rows.append([b, 0] + row("MG_S56_none"))
        rows += [[b, d] + row(f"MG_S4_{b}_{d:02d}") for d in (10, 20, 30, 40, 50)]
    w(os.path.join(dst, "Step4_buffer_thickness.csv"), ["buffer", "d_buffer_nm"] + H, rows)
    names = {"none": "No buffer", "WOx": "WOx", "NiOx": "NiOx", "V2O5": "V2O5"}
    rows = []
    for s, n in names.items():
        p = par(f"MG_S56_{s}")
        rows.append([n] + row(f"MG_S56_{s}") + [np.nan, np.nan])
    w(os.path.join(dst, "Step5_6_optimum_structures.csv"), ["structure"] + H + ["Vmp_V", "Jmp_mAcm2"], rows)
    Vg = np.round(np.arange(0, 1.6001, 0.01), 3)
    cols = []
    for s in names:
        k = f"MG_S56_{s}"
        V, J = (P[k][1], P[k][2]) if k in P and P[k][1] is not None else (None, None)
        cols.append(np.interp(Vg, V, J, right=np.nan) if V is not None else np.full(len(Vg), np.nan))
    w(os.path.join(dst, "Step5_6_JV_PV_curves.csv"), ["V"] + [f"J_{n}" for n in names.values()] + [f"P_{n}" for n in names.values()],
      [[Vg[i]] + [c[i] for c in cols] + [Vg[i] * c[i] for c in cols] for i in range(len(Vg))])
    w(os.path.join(dst, "Temperature.csv"), ["structure", "T_K"] + H,
      [[n, T] + row(f"MG_T_{s}_{T}") for s, n in names.items() for T in (280, 300, 320, 340, 360)])
    w(os.path.join(dst, "Absorber_Nt.csv"), ["structure", "Nt_cm3"] + H,
      [[names[s], float(f"1e{e}")] + row(f"MG_Nt_{s}_1E{e}") for s in ("none", "NiOx") for e in (14, 15, 16, 17, 18)])
    w(os.path.join(dst, "V2O5_band_offset.csv"), ["chi_V2O5_eV", "VBO_eV"] + H,
      [[c, round(c + 3.99 - 5.6, 2)] + row(f"MG_VBO_chi{int(round(c * 100)):03d}")
       for c in (1.2, 1.4, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.3)])
    # QE
    qe = {}
    for s, n in names.items():
        k = f"MG_QE_{s}"
        if k in files:
            head, tab = numeric_table(read_text(files[k]))
            if tab is not None:
                qe[n] = tab
    if qe:
        lam = np.arange(300, 901, 10.0)
        from_tab = {n: np.interp(lam, t[:, 0], t[:, -1] if t[:, -1].max() > 1.5 else 100 * t[:, -1]) for n, t in qe.items()}
        w(os.path.join(dst, "Step7_EQE.csv"), ["lambda_nm"] + [f"EQE_{n}" for n in from_tab], [[lam[i]] + [from_tab[n][i] for n in from_tab] for i in range(len(lam))])
    print("converted ->", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
