"""Stage 1b: steps 2-3 around the new optimum absorber thickness (300 nm), finer TiO2/Spiro grid. Outputs MG_R1B_*.iv"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DEF = "10_RERUN_noBuffer.def"
L = ["// MAGeI3 thesis - re-simulation stage 1b", "set errorhandling.overwritefile", "clear all",
     "clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv", "action iv.startv 0",
     "action iv.stopv 2.0", "action iv.increment 0.02", "action iv.stopaftervoc 1"]
n = 0
def run(tag, htl, ab, etl):
    global n
    L.extend([f"load definitionfile {DEF}", f"set layer1.thickness {htl/1000}", f"set layer2.thickness {ab/1000}",
              f"set layer3.thickness {etl/1000}", "calculate singleshot", f"save results.iv MG_R1B_{tag}.iv"]); n += 1
L.append("// step 1 refinement: absorber 250, 350 nm")
for ab in (250, 350): run(f"S1_abs{ab:03d}", 100, ab, 100)
L.append("// step 2 at absorber 300 nm (Spiro 100)")
for etl in (1, 5, 10, 20, 30, 50, 100, 200, 400): run(f"S2_abs300_etl{etl:03d}", 100, 300, etl)
L.append("// step 3 at absorber 300 nm for TiO2 1/5/10/20 nm")
for etl in (1, 5, 10, 20):
    for htl in (1, 10, 25, 50, 100, 200): run(f"S3_abs300_etl{etl:03d}_htl{htl:03d}", htl, 300, etl)
with open(os.path.join(HERE, "def", "MAGeI3_RERUN_stage1b.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(L) + "\r\n")
print(n, "runs")
