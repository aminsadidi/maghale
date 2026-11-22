"""
WOx re-simulation with literature WO3 parameters.
Source: J.C. Zepeda Medina et al., Coatings 13 (2023) 1436, Table 1, doi:10.3390/coatings13081436
  Eg 3.15 eV, chi 4.55 eV, eps 10, Nc 4.2e18, Nv 9e18 cm-3, mu_n 20, mu_p 10 cm2/Vs,
  vth 1e7 cm/s, n-type (ND 1e13-1e19, optimum 1e19 cm-3), bulk defect density 1e12 cm-3 (donor).
  Defect level not given -> mid-gap (SCAPS default)  [ASSUMPTION, stated in the thesis]
All other layers, defects, interfaces and contacts: unchanged (thesis Chapter 3 tables).
Structure (back -> front): Spiro-OMeTAD(50) | WOx | MAGeI3(800) | TiO2(50) | ITO(200)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "sim")); sys.path.insert(0, os.path.join(ROOT, "scaps"))
import params as P
from dd1d import Layer, defect
import make_def as M

def WOx_lit(d=10):
    return Layer("WOx", d, Eg=3.15, chi=4.55, eps=10.0, Nc=4.2e18, Nv=9e18, mun=20.0, mup=10.0,
                 ND=1e19, NA=0.0, defects=[defect("donor", 1e12, 3.15 / 2)])
P.BUFFERS["WOx"] = WOx_lit
P.WOx = WOx_lit

DEF = "03b_WOx_Coatings2023.def"
out = os.path.join(HERE, "def"); os.makedirs(out, exist_ok=True)
with open(os.path.join(out, DEF), "w", newline="", encoding="ascii") as fh:
    fh.write(M.make_def("WOx buffer with WO3 parameters of Zepeda Medina et al., Coatings 13 (2023) 1436",
                        d_abs=800, d_etl=50, d_htl=50, buffer="WOx", d_buf=10))

L = ["// MAGeI3 thesis - WOx re-simulation with WO3 parameters from Coatings 13 (2023) 1436",
     "// layers: 1 Spiro | 2 WOx | 3 MAGeI3 | 4 TiO2 | 5 ITO ; outputs MG_W2_*",
     "set errorhandling.overwritefile", "clear all"]
def iv(qe=False):
    L.extend(["clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv",
              "action iv.startv 0", "action iv.stopv 1.6", "action iv.increment 0.02", "action iv.stopaftervoc 1"])
    if qe:
        L.extend(["action qe.doqe", "action qe.startlambda 300", "action qe.stoplambda 900", "action qe.increment 10"])
def load(d_buf=0.01):
    L.extend([f"load definitionfile {DEF}", "set layer1.thickness 0.05", f"set layer2.thickness {d_buf}",
              "set layer3.thickness 0.8", "set layer4.thickness 0.05"])
def run(tag, qe=False):
    L.extend(["calculate singleshot", f"save results.iv MG_W2_{tag}.iv"] + ([f"save results.qe MG_W2_{tag}.qe"] if qe else []))

L.append("// ===== 1) WOx thickness 10..50 nm (step 4)")
iv()
for d in (10, 20, 30, 40, 50):
    load(d / 1000); run(f"thick{d:02d}")
L.append("// ===== 2) WOx donor density (10 nm)")
for e in (15, 17, 19):
    load(); L.append(f"set layer2.nd 1E{e}"); run(f"ND1E{e}")
L.append("// ===== 3) WOx electron affinity sweep (10 nm): VBO = chi - 2.45 eV")
for chi in (4.55, 4.0, 3.5, 3.0, 2.75, 2.55, 2.45, 2.35, 2.25, 2.05):
    load(); L.append(f"set layer2.chi {chi}"); run(f"chi{int(round(chi*100)):03d}")
L.append("// ===== 4) IPCE, 10 nm")
iv(qe=True); load(); run("QE10", qe=True)
with open(os.path.join(out, "MAGeI3_WOx_rerun.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(L) + "\r\n")
print("ok", sum(1 for x in L if x.startswith("calculate")), "runs")
