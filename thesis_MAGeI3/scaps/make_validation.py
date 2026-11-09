"""
Validation input for SCAPS-1D: reproduce the optimised n-i-p MAGeI3 cell of
Bhattarai & Das, Solar Energy 217 (2021) 200-207 (thesis ref. [65]):

    ITO / ZnO (50 nm) / MAGeI3 (400 nm) / Spiro-OMeTAD (50 nm) / Au
    reported (Table 2, 7):  Jsc 16.27 mA/cm2, Voc 1.74 V, FF 64.5 %, PCE 18.3 %

Layer parameters: Bhattarai & Das Table 1 (ZnO, MAGeI3, Spiro-OMeTAD).
Not given in that paper (ASSUMPTIONS, stated in the thesis text):
  * ITO layer           -> Hima & Lakhdar, Opt. Mater. 99 (2020) 109607, Table 1
  * defect densities    -> MAGeI3 1e14 cm-3 (Hima & Lakhdar Table 1), ZnO / Spiro 1e15 cm-3,
                           neutral, single level at mid-gap, sigma = 1e-15 cm2
  * no interface defects, Au work function 5.1 eV, S = 1e7 cm/s at both contacts
  * absorption: SCAPS sqrt model, A = 1e5 cm-1 eV-1/2 for all layers
Because the defect parameters are not reported, the script also sweeps the
MAGeI3 defect density (1e13 .. 1e16 cm-3).

usage: python make_validation.py   -> def/00_validation_Bhattarai2021.def
                                      def/MAGeI3_validation.script
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sim"))
from dd1d import Layer, defect  # noqa: E402  (only the parameter container is used)
from make_def import layer_block, interface_block  # noqa: E402

DEF_NAME = "00_validation_Bhattarai2021.def"
SCRIPT_NAME = "MAGeI3_validation.script"


def mid(Eg):
    return Eg / 2.0


def layers():
    spiro = Layer("Spiro-OMeTAD", 50, Eg=3.0, chi=2.45, eps=3.0, Nc=1e19, Nv=1e19,
                  mun=2e-4, mup=2e-4, ND=0.0, NA=2e18,
                  defects=[defect("neutral", 1e15, mid(3.0))])
    mag = Layer("MAGeI3", 400, Eg=1.9, chi=3.98, eps=10.0, Nc=1e16, Nv=1e15,
                mun=16.2, mup=10.1, ND=1e9, NA=1e9,
                defects=[defect("neutral", 1e14, mid(1.9))])
    zno = Layer("ZnO", 50, Eg=3.3, chi=4.1, eps=9.0, Nc=4e18, Nv=4e19,
                mun=100.0, mup=25.0, ND=1e18, NA=1e5,
                defects=[defect("neutral", 1e15, mid(3.3))])
    ito = Layer("ITO", 200, Eg=3.5, chi=4.0, eps=9.0, Nc=2.2e18, Nv=1.8e19,
                mun=20.0, mup=10.0, ND=2e19, NA=0.0,
                defects=[defect("neutral", 1e15, mid(3.5))])
    return [spiro, mag, zno, ito]          # left (back) -> right (front)


def make_def():
    out = [
        "> SCAPS 3.3.02 ELIS-UGent: Version scaps3302.exe, dated 28-08-2015, 11:48:47 Problem definition file",
        "> last saved by SCAPS: \t09-11-2026 at 12:00:00",
        "> ",
        "> VALIDATION: Bhattarai & Das, Solar Energy 217 (2021) 200: ITO/ZnO/MAGeI3/Spiro-OMeTAD/Au",
        "> layer parameters: Table 1 of that paper; ITO from Hima & Lakhdar (2020); defects assumed",
        "> left = back contact (Au), right = front contact (ITO), illuminated from the right",
        "> ",
        "convergence", "",
        "recalculate mesh :  0 (0: fixed mesh, 1: adaptive mesh)",
        "Mott-Schottky analysis epsilon of sheet # :  0",
        "Mott-Schottky analysis epsilon of sheet side :  1\t(left side = -1; right side = +1)",
        "", "",
        "back contact", "",
        "flatband : 0 (1: flatband contact imposed; 0: fixed Phi_m value)",
        "recalculate : 0 (1 = do or 0 = do not recalculate phi_m to set flatband in each batch step)",
        "Fi_m :   5.1000 [eV]",
        "Sn :  1.000e+05 [m/s]",
        "Sp :  1.000e+05 [m/s]",
        "Tunneling to contact: 0 (0: no tunneling, 1: with tunneling)",
        "Relative electron mass :  1.00e+00",
        "Relative hole mass :  1.00e+00",
        "",
        "optical filter : reflection",
        "wavelength independent: 1",
        "filter value: 0.00000000e+00",
        "",
    ]
    Ls = layers()
    for k, L in enumerate(Ls):
        out += layer_block(L)
        if k < len(Ls) - 1:
            R = Ls[k + 1]
            out += [""] + interface_block(f"{L.name.split('-')[0]} / {R.name}"[:20], None) + ["", ""]
    out += ["", "",
            "front contact", "",
            "flatband : 1 (1: flatband contact imposed; 0: fixed Phi_m value)",
            "recalculate : 1 (1 = do or 0 = do not recalculate phi_m to set flatband in each batch step)",
            "Fi_m :  4.00 [eV]",
            "Sn : 1.000e+05 [m/s]",
            "Sp : 1.000e+05 [m/s]",
            "Tunneling to contact: 0 (0: no tunneling, 1: with tunneling)",
            "Relative electron mass :  1.00e+00",
            "Relative hole mass :  1.00e+00",
            "",
            "optical filter : transmission",
            "wavelength independent: 1",
            "filter value: 1.00000000e+00",
            "",
            "working point", "",
            "illuminated from : right",
            "internal Rfront :   0.00000000",
            "internal Tfront :  1.0000e+00",
            "voltage V applied to : -1 (+1: right contact; -1: left contact)",
            "cell reference system :  1 (1: as a consumer (consumed power = +VJ; 0: as a generator (generated power = +VJ) )",
            ]
    return "\r\n".join(out) + "\r\n"


def make_script():
    L = []
    a = L.append
    a("// Validation of the SCAPS set-up against Bhattarai & Das, Solar Energy 217 (2021) 200")
    a("// outputs: SCAPS results folder, files MG_VAL_*.iv / MG_VAL_*.qe")
    a("set errorhandling.overwritefile")
    a("clear all")
    for tag, nt in [("base", None), ("Nt1e13", 1e13), ("Nt1e15", 1e15), ("Nt1e16", 1e16), ("Nt1e17", 1e17)]:
        a("clear actions")
        a("action light")
        a("action workingpoint.temperature 300")
        a("action iv.doiv")
        a("action iv.startv 0")
        a("action iv.stopv 1.9")
        a("action iv.increment 0.01")
        a("action iv.stopaftervoc 1")
        if tag == "base":
            a("action qe.doqe")
            a("action qe.startlambda 300")
            a("action qe.stoplambda 900")
            a("action qe.increment 10")
        a(f"load definitionfile {DEF_NAME}")
        if nt is not None:
            a(f"set layer2.defect1.ntotal 1E{round(__import__('math').log10(nt))}")   # MAGeI3 = layer 2; cm^-3 as in make_script.py (verified)
        a("calculate singleshot")
        a(f"save results.iv MG_VAL_{tag}.iv")
        if tag == "base":
            a(f"save results.qe MG_VAL_{tag}.qe")
    return "\r\n".join(L) + "\r\n"


if __name__ == "__main__":
    outdir = os.path.join(HERE, "def")
    with open(os.path.join(outdir, DEF_NAME), "w", newline="", encoding="ascii") as fh:
        fh.write(make_def())
    with open(os.path.join(outdir, SCRIPT_NAME), "w", newline="", encoding="ascii") as fh:
        fh.write(make_script())
    print("wrote", DEF_NAME, SCRIPT_NAME)
