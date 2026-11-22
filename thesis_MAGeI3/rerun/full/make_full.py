"""
ONE script for the whole remaining re-simulation (run once):
  part A  : steps 1-3 refinement around the new optimum (absorber 300 nm)
  part B  : steps 4-7 and all supporting analyses at absorber 300 nm, TiO2 10 nm, Spiro-OMeTAD 50 nm
            (10 nm = thinnest practical continuous TiO2 film; Spiro 50 nm best in every stage-1 case)
Outputs: MG_F_*.iv / .qe / .cv
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rerun_params as R
ABS, ETL, HTL, BUF = 0.30, 0.010, 0.050, 0.010
DEF = {"none": "10_RERUN_noBuffer.def", "WOx": "11_RERUN_WOx.def", "NiOx": "12_RERUN_NiOx.def", "V2O5": "13_RERUN_V2O5.def"}
for s, fn in DEF.items():
    kw = dict(d_abs=600, d_etl=100, d_htl=100, Nit=R.NIT)
    if s != "none": kw.update(buffer=s, d_buf=10)
    with open(os.path.join(HERE, "def", fn), "w", newline="", encoding="ascii") as fh:
        fh.write(R.M.make_def(f"RERUN (sourced parameters): {s}", **kw))
L = ["// MAGeI3 thesis - complete re-simulation (part A + part B) with sourced parameters; outputs MG_F_*",
     "set errorhandling.overwritefile", "clear all"]
a = L.append
n = 0
def iv(inc=0.02, T=300):
    L.extend(["clear actions", "action light", f"action workingpoint.temperature {T}", "action iv.doiv", "action iv.startv 0",
              "action iv.stopv 2.0", f"action iv.increment {inc}", "action iv.stopaftervoc 1"])
def load(s, d_abs=ABS, d_etl=ETL, d_htl=HTL, d_buf=BUF):
    a(f"load definitionfile {DEF[s]}")
    if s == "none":
        L.extend([f"set layer1.thickness {d_htl}", f"set layer2.thickness {d_abs}", f"set layer3.thickness {d_etl}"])
    else:
        L.extend([f"set layer1.thickness {d_htl}", f"set layer2.thickness {d_buf}", f"set layer3.thickness {d_abs}",
                  f"set layer4.thickness {d_etl}"])
def run(tag, kind="iv"):
    global n
    L.extend(["calculate singleshot", f"save results.{kind} MG_F_{tag}.{kind}"]); n += 1
# ---------------- PART A
a("// ===== A1: absorber 250, 350 nm (TiO2 100, Spiro 100)"); iv()
for d in (250, 350): load("none", d_abs=d / 1000, d_etl=0.1, d_htl=0.1); run(f"A1_abs{d}")
a("// ===== A2: TiO2 thickness at absorber 300 nm (Spiro 100)")
for d in (1, 5, 10, 20, 30, 50, 100, 200, 400): load("none", d_etl=d / 1000, d_htl=0.1); run(f"A2_etl{d:03d}")
a("// ===== A3: Spiro thickness at absorber 300 nm, TiO2 10 nm")
for d in (1, 10, 25, 50, 100, 200): load("none", d_htl=d / 1000); run(f"A3_htl{d:03d}")
# ---------------- PART B
a("// ===== B4: buffer thickness 10..50 nm")
for b in ("WOx", "NiOx", "V2O5"):
    for d in (10, 20, 30, 40, 50): load(b, d_buf=d / 1000); run(f"B4_{b}_{d:02d}")
a("// ===== B56: J-V fine (0.01 V) for no buffer and each buffer at 10 and 50 nm"); iv(0.01)
load("none"); run("B56_none")
for b in ("WOx", "NiOx", "V2O5"):
    for d in (10, 50): load(b, d_buf=d / 1000); run(f"B56_{b}_{d:02d}")
a("// ===== B7: IPCE")
for s in ("none", "WOx", "NiOx"):
    L.extend(["clear actions", "action light", "action workingpoint.temperature 300", "action qe.doqe",
              "action qe.startlambda 300", "action qe.stoplambda 900", "action qe.increment 10"])
    load(s); run(f"B7_QE_{s}", "qe")
a("// ===== temperature 280-360 K")
for s in ("none", "WOx", "NiOx"):
    for T in (280, 300, 320, 340, 360): iv(T=T); load(s); run(f"BT_{s}_{T}")
iv()
a("// ===== absorber bulk defect density")
for s, layer in (("none", 2), ("NiOx", 3)):
    for e in (14, 15, 16, 17): load(s); a(f"set layer{layer}.defect1.ntotal 1E{e}"); run(f"BNt_{s}_1E{e}")
a("// ===== WOx electron affinity sweep (VBO = chi - 2.73 eV; MAGeI3 EV = -5.88 eV)")
for chi in (4.55, 4.0, 3.5, 3.0, 2.73, 2.53, 2.33, 2.13):
    load("WOx"); a(f"set layer2.chi {chi}"); run(f"BWchi{int(round(chi*100)):03d}")
a("// ===== V2O5 electron affinity sweep (VBO = chi - 1.89 eV)")
for chi in (1.2, 1.4, 1.6, 1.8, 1.89, 2.0, 2.1, 2.3):
    load("V2O5"); a(f"set layer2.chi {chi}"); run(f"BVchi{int(round(chi*100)):03d}")
a("// ===== Spiro acceptor density")
for s in ("none", "NiOx"):
    for e in (16, 17, 18, 19):
        load(s); a(f"set layer1.na 1E{e}"); run(f"BHTLna_{s}_1E{e}")
a("// ===== NiOx buffer acceptor density and permittivity")
for e in (14, 16, 17, 18, 19): load("NiOx"); a(f"set layer2.na 1E{e}"); run(f"BNiNA_1E{e}")
for eps in (3, 6, 10.7, 24): load("NiOx"); a(f"set layer2.epsilon {eps}"); run(f"BNiEPS_{eps}")
a("// ===== C-V, dark, 1 kHz")
for s in ("none", "WOx", "NiOx"):
    L.extend(["clear actions", "action dark", "action workingpoint.temperature 300", "action workingpoint.frequency 1000",
              "action cv.docv", "action cv.startv 0", "action cv.stopv 0.9", "action cv.increment 0.05"])
    load(s); run(f"BCV_{s}", "cv")
a("action workingpoint.frequency 1000000")
a("// ===== finished")
with open(os.path.join(HERE, "def", "MAGeI3_RERUN_FULL.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(L) + "\r\n")
print(n, "runs")
