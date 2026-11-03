"""
Generate SCAPS-1D problem-definition files (.def) for the MAGeI3 thesis.

The file layout is copied line-by-line from the definition files distributed
with SCAPS 3.3.02 / 3.3.05 (e.g. "Numos CIGS baseline.def", "example CIGS.def"):
CRLF line endings, TAB separated 7-column parameter rows, SI units (m, m^-3,
m^2/Vs, m/s). Parameter values come from ../sim/params.py, i.e. Tables 3-1..3-4.

SCAPS orientation: left = back contact (Au), right = front contact (ITO),
illumination from the right. Layer order left->right:
    Spiro-OMeTAD | [buffer] | MAGeI3 | TiO2 | ITO

usage:  python make_def.py  [output_dir]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sim"))
import params as P  # noqa: E402

CM3 = 1e6      # 1/cm^3 -> 1/m^3
CM2 = 1e4      # 1/cm^2 -> 1/m^2


def row(name, v, fmt, unit, last="2"):
    """7-column SCAPS row: y=0, y=1, y=..., 1, 1, value, value, 0, flag."""
    f = lambda x: format(x, fmt)
    cols = [f(v), f(v), f(v), f(1.0), f(1.0), f(v), f(v)]
    return f"{name} :\t" + "\t".join(cols) + f"\t 0\t {last}\t[{unit}]"


def row_fixed(name, cols, unit, last="0"):
    return f"{name} :\t" + "\t".join(cols) + f"\t 0\t {last}\t[{unit}]"


def e(x, nd=6):
    return f" {x:.{nd}e}"


def layer_block(L):
    lines = ["layer", "",
             f"name : {L.name}",
             f"d : {L.d * 1e-2:.3e} [m]",
             row_fixed("composition grading",
                       ["  0.00000", "  1.00000"] + ["  0.00000"] * 5, "-", last="1"),
             row("v_th_n", L.vth_n * 1e-2, " .3e", "m/s"),
             row("v_th_p", L.vth_p * 1e-2, " .3e", "m/s"),
             row("eps", L.eps, "13.6f", "-"),
             row("chi", L.chi, "10.6f", "eV"),
             row("Eg", L.Eg, "10.6f", "eV"),
             row("Nc", L.Nc * CM3, " .6e", "/m^3"),
             row("Nv", L.Nv * CM3, " .6e", "/m^3"),
             row("mu_n", L.mun * 1e-4, " .6e", "m^2/Vs"),
             row("mu_p", L.mup * 1e-4, " .6e", "m^2/Vs"),
             "Tunneling in layer: 0 (0: no tunneling, 1: with tunneling)",
             row_fixed("Relative electron mass", [" 1.000000e+00"] * 7, "-"),
             row_fixed("Relative hole mass", [" 1.000000e+00"] * 7, "-"),
             row_fixed("K_rad", [" 0.000000e+00", " 0.000000e+00", " 1.000000e+01",
                                 " 1.000000e+01", " 1.000000e+01", " 0.000000e+00",
                                 " 0.000000e+00"], "m^3/s"),
             row_fixed("c_n_auger", [" 0.000000e+00", " 0.000000e+00", " 1.000000e+01",
                                     " 1.000000e+01", " 1.000000e+01", " 0.000000e+00",
                                     " 0.000000e+00"], "m^6/s"),
             row_fixed("c_p_auger", [" 0.000000e+00", " 0.000000e+00", " 1.000000e+01",
                                     " 1.000000e+01", " 1.000000e+01", " 0.000000e+00",
                                     " 0.000000e+00"], "m^6/s"),
             row("Na(uniform)", L.NA * CM3, " .6e", "/m^3"),
             row("Nd(uniform)", L.ND * CM3, " .6e", "/m^3"),
             ]
    lam_c = 1239.84 / L.Eg
    lines.append(row_fixed("absorption grading",
                           [f"{lam_c:8.2f}", f"{lam_c:8.2f}", "  250.00", "  250.00",
                            "    0.00", "    1.20", "    1.20"], "nm"))
    A = L.A_abs * 1e2      # 1/(cm sqrt eV) -> 1/(m sqrt eV)
    lines += ["absorptionmodel pure A material (y=0) : coefficients A and B",
              f"A : {A:.3e} [/(m*sqrt(eV))]",
              "B : 0.000e+00 [sqrt(eV)/m]",
              "absorption pure B material (y=1), model : coefficients A and B",
              f"pure B material (y=1), A : {A:.3e} [/(m*sqrt(eV))]",
              "pure B material (y=1), B : 0.000e+00 [sqrt(eV)/m]"]
    for dft in L.defects:
        lines += [""] + defect_block(dft)
    return lines


def defect_block(d):
    kind = d["kind"]
    lvl = {"neutral": "neutral", "donor": "+/0", "acceptor": "0/-"}[kind]
    Nt = d["Nt"] * CM3
    Ek = d["Echar"]
    if d["dist"] == "gauss":
        dist = "gauss"
        Npk = Nt / (Ek * math.sqrt(math.pi))
        unitN = "/m^3 eV"
    else:
        dist = "single"
        Npk = Nt
        unitN = "/m^3"
    return ["srhrecombination", "",
            f"type : {kind} ( 1 level(s) )",
            f"energy distribution : {dist}",
            "Reference for defect energy :  0 ; 0 = above EV (SCAPS<2.7); 1 = above Ei; 2 = below EC",
            f"Ekar : {Ek:7.4f} [eV]",
            row("Nt(uniform)", Nt, " .6e", "/m^3"),
            "profile : homogenous",
            "Lkar : 1.000e+00 [m]",
            f"Nleft : {Npk:.3e} [{unitN}]",
            f"Nright : {Npk:.3e} [{unitN}]",
            f"leveltype : {lvl}\t",
            f"sigma_n : {d['sn'] * 1e-4:.3e}\t[m^2]",
            f"sigma_p : {d['sp'] * 1e-4:.3e}\t[m^2]",
            f"Et : {d['Et']:7.3f}\t[eV]"]


def interface_block(name, rec=None):
    lines = ["interface properties", "",
             f"interfacename : {name}",
             "Intraband tunneling : 0 (0: no tunneling, 1: with tunneling)",
             "Relative electron mass :  1.00e+00",
             "Relative hole mass :  1.00e+00"]
    if rec is not None:
        Nit, Et, ref = rec
        s = 1e-15 * 1e-4
        lines += ["", "interface recombination", "",
                  "type : neutral",
                  f"sigma_nleft : {s:.3e} [m^2]",
                  f"sigma_nright : {s:.3e} [m^2]",
                  f"sigma_pleft : {s:.3e} [m^2]",
                  f"sigma_pright : {s:.3e} [m^2]",
                  "Tunneling to trap: 0 (0: no tunneling, 1: with tunneling)",
                  "Relative electron mass :  1.00e+00",
                  "Relative hole mass :  1.00e+00",
                  "energy distribution : single",
                  f"Reference for defect energy :  {ref} ; 3 = above highest EV; 4 = below lowest EC; "
                  "5 = above Ei left; 6 = above Ei right; 7 = above EV left (= SCAPS%<2.7 reference); "
                  "8 = above EV right; 9 = above middle of interface gap",
                  f"Et : {Et:5.2f} [eV]",
                  "Ekar :  0.10 [eV]",
                  f"N : {Nit * CM2:.3e} [/m^2]"]
    return lines


def make_def(title, d_abs=600, d_etl=100, d_htl=100, buffer=None, d_buf=10,
             Nit=P.NIT_DEFAULT):
    layers = [P.Spiro(d_htl)]
    if buffer:
        layers.append(P.BUFFERS[buffer](d_buf))
    layers += [P.MAGeI3(d_abs), P.TiO2(d_etl), P.ITO(200)]
    i_abs = len(layers) - 3
    out = [
        "> SCAPS 3.3.02 ELIS-UGent: Version scaps3302.exe, dated 28-08-2015, 11:48:47 Problem definition file",
        "> last saved by SCAPS: \t01-11-2026 at 12:00:00",
        "> ",
        f"> {title}",
        "> MSc thesis: buffer layers (V2O5, WOx, NiOx) at the HTL interface of MAGeI3 perovskite solar cells",
        "> parameters: thesis Chapter 3, Tables 3-1 to 3-4 (generated by make_def.py)",
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
    for k, L in enumerate(layers):
        out += layer_block(L)
        if k < len(layers) - 1:
            R = layers[k + 1]
            rec = None
            if k + 1 == i_abs:          # HTL-or-buffer / MAGeI3 : Et above EV right
                rec = (Nit, 0.60, 8)
            elif k == i_abs:            # MAGeI3 / TiO2 : Et above EV left
                rec = (Nit, 0.60, 7)
            out += [""] + interface_block(f"{L.name.split('-')[0]} / {R.name.split('-')[0]}"[:20], rec) + ["", ""]
    out += ["", "",
            "front contact", "",
            "flatband : 1 (1: flatband contact imposed; 0: fixed Phi_m value)",
            "recalculate : 1 (1 = do or 0 = do not recalculate phi_m to set flatband in each batch step)",
            "Fi_m :  4.26 [eV]",
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


FILES = [
    ("01_Step1_noBuffer_MAGeI3-batch.def", "Step 1: absorber thickness sweep (MAGeI3 100-800 nm), TiO2 100 nm, Spiro 100 nm",
     dict(d_abs=500, d_etl=100, d_htl=100)),
    ("02_noBuffer_reference.def", "Reference cell without buffer: TiO2 100 nm, MAGeI3 600 nm, Spiro 100 nm",
     dict(d_abs=600, d_etl=100, d_htl=100)),
    ("03_WOx_buffer_10nm.def", "WOx buffer 10 nm between MAGeI3 and Spiro-OMeTAD",
     dict(d_abs=600, d_etl=100, d_htl=100, buffer="WOx", d_buf=10)),
    ("04_NiOx_buffer_10nm.def", "NiOx buffer 10 nm between MAGeI3 and Spiro-OMeTAD",
     dict(d_abs=600, d_etl=100, d_htl=100, buffer="NiOx", d_buf=10)),
    ("05_V2O5_buffer_10nm.def", "V2O5 buffer 10 nm between MAGeI3 and Spiro-OMeTAD",
     dict(d_abs=600, d_etl=100, d_htl=100, buffer="V2O5", d_buf=10)),
]

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "def")
    os.makedirs(outdir, exist_ok=True)
    for fn, title, kw in FILES:
        with open(os.path.join(outdir, fn), "w", newline="", encoding="ascii") as fh:
            fh.write(make_def(title, **kw))
        print("wrote", fn)
