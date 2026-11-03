"""Low-level helpers that write RTL Persian paragraphs in the formatting of
the University of Kashan thesis template (B Nazanin 12 pt body, B Titr
headings, line spacing 1.2)."""
import re
from copy import deepcopy

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
LATIN = re.compile(r"([A-Za-z₀-ₜ°±α-ωΔΩ≤≥×]"
                   r"[A-Za-z0-9₀-ₜ⁰-ⁿ°±α-ωΔΩ≤≥×"
                   r"\-\+\./\(\)%:=\^_,\*' ]*[A-Za-z0-9₀-ₜ⁰-ⁿ\)%°'\*]"
                   r"|[A-Za-z₀-ₜ])")


def fa(x, nd=2):
    """Number -> Persian digits with '/' as decimal separator (thesis style)."""
    if isinstance(x, str):
        return x.translate(FA_DIGITS)
    s = f"{x:.{nd}f}".replace(".", "/")
    return s.translate(FA_DIGITS)


def fa_sci(x, nd=1):
    m, e = f"{x:.{nd}e}".split("e")
    e = int(e)
    return f"{m.replace('.', '/')}×10^{e}".translate(FA_DIGITS) if False else f"{m}×10^{e}"


def _rpr(font_cs="B Nazanin", size=12, bold=False, rtl=True, color=None, italic=False,
         latin_font="Times New Roman", latin_size=None, superscript=False, subscript=False):
    rPr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    rf.set(qn("w:ascii"), latin_font); rf.set(qn("w:hAnsi"), latin_font)
    rf.set(qn("w:cs"), font_cs)
    rPr.append(rf)
    if bold:
        rPr.append(OxmlElement("w:b")); rPr.append(OxmlElement("w:bCs"))
    if italic:
        rPr.append(OxmlElement("w:i")); rPr.append(OxmlElement("w:iCs"))
    if color:
        c = OxmlElement("w:color"); c.set(qn("w:val"), color); rPr.append(c)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int((latin_size or size) * 2))); rPr.append(sz)
    szc = OxmlElement("w:szCs"); szc.set(qn("w:val"), str(int(size * 2))); rPr.append(szc)
    if superscript or subscript:
        va = OxmlElement("w:vertAlign"); va.set(qn("w:val"), "superscript" if superscript else "subscript")
        rPr.append(va)
    if rtl:
        rPr.append(OxmlElement("w:rtl"))
    return rPr


def _run(text, **kw):
    r = OxmlElement("w:r")
    r.append(_rpr(**kw))
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    return r


def _ppr(jc="both", line=288, before=0, after=120, bidi=True, keep_next=False, ind_first=None,
         outline=None, page_break_before=False):
    pPr = OxmlElement("w:pPr")
    if keep_next:
        pPr.append(OxmlElement("w:keepNext"))
    if page_break_before:
        pPr.append(OxmlElement("w:pageBreakBefore"))
    if bidi:
        pPr.append(OxmlElement("w:bidi"))
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:before"), str(before)); sp.set(qn("w:after"), str(after))
    sp.set(qn("w:line"), str(line)); sp.set(qn("w:lineRule"), "auto")
    pPr.append(sp)
    if ind_first is not None:
        ind = OxmlElement("w:ind"); ind.set(qn("w:firstLine"), str(ind_first)); pPr.append(ind)
    j = OxmlElement("w:jc"); j.set(qn("w:val"), jc); pPr.append(j)
    if outline is not None:
        o = OxmlElement("w:outlineLvl"); o.set(qn("w:val"), str(outline)); pPr.append(o)
    return pPr


def add_runs_mixed(p, text, size=12, bold=False, font_cs="B Nazanin", latin_size=None, color=None):
    """Split text into Persian (rtl) and Latin (ltr) runs. ^{..} = superscript,
    _{..} = subscript (Latin only)."""
    pos = 0
    for m in LATIN.finditer(text):
        if m.start() > pos:
            p.append(_run(text[pos:m.start()], size=size, bold=bold, font_cs=font_cs, rtl=True, color=color))
        _latin(p, m.group(0), size=size, bold=bold, latin_size=latin_size, color=color)
        pos = m.end()
    if pos < len(text):
        p.append(_run(text[pos:], size=size, bold=bold, font_cs=font_cs, rtl=True, color=color))


def _latin(p, s, size=12, bold=False, latin_size=None, color=None):
    ls = latin_size or (size - 1)
    for part in re.split(r"(\^\{[^}]*\}|_\{[^}]*\})", s):
        if not part:
            continue
        if part.startswith("^{"):
            p.append(_run(part[2:-1], size=size, bold=bold, rtl=False, latin_size=ls, superscript=True,
                          font_cs="Times New Roman", color=color))
        elif part.startswith("_{"):
            p.append(_run(part[2:-1], size=size, bold=bold, rtl=False, latin_size=ls, subscript=True,
                          font_cs="Times New Roman", color=color))
        else:
            p.append(_run(part, size=size, bold=bold, rtl=False, latin_size=ls, font_cs="Times New Roman",
                          color=color))


class Writer:
    """Inserts content before an anchor paragraph element."""

    def __init__(self, doc, anchor_p):
        self.doc = doc
        self.anchor = anchor_p
        self.fig_n = 0
        self.tab_n = 0
        self.eq_n = 0
        self.chapter = 4

    def _insert(self, p):
        self.anchor.addprevious(p)
        return p

    def para(self, text, jc="both", size=12, bold=False, after=120, before=0, keep_next=False,
             first_line=None):
        p = OxmlElement("w:p")
        p.append(_ppr(jc=jc, line=288, before=before, after=after, keep_next=keep_next, ind_first=first_line))
        add_runs_mixed(p, text, size=size, bold=bold)
        return self._insert(p)

    def page_break(self):
        p = OxmlElement("w:p")
        p.append(_ppr(jc="right", after=0))
        r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br)
        p.append(r)
        return self._insert(p)

    def chapter_title(self, number_text, title):
        p = OxmlElement("w:p")
        p.append(_ppr(jc="center", line=240, before=3600, after=600, outline=0))
        p.append(_run(number_text, size=36, bold=True, font_cs="B Titr"))
        self._insert(p)
        p = OxmlElement("w:p")
        p.append(_ppr(jc="center", line=360, after=0))
        p.append(_run(title, size=28, bold=True, font_cs="B Titr"))
        self._insert(p)
        self.page_break()

    def h1(self, num, text):
        p = OxmlElement("w:p")
        p.append(_ppr(jc="right", line=288, before=240, after=120, keep_next=True, outline=1))
        p.append(_run(f"{num}- ", size=16, bold=True, font_cs="B Titr", rtl=True))
        add_runs_mixed(p, text, size=16, bold=True, font_cs="B Titr")
        return self._insert(p)

    def h2(self, num, text):
        p = OxmlElement("w:p")
        p.append(_ppr(jc="right", line=288, before=180, after=100, keep_next=True, outline=2))
        p.append(_run(f"{num}- ", size=14, bold=True, font_cs="B Titr", rtl=True))
        add_runs_mixed(p, text, size=14, bold=True, font_cs="B Titr")
        return self._insert(p)

    def equation(self, text):
        """Centred LTR equation (Cambria Math) with number on the right."""
        self.eq_n += 1
        p = OxmlElement("w:p")
        pPr = _ppr(jc="center", line=288, before=60, after=60, bidi=False)
        tabs = OxmlElement("w:tabs")
        for val, pos in (("center", 4800), ("right", 9300)):
            t = OxmlElement("w:tab"); t.set(qn("w:val"), val); t.set(qn("w:pos"), str(pos)); tabs.append(t)
        pPr.insert(0, tabs)
        p.append(pPr)
        r = OxmlElement("w:r"); r.append(_rpr(rtl=False, latin_font="Cambria Math", font_cs="Cambria Math")); r.append(OxmlElement("w:tab")); p.append(r)
        for part in re.split(r"(\^\{[^}]*\}|_\{[^}]*\})", text):
            if not part:
                continue
            kw = dict(rtl=False, latin_font="Cambria Math", font_cs="Cambria Math", size=12, italic=False)
            if part.startswith("^{"):
                p.append(_run(part[2:-1], superscript=True, **kw))
            elif part.startswith("_{"):
                p.append(_run(part[2:-1], subscript=True, **kw))
            else:
                p.append(_run(part, **kw))
        r = OxmlElement("w:r"); r.append(_rpr(rtl=False)); r.append(OxmlElement("w:tab")); p.append(r)
        p.append(_run(f"({self.chapter}-{self.eq_n})", rtl=False, size=12))
        self._insert(p)
        return f"{self.chapter}-{self.eq_n}"

    def figure(self, path, caption, width_cm=15.0):
        self.fig_n += 1
        # use python-docx to create the inline picture in a temp paragraph
        tmp = self.doc.add_paragraph()
        tmp.add_run().add_picture(path, width=Cm(width_cm))
        pic_p = tmp._p
        pic_p.getparent().remove(pic_p)
        pPr = _ppr(jc="center", line=240, before=120, after=60, keep_next=True)
        pic_p.insert(0, pPr)
        self._insert(pic_p)
        p = OxmlElement("w:p")
        p.append(_ppr(jc="center", line=288, after=200))
        p.append(_run(f"شکل {self.chapter}-{self.fig_n}- ", size=11, bold=True))
        add_runs_mixed(p, caption, size=11)
        self._insert(p)
        return f"{self.chapter}-{self.fig_n}"

    def table(self, caption, header, rows, col_widths=None, highlight_row=None, font_size=10):
        self.tab_n += 1
        p = OxmlElement("w:p")
        p.append(_ppr(jc="center", line=288, before=120, after=60, keep_next=True))
        p.append(_run(f"جدول {self.chapter}-{self.tab_n}- ", size=11, bold=True))
        add_runs_mixed(p, caption, size=11, bold=True)
        self._insert(p)
        tbl = OxmlElement("w:tbl")
        tblPr = OxmlElement("w:tblPr")
        st = OxmlElement("w:tblStyle"); st.set(qn("w:val"), "TableGrid")
        tblPr.append(OxmlElement("w:bidiVisual"))
        w = OxmlElement("w:tblW"); w.set(qn("w:w"), "0"); w.set(qn("w:type"), "auto"); tblPr.append(w)
        jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); tblPr.append(jc)
        borders = OxmlElement("w:tblBorders")
        for side, val, sz in (("top", "single", 12), ("bottom", "single", 12), ("insideH", "single", 4),
                              ("left", "nil", 0), ("right", "nil", 0), ("insideV", "nil", 0)):
            b = OxmlElement(f"w:{side}"); b.set(qn("w:val"), val)
            if sz:
                b.set(qn("w:sz"), str(sz)); b.set(qn("w:space"), "0"); b.set(qn("w:color"), "000000")
            borders.append(b)
        tblPr.append(borders)
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "autofit"); tblPr.append(lay)
        tbl.append(tblPr)
        grid = OxmlElement("w:tblGrid")
        for _ in header:
            gc = OxmlElement("w:gridCol"); grid.append(gc)
        tbl.append(grid)
        for ri, r in enumerate([header] + rows):
            tr = OxmlElement("w:tr")
            trPr = OxmlElement("w:trPr"); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
            if ri == 0:
                trPr.append(OxmlElement("w:tblHeader"))
            tr.append(trPr)
            for cell in r:
                tc = OxmlElement("w:tc")
                tcPr = OxmlElement("w:tcPr")
                if ri == 0:
                    b = OxmlElement("w:tcBorders")
                    bb = OxmlElement("w:bottom"); bb.set(qn("w:val"), "single"); bb.set(qn("w:sz"), "8")
                    bb.set(qn("w:space"), "0"); bb.set(qn("w:color"), "000000"); b.append(bb); tcPr.append(b)
                if highlight_row is not None and ri == highlight_row + 1:
                    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto")
                    sh.set(qn("w:fill"), "E2EFDA"); tcPr.append(sh)
                elif ri > 0 and ri % 2 == 0:
                    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto")
                    sh.set(qn("w:fill"), "F2F2F2"); tcPr.append(sh)
                va = OxmlElement("w:vAlign"); va.set(qn("w:val"), "center"); tcPr.append(va)
                tc.append(tcPr)
                cp = OxmlElement("w:p")
                cp.append(_ppr(jc="center", line=240, before=20, after=20))
                add_runs_mixed(cp, str(cell), size=font_size + (0 if ri else 0), bold=(ri == 0),
                               latin_size=font_size)
                tc.append(cp)
                tr.append(tc)
            tbl.append(tr)
        self._insert(tbl)
        sp = OxmlElement("w:p"); sp.append(_ppr(after=120)); self._insert(sp)
        return f"{self.chapter}-{self.tab_n}"
