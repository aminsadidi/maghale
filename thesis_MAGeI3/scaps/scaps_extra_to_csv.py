"""Convert MG_X_* SCAPS outputs (supplementary script) to CSV tables."""
import glob, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scaps_to_csv import iv_params, read_text, last_block, w


def main(src, dst):
    f = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(src, "**", "MG_X_*.iv"), recursive=True)}
    par = lambda k: iv_params(f[k])[0] if k in f else dict(Voc=np.nan, Jsc=np.nan, FF=np.nan, PCE=np.nan)
    row = lambda k: [par(k)[c] for c in ("Voc", "Jsc", "FF", "PCE")]
    H = ["Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct"]
    names = {"none": "No buffer", "WOx": "WOx", "NiOx": "NiOx"}
    w(os.path.join(dst, "HTL_doping.csv"), ["structure", "NA_cm3"] + H,
      [[names[s], float(f"1e{e}")] + row(f"MG_X_htlNA_{s}_1E{e}") for s in ("none", "WOx") for e in (16, 17, 18, 19)])
    w(os.path.join(dst, "Buffer_doping.csv"), ["structure", "NA_cm3"] + H,
      [["WOx", float(f"1e{e}")] + row(f"MG_X_bufNA_WOx_1E{e}") for e in (14, 15, 16, 17, 18)])
    w(os.path.join(dst, "Buffer_permittivity.csv"), ["structure", "eps"] + H,
      [["WOx", e] + row(f"MG_X_bufEPS_WOx_{e}") for e in (3, 6, 12, 24)])
    cols = {}
    for s, n in names.items():
        k = f"MG_X_dark_{s}"
        if k in f:
            t = last_block(read_text(f[k]), "Single shot simulation #")
            rows = [l.split() for l in t.replace("\r", "").split("\n") if re.match(r"^\s+-?\d", l) and len(l.split()) == 11]
            a = np.array(rows, float); cols[n] = a
    if cols:
        V = cols["No buffer"][:, 0]
        w(os.path.join(dst, "Dark_JV.csv"), ["V"] + [f"Jdark_{n}_mAcm2" for n in cols],
          [[V[i]] + [np.interp(V[i], a[:, 0], np.abs(a[:, 1])) for a in cols.values()] for i in range(len(V))])
    print("extra converted")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
