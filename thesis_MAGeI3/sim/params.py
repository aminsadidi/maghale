"""
Input parameters - taken verbatim from Chapter 3 of the thesis
(Tables 3-1, 3-2, 3-3, 3-4). Every assumption that is NOT in those tables
is marked with  # ASSUMPTION  and is reported in Table 4-1 of Chapter 4.
"""
from dd1d import Layer, defect, Device

# ---------------------------------------------------------------- Table 3-1
def ITO(d=200):
    return Layer("ITO", d, Eg=3.5, chi=4.3, eps=9.0, Nc=2.2e18, Nv=1.8e19,
                 mun=40.0, mup=5.0, ND=1.0e19, NA=0.0,
                 # Table 3-1 lists "200" for ITO defect density (typo) -> 1e15 used  # ASSUMPTION
                 defects=[defect("neutral", 1e15, 1.75)])


def TiO2(d=100):
    # Table 3-3: ETL defect neutral, single, 0.65 eV above Ev, Nt = 2.2e15
    return Layer("TiO2", d, Eg=3.2, chi=4.1, eps=35.0, Nc=2.2e18, Nv=1.8e19,
                 mun=20.0, mup=0.01, ND=2.1e18, NA=0.0,
                 defects=[defect("neutral", 2.2e15, 0.65, dist="single", Echar=0.1)])


def Spiro(d=100):
    # Table 3-3: HTL defect donor, gaussian, 1.65 eV above Ev, Echar 0.1, Nt = 1.1e15
    return Layer("Spiro-OMeTAD", d, Eg=3.0, chi=2.2, eps=3.0, Nc=1.0e18, Nv=9.0e16,
                 mun=2.0e-4, mup=1.0e-4, ND=0.0, NA=1.0e18,
                 defects=[defect("donor", 1.1e15, 1.65, dist="gauss", Echar=0.1)])


# ---------------------------------------------------------------- Table 3-2
def MAGeI3(d=600, Nt=1e16):
    # Table 3-3: perovskite defect donor, gaussian, 0.6 eV above Ev, Echar 0.1, Nt = 1e16
    return Layer("MAGeI3", d, Eg=1.9, chi=3.7, eps=10.0, Nc=2.8e18, Nv=2.8e18,
                 mun=10.1, mup=16.2, ND=1.0e18, NA=1.1e18,
                 defects=[defect("donor", Nt, 0.6, dist="gauss", Echar=0.1)])


def WOx(d=10):
    # Column labelled "MoOx [67]" in Table 3-2 is used for WOx (as in the text).
    # Buffer bulk defects: neutral, single, mid-gap, 1e15 (type not given)  # ASSUMPTION
    return Layer("WOx", d, Eg=3.0, chi=2.3, eps=6.0, Nc=2.0e18, Nv=1.8e16,
                 mun=1.0, mup=0.1, ND=0.0, NA=7.0e14,
                 defects=[defect("neutral", 1e15, 1.5)])


def V2O5(d=10):
    return Layer("V2O5", d, Eg=3.99, chi=2.3, eps=4.28, Nc=2.2e18, Nv=1.8e19,
                 mun=1.26, mup=34.5, ND=1.0e17, NA=0.0,
                 defects=[defect("neutral", 1e15, 2.0)])


def NiOx(d=10):
    return Layer("NiOx", d, Eg=3.25, chi=2.05, eps=11.75, Nc=2.0e18, Nv=2.0e16,
                 mun=8.0, mup=2.0, ND=0.0, NA=7.0e14,
                 defects=[defect("neutral", 1e15, 1.625)])


BUFFERS = {"WOx": WOx, "NiOx": NiOx, "V2O5": V2O5}

# ---------------------------------------------------------------- Table 3-4
# Interfaces ETL/perovskite and perovskite/HTL(or buffer): neutral, single,
# 0.6 eV above Ev of the absorber, Nit = 1.1e5 cm^-2.
# Capture cross sections not listed -> 1e-15 cm2 (same as bulk)  # ASSUMPTION
NIT_DEFAULT = 1.1e5


def build_device(d_abs=600, d_etl=100, d_htl=100, buffer=None, d_buf=10,
                 Nit=NIT_DEFAULT, T=300.0, Nt_abs=1e16, buffer_overrides=None):
    layers = [ITO(200), TiO2(d_etl), MAGeI3(d_abs, Nt=Nt_abs)]
    if buffer is not None and d_buf > 0:
        b = BUFFERS[buffer](d_buf)
        if buffer_overrides:
            b = b.copy(**buffer_overrides)
        layers.append(b)
    layers.append(Spiro(d_htl))
    absorber = 2
    # interface index j counts heterointerfaces from the front:
    # 0: ITO/TiO2, 1: TiO2/MAGeI3, 2: MAGeI3/(buffer or HTL), 3: buffer/HTL
    ifd = {1: dict(Nit=Nit, Et=0.6), 2: dict(Nit=Nit, Et=0.6)}
    return Device(layers, T=T,
                  front_Sn=1e7, front_Sp=1e7,     # SCAPS default values  # ASSUMPTION
                  back_Sn=1e7, back_Sp=1e7,
                  back_wf=5.1,                    # Au, chapter 3
                  interface_defects=ifd, absorber_index=absorber)
