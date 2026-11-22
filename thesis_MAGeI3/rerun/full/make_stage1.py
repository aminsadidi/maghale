"""Stage 1 of the re-simulation: optimisation steps 1-3 (no buffer). Outputs MG_R1_*.iv
Layers (back -> front): 1 Spiro | 2 MAGeI3 | 3 TiO2 | 4 ITO
Steps 2 and 3 are run for the two candidate absorber thicknesses (600, 800 nm) and two ETL thicknesses (50, 100 nm),
so the sequential protocol of Chapter 3 can be followed without re-running SCAPS."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rerun_params as R
DEF = "10_RERUN_noBuffer.def"
with open(os.path.join(HERE, "def", DEF), "w", newline="", encoding="ascii") as fh:
    fh.write(R.M.make_def("RERUN (sourced parameters): no buffer", d_abs=600, d_etl=100, d_htl=100, Nit=R.NIT))
L = ["// MAGeI3 thesis - re-simulation stage 1 (steps 1-3) with sourced parameters", "set errorhandling.overwritefile", "clear all",
     "clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv", "action iv.startv 0",
     "action iv.stopv 2.0", "action iv.increment 0.02", "action iv.stopaftervoc 1"]
n = 0
def run(tag, htl, ab, etl):
    global n
    L.extend([f"load definitionfile {DEF}", f"set layer1.thickness {htl/1000}", f"set layer2.thickness {ab/1000}",
              f"set layer3.thickness {etl/1000}", "calculate singleshot", f"save results.iv MG_R1_{tag}.iv"]); n += 1
L.append("// step 1: absorber 100..800 nm (TiO2 100, Spiro 100)")
for ab in range(100, 900, 100): run(f"S1_abs{ab:03d}", 100, ab, 100)
L.append("// step 2: TiO2 1..400 nm (Spiro 100) for absorber 600 and 800 nm")
for ab in (600, 800):
    for etl in (1, 50, 100, 150, 200, 250, 300, 350, 400): run(f"S2_abs{ab}_etl{etl:03d}", 100, ab, etl)
L.append("// step 3: Spiro 1..200 nm for absorber 600/800 and TiO2 50/100")
for ab in (600, 800):
    for etl in (50, 100):
        for htl in (1, 50, 100, 150, 200): run(f"S3_abs{ab}_etl{etl:03d}_htl{htl:03d}", htl, ab, etl)
with open(os.path.join(HERE, "def", "MAGeI3_RERUN_stage1.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(L) + "\r\n")
print(n, "runs")
