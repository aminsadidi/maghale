"""make_excel.py - collect every results/*.csv into one Excel workbook laid out
for OriginPro (row 1 = long name, row 2 = units, data from row 3).
In Origin: File > Open > Origin_Data_MAGeI3.xlsx  (or drag & drop), then
select the columns of one sheet and choose Plot > Line+Symbol."""
import csv
import glob
import os
import re

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.environ.get("MG_RESULTS", os.path.join(HERE, "..", "results"))
OUT = os.environ.get("MG_XLSX", os.path.join(HERE, "..", "origin", "Origin_Data_MAGeI3.xlsx"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)

UNITS = [(r"_V$|^V$|Vbi_V", "V"), (r"mAcm2", "mA/cm2"), (r"_pct$", "%"), (r"_nm$|^x_nm", "nm"),
         (r"^lambda", "nm"), (r"^T_K", "K"), (r"Nit_cm2", "cm^-2"), (r"_cm3$|^n_sc|^p_sc", "cm^-3"),
         (r"^f_Hz", "Hz"), (r"^Z", "Ohm cm2"), (r"nFcm2", "nF/cm2"), (r"invC2", "cm4/F2"),
         (r"_eV$|^E[cvF]|^F[np]_", "eV"), (r"_Vcm", "V/cm"), (r"^[GR]_sc", "cm^-3 s^-1"),
         (r"^Jint", "mA/cm2"), (r"^EQE", "%"), (r"^J_", "mA/cm2"), (r"^P_", "mW/cm2")]


def unit(h):
    for pat, u in UNITS:
        if re.search(pat, h):
            return u
    return ""


def main():
    wb = Workbook()
    wb.remove(wb.active)
    bold = Font(bold=True)
    fill = PatternFill("solid", fgColor="DDEBF7")
    for path in sorted(glob.glob(os.path.join(RES, "*.csv"))):
        name = os.path.splitext(os.path.basename(path))[0][:31]
        ws = wb.create_sheet(name)
        with open(path, encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        head = rows[0]
        ws.append(head)
        ws.append([unit(h) for h in head])
        for r in rows[1:]:
            vals = []
            for v in r:
                try:
                    vals.append(float(v))
                except ValueError:
                    vals.append(v)
            ws.append(vals)
        for c in ws[1] + ws[2]:
            c.font = bold; c.fill = fill; c.alignment = Alignment(horizontal="center")
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = max(12, len(str(col[0].value)) + 2)
        ws.freeze_panes = "A3"
    wb.save(OUT)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
