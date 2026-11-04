# -*- coding: utf-8 -*-
"""Defense presentation (PowerPoint, 16:9) from the SCAPS figures."""
import os
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures_scaps")
OUT = os.path.join(HERE, "Defense_Presentation_MAGeI3.pptx")
NAVY = RGBColor(0x1F, 0x3B, 0x73)

prs = Presentation()
prs.slide_width, prs.slide_height = Cm(33.867), Cm(19.05)
BLANK = prs.slide_layouts[6]


def rtl(par):
    par.alignment = PP_ALIGN.RIGHT
    par._p.get_or_add_pPr().set("rtl", "1")


def text(slide, x, y, w, h, lines, size=20, bold=False, color=None, center=False):
    tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        rtl(p)
        if center:
            p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = ln
        r.font.size = Pt(size); r.font.bold = bold; r.font.name = "B Nazanin"
        r._r.get_or_add_rPr().append(r._r.makeelement(qn("a:cs"), {"typeface": "B Nazanin"}))
        if color:
            r.font.color.rgb = color
        p.space_after = Pt(6)
    return tb


def slide(title, bullets=None, fig=None, fig_w=19.0):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Cm(2.4)); bar.fill.solid(); bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    text(s, 1, 0.35, 31.8, 2, [title], size=28, bold=True, color=RGBColor(255, 255, 255))
    if fig:
        s.shapes.add_picture(os.path.join(FIG, fig), Cm(0.8), Cm(3.0), width=Cm(fig_w))
        if bullets:
            text(s, fig_w + 1.2, 3.2, 33.0 - fig_w - 1.6, 15, ["• " + b for b in bullets], size=17)
    elif bullets:
        text(s, 1.5, 3.2, 30.8, 15, ["• " + b for b in bullets], size=22)
    return s


# 1 title
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height); bg.fill.solid(); bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
text(s, 2, 3.0, 29.8, 6, ["بررسی تأثیر لایه‌های میان‌انداز اکسید فلزی V₂O₅، WOₓ و NiOₓ بر خواص الکتریکی فصل مشترک HTL "
                          "در سلول‌های خورشیدی پروسکایتی MAGeI₃"], size=32, bold=True, color=RGBColor(255, 255, 255), center=True)
text(s, 2, 10.5, 29.8, 6, ["ارائه‌دهنده: ..............................", "استاد راهنما: دکتر ..............................",
                           "دانشگاه کاشان"], size=22, color=RGBColor(230, 230, 230), center=True)

slide("انگیزه و هدف پژوهش", [
    "پروسکایت‌های سربی بازده بالا دارند اما سمی‌اند؛ MAGeI₃ (Eg = 1.9 eV) جایگزین بدون سرب است.",
    "فصل مشترک جاذب/HTL یکی از مهم‌ترین محل‌های تلفات بازترکیب است.",
    "پرسش: درج یک لایه‌ی بافر اکسید فلزی (V₂O₅، WOₓ، NiOₓ) چه اثری بر این فصل مشترک و بازده دارد؟ سازوکار آن چیست؟",
    "ابزار: شبیه‌سازی یک‌بعدی با SCAPS-1D 3.3.06 (۱۱۲ شبیه‌سازی خودکار با اسکریپت SCAPS)."])
slide("ساختار سلول و هم‌ترازی نوارها", [
    "ITO / TiO₂ / MAGeI₃ / buffer / Spiro-OMeTAD / Au",
    "WOₓ و NiOₓ: پلکان حفره (VBO ≈ −0.3 eV) و سد الکترون (> 1.4 eV)",
    "V₂O₅ (پارامترهای فصل ۳): سد حفره‌ی 0.69 eV",
    "تراز فرمی Spiro و Au کم‌عمق‌تر از جاذب ← تهی‌شدگی حفره در پشت جاذب"], "Fig4_01_structure_bands.png")
slide("روش: پروتکل هفت‌مرحله‌ای در SCAPS", [
    "۱) ضخامت جاذب ۱۰۰ تا ۸۰۰ nm   ۲) ضخامت TiO₂ ۱ تا ۴۰۰ nm   ۳) ضخامت Spiro ۱ تا ۲۰۰ nm",
    "۴) نوع و ضخامت بافر ۰ تا ۵۰ nm   ۵-۶) J-V و P-V ساختارهای بهینه   ۷) IPCE",
    "تحلیل‌های تکمیلی: مؤلفه‌های بازترکیب، C-V و موت-شاتکی، دما، چگالی نقص، آفست نوار V₂O₅، آلایش HTL، آلایش و ثابت دی‌الکتریک بافر",
    "شرایط: AM1.5G، 300 K، اتصال Au با تابع کار 5.1 eV؛ پارامترها از جدول‌های ۳-۱ تا ۳-۴"])
slide("گام ۱: ضخامت جاذب MAGeI₃", ["Jsc و PCE با ضخامت افزایش و بالای ۶۰۰ nm اشباع می‌شوند",
                                     "علت اشباع: طول نفوذ الکترون ≈ 0.5 µm", "بهینه: 800 nm (PCE = 16.05 %)"], "Fig4_03_step1_absorber.png")
slide("گام‌های ۲ و ۳: ضخامت TiO₂ و Spiro", ["TiO₂ = 1 nm: پیوند ناقص، FF پایین", "TiO₂ > 50 nm: جذب پارازیتی UV",
                                           "Spiro: حساسیت کم؛ ضخامت زیاد ← مقاومت سری", "بهینه: TiO₂ = 50 nm و Spiro = 50 nm"],
      "Fig4_04_step2_ETL.png")
slide("گام ۴: نوع و ضخامت بافر", ["WOₓ و NiOₓ هر دو بازده را افزایش می‌دهند؛ WOₓ بهتر",
                                  "بهبود عمدتاً از Jsc و FF؛ اشباع در حدود 30 nm",
                                  "V₂O₅: SCAPS در هیچ ضخامتی همگرا نشد (سد حفره)"], "Fig4_06_step4_buffer.png")
slide("گام‌های ۵ و ۶: مقایسه‌ی ساختارهای بهینه", ["بدون بافر: PCE = 16.23 %", "NiOₓ: PCE = 16.54 %",
                                                 "WOₓ: PCE = 16.71 % (+3.0 % نسبی)", "Voc تقریباً ثابت (≈ 1.50 V)"], "Fig4_07_JV_PV.png")
slide("گام ۷: IPCE", ["لبه‌ی جذب ≈ 653 nm (Eg = 1.9 eV)", "افت زیر 380 nm: جذب ITO و TiO₂",
                      "Jsc انتگرالی با J-V در حد ۱ تا ۲ درصد سازگار"], "Fig4_09_EQE.png")
slide("سازوکار: مؤلفه‌های بازترکیب (خروجی SCAPS)", ["بازترکیب SRH حجمی در Jsc:", "بدون بافر 2.41 → WOₓ 2.09 mA/cm²",
                                                    "کاهش بازترکیب (0.32) ≈ افزایش Jsc (0.32)",
                                                    "بازترکیب فصل مشترک ناچیز (Nit = 1.1×10⁵ cm⁻²)"], "Fig4_10_recombination_components.png")
slide("آزمون مستقیم سازوکار: ثابت دی‌الکتریک بافر", ["پیش‌بینی: εr کوچک‌تر ← افت پتانسیل بیشتر در بافر ← بازترکیب کمتر در جاذب",
                                                    "نتیجه‌ی SCAPS: εr = 24 → 16.28 %   ...   εr = 3 → 16.98 %",
                                                    "εr = 12 (≈ NiOₓ) ≈ بازده NiOₓ ← علت برتری WOₓ"], "Fig4_21_buffer_permittivity.png")
slide("V₂O₅: معیار طراحی آفست نوار ظرفیت", ["VBO = −0.41 eV: 15.93 %", "VBO ≈ 0: بیشینه 16.74 %",
                                            "VBO = +0.49 eV: FF = 50 %، PCE = 7.9 %", "VBO = +0.69 eV (جدول ۳-۲): عدم همگرایی",
                                            "بافر مؤثر: −0.2 ≤ VBO ≤ +0.1 eV"], "Fig4_18_V2O5_band_offset.png")
slide("موت-شاتکی و اثر دما", ["Vbi ≈ 1.40 V و N ≈ 9.3×10¹⁶ cm⁻³ (سازگار با آلایش خالص جاذب)",
                              "بافرها پیوند اصلی را تغییر نمی‌دهند", "dVoc/dT ≈ −1.7 mV/K؛ افت بازده با بافر کمتر"],
      "Fig4_13_CV_MottSchottky.png")
slide("چگالی نقص جاذب و آلایش لایه‌ها", ["Nt: 10¹⁶ → 10¹⁴ cm⁻³ ← PCE: 16.2 → 22.8 %",
                                         "آلایش Spiro ≥ 10¹⁸ cm⁻³ لازم است", "آلایش WOₓ = 10¹⁸ cm⁻³ ← PCE = 17.06 %"],
      "Fig4_17_absorber_Nt.png")
slide("نتیجه‌گیری", [
    "ساختار بهینه: ITO/TiO₂(50)/MAGeI₃(800)/WOₓ(50)/Spiro(50)/Au با PCE = 16.71 %",
    "WOₓ > NiOₓ > بدون بافر؛ V₂O₅ با پارامترهای فصل ۳ مانع عبور حفره است",
    "سازوکار: کاهش تهی‌شدگی حفره و بازترکیب SRH در پشت جاذب؛ تأیید با تغییر εr و آلایش بافر",
    "معیار طراحی بافر: VBO ≈ 0، εr کوچک، آلایش p حدود 10¹⁸ cm⁻³"])
slide("پیشنهادها برای کارهای آینده", [
    "بازنگری پارامترهای V₂O₅ با داده‌های تجربی (UPS/XPS) و فعال‌سازی تونل‌زنی در SCAPS",
    "بررسی Nit واقعی (10¹⁰ تا 10¹³ cm⁻²) و اثر passivation بافر",
    "بهینه‌سازی هم‌زمان تابع کار اتصال پشتی و بافر؛ ساختار بدون HTL آلی",
    "ساخت تجربی ساختار بهینه و مقایسه با شبیه‌سازی"])
s = prs.slides.add_slide(BLANK)
text(s, 2, 7, 29.8, 4, ["با سپاس از توجه شما"], size=40, bold=True, color=NAVY, center=True)
prs.save(OUT)
print("wrote", OUT, len(prs.slides), "slides")
