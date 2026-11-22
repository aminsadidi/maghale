"""WOx follow-up: lower donor density within the range of Coatings 13 (2023) 1436 (1e13-1e19 cm-3).
Structure as part B: absorber 300 nm, TiO2 10 nm, Spiro 50 nm. Outputs MG_W3_*"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
DEF = "11_RERUN_WOx.def"
L = ["// MAGeI3 thesis - WOx donor-density follow-up (outputs MG_W3_*)", "set errorhandling.overwritefile", "clear all"]
def load(d_buf):
    L.extend([f"load definitionfile {DEF}", "set layer1.thickness 0.05", f"set layer2.thickness {d_buf}",
              "set layer3.thickness 0.3", "set layer4.thickness 0.01"])
def iv():
    L.extend(["clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv", "action iv.startv 0",
              "action iv.stopv 2.0", "action iv.increment 0.02", "action iv.stopaftervoc 1"])
n = 0
iv()
for e in (13, 15, 17):
    for d in (10, 30, 50):
        load(d / 1000); L.append(f"set layer2.nd 1E{e}")
        L.extend(["calculate singleshot", f"save results.iv MG_W3_ND1E{e}_{d:02d}.iv"]); n += 1
for e in (13, 15, 17):
    L.extend(["clear actions", "action light", "action workingpoint.temperature 300", "action qe.doqe",
              "action qe.startlambda 300", "action qe.stoplambda 900", "action qe.increment 10"])
    load(0.01); L.append(f"set layer2.nd 1E{e}")
    L.extend(["calculate singleshot", f"save results.qe MG_W3_QE_ND1E{e}.qe"]); n += 1
with open(os.path.join(HERE, "def", "MAGeI3_WOx_doping.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(L) + "\r\n")
print(n, "runs")
