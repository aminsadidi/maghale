"""
Corrected, sourced input parameters for the re-simulation (every value checked against the source table).
  MAGeI3, Spiro-OMeTAD : Bhattarai & Das, Solar Energy 217 (2021) 200, Table 1   [65]
                         (Nc/Nv unit printed as m^-3 in the paper = typo; values are cm^-3, same as [66])
  ITO, NiOx (NiO)      : Hima & Lakhdar, Optical Materials 99 (2020) 109607, Table 1   [66]
  TiO2                 : Stanic et al., Materials 15 (2022) 7310, Table 1   [63]
  WOx (WO3)            : Zepeda Medina et al., Coatings 13 (2023) 1436, Table 1 (doi 10.3390/coatings13081436)
  V2O5                 : unchanged (thesis Table 3-2, ref [62]; source not available)
  Bulk defects         : unchanged thesis Table 3-3 (ref [69]) except ITO (1e15, [66]), NiOx (1e14, [66]), WOx (1e12, Coatings)
  Interface defects    : El Arfaoui et al., J. Opt. 53 (2024) 4452, Table 2   [70]
                         neutral, Gaussian, Et = 0.6 eV, Echar = 0.1 eV, sigma_n = sigma_p = 1e-19 cm2, N = 1e15 cm^-2
                         (unit printed as "cm3" in the paper; an interface density is per cm2)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "sim")); sys.path.insert(0, os.path.join(ROOT, "scaps"))
import params as P
from dd1d import Layer, defect
import make_def as M

_mag, _spiro, _tio2 = P.MAGeI3, P.Spiro, P.TiO2

def ITO(d=200):
    return Layer("ITO", d, Eg=3.5, chi=4.0, eps=9.0, Nc=2.2e18, Nv=1.8e19, mun=20.0, mup=10.0, ND=2e19, NA=0.0,
                 defects=[defect("neutral", 1e15, 1.75)])
def TiO2(d=50):      # bulk defect kept from Table 3-3
    return _tio2(d).copy(Eg=3.26, chi=4.2, eps=9.0, Nc=2.2e18, Nv=1.8e18, mun=20.0, mup=10.0, ND=5e16, NA=0.0)
def MAGeI3(d=600, Nt=1e16):   # bulk defect kept from Table 3-3
    return _mag(d, Nt).copy(Eg=1.9, chi=3.98, eps=10.0, Nc=1e16, Nv=1e15, mun=16.2, mup=10.1, ND=1e9, NA=1e9)
def Spiro(d=50):     # bulk defect kept from Table 3-3
    return _spiro(d).copy(Eg=3.0, chi=2.45, eps=3.0, Nc=1e19, Nv=1e19, mun=2e-4, mup=2e-4, ND=0.0, NA=2e18)
def NiOx(d=10):
    return Layer("NiOx", d, Eg=3.8, chi=1.46, eps=10.7, Nc=2.8e19, Nv=1e19, mun=12.0, mup=2.8, ND=0.0, NA=1e18,
                 defects=[defect("neutral", 1e14, 1.9)])
def WOx(d=10):
    return Layer("WOx", d, Eg=3.15, chi=4.55, eps=10.0, Nc=4.2e18, Nv=9e18, mun=20.0, mup=10.0, ND=1e19, NA=0.0,
                 defects=[defect("donor", 1e12, 1.575)])

P.ITO, P.TiO2, P.MAGeI3, P.Spiro, P.NiOx, P.WOx = ITO, TiO2, MAGeI3, Spiro, NiOx, WOx
P.BUFFERS.update({"WOx": WOx, "NiOx": NiOx})
M.IF_SIGMA_CM2 = 1e-19
M.IF_DIST = "gauss"
NIT = 1e15
