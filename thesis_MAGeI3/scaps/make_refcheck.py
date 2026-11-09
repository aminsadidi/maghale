"""
Robustness check: does the buffer effect of Chapter 4 survive if the MAGeI3,
Spiro-OMeTAD and ITO parameters are taken exactly from the papers cited in
Tables 3-1/3-2 ([65] Bhattarai & Das 2021, [66] Hima & Lakhdar 2020) instead
of the values printed in those tables?

Everything else (TiO2, buffers, defect table 3-3, interfaces, contacts,
thicknesses of the optimum structures) is unchanged.

usage: python make_refcheck.py  -> def/06_REF_noBuffer.def, 07_REF_WOx.def,
                                    08_REF_NiOx.def, def/MAGeI3_refcheck.script
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sim"))
import params as P  # noqa: E402
import make_def as M  # noqa: E402

_mag, _spiro, _ito = P.MAGeI3, P.Spiro, P.ITO


def MAGeI3_ref(d=600, Nt=1e16):
    # [65] Table 1 = [66] Table 1; defect profile of Table 3-3 kept
    return _mag(d, Nt).copy(chi=3.98, Nc=1e16, Nv=1e15, mun=16.2, mup=10.1, ND=1e9, NA=1e9)


def Spiro_ref(d=100):
    return _spiro(d).copy(chi=2.45, Nc=1e19, Nv=1e19, mun=2e-4, mup=2e-4, NA=2e18)


def ITO_ref(d=200):
    return _ito(d).copy(chi=4.0, ND=2e19, mun=20.0, mup=10.0)


P.MAGeI3, P.Spiro, P.ITO = MAGeI3_ref, Spiro_ref, ITO_ref

FILES = [
    ("06_REF_noBuffer.def", None),
    ("07_REF_WOx.def", "WOx"),
    ("08_REF_NiOx.def", "NiOx"),
]

if __name__ == "__main__":
    out = os.path.join(HERE, "def")
    for fn, buf in FILES:
        kw = dict(d_abs=800, d_etl=50, d_htl=50)
        if buf:
            kw.update(buffer=buf, d_buf=50)
        txt = M.make_def(f"REFCHECK: MAGeI3/Spiro/ITO parameters from refs [65,66]; buffer={buf}", **kw)
        with open(os.path.join(out, fn), "w", newline="", encoding="ascii") as fh:
            fh.write(txt)
    L = ["// Robustness check with MAGeI3/Spiro/ITO parameters of refs [65,66]",
         "set errorhandling.overwritefile", "clear all"]
    abs_layer = {None: 2, "WOx": 3, "NiOx": 3}
    for fn, buf in FILES:
        for nt in (16, 14):
            tag = f"{buf or 'none'}_Nt1e{nt}"
            L += ["clear actions", "action light", "action workingpoint.temperature 300", "action iv.doiv",
                  "action iv.startv 0", "action iv.stopv 1.9", "action iv.increment 0.01", "action iv.stopaftervoc 1",
                  f"load definitionfile {fn}"]
            if nt != 16:
                L.append(f"set layer{abs_layer[buf]}.defect1.ntotal 1E{nt}")
            L += ["calculate singleshot", f"save results.iv MG_REF_{tag}.iv"]
    with open(os.path.join(out, "MAGeI3_refcheck.script"), "w", newline="", encoding="ascii") as fh:
        fh.write("\r\n".join(L) + "\r\n")
    print("written")
