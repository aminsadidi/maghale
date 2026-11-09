"""Convert the SCAPS validation outputs (MG_VAL_*.iv / .qe) to CSV.

usage: python scaps_validation_to_csv.py <folder with MG_VAL files>
writes ../results_scaps/Validation_summary.csv, Validation_JV.csv, Validation_QE.csv
SCAPS appends every simulation of a session to each output file, so only the
last 'Single shot simulation' block of a file is used.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results_scaps")
CASES = [("base", 1e14), ("Nt1e13", 1e13), ("Nt1e15", 1e15), ("Nt1e16", 1e16), ("Nt1e17", 1e17)]


def last_block(path):
    txt = open(path, encoding="latin-1").read()
    parts = re.split(r"Single shot simulation #", txt)
    return parts[-1]


def table(block, header_key):
    rows, on = [], False
    for ln in block.splitlines():
        s = ln.strip()
        if s.startswith(header_key):
            on = True
            continue
        if on:
            if not s:
                if rows:
                    break
                continue
            tok = s.split()
            try:
                rows.append([float(t) for t in tok])
            except ValueError:
                if rows:
                    break
    return rows


def val(block, key):
    m = re.search(rf"^{key} =\s*([-\d.eE+]+)", block, re.M)
    return float(m.group(1)) if m else float("nan")


def main(src):
    summ, jv, gen = [], {}, {}
    for tag, nt in CASES:
        b = last_block(os.path.join(src, f"MG_VAL_{tag}.iv"))
        summ.append([nt, val(b, "Voc"), val(b, "Jsc"), val(b, "FF"), val(b, "eta"),
                     "extrapolated" in b.split("Voc =")[1].splitlines()[0]])
        t = table(b, "v(V)")
        jv[nt] = [(r[0], -r[1]) for r in t]          # J>0 = generated current
        gen[nt] = [(r[0], r[3]) for r in t]          # generation current (col 4)
    with open(os.path.join(OUT, "Validation_summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Nt_abs_cm3", "Voc_V", "Jsc_mAcm2", "FF_pct", "PCE_pct", "Voc_extrapolated"])
        w.writerows(sorted(summ))
    with open(os.path.join(OUT, "Validation_JV.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Nt_abs_cm3", "V", "J_mAcm2", "Jgen_mAcm2"])
        for tag, nt in CASES:
            for (v, j), (_, g) in zip(jv[nt], gen[nt]):
                w.writerow([nt, v, j, g])
    qb = last_block(os.path.join(src, "MG_VAL_base.qe"))
    q = table(qb, "lambda(nm)")
    with open(os.path.join(OUT, "Validation_QE.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lambda_nm", "QE_pct"])
        w.writerows([[r[0], r[1]] for r in q])
    for r in sorted(summ):
        print(r)
    print("QE points:", len(q))


if __name__ == "__main__":
    main(sys.argv[1])
