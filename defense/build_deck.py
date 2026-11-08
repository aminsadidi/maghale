"""Builds defense_final.pptx from original.pptx: replaces the stock geometry picture (slide 6) with the real
schematic and inserts 5 data slides (theory, Purcell spectrum, monitor boxes, rod-vs-sphere charts, limitations)."""
import copy, os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

D = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(D, 'img')
INK, MUTED, LIGHT, ACC, BG, WHITE, GREY = (RGBColor.from_string(c) for c in ('1C1917', '555555', 'A8A29E', 'D97706', 'FAFAF9', 'FFFFFF', '78716C'))
FONT = 'Vazirmatn'
prs = Presentation(os.path.join(D, 'original.pptx'))
SW, SH = prs.slide_width, prs.slide_height
blank = next(l for l in prs.slide_layouts if l.name == 'BLANK')


def setfont(rPr):
    rPr.set('lang', 'fa-IR')
    for tag in ('a:latin', 'a:ea', 'a:cs'):
        e = rPr.find(qn(tag))
        if e is None: e = etree.SubElement(rPr, qn(tag))
        e.set('typeface', FONT)


def rtl(p):
    p.alignment = PP_ALIGN.RIGHT
    p._p.get_or_add_pPr().set('rtl', '1')


def text(slide, s, x, y, w, h, size=18, color=INK, bold=False, align='right', anchor=MSO_ANCHOR.TOP, name=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, m, 0)
    lines = s if isinstance(s, list) else [s]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = line; f = r.font
        f.size = Pt(size); f.color.rgb = color; f.bold = bold; f.name = FONT
        setfont(r._r.get_or_add_rPr())
        if align == 'right': rtl(p)
        elif align == 'center': p.alignment = PP_ALIGN.CENTER; p._p.get_or_add_pPr().set('rtl', '1')
        if i: p.space_before = Pt(6)
    if name: tb.name = name
    return tb


def new_slide(title, kicker=None):
    s = prs.slides.add_slide(blank)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    if kicker: text(s, kicker, 0.6, 0.45, 12.1, 0.4, 14, ACC, name='Kicker')
    text(s, title, 0.6, 0.8 if kicker else 0.6, 12.1, 0.9, 32, INK, bold=True, name='Title')
    return s


def card(slide, x, y, w, h, fill=WHITE):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.adjustments[0] = 0.06; c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.color.rgb = RGBColor.from_string('E7E5E4'); c.line.width = Pt(0.75)
    c.shadow.inherit = False
    return c


def picture(slide, path, x, y, w=None, h=None, name=None):
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if name: pic.name = name
    return pic


# ---------- 0. text corrections on the original slides ----------
def set_text(slide, shape_id, new, rtl_on=True):
    sh = next(x for x in slide.shapes if x.shape_id == shape_id)
    p = sh.text_frame.paragraphs[0]; runs = p.runs
    runs[0].text = new
    for r in runs[1:]: r._r.getparent().remove(r._r)
    if rtl_on: p._p.get_or_add_pPr().set('rtl', '1')
    return sh


def drop(slide, ids):
    for x in [x for x in slide.shapes if x.shape_id in ids]: x._element.getparent().remove(x._element)


S = prs.slides
set_text(S[0], 86, 'دفاع از پروژه‌ی کارشناسی')
set_text(S[0], 88, 'تحلیل و بهینه‌سازی برهم‌کنش گسیلنده‌ی کوانتومی با نانومیله‌ی کلاهک‌دار به روش FDTD سه‌بعدی')
set_text(S[1], 101, 'نیاز حیاتی به تولید فوتون‌های کاملاً منفرد و پرسرعت')
set_text(S[1], 103, 'تسریع چشمگیر نرخ گسیل توسط محیط ساختاریافته')
set_text(S[2], 115, 'جفت‌شدگی گسیلنده با مد پلاسمونی و تابش به فضای دوردست')
set_text(S[2], 117, 'اتلاف شدید اهمی و حرارتی در فواصل زیر ۵ نانومتر')
set_text(S[3], 127, 'حل سه‌بعدی معادلات ماکسول با روش FDTD')
set_text(S[3], 129, 'جداسازی دقیق نرخ تابش مفید از اتلاف اهمی')
set_text(S[3], 131, 'یافتن فاصله‌ی بهینه برای بیشینه‌سازی بازده کوانتومی')
set_text(S[4], 144, ' شرایط مرزی : جذب امواج بدون بازتاب')
for x in S[4].shapes:
    if x.shape_id == 5: x.left = Inches(6.85)
set_text(S[4], 5, 'PML', rtl_on=False)
s8 = S[7]
set_text(s8, 182, 'افزایش نرخ تابش فوتون‌ها نسبت به خلأ در طول موج تشدید')
ref = next(x for x in s8.shapes if x.shape_id == 182)
note = copy.deepcopy(ref._element); s8.shapes._spTree.append(note)
from pptx.shapes.autoshape import Shape as _Shape
nsh = _Shape(note, s8.shapes); nsh.top = ref.top + ref.height + Inches(0.1)
nsh.text_frame.paragraphs[0].runs[0].text = 'در گاف ۳ نانومتر؛ اما بازده در همین فاصله فقط ۶٪ است'
nsh.text_frame.paragraphs[0].runs[0].font.size = Pt(16); nsh.text_frame.paragraphs[0].runs[0].font.color.rgb = ACC
nsh._element.nvSpPr.cNvPr.set('id', '900'); nsh.name = 'Efficiency note'
for sid, t in ((190, 'پویش فاصله (گاف) در طول موج تشدید ۶۰۷ نانومتر'), (192, '۵/۵٪'), (195, '۷/۱٪'), (198, '۸/۷٪'),
               (193, 'تقویت تابشی ۲۳۲×؛ خاموشی شدید'), (196, 'تقویت تابشی ۱۰۴×'), (199, 'تقویت تابشی فقط ۸×')):
    set_text(S[8], sid, t)
set_text(S[9], 206, 'بازده در طول موج تشدید')
set_text(S[9], 207, '۵ تا ۹٪')
s208 = set_text(S[9], 208, 'از گاف ۳ تا ۲۰ نانومتر بازده فقط از ۵/۵ به ۸/۷ درصد می‌رسد؛ سقف آن را جذب طلا تعیین می‌کند، نه فاصله')
s208.left = Inches(3.25); s208.width = Inches(6.85); s208.height = Inches(0.8); s208.text_frame.word_wrap = True
set_text(S[10], 221, 'در گاف ۳ تا ۵ نانومتر، ۲۱ تا ۳۴ برابر تقویت تابشی بیشتر نسبت به کره‌ی هم‌حجم')
set_text(S[11], 231, 'عملکرد به عنوان فیلتر قطبشی نانومتری؛ در نانوکره‌ی هم‌حجم این نسبت فقط ۲/۴ است')
set_text(S[12], 240, 'پرهیز از فواصل زیر ۵ نانومتر (خاموشی)')
set_text(S[12], 241, 'بازده در تشدید ۵ تا ۹ درصد؛ محدود به جذب طلا')
set_text(S[12], 242, 'تقویت تابشی ۲۱ تا ۳۴ برابر کره‌ی هم‌حجم (گاف ۳ تا ۵ نانومتر)')
s15 = S[14]
drop(s15, {255, 258, 259, 261, 266, 267})
for x in s15.shapes:
    if x.shape_id in (262, 268, 269): x.top = x.top - Inches(0.84)

# ---------- 1. slide 6: real geometry schematic instead of the generic nanoparticle picture ----------
s6 = prs.slides[5]
pics = [sh for sh in s6.shapes if sh.shape_type == 13]
pos = (pics[0].left, pics[0].top, pics[0].width, pics[0].height)
for p in pics: p._element.getparent().remove(p._element)
g = s6.shapes.add_picture(os.path.join(IMG, 'geometry.png'), *pos); g.name = 'Geometry schematic'
s6.shapes._spTree.remove(g._element); s6.shapes._spTree.insert(2, g._element)

# ---------- 2. new: theory (key relations) ----------
th = new_slide('روابط کلیدی محاسبه', 'چارچوب نظری')
rows = [('eq_purcell.png', 'فاکتور پورسل: نرخ کل واپاشی نسبت به خلأ؛ از بخش موهومی تابع گرین پراکنده در محل گسیلنده'),
        ('eq_split.png', 'تفکیک توان: جعبه‌ی کوچک کل توان و جعبه‌ی بزرگ توان تابشی را می‌سنجد'),
        ('eq_near.png', 'سهم غیرتابشی در میدان نزدیک با عکس مکعب فاصله رشد می‌کند؛ ریشه‌ی خاموشی')]
for i, (img, cap) in enumerate(rows):
    y = 1.95 + i * 1.75
    card(th, 0.6, y, 12.1, 1.5)
    pic = picture(th, os.path.join(IMG, img), 0.85, y, w=(6.6, 6.6, 3.6)[i], name=f'Equation {i+1}')
    pic.top = Inches(y) + (Inches(1.5) - pic.height) // 2
    text(th, cap, 7.9, y + 0.25, 4.55, 1.0, 16, MUTED, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 3. new: Purcell spectrum ----------
ps = new_slide('طیف فاکتور پورسل (خروجی FDTD، گاف ۳ نانومتر)', 'نتایج شبیه‌سازی')
card(ps, 0.6, 1.9, 12.1, 4.15)
picture(ps, os.path.join(IMG, 'purcell.png'), 0.8, 2.15, w=11.7, name='Purcell spectrum')
text(ps, 'محور افقی: طول موج (متر)  |  محور عمودی: فاکتور پورسل', 0.6, 5.55, 12.1, 0.35, 12, LIGHT, align='center')
for x, t1, t2 in ((7.2, 'قله‌ی ۵۱۵ نانومتر: ۷۲۰۰', 'جذب بین‌نواری؛ تقریباً بدون تابش'),
                  (0.6, 'قله‌ی ۶۰۷ نانومتر: ۴۲۱۱', 'مد طولی؛ پنجره‌ی تابشی')):
    card(ps, x, 6.2, 5.5, 0.95, WHITE)
    text(ps, [t1, t2], x + 0.25, 6.27, 5.0, 0.85, 15, INK, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 4. new: monitor boxes ----------
bx = new_slide('توان عبوری از وجوه جعبه‌ی تابشی', 'پایش انرژی در فضای دوردست')
for i, (img, cap) in enumerate((('box_x2_T.png', 'وجه جانبی (+x): قله‌ی ۵۴/۵'), ('box_z2_T.png', 'وجه انتهایی (+z، امتداد محور میله): قله‌ی ۱۶/۵'))):
    x = 6.75 - i * 6.15
    card(bx, x, 1.9, 5.95, 4.2)
    picture(bx, os.path.join(IMG, img), x + 0.55, 2.0, h=3.45, name=f'Monitor {i+1}')
    text(bx, cap, x + 0.2, 5.55, 5.55, 0.45, 15, INK, align='center')
text(bx, ['چهار وجه جانبی (±x و ±y) هر کدام ۵۴/۵ و دو وجه انتهایی ۱۷/۵ و ۱۶/۵ ← مجموع ۲۵۲ برابر خلأ',
          'دوقطبی و میله در راستای z هستند؛ الگوی تابش ∝ sin²θ است و در امتداد محور میله تابش کمی دارد.'],
     0.6, 6.25, 12.1, 0.9, 15, MUTED)

# ---------- 5. new: rod vs sphere charts ----------
ch = new_slide('نانومیله در برابر نانوکره‌ی هم‌حجم', 'شرایط یکسان: ۶۰۷ نانومتر، خلأ، جانسون-کریستی، دوقطبی عمود بر سطح')
cats = ['۳', '۵', '۱۰', '۲۰']
specs = [('بازده کوانتومی ظاهری (درصد)', [5.5, 7.1, 7.5, 8.7], [1.4, 4.5, 18.5, 60.5], False, '0.#'),
         ('تقویت نرخ تابشی نسبت به خلأ (لگاریتمی)', [232, 104, 41, 7.8], [6.9, 4.85, 2.66, 1.53], True, '0.#')]
for i, (ttl, rod, sph, log, fmt) in enumerate(specs):
    x = 6.75 - i * 6.15
    card(ch, x, 1.9, 5.95, 4.6)
    cd = CategoryChartData(); cd.categories = cats
    cd.add_series('نانومیله (FDTD)', rod); cd.add_series('نانوکره (حل تحلیلی)', sph)
    gf = ch.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x + 0.2), Inches(2.0), Inches(5.55), Inches(4.05), cd)
    text(ch, 'فاصله‌ی گسیلنده تا سطح، d (نانومتر)', x + 0.2, 6.05, 5.55, 0.35, 12, LIGHT, align='center')
    gf.name = f'Chart {i+1}'; c = gf.chart
    c.has_title = True; c.chart_title.text_frame.text = ttl
    tp = c.chart_title.text_frame.paragraphs[0]; tp.font.size = Pt(14); tp.font.bold = True; tp.font.name = FONT; tp.font.color.rgb = INK
    c.has_legend = True; c.legend.position = XL_LEGEND_POSITION.BOTTOM; c.legend.include_in_layout = False
    c.legend.font.size = Pt(12); c.legend.font.name = FONT; c.legend.font.color.rgb = MUTED
    c.font.name = FONT; c.font.size = Pt(12); c.font.color.rgb = MUTED
    for rPr in c._chartSpace.iter(qn('a:defRPr')): setfont(rPr); rPr.attrib.pop('lang', None)
    va = c.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGBColor.from_string('E7E5E4')
    va.format.line.fill.background(); va.tick_labels.font.size = Pt(11)
    if log:
        sc = va._element.find(qn('c:scaling')); lb = etree.SubElement(sc, qn('c:logBase')); lb.set('val', '10'); sc.remove(lb); sc.insert(0, lb)
        va.minimum_scale = 1; va.maximum_scale = 1000
    else:
        va.minimum_scale = 0; va.maximum_scale = 100
    c.category_axis.tick_labels.font.size = Pt(12); c.category_axis.format.line.color.rgb = RGBColor.from_string('A8A29E')
    for s, col, lp in zip(c.plots[0].series, (ACC, GREY), (XL_LABEL_POSITION.ABOVE, XL_LABEL_POSITION.BELOW)):
        s.format.line.color.rgb = col; s.format.line.width = Pt(2.5); s.smooth = False
        s.marker.style = XL_MARKER_STYLE.CIRCLE; s.marker.size = 8
        s.marker.format.fill.solid(); s.marker.format.fill.fore_color.rgb = col; s.marker.format.line.color.rgb = col
        s.data_labels.show_value = True; s.data_labels.number_format = fmt; s.data_labels.number_format_is_linked = False
        s.data_labels.position = lp; s.data_labels.font.size = Pt(11); s.data_labels.font.color.rgb = col
for shp in ch.shapes:
    if shp.has_chart:
        for t in ('a:defRPr', 'a:rPr'):
            for rPr in shp.chart._chartSpace.iter(qn(t)): setfont(rPr); rPr.attrib.pop('lang', None)
text(ch, 'در گاف ۳ تا ۵ نانومتر تقویت تابشی نانومیله ۲۱ تا ۳۴ برابر کره است و در ۲۰ نانومتر ۵ برابر؛ بازده بالاتر کره در فواصل دور فقط به این دلیل است که تقویتش عملاً ناچیز است (۱/۵ برابر).',
     0.6, 6.62, 12.1, 0.7, 14, MUTED)

# ---------- 6. new: limitations and next steps ----------
lm = new_slide('محدودیت‌ها و گام‌های بعدی', 'جمع‌بندی صادقانه')
items = [('عدم قطعیت مش', 'در گاف ۳ نانومتر ارتفاع قله‌ها با ریز شدن مش تا حدود ۴۰ درصد تغییر می‌کند؛ مکان قله و روندها پایدارند.'),
         ('مدل ماده', 'داده‌ی توده‌ای جانسون-کریستی؛ میرایی سطحی در قطر ۲۰ نانومتر قله‌ها را کمی پهن‌تر می‌کند.'),
         ('گام بعدی', 'دایمر و آنتن پاپیونی، میله‌ی بزرگ‌تر برای بازده بیشتر، و جفت‌شدن به موجبر روی تراشه.')]
for i, (h, b) in enumerate(items):
    x = 8.8 - i * 4.1
    card(lm, x, 2.5, 3.9, 2.75)
    num = lm.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 3.9 - 1.0), Inches(2.75), Inches(0.62), Inches(0.62))
    num.fill.solid(); num.fill.fore_color.rgb = ACC; num.line.fill.background()
    tf = num.text_frame; tf.text = '۱۲۳'[i]; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    p.runs[0].font.size = Pt(18); p.runs[0].font.bold = True; p.runs[0].font.color.rgb = WHITE; p.runs[0].font.name = FONT
    text(lm, h, x + 0.25, 3.55, 3.4, 0.5, 20, INK, bold=True)
    text(lm, b, x + 0.25, 4.15, 3.4, 1.6, 15, MUTED)

# ---------- 7. revision 2: LDOS of the rod, two sphere slides (figures: make_figures2.py) ----------
def fig_slide(title, kicker, img, w, cap):
    sl = new_slide(title, kicker)
    pic = picture(sl, os.path.join(IMG, img), 0, 1.9, w=w); pic.left = (SW - pic.width) // 2
    text(sl, cap, 0.6, Emu(pic.top + pic.height).inches + 0.12, 12.1, 0.9, 14, MUTED)
    return sl
ld = fig_slide('نقشه‌ی چگالی موضعی حالات (LDOS) نانومیله', 'نتایج شبیه‌سازی', 'ldos_rod.png', 10.4,
               ['محاسبه‌ی مستقل با روش المان مرزی (BEM) [۶] برای همین نانومیله در خلأ؛ نقاط نارنجی: نتایج FDTD همین پروژه در ۶۰۷ نانومتر.',
                'LDOS در نوک‌ها متمرکز است و با فاصله به‌شدت افت می‌کند، اما بازده در تشدید فقط از ۵/۵ به ۸/۷ درصد می‌رسد.'])
sp1 = fig_slide('نانوکره‌ی طلا: طیف پورسل و تقویت تابشی', 'مرجع مقایسه: نانوکره‌ی هم‌حجم (قطر ۳۲ نانومتر)', 'sphere_spectrum.png', 11.9,
                ['حل تحلیلی دقیق شبه‌استاتیک چندقطبی [۱، ۲]، دوقطبی عمود بر سطح، داده‌ی طلای جانسون-کریستی [۵]؛ دایره‌ها: شبیه‌سازی FDTD همین پروژه در فاصله‌ی ۵ نانومتری.',
                 'تشدید کره در ۵۳۰ نانومتر و روی ناحیه‌ی پرتلفات بین‌نواری است؛ تقویت تابشی آن حتی در گاف ۳ نانومتر از ۹ برابر فراتر نمی‌رود.'])
sp2 = fig_slide('نانوکره‌ی طلا: خاموشی در فواصل کم', 'مرجع مقایسه: نانوکره‌ی هم‌حجم', 'sphere_distance.png', 11.9,
                ['نرخ کل = تابشی + غیرتابشی [۱–۴]. زیر حدود ۱۰ نانومتر نرخ غیرتابشی (متناسب با عکس مکعب فاصله) غالب است و بازده کره به چند درصد می‌رسد؛',
                 'بازده کره فقط در فواصلی بالا می‌رود که تقویت عملاً از بین رفته است (در ۶۰۷ نانومتر و فاصله‌ی ۲۰ نانومتری: نرخ کل ۲/۵ و تابشی ۱/۵ برابر).'])

# references (scientific) on the sources slide, under the remaining image sources
REFS = ['[1] J. Gersten and A. Nitzan, J. Chem. Phys. 75, 1139 (1981).',
        '[2] R. Ruppin, J. Chem. Phys. 76, 1681 (1982).',
        '[3] P. Anger, P. Bharadwaj, and L. Novotny, Phys. Rev. Lett. 96, 113002 (2006).',
        '[4] H. Mertens, A. F. Koenderink, and A. Polman, Phys. Rev. B 76, 115123 (2007).',
        '[5] P. B. Johnson and R. W. Christy, Phys. Rev. B 6, 4370 (1972).',
        '[6] U. Hohenester and A. Trügler, Comput. Phys. Commun. 183, 370 (2012) (MNPBEM).']
src = S[14]
text(src, 'References', 0.62, 3.0, 12.08, 0.45, 18, INK, bold=True, align='left')
rb = text(src, REFS, 0.62, 3.55, 12.08, 3.3, 14, MUTED, align='left')
for p in rb.text_frame.paragraphs: p._p.get_or_add_pPr().set('rtl', '0')

# ---------- order (Q&A slide removed) ----------
lst = prs.slides._sldIdLst; ids = list(lst)
orig, new = ids[:15], ids[15:]           # new: theory, purcell, boxes, charts, limits, LDOS, sphere 1, sphere 2
th_, ps_, bx_, ch_, lm_, ld_, s1_, s2_ = new
order = (orig[:5] + [th_] + orig[5:7] + [ps_] + [orig[7]] + [bx_] + [ld_] + orig[8:10] + [s1_, s2_] + [orig[10]] + [ch_] + [orig[11]]
         + [lm_] + [orig[12]] + [orig[14]])
qa = orig[13]; prs.part.drop_rel(qa.get(qn('r:id')))
for e in ids: lst.remove(e)
for e in order: lst.append(e)

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
for i, sl in enumerate(prs.slides, 1):                  # slide number in the bottom-left corner
    text(sl, str(i).translate(FA), 0.25, 6.95, 0.6, 0.4, 14, GREY, align='left', name='Slide number')
prs.save(os.path.join(D, 'defense_final.pptx')); print('saved', len(order), 'slides')
