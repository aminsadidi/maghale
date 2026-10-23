"""Technical report (PDF) for Dr. J.-A. Huang from summary.json and figures/. Usage: python make_report.py"""
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

import matplotlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# DejaVu (shipped with matplotlib) has the Greek letters and symbols the built-in PDF fonts lack
_fonts = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(_fonts, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(_fonts, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", os.path.join(_fonts, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Oblique",
                              boldItalic="DejaVu-Bold")
S = json.load(open("summary.json"))
ss = getSampleStyleSheet()
for _st in ss.byName.values():
    _st.fontName = "DejaVu-Bold" if "Heading" in _st.name or _st.name == "Title" else "DejaVu"
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=12.5, spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#444444"))
h1 = ParagraphStyle("h1", parent=ss["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=ss["Heading3"], fontSize=10.5, spaceBefore=6, spaceAfter=3)
W = A4[0] - 4 * cm


def P(t, st=body):
    return Paragraph(t, st)


def fig(path, width, caption):
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(path).getSize()
    return KeepTogether([Image(path, width=width, height=width * h / w), P(caption, small), Spacer(1, 4)])


def table(rows, widths=None):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "DejaVu"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def lam(k):
    return f"{S[k]['lam_res_nm']:.0f}" if k in S else "-"


def mx(k, key="max_at_res"):
    return f"{S[k][key]:.0f}" if k in S else "-"


mie = {(round(r["res_nm"], 2), round(r["lam_nm"]), round(r["dist_nm"])): r["err_pct"] for r in S["mie_validation"]}
story = [
    P("Bowl-shaped and particle-in-hole gold nanopores at 785 nm: open-source FDTD simulations",
      ParagraphStyle("t", parent=ss["Title"], fontSize=15, leading=19)),
    P("Amin Hossain Sadidi, Department of Physics, University of Isfahan (supervisor: Dr. Malek Bagheri Harouni) "
      "&nbsp;&middot;&nbsp; October 2026", small),
    Spacer(1, 6),
    P("Summary", h1),
    P("Both geometries suggested by Dr. Huang were simulated with Meep (open-source FDTD, MIT). The bowl-shaped nanopore "
      "of Zhao <i>et al.</i>, Nano Lett. 23, 4830 (2023) was modelled from Table S1/Fig. S2 of its Supporting Information; "
      "because the structure is axisymmetric it is solved exactly in cylindrical coordinates, which allows 0.5-1 nm grids."),
    P(f"&bull; <b>Validation.</b> For a 50 nm Au sphere in water the solver agrees with exact Mie theory within "
      f"{abs(mie[(0.5, 780, 5)]):.1f} % at 5 nm and {abs(mie[(0.5, 780, 10)]):.1f} % at 10 nm from the surface "
      f"(0.5 nm grid, 780 nm), and the error decreases with mesh refinement.<br/>"
      f"&bull; <b>Conventional pore.</b> Where the geometry is fully specified the result matches Fig. S4: "
      f"R = 2.5 nm resonates at {lam('rf_conv_R2.5_r1500')} nm (paper 640 nm) with |E|<super>2</super>/|E<sub>0</sub>|<super>2</super> "
      f"of about {mx('rf_conv_R2.5_r1500')} (paper ~10).<br/>"
      f"&bull; <b>Bowl pore.</b> One hot spot at the pore rim, as in Fig. 1D-F. The resonance is set mainly by the Au "
      f"thickness at the rim h<sub>3</sub>: {lam('rf_bowl_R10_h10_r1000')} nm for h<sub>3</sub> = 10 nm to "
      f"{lam('rf_bowl_R10_h2.5_r1000')} nm for 2.5 nm. With h<sub>3</sub> = 3 nm (within the 2.5-10 nm range of Table S1), "
      f"a 1 nm rounded rim and the 500 nm Gaussian beam of SI Note 2, the resonances are {lam('fit_bowl_R10_h3_r1500')} nm "
      f"(R = 10 nm), {lam('fit_bowl_R2.5_h3_r1500')} nm (R = 2.5 nm) and {lam('fit_bowl_R1_h3_r1500')} nm (R = 1 nm), "
      f"against 785, 710 and 640 nm in Fig. S4.<br/>"
      f"&bull; <b>Absolute enhancement.</b> The resonance position is mesh-converged, the peak |E|<super>2</super> at the "
      f"rim is not: it keeps rising with refinement because the rim is a (near-)sharp metal edge. Absolute values such as "
      f"the ~140 of Fig. S4 therefore depend on the edge radius and the mesh, and I report them with that caveat.<br/>"
      f"&bull; <b>Particle in the 200 nm nanohole.</b> A 50 nm Au sphere near the wall creates a gap hot spot along the "
      f"polarisation, as in Fig. 1e of the Nat. Commun. paper; 3D values are given in Section 5 with their mesh dependence."),
    fig("figures/resonance_vs_R_paper.png", 0.62 * W,
        "Figure 1. Resonance wavelength of the bowl nanopore versus pore radius: Fig. S4 of the paper (black) and Meep, "
        "for the nominal h<sub>3</sub> = 5 nm with a sharp rim (red) and for h<sub>3</sub> = 3 nm with a 1 nm rounded rim "
        "and the 500 nm Gaussian beam of SI Note 2 (blue). 0.67 nm grid."),
    PageBreak(),

    P("1. Method", h1),
    P("<b>Geometry (Table S1, Fig. S2).</b> Au layer h<sub>1</sub> = 100 nm on Si<sub>3</sub>N<sub>4</sub> "
      "h<sub>2</sub> = 30 nm; bowl opening D = 250 nm; Au thickness at the pore h<sub>3</sub>; pore radius R through the "
      "Au and the SiN. The bowl surface is the sphere through (D/2, h<sub>1</sub>) and (R, h<sub>3</sub>) centred on the axis. "
      "Water n = 1.33, SiN n = 2.0 (the SI lists the two values in swapped order). Excitation along -z from the Au side, "
      "550-1000 nm in one broadband run."),
    P("<b>Gold.</b> Rakic <i>et al.</i>, Appl. Opt. 37, 5271 (1998), the reference of the SI. The 6-pole Lorentz-Drude "
      "model distributed with Meep diverges on sub-nanometre grids when the Au rim is 5 nm thick or thinner, so the same "
      "Rakic permittivity was refitted between 500 and 1050 nm with one Drude and two Lorentz poles (maximum relative error "
      "0.19 %, &epsilon;(785 nm) = -19.26 + 2.03i). A Johnson-Christy run is included for comparison."),
    P("<b>Axisymmetric solution.</b> For normal incidence on an axisymmetric structure a linearly polarised beam is the sum "
      "of the m = +1 and m = -1 angular orders, which are mirror images of each other. One 2D (r, z) run with m = +1 and a "
      "source E<sub>r</sub> = 1, E<sub>&phi;</sub> = i gives the full 3D field: |E|<super>2</super>(r, &phi;, z) = "
      "(|E<sub>r</sub>|<super>2</super> + |E<sub>z</sub>|<super>2</super>) cos<super>2</super>&phi; + "
      "|E<sub>&phi;</sub>|<super>2</super> sin<super>2</super>&phi;. This makes 0.5 nm grids affordable."),
    P("<b>Normalisation.</b> |E<sub>0</sub>|<super>2</super> is the incident intensity at the pore position from an "
      "identical run without the structure (water only), on the same grid and with the same source (plane wave or Gaussian)."),
    P("<b>Rim shape.</b> Runs marked 'rounded' replace the two 90&deg; Au corners of the rim (top and bottom of the "
      "h<sub>3</sub> edge) by quarter circles of 1 nm radius."),
    P("2. Validation against Mie theory", h1),
    table([["grid", "1 nm", "2 nm", "5 nm", "10 nm  (distance from surface)"]] +
          [[f"{g:g} nm"] + [f"{mie.get((g, 780, d), float('nan')):+.1f} %" for d in (1, 2, 5, 10)]
           for g in (1.0, 0.5)], [2.5 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 5 * cm]),
    P("Table 1. Relative error of |E|<super>2</super>/|E<sub>0</sub>|<super>2</super> along the polarisation for a 50 nm "
      "Au sphere in water at 780 nm, Meep versus exact Mie theory (scattnlay), same Rakic permittivity.", small),
    fig("figures/mie_validation.png", 0.6 * W,
        "Figure 2. Near field of a 50 nm Au sphere in water: Meep on 1, 0.67 and 0.5 nm grids (symbols) and exact Mie "
        "theory (lines), at 550 and 780 nm."),
    PageBreak(),

    P("3. Bowl-shaped versus conventional nanopore", h1),
    table([["case", "grid", "λ_res (nm)", "paper λ_res", "paper max"],
           ["conventional R = 10 nm, Au 5 nm", "1 nm", lam("rf_conv_R10_r1000"), "840", "~40"],
           ["conventional R = 2.5 nm, Au 5 nm", "0.67 nm", lam("rf_conv_R2.5_r1500"), "640", "~10"],
           ["bowl R = 10, h3 = 5, sharp rim", "1 / 0.67 / 0.5 nm",
            f"{lam('rf_bowl_R10_r1000')} / {lam('rf_bowl_R10_r1500')} / {lam('rf_bowl_R10_r2000')}", "785", "~140"],
           ["bowl R = 10, h3 = 5, rounded, Gaussian", "1 / 0.67 nm",
            f"{lam('fit_bowl_R10_h5_r1000')} / {lam('fit_bowl_R10_h5_r1500')}", "785", "~140"],
           ["bowl R = 10, h3 = 3, rounded, Gaussian", "1 / 0.67 nm",
            f"{lam('fit_bowl_R10_h3_r1000')} / {lam('fit_bowl_R10_h3_r1500')}", "785", "~140"],
           ["bowl R = 2.5, h3 = 3, rounded, Gaussian", "0.67 nm", lam("fit_bowl_R2.5_h3_r1500"), "710", "~250"],
           ["bowl R = 1, h3 = 3, rounded, Gaussian", "0.67 nm", lam("fit_bowl_R1_h3_r1500"), "640", "~500"]],
          [6.2 * cm, 2.8 * cm, 3 * cm, 2 * cm, 1.8 * cm]),
    P("Table 2. Resonance wavelengths (maximum |E|<super>2</super> in the water next to the rim). Paper values are read "
      "from Fig. S4.", small),
    P("The conventional pore reproduces Fig. S4 (exactly for R = 2.5 nm; 880-890 nm against 840 nm for R = 10 nm). The bowl "
      "pore concentrates the field in a single hot spot on the few-nanometre metal edge of the rim (Fig. 3, 4), where "
      "the bowl funnels the incident light, and is resonant anywhere in the 650-800 nm range depending on the rim, as "
      "discussed in Section 4."),
    fig("figures/bowl_R10_side.png", W,
        "Figure 3. |E|<super>2</super>/|E<sub>0</sub>|<super>2</super> at 785 nm (log scale), cross-section of the bowl pore; "
        "left half in the plane perpendicular to E, right half in the plane of E. Right: zoom on the pore."),
    fig("figures/bowl_R10_top.png", 0.42 * W,
        "Figure 4. Top view in the plane of the hot spot, 785 nm: two lobes on the rim along the polarisation, "
        "as in Fig. 1E of the paper."),
    PageBreak(),

    P("4. What sets the resonance and the enhancement", h1),
    fig("figures/bowl_sweep_h3.png", 0.55 * W,
        "Figure 5. Bowl pore, R = 10 nm, sharp rim, plane wave, 1 nm grid: resonance wavelength (blue) and |E|<super>2</super> "
        "at 785 nm (red) versus the Au thickness at the rim h<sub>3</sub>."),
    P(f"<b>Rim thickness.</b> Thinning the Au at the rim from 10 to 2.5 nm moves the resonance from "
      f"{lam('rf_bowl_R10_h10_r1000')} to {lam('rf_bowl_R10_h2.5_r1000')} nm (Fig. 5), about 12-36 nm per nanometre of "
      f"Au, most steeply for the thinnest rims. Table S1 gives h<sub>3</sub> as 2.5-10 nm and Fig. S2 as 5-10 nm, so the 785 nm of Fig. S4 lies inside the range "
      f"spanned by the published geometry; with h<sub>3</sub> = 3 nm the model resonates at {lam('fit_bowl_R10_h3_r1500')} nm. "
      f"Details not given in the paper (exact bowl profile near the pore, the 2 nm Ti adhesion layer, the 5-10 nm Au "
      f"overcoat on the pore wall) act on the same thin rim and are expected to shift the resonance by similar amounts."),
    P(f"<b>Pore radius.</b> With the same rim, smaller pores resonate at shorter wavelength, as in Fig. S4 (Fig. 1). A 40 nm "
      f"pore with h<sub>3</sub> = 5 nm resonates at {lam('rf_bowl_R20_r1000')} nm."),
    P(f"<b>Absolute |E|<super>2</super>.</b> The hot spot sits on the edge of the rim. For a sharp 90&deg; edge the peak "
      f"field grows without limit as the mesh is refined (R = 10 nm, h<sub>3</sub> = 5 nm: {mx('rf_bowl_R10_r1000')}, "
      f"{mx('rf_bowl_R10_r1500')} and {mx('rf_bowl_R10_r2000')} on 1, 0.67 and 0.5 nm grids), while the resonance "
      f"wavelength stays at {lam('rf_bowl_R10_r1500')} nm. Rounding the edge by 1 nm lowers the peak, but a 1 nm radius is "
      f"itself only resolved on grids well below 0.5 nm. Converged absolute enhancements therefore require the actual edge "
      f"radius of the fabricated rim and a mesh finer than that radius; the value reported in Fig. S4 depends on the same "
      f"choices in the COMSOL model."),
    fig("figures/hotspot_spectra.png", 0.62 * W,
        "Figure 6. Maximum |E|<super>2</super>/|E<sub>0</sub>|<super>2</super> next to the rim versus wavelength for "
        "bowl and conventional pores. Absolute values are mesh dependent (see text); the peak positions are converged."),
    PageBreak(),

    P("5. Particle in the 200 nm Au nanohole (Nat. Commun. 2019)", h1),
    P("Full 3D model at 785 nm: 200 nm hole through 100 nm Au on 100 nm SiN, water, plane wave from the Au side polarised "
      "along x; one period of a 400 nm hole array (the device is an array; the periodic cell also keeps the incident wave "
      "clean). Gold is a single Drude pole fitted exactly to the Rakic permittivity at 785 nm, which gives the exact "
      "frequency-domain solution at that wavelength. The nanourchin is replaced by a smooth 50 nm sphere at mid-height of the "
      "Au, with its surface 5 or 10 nm from the wall along the polarisation."),
    table([["case", "2 nm grid", "1.5 nm grid"],
           ["hole only: maximum (upper rim)", mx("pip_hole_r500", "max_xz"), mx("pip_hole_r667", "max_xz")],
           ["sphere, 10 nm gap: maximum", mx("pip_g10_r500", "max_xz"), mx("pip_g10_r667", "max_xz")],
           ["sphere, 10 nm gap: gap centre", mx("pip_g10_r500", "gap_centre"), mx("pip_g10_r667", "gap_centre")],
           ["sphere, 5 nm gap: maximum", mx("pip_g5_r500", "max_xz"), mx("pip_g5_r667", "max_xz")],
           ["sphere, 5 nm gap: gap centre", mx("pip_g5_r500", "gap_centre"), mx("pip_g5_r667", "gap_centre")]],
          [7 * cm, 3 * cm, 3 * cm]),
    P("Table 3. |E|<super>2</super>/|E<sub>0</sub>|<super>2</super> at 785 nm in the water.", small),
    P("The sphere couples to the hole wall and creates a hot spot in the particle-wall gap along the polarisation, as in "
      "Fig. 1e of the paper. For a 5 nm gap it is the strongest field in the hole; for a 10 nm gap it is comparable to the "
      "hole rim. The hole-rim value is stable between the two grids; the gap values are not yet converged "
      "(5-7 cells across a 10 nm gap, 2-3 across 5 nm). A uniform 3D grid fine enough for few-nanometre gaps or urchin tips "
      "exceeds the computing time available to me (one 1.5 nm run takes 3 h on 4 cores); a locally refined mesh (FEM, or "
      "FDTD with mesh override) would be needed."),
    fig("figures/pip_g10_maps.png", W,
        "Figure 7. 50 nm Au sphere 10 nm from the wall of a 200 nm Au nanohole, 785 nm, 1.5 nm grid: side view in the plane of "
        "E (left) and top view at mid-height of the Au (right)."),
    PageBreak(),

    P("6. Summary and next steps", h1),
    P("The open-source workflow reproduces exact Mie theory and the conventional-pore results of Fig. S4, and the bowl-pore "
      "resonances of Fig. S4 within the range allowed by the published geometry. The remaining differences come from the "
      "rim geometry (thickness, edge radius, Ti and Au overcoat) and, for absolute enhancements, from the mesh at the rim."),
    P("To make the comparison quantitative I would need the COMSOL geometry (or the exact rim profile and thickness), the "
      "mesh size at the rim and the illumination side. With these, the natural next steps are (i) converged enhancement "
      "maps of the bowl pore for your current pore sizes and laser, (ii) the clustering states of Au particles in the pore "
      "from your Raman-feedback work, and (iii) Purcell/LDOS maps for the SERS emission inside the hot spot, which is the "
      "subject of my current work with Dr. Bagheri Harouni."),
    P("Appendix: numerical notes", h1),
    P("&bull; Cylindrical runs: 2D (r, z) cell of 1.25 x 0.88 &mu;m (Gaussian beam) or 0.75 x 0.88 &mu;m (plane wave) with "
      "0.25 &mu;m PML on all sides; broadband pulse, DFT fields recorded until they decay to 10<sup>-6</sup>.<br/>"
      "&bull; The PML crossing the Au film is stable with the refitted gold; with the 6-pole Rakic model of the Meep library "
      "the fields diverge (NaN) on &le; 1 nm grids for h<sub>3</sub> &le; 5 nm, and halving the Courant number does not "
      "cure it.<br/>"
      "&bull; 3D runs: periodic 400 nm cell, PML along z only, mirror symmetry y &rarr; -y.<br/>"
      "&bull; All runs were executed in parallel on GitHub Actions (4 cores per case); scripts, data and figures are "
      "available on request.", body),
]
SimpleDocTemplate("Sadidi_nanopore_FDTD_report.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Plasmonic gold nanopores at 785 nm (Meep FDTD)",
                  author="Amin Hossain Sadidi").build(story)
print("written Sadidi_nanopore_FDTD_report.pdf")
