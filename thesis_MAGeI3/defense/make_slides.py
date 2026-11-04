# -*- coding: utf-8 -*-
"""Defense presentation v2 - clean 16:9 design (python-pptx)."""
import os
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures_scaps")
OUT = os.path.join(HERE, "Defense_Presentation_MAGeI3.pptx")

NAVY = RGBColor(0x14, 0x2B, 0x52)
ACC = RGBColor(0xE8, 0x74, 0x3B)      # orange accent (MAGeI3 colour)
INK = RGBColor(0x22, 0x26, 0x2E)
MUTE = RGBColor(0x5B, 0x64, 0x72)
CARD = RGBColor(0xF3, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
W, H = Cm(33.867), Cm(19.05)

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
N = [0]


def _font(run, size, bold=False, color=INK):
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color
    run.font.name = "Times New Roman"
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:cs",):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {}); rpr.append(el)
        el.set("typeface", "B Nazanin")


def box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Cm(x), Cm(y), Cm(w), Cm(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
    return s


def para(tf, txt, size, bold=False, color=INK, align="right", first=False, space=8, bullet=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    if align == "right":
        p.alignment = PP_ALIGN.RIGHT; pPr.set("rtl", "1")
    elif align == "center":
        p.alignment = PP_ALIGN.CENTER; pPr.set("rtl", "1")
    else:
        p.alignment = PP_ALIGN.LEFT
    if bullet:
        pPr.set("marR", str(Cm(0.7))); pPr.set("indent", str(-Cm(0.6)))
        bu = pPr.makeelement(qn("a:buChar"), {"char": "■"})
        bc = pPr.makeelement(qn("a:buClr"), {}); sc = bc.makeelement(qn("a:srgbClr"), {"val": "E8743B"}); bc.append(sc)
        bs = pPr.makeelement(qn("a:buSzPct"), {"val": "70000"})
        pPr.append(bc); pPr.append(bs); pPr.append(bu)
    p.space_after = Pt(space)
    r = p.add_run(); r.text = txt; _font(r, size, bold, color)
    return p


def textbox(slide, x, y, w, h, items, size=20, color=INK, anchor="top", bullet=True, align="right", bold_first=False):
    tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE}[anchor]
    for i, it in enumerate(items):
        para(tf, it, size, bold=(bold_first and i == 0), color=color, align=align, first=(i == 0), bullet=bullet,
             space=10)
    return tb


def header(slide, title, section=""):
    box(slide, 0, 0, 33.867, 2.6, NAVY)
    box(slide, 0, 2.6, 33.867, 0.18, ACC)
    tb = slide.shapes.add_textbox(Cm(1.2), Cm(0.35), Cm(31.4), Cm(2.0))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, title, 28, bold=True, color=WHITE, first=True)
    N[0] += 1
    ft = slide.shapes.add_textbox(Cm(1.0), Cm(18.0), Cm(31.8), Cm(0.8))
    p = ft.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = f"{N[0] + 1}"; _font(r, 12, color=MUTE)
    if section:
        p2 = ft.text_frame.paragraphs[0]
        r2 = p2.add_run(); r2.text = "     " + section; _font(r2, 12, color=MUTE)


def picture(slide, name, x, y, max_w, max_h):
    path = os.path.join(FIG, name)
    iw, ih = Image.open(path).size
    w = max_w; h = w * ih / iw
    if h > max_h:
        h = max_h; w = h * iw / ih
    slide.shapes.add_picture(path, Cm(x + (max_w - w) / 2), Cm(y + (max_h - h) / 2), Cm(w), Cm(h))


def kpi(slide, x, y, w, value, label, color=ACC):
    box(slide, x, y, w, 3.0, CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tb = slide.shapes.add_textbox(Cm(x), Cm(y + 0.15), Cm(w), Cm(1.7))
    para(tb.text_frame, value, 30, bold=True, color=color, align="center", first=True, space=0)
    tb = slide.shapes.add_textbox(Cm(x), Cm(y + 1.85), Cm(w), Cm(1.0))
    para(tb.text_frame, label, 15, color=MUTE, align="center", first=True, space=0)


def fig_slide(title, fig, points, kpis=None, section=""):
    s = prs.slides.add_slide(BLANK); header(s, title, section)
    picture(s, fig, 0.8, 3.4, 19.6, 14.4)
    x0, w0 = 21.0, 12.0
    y = 3.6
    if kpis:
        kw = (w0 - 0.4 * (len(kpis) - 1)) / len(kpis)
        for i, (v, l, c) in enumerate(kpis):
            kpi(s, x0 + i * (kw + 0.4), y, kw, v, l, c)
        y += 3.6
    box(s, x0, y, w0, 17.6 - y, CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    textbox(s, x0 + 0.3, y + 0.3, w0 - 0.6, 17.6 - y - 0.6, points, size=21, anchor="middle")
    return s


def text_slide(title, cards, section=""):
    """cards: list of (heading, [lines]) laid out in a grid"""
    s = prs.slides.add_slide(BLANK); header(s, title, section)
    n = len(cards); cols = 2 if n > 2 else n; rows = (n + cols - 1) // cols
    gw, gh = 31.4, 14.2
    cw = (gw - 0.8 * (cols - 1)) / cols; ch = (gh - 0.8 * (rows - 1)) / rows
    for i, (hd, lines) in enumerate(cards):
        r, c = divmod(i, cols)
        x = 1.2 + gw - (c + 1) * cw - c * 0.8      # right-to-left order
        y = 3.5 + r * (ch + 0.8)
        box(s, x, y, cw, ch, CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        box(s, x + cw - 0.35, y + 0.4, 0.18, 1.1, ACC)
        tb = s.shapes.add_textbox(Cm(x + 0.4), Cm(y + 0.3), Cm(cw - 1.0), Cm(1.4))
        para(tb.text_frame, hd, 22, bold=True, color=NAVY, first=True, space=0)
        textbox(s, x + 0.4, y + 1.8, cw - 1.0, ch - 2.0, lines, size=22)
    return s


# ------------------------------------------------------------------ 1 title
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 33.867, 19.05, NAVY)
box(s, 0, 12.6, 33.867, 0.2, ACC)
tb = s.shapes.add_textbox(Cm(2.5), Cm(2.2), Cm(28.9), Cm(7.5)); tf = tb.text_frame; tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tf, "بررسی تأثیر لایه‌های میان‌انداز اکسید فلزی V₂O₅، WOₓ و NiOₓ", 34, True, WHITE, "center", True, 4)
para(tf, "بر خواص الکتریکی فصل مشترک HTL در سلول‌های خورشیدی پروسکایتی MAGeI₃", 34, True, WHITE, "center", False, 4)
tb = s.shapes.add_textbox(Cm(2.5), Cm(9.8), Cm(28.9), Cm(1.6))
para(tb.text_frame, "پایان‌نامه‌ی کارشناسی ارشد  |  شبیه‌سازی با SCAPS-1D", 20, False, RGBColor(0xC9, 0xD3, 0xE6), "center", True)
tb = s.shapes.add_textbox(Cm(2.5), Cm(13.4), Cm(28.9), Cm(4.5)); tf = tb.text_frame
para(tf, "ارائه‌دهنده: ..............................", 20, False, WHITE, "center", True, 6)
para(tf, "استاد راهنما: دکتر ..............................", 20, False, WHITE, "center", False, 6)
para(tf, "دانشگاه کاشان", 20, True, WHITE, "center", False, 6)

# ------------------------------------------------------------------ 2 outline
text_slide("فهرست مطالب", [
    ("مقدمه", ["انگیزه و هدف پژوهش", "ساختار سلول و هم‌ترازی نوارها"]),
    ("روش", ["SCAPS-1D 3.3.06", "پروتکل هفت‌مرحله‌ای بهینه‌سازی"]),
    ("نتایج", ["بهینه‌سازی ضخامت لایه‌ها", "اثر نوع و ضخامت بافر", "J-V، P-V و IPCE"]),
    ("تحلیل و جمع‌بندی", ["سازوکار فیزیکی و آزمون آن", "V₂O₅ و معیار طراحی بافر", "نتیجه‌گیری و پیشنهادها"]),
])
# ------------------------------------------------------------------ 3 motivation
text_slide("انگیزه و هدف پژوهش", [
    ("چرا MAGeI₃؟", ["پروسکایت بدون سرب و کم‌سمیت", "گاف نواری ۱٫۹ الکترون‌ولت", "مناسب سلول‌های تک‌پیوندی و تاندم"]),
    ("مسئله", ["فصل مشترک جاذب/HTL محل اصلی تلفات بازترکیب", "انتقال حفره به HTL با افت انرژی همراه است"]),
    ("ایده", ["درج یک لایه‌ی میان‌انداز اکسید فلزی", "سه گزینه: V₂O₅، WOₓ و NiOₓ"]),
    ("هدف", ["تعیین اثر هر بافر بر Voc، Jsc، FF و PCE", "شناسایی سازوکار فیزیکی و معیار طراحی"]),
], "مقدمه")
# ------------------------------------------------------------------ 4 structure
s = prs.slides.add_slide(BLANK); header(s, "ساختار سلول و هم‌ترازی نوارهای انرژی", "مقدمه")
picture(s, "Fig4_01_structure_bands.png", 0.8, 3.3, 21.5, 11.6)
box(s, 23.0, 3.6, 10.0, 13.9, CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
textbox(s, 23.3, 3.9, 9.4, 13.3, [
    "ITO / TiO₂ / MAGeI₃ / بافر / Spiro / Au",
    "WOₓ و NiOₓ: پلکان حفره و سد الکترون",
    "V₂O₅ (جدول ۳-۲): سد ۰٫۶۹ الکترون‌ولتی برای حفره",
    "تراز فرمی Spiro و Au کم‌عمق‌تر از جاذب"], size=19, anchor="middle")
tb = s.shapes.add_textbox(Cm(1.2), Cm(15.3), Cm(21.0), Cm(2.4))
para(tb.text_frame, "تابش AM1.5G از سمت ITO  •  دما ۳۰۰ کلوین  •  تابع کار طلا ۵٫۱ الکترون‌ولت", 17, color=MUTE, align="center", first=True)
# ------------------------------------------------------------------ 5 method
text_slide("روش: پروتکل هفت‌مرحله‌ای در SCAPS-1D", [
    ("بهینه‌سازی ضخامت", ["۱. جاذب MAGeI₃: ۱۰۰ تا ۸۰۰ nm", "۲. TiO₂: ۱ تا ۴۰۰ nm", "۳. Spiro-OMeTAD: ۱ تا ۲۰۰ nm"]),
    ("بافر و مقایسه", ["۴. نوع و ضخامت بافر: ۰ تا ۵۰ nm", "۵ و ۶. J-V و P-V ساختارهای بهینه", "۷. طیف IPCE"]),
    ("تحلیل‌های تکمیلی", ["مؤلفه‌های بازترکیب، C-V و موت-شاتکی", "دما، چگالی نقص، آلایش لایه‌ها", "آفست نوار V₂O₅ و ثابت دی‌الکتریک بافر"]),
    ("اجرا", ["۱۱۲ شبیه‌سازی خودکار با اسکریپت SCAPS", "پارامترها از جدول‌های ۳-۱ تا ۳-۴"]),
], "روش")
# ------------------------------------------------------------------ results
fig_slide("گام ۱: بهینه‌سازی ضخامت جاذب MAGeI₃", "Fig4_03_step1_absorber.png",
          ["Jsc و بازده با ضخامت افزایش می‌یابند", "بالای ۶۰۰ nm اشباع می‌شوند", "علت: طول نفوذ الکترون ≈ ۰٫۵ µm"],
          [("800 nm", "ضخامت بهینه", NAVY), ("16.05 %", "بازده", ACC)], "نتایج")
fig_slide("گام‌های ۲ و ۳: ضخامت TiO₂ و Spiro-OMeTAD", "Fig4_04_step2_ETL.png",
          ["TiO₂ یک نانومتری: پیوند ناقص، FF پایین", "TiO₂ ضخیم‌تر: جذب پارازیتی نور فرابنفش",
           "Spiro: حساسیت کم؛ ضخامت زیاد = مقاومت سری"],
          [("50 nm", "TiO₂ بهینه", NAVY), ("50 nm", "Spiro بهینه", NAVY)], "نتایج")
fig_slide("گام ۴: اثر نوع و ضخامت بافر", "Fig4_06_step4_buffer.png",
          ["WOₓ و NiOₓ هر دو بازده را بالا می‌برند", "بهبود عمدتاً از Jsc و FF", "اشباع در حدود ۳۰ nm",
           "V₂O₅: SCAPS همگرا نشد (سد حفره)"],
          [("+0.48 %", "WOₓ", ACC), ("+0.31 %", "NiOₓ", RGBColor(0x2C, 0xA0, 0x2C))], "نتایج")
# comparison table slide
s = prs.slides.add_slide(BLANK); header(s, "گام‌های ۵ و ۶: مقایسه‌ی ساختارهای بهینه", "نتایج")
picture(s, "Fig4_07_JV_PV.png", 0.8, 3.3, 32.2, 7.6)
rows = [("ساختار", "Voc (V)", "Jsc (mA/cm²)", "FF (%)", "PCE (%)"),
        ("بدون بافر", "1.495", "13.95", "77.80", "16.23"),
        ("NiOₓ", "1.496", "14.16", "78.04", "16.54"),
        ("WOₓ", "1.497", "14.27", "78.18", "16.71"),
        ("V₂O₅", "—", "—", "—", "عدم همگرایی")]
tbl = s.shapes.add_table(len(rows), 5, Cm(4.5), Cm(11.3), Cm(24.8), Cm(6.2)).table
for i, row in enumerate(rows):
    for j, val in enumerate(row[::-1]):
        c = tbl.cell(i, j); c.text = ""
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p._p.get_or_add_pPr().set("rtl", "1")
        r = p.add_run(); r.text = val
        _font(r, 18, bold=(i == 0 or i == 3), color=WHITE if i == 0 else (ACC if i == 3 else INK))
        c.fill.solid(); c.fill.fore_color.rgb = NAVY if i == 0 else (RGBColor(0xFD, 0xEE, 0xE5) if i == 3 else (CARD if i % 2 else WHITE))
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
fig_slide("گام ۷: بازده کوانتومی خارجی (IPCE)", "Fig4_09_EQE.png",
          ["لبه‌ی جذب ≈ ۶۵۳ nm (گاف ۱٫۹ eV)", "افت زیر ۳۸۰ nm: جذب ITO و TiO₂", "Jsc انتگرالی با J-V سازگار (۱ تا ۲٪)"],
          [("≈ 95 %", "بیشینه‌ی IPCE", NAVY)], "نتایج")
fig_slide("سازوکار: مؤلفه‌های جریان بازترکیب", "Fig4_10_recombination_components.png",
          ["بازترکیب SRH حجمی در اتصال کوتاه کم می‌شود", "کاهش بازترکیب ≈ افزایش Jsc (۰٫۳۲)",
           "علت: کاهش تهی‌شدگی حفره در پشت جاذب", "بازترکیب فصل مشترک ناچیز است"],
          [("2.41", "بدون بافر (mA/cm²)", INK), ("2.09", "WOₓ (mA/cm²)", ACC)], "تحلیل")
fig_slide("آزمون مستقیم سازوکار: ثابت دی‌الکتریک بافر", "Fig4_21_buffer_permittivity.png",
          ["پیش‌بینی: εr کوچک‌تر ← افت پتانسیل بیشتر در بافر", "نتیجه: بازده با کاهش εr پیوسته افزایش می‌یابد",
           "εr = 12 (مانند NiOₓ) ≈ بازده NiOₓ", "← علت برتری WOₓ (εr = 6)"],
          [("16.28 %", "εr = 24", INK), ("16.98 %", "εr = 3", ACC)], "تحلیل")
fig_slide("V₂O₅: معیار طراحی آفست نوار ظرفیت", "Fig4_18_V2O5_band_offset.png",
          ["سد بزرگ‌تر ← افت Voc و FF", "VBO = +۰٫۴۹ eV: FF = ۵۰٪", "VBO = +۰٫۶۹ eV (جدول ۳-۲): عدم همگرایی",
           "بافر مؤثر: −۰٫۲ ≤ VBO ≤ +۰٫۱ eV"],
          [("16.74 %", "بهترین (VBO ≈ 0)", ACC), ("7.87 %", "VBO = +0.49 eV", INK)], "تحلیل")
fig_slide("موت-شاتکی و اثر دما", "Fig4_13_CV_MottSchottky.png",
          ["N استخراجی با آلایش خالص جاذب سازگار است", "بافرها پیوند اصلی را تغییر نمی‌دهند",
           "ضریب دمایی Voc ≈ −۱٫۷ mV/K", "افت بازده با دما در حضور بافر کمتر است"],
          [("1.40 V", "Vbi", NAVY), ("9.3×10¹⁶", "N (cm⁻³)", NAVY)], "تحلیل")
fig_slide("چگالی نقص جاذب: مهم‌ترین عامل محدودکننده", "Fig4_17_absorber_Nt.png",
          ["کاهش Nt از 10¹⁶ به 10¹⁴ cm⁻³", "Voc حدود ۶۰ mV در هر دهه افزایش می‌یابد", "آلایش Spiro ≥ 10¹⁸ cm⁻³ لازم است",
           "آلایش WOₓ = 10¹⁸ cm⁻³ ← بازده ۱۷٫۰۶٪"],
          [("16.2 %", "Nt = 10¹⁶", INK), ("22.8 %", "Nt = 10¹⁴", ACC)], "تحلیل")
# conclusion
text_slide("نتیجه‌گیری", [
    ("ساختار بهینه", ["ITO/TiO₂(50)/MAGeI₃(800)/WOₓ(50)/Spiro(50)/Au", "بازده ۱۶٫۷۱٪ (۳٪ بهبود نسبی)"]),
    ("مقایسه‌ی بافرها", ["WOₓ > NiOₓ > بدون بافر", "V₂O₅ با پارامترهای فصل ۳ مانع عبور حفره است"]),
    ("سازوکار", ["کاهش تهی‌شدگی حفره و بازترکیب SRH در پشت جاذب", "تأیید با تغییر ثابت دی‌الکتریک و آلایش بافر"]),
    ("معیار طراحی بافر", ["VBO نزدیک صفر", "ثابت دی‌الکتریک کوچک", "آلایش نوع p حدود 10¹⁸ cm⁻³"]),
], "جمع‌بندی")
text_slide("پیشنهادها برای کارهای آینده", [
    ("V₂O₅", ["بازنگری پارامترها با داده‌های تجربی UPS/XPS", "فعال‌سازی تونل‌زنی در SCAPS"]),
    ("فصل مشترک", ["Nit واقعی (10¹⁰ تا 10¹³ cm⁻²)", "اثر passivation بافر"]),
    ("طراحی", ["بهینه‌سازی هم‌زمان اتصال پشتی و بافر", "ساختار بدون HTL آلی"]),
    ("تجربی", ["ساخت ساختار بهینه", "مقایسه‌ی J-V، IPCE و C-V با شبیه‌سازی"]),
], "جمع‌بندی")
# thanks
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 33.867, 19.05, NAVY); box(s, 12.9, 11.0, 8.0, 0.2, ACC)
tb = s.shapes.add_textbox(Cm(2), Cm(6.0), Cm(29.8), Cm(4.5)); tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
para(tb.text_frame, "با سپاس از توجه شما", 44, True, WHITE, "center", True)
tb = s.shapes.add_textbox(Cm(2), Cm(11.8), Cm(29.8), Cm(2))
para(tb.text_frame, "پرسش و پاسخ", 24, False, RGBColor(0xC9, 0xD3, 0xE6), "center", True)

prs.save(OUT)
print("wrote", OUT, len(prs.slides), "slides")
