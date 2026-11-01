"""check_text.py - source-level checks for a Persian xepersian thesis (things the LaTeX log does not catch).
usage: python3 check_text.py main.tex        exit 1 if a blocking problem is found
Blocking : Latin letters outside \\lr{}/math/latin env (invisible with a Persian-only font such as Yas),
           en/em dashes and '%' / '--' in Persian text (missing glyphs in many Persian fonts),
           Arabic Yeh/Kaf instead of Persian, '.' used as decimal point between Persian digits (prints reversed).
Warnings : overstated wording that examiners flag, the word 'exponential' (often wrong for near-field laws),
           citations inside the abstract, figures/tables never referenced in the text.
"""
import re, sys

src = open(sys.argv[1], encoding='utf-8').read()
body = src[src.index('\\begin{document}'):]
lat = body.find('\\begin{latin}')
persian = body[:lat] if lat > 0 else body
bad, warn = [], []


def strip_cmd_arg(t, cmd):
    out, i = [], 0
    while i < len(t):
        if t.startswith(cmd + '{', i):
            d, j = 0, i + len(cmd)
            while j < len(t):
                d += (t[j] == '{') - (t[j] == '}')
                if d == 0: break
                j += 1
            i = j + 1
        else:
            out.append(t[i]); i += 1
    return ''.join(out)


t = re.sub(r'(?m)(?<!\\)%.*$', '', persian)
t = re.sub(r'\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]', ' ', t, flags=re.S)
for env in ('equation', 'align', 'multline', 'gather'):
    t = re.sub(r'\\begin\{%s\*?\}.*?\\end\{%s\*?\}' % (env, env), ' ', t, flags=re.S)
for c in ('\\lr', '\\label', '\\ref', '\\cite', '\\figbox', '\\includegraphics', '\\begin', '\\end', '\\detokenize', '\\texttt'):
    t = strip_cmd_arg(t, c)
t = re.sub(r'\\[A-Za-z@]+\*?(\[[^\]]*\])?', ' ', t)
t = re.sub(r'\[[^\]\n]{0,20}\]', ' ', t)          # optional args: [htbp], [6pt], [t]
t = re.sub(r'\{[A-Za-z0-9:._\-|!, ]*\}', ' ', t)
for m in re.finditer(r'[A-Za-z]{2,}', t):
    bad.append('Latin text outside \\lr{}: ...%s...' % t[max(0, m.start() - 25):m.end() + 10].replace('\n', ' '))

if re.search('[\u2013\u2014]', persian): bad.append('en/em dash in Persian text (use "-")')
if re.search(r'(?<![\\$])--(?!-)', re.sub(r'\$[^$]*\$', '', persian)): bad.append("'--' in Persian text becomes an en dash (missing glyph); use '-' or $-$")
if '\\%' in persian: bad.append("'\\%' in Persian text (missing glyph in Yas): write «درصد» instead")
if re.search('[\u064a\u0643]', persian): bad.append('Arabic ي/ك found: use Persian ی/ک')
if re.search('[\u06f0-\u06f9]\\.[\u06f0-\u06f9]', persian): bad.append("decimal '.' between Persian digits prints reversed: use '/' (e.g. ۵۴/۵)")

for w in ('بی‌نقص', 'خیره‌کننده', 'شگرف', 'بی‌رقیب', 'شگفت‌انگیز', 'کورکورانه', 'بی‌ارزش', 'نجومی'):
    if w in persian: warn.append('overstated wording: ' + w)
for m in re.finditer(r'.{25}نمایی.{25}', persian):
    warn.append('check "نمایی" (exponential) is really exponential: ...' + m.group(0) + '...')
ab = re.search(r'\\chapter\*\{چکیده\}(.*?)\\tableofcontents', body, re.S)
if ab and '\\cite' in ab.group(1): warn.append('citations inside the abstract')
for lab in re.findall(r'\\label\{((?:fig|tab):[^}]*)\}', body):
    if body.count('\\ref{%s}' % lab) == 0: warn.append('never referenced: ' + lab)

for b in bad: print('ERROR  :', b)
for w in warn: print('WARNING:', w)
print('text check: %d error(s), %d warning(s)' % (len(bad), len(warn)))
sys.exit(1 if bad else 0)
