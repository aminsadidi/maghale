"""Second SCAPS script: dark J-V, HTL doping, buffer doping and buffer permittivity.
Outputs MG_X_*.iv in the SCAPS results folder."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
DEF = {"none": "02_noBuffer_reference.def", "WOx": "03_WOx_buffer_10nm.def", "NiOx": "04_NiOx_buffer_10nm.def"}
L = []; a = L.append


def load(s, d_buf=0.05):
    a(f"load definitionfile {DEF[s]}")
    a("set layer1.thickness 0.05")
    if s == "none":
        a("set layer2.thickness 0.8"); a("set layer3.thickness 0.05")
    else:
        a(f"set layer2.thickness {d_buf}"); a("set layer3.thickness 0.8"); a("set layer4.thickness 0.05")


def iv(light=True):
    a("clear actions"); a("action light" if light else "action dark"); a("action workingpoint.temperature 300")
    a("action iv.doiv"); a("action iv.startv 0"); a("action iv.stopv 1.6"); a("action iv.increment 0.01")
    a(f"action iv.stopaftervoc {1 if light else 0}")


def run(name):
    a("calculate singleshot"); a(f"save results.iv MG_X_{name}.iv")


a("// MAGeI3 thesis - supplementary SCAPS runs"); a("set errorhandling.overwritefile"); a("clear all")
a("// dark J-V"); iv(False)
for s in ("none", "WOx", "NiOx"):
    load(s); run(f"dark_{s}")
a("// HTL (Spiro) acceptor doping"); iv()
for s in ("none", "WOx"):
    for e in (16, 17, 18, 19):
        load(s); a(f"set layer1.na 1E{e}"); run(f"htlNA_{s}_1E{e}")
a("// WOx buffer acceptor doping")
for e in (14, 15, 16, 17, 18):
    load("WOx"); a(f"set layer2.na 1E{e}"); run(f"bufNA_WOx_1E{e}")
a("// WOx buffer permittivity")
for eps in (3, 6, 12, 24):
    load("WOx"); a(f"set layer2.epsilon {eps}"); run(f"bufEPS_WOx_{eps}")
a("// finished")
L_ALL = L
if __name__ == "__main__":
    out = os.path.join(HERE, "def", "MAGeI3_extra.script")
    open(out, "w", newline="", encoding="ascii").write("\r\n".join(L) + "\r\n")
    print("wrote", out, len(L))
