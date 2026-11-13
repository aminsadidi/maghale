"""
Feasibility test for the topic: Cu2O/NiOx bilayer HTL vs back-contact barrier in FAPbI3 cells (SCAPS-1D).
Structure (light from FTO): FTO / TiO2 (50) / FAPbI3 (600) / HTL / metal
HTL: Cu2O (50) | NiOx (50) | Cu2O(25)/NiOx(25) | NiOx(25)/Cu2O(25)  (first layer touches FAPbI3)
Back-contact work function: 4.5, 4.8, 5.1 eV.  NiOx parameter sets A and B.
Typical literature-style parameters; to be replaced by a sourced table before the real study.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "thesis_MAGeI3", "sim"))
sys.path.insert(0, os.path.join(HERE, "..", "thesis_MAGeI3", "scaps"))
from dd1d import Layer, defect
from make_def import layer_block, interface_block

def FTO():   return Layer("FTO", 200, Eg=3.5, chi=4.0, eps=9.0, Nc=2.2e18, Nv=1.8e19, mun=20, mup=10, ND=1e19, NA=0, defects=[defect("neutral",1e15,1.75)])
def TiO2():  return Layer("TiO2", 50, Eg=3.2, chi=4.0, eps=9.0, Nc=2.2e18, Nv=1.8e19, mun=20, mup=10, ND=1e17, NA=0, defects=[defect("neutral",1e15,1.6)])
def FAPI():  return Layer("FAPbI3", 600, Eg=1.51, chi=4.0, eps=6.6, Nc=1.2e19, Nv=2.9e18, mun=2.7, mup=1.8, ND=0, NA=1e13, defects=[defect("neutral",1e14,0.755)])
def Cu2O(d): return Layer("Cu2O", d, Eg=2.17, chi=3.2, eps=7.11, Nc=2.02e17, Nv=1.1e19, mun=200, mup=80, ND=0, NA=1e18, defects=[defect("neutral",1e15,1.08)])
NIO = {"A": (3.8, 1.46), "B": (3.6, 1.8)}
def NiO(d, s):
    Eg, chi = NIO[s]
    return Layer("NiOx", d, Eg=Eg, chi=chi, eps=10.7, Nc=2.8e19, Nv=1e19, mun=12, mup=2.8, ND=0, NA=1e18, defects=[defect("neutral",1e15,Eg/2)])

def make(title, htl, wf):
    out = ["> SCAPS 3.3.02 ELIS-UGent: Version scaps3302.exe, dated 28-08-2015, 11:48:47 Problem definition file",
           "> last saved by SCAPS: \t13-11-2026 at 12:00:00", "> ", f"> {title}",
           "> left = back contact (metal), right = front contact (FTO), illuminated from the right", "> ",
           "convergence", "", "recalculate mesh :  0 (0: fixed mesh, 1: adaptive mesh)",
           "Mott-Schottky analysis epsilon of sheet # :  0",
           "Mott-Schottky analysis epsilon of sheet side :  1\t(left side = -1; right side = +1)", "", "",
           "back contact", "", "flatband : 0 (1: flatband contact imposed; 0: fixed Phi_m value)",
           "recalculate : 0 (1 = do or 0 = do not recalculate phi_m to set flatband in each batch step)",
           f"Fi_m :   {wf:.4f} [eV]", "Sn :  1.000e+05 [m/s]", "Sp :  1.000e+05 [m/s]",
           "Tunneling to contact: 0 (0: no tunneling, 1: with tunneling)",
           "Relative electron mass :  1.00e+00", "Relative hole mass :  1.00e+00", "",
           "optical filter : reflection", "wavelength independent: 1", "filter value: 0.00000000e+00", ""]
    Ls = list(reversed(htl)) + [FAPI(), TiO2(), FTO()]      # left (back) -> right (front)
    for k, L in enumerate(Ls):
        out += layer_block(L)
        if k < len(Ls) - 1:
            out += [""] + interface_block(f"{L.name} / {Ls[k+1].name}"[:20], None) + ["", ""]
    out += ["", "", "front contact", "", "flatband : 1 (1: flatband contact imposed; 0: fixed Phi_m value)",
            "recalculate : 1 (1 = do or 0 = do not recalculate phi_m to set flatband in each batch step)",
            "Fi_m :  4.00 [eV]", "Sn : 1.000e+05 [m/s]", "Sp : 1.000e+05 [m/s]",
            "Tunneling to contact: 0 (0: no tunneling, 1: with tunneling)",
            "Relative electron mass :  1.00e+00", "Relative hole mass :  1.00e+00", "",
            "optical filter : transmission", "wavelength independent: 1", "filter value: 1.00000000e+00", "",
            "working point", "", "illuminated from : right", "internal Rfront :   0.00000000",
            "internal Tfront :  1.0000e+00", "voltage V applied to : -1 (+1: right contact; -1: left contact)",
            "cell reference system :  1 (1: as a consumer (consumed power = +VJ; 0: as a generator (generated power = +VJ) )"]
    return "\r\n".join(out) + "\r\n"

cases = [("Cu2O", None, lambda s: [Cu2O(50)])]
for s in NIO:
    cases += [("NiOx", s, lambda s: [NiO(50, s)]),
              ("Cu2O-NiOx", s, lambda s: [Cu2O(25), NiO(25, s)]),
              ("NiOx-Cu2O", s, lambda s: [NiO(25, s), Cu2O(25)])]
script = ["// Feasibility test: FAPbI3 with Cu2O / NiOx / bilayer HTL and back-contact work function",
          "set errorhandling.overwritefile", "clear all"]
n = 0
for wf in (4.5, 4.8, 5.1):
    for name, s, f in cases:
        tag = f"FA_{name}{'' if s is None else '_'+s}_WF{int(round(wf*10))}"
        fn = tag + ".def"
        with open(os.path.join(HERE, "def", fn), "w", newline="", encoding="ascii") as fh:
            fh.write(make(f"{tag}: HTL first layer touches FAPbI3", f(s), wf))
        script += ["clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv",
                   "action iv.startv 0", "action iv.stopv 1.3", "action iv.increment 0.02", "action iv.stopaftervoc 1",
                   f"load definitionfile {fn}", "calculate singleshot", f"save results.iv MG_{tag}.iv"]
        n += 1
with open(os.path.join(HERE, "def", "FA_feasibility.script"), "w", newline="", encoding="ascii") as fh:
    fh.write("\r\n".join(script) + "\r\n")
print(n, "def files + FA_feasibility.script")
