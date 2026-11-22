"""Convert the checked SCAPS outputs (stage 1 + full run) into CSV files for Chapter 4 (results_v2/).
Rules: a run counts only if its 'Single shot simulation #' equals its position in the script (otherwise SCAPS
saved the previous result again = failed run).  Voc above the absorber gap (1.9 V) is an extrapolation artefact:
Voc and FF are then dropped, PCE (maximum power inside the computed range) is kept."""
import os, re, csv, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "results_v2"); os.makedirs(OUT, exist_ok=True)
R1 = os.path.join(HERE, "results_stage1"); RF = os.path.join(HERE, "results_final")
NUMRE = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"

def order(script):
    return [l.split()[-1] for l in open(os.path.join(HERE, "def", script)).read().splitlines() if l.startswith("save results.")]

def block(path):
    t = open(path, encoding="latin-1").read()
    return t.split("Single shot simulation #")[-1]

def val(b, k):
    m = re.search(rf"^{k} =\s*({NUMRE})", b, re.M); return float(m.group(1)) if m else float("nan")

def table(b, head):
    rows, on = [], False
    for ln in b.splitlines():
        s = ln.strip()
        if s.startswith(head): on = True; continue
        if on:
            if not s:
                if rows: break
                continue
            try: rows.append([float(x) for x in s.split()])
            except ValueError:
                if rows: break
    return np.array(rows) if rows else None

def load(folder, script):
    res = {}
    for i, fn in enumerate(order(script), 1):
        b = block(os.path.join(folder, fn)); sim = int(b.split()[0]); okrun = sim == i
        tag = fn.split("_", 2)[2].rsplit(".", 1)[0]
        d = dict(ok=okrun, file=fn, b=b)
        if fn.endswith(".iv"):
            d.update(Voc=val(b, "Voc"), Jsc=val(b, "Jsc"), FF=val(b, "FF"), PCE=val(b, "eta"),
                     extrap=bool(re.search(r"^Voc =.*extrapolated", b, re.M)))
            if not okrun: d.update(Voc=np.nan, Jsc=np.nan, FF=np.nan, PCE=np.nan)
            elif d["Voc"] != d["Voc"]: d.update(PCE=np.nan, Jsc=np.nan, FF=np.nan, ok=False)  # stopped before Voc
            elif d["Voc"] > 1.9: d.update(Voc=np.nan, FF=np.nan, artefact=True)
        res[tag] = d
    return res

S1 = load(R1, "MAGeI3_RERUN_stage1.script"); F = load(RF, "MAGeI3_RERUN_FULL.script")

def w(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        c = csv.writer(fh); c.writerow(header)
        for r in rows: c.writerow([f"{x:.6g}" if isinstance(x, (float, np.floating)) else x for x in r])

P = lambda d: [d["Voc"], d["Jsc"], d["FF"], d["PCE"]]
H = ["Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"]
# step 1 (TiO2 100, Spiro 100)
rows = [[ab] + P(S1[f"S1_abs{ab:03d}"]) for ab in range(100, 900, 100)]
rows += [[ab] + P(F[f"A1_abs{ab}"]) for ab in (250, 350)]
w("Step1_absorber.csv", ["d_abs_nm"] + H, sorted(rows))
w("Step2_TiO2.csv", ["d_TiO2_nm"] + H, [[d] + P(F[f"A2_etl{d:03d}"]) for d in (1, 5, 10, 20, 30, 50, 100, 200, 400)])
w("Step3_Spiro.csv", ["d_Spiro_nm"] + H, [[d] + P(F[f"A3_htl{d:03d}"]) for d in (1, 10, 25, 50, 100, 200)])
rows = [["None", 0] + P(F["B56_none"])]
for b in ("WOx", "NiOx", "V2O5"):
    for d in (10, 20, 30, 40, 50): rows.append([b, d] + P(F[f"B4_{b}_{d:02d}"]))
w("Step4_buffer.csv", ["buffer", "d_nm"] + H, rows)
# steps 5-6 + J-V curves + recombination components
opt = [["None", 0] + P(F["B56_none"])]
curves, recs = [], []
for tag, name, d in (("B56_none", "None", 0), ("B56_NiOx_10", "NiOx", 10), ("B56_NiOx_50", "NiOx", 50),
                     ("B56_V2O5_10", "V2O5", 10), ("B56_V2O5_50", "V2O5", 50), ("B56_WOx_10", "WOx", 10)):
    r = F[tag]
    if tag != "B56_none": opt.append([name, d] + P(r))
    if not r["ok"]: continue
    t = table(r["b"], "v(V)")
    for row in t: curves.append([name, d, row[0], -row[1], -row[0] * row[1]])
    for V in (0.0, 1.0):
        k = np.argmin(abs(t[:, 0] - V)); row = t[k]
        recs.append([name, d, row[0], row[3], row[4], row[5], row[6], row[7]])
w("Step56_structures.csv", ["buffer", "d_nm"] + H, opt)
w("Step56_JV.csv", ["buffer", "d_nm", "V", "J_mAcm2", "P_mWcm2"], curves)
w("Recombination.csv", ["buffer", "d_nm", "V", "Jgen", "Jbulk", "Jifr", "Jminor_back", "Jminor_front"], recs)
# step 7 QE
qe = []
for s in ("none", "NiOx", "WOx"):
    r = F[f"B7_QE_{s}"]
    if not r["ok"]: continue
    t = table(r["b"], "lambda(nm)")
    for row in t: qe.append([s, row[0], row[1]])
w("Step7_QE.csv", ["structure", "lambda_nm", "QE_pct"], qe)
# temperature, Nt, chi sweeps, HTL doping, NiOx NA/eps
w("Temperature.csv", ["structure", "T_K"] + H, [[s, T] + P(F[f"BT_{s}_{T}"]) for s in ("none", "WOx", "NiOx") for T in (280, 300, 320, 340, 360)])
w("Absorber_Nt.csv", ["structure", "Nt_cm3"] + H, [[s, 10.0 ** e] + P(F[f"BNt_{s}_1E{e}"]) for s in ("none", "NiOx") for e in (14, 15, 16, 17)])
w("WOx_chi.csv", ["chi_eV", "VBO_eV"] + H, [[c, round(c - 2.73, 2)] + P(F[f"BWchi{int(round(c*100)):03d}"]) for c in (4.55, 4.0, 3.5, 3.0, 2.73, 2.53, 2.33, 2.13)])
w("V2O5_chi.csv", ["chi_eV", "VBO_eV"] + H, [[c, round(c - 1.89, 2)] + P(F[f"BVchi{int(round(c*100)):03d}"]) for c in (1.2, 1.4, 1.6, 1.8, 1.89, 2.0, 2.1, 2.3)])
w("HTL_doping.csv", ["structure", "NA_cm3"] + H, [[s, 10.0 ** e] + P(F[f"BHTLna_{s}_1E{e}"]) for s in ("none", "NiOx") for e in (16, 17, 18, 19)])
w("NiOx_doping.csv", ["NA_cm3"] + H, [[10.0 ** e] + P(F[f"BNiNA_1E{e}"]) for e in (14, 16, 17, 18, 19)])
w("NiOx_eps.csv", ["eps"] + H, [[e] + P(F[f"BNiEPS_{e}"]) for e in ("3", "6", "10.7", "24")])
# C-V
cv = []
for s in ("none", "WOx", "NiOx"):
    r = F[f"BCV_{s}"]
    t = table(r["b"], "v(V)")
    if t is None or not r["ok"]: print("CV missing", s); continue
    for row in t: cv.append([s, row[0], row[1], row[2] if t.shape[1] > 2 else np.nan])
w("CV.csv", ["structure", "V", "C_nFcm2", "G"], cv)
flags = [(k, d["ok"], d.get("artefact", False)) for k, d in F.items()]
w("run_status.csv", ["run", "converged", "Voc_artefact"], flags)
print("written to", os.path.abspath(OUT))
