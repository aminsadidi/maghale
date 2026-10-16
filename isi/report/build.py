"""Build a self-contained report: replaces {{IMG:name}} in <src>.src.html by the base64 PNG isi/figures/<name>.png,
writes <src>.html and prints <src>.pdf (A4) with headless Chromium.
usage: python isi/report/build.py isi/report/report_trimer"""
import base64, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, '..', 'figures')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
stem = sys.argv[1]
html = open(stem + '.src.html', encoding='utf-8').read()
def img(m):
    return 'data:image/png;base64,' + base64.b64encode(open(os.path.join(FIG, m.group(1) + '.png'), 'rb').read()).decode()
html = re.sub(r'\{\{IMG:([\w.-]+)\}\}', img, html)
open(stem + '.html', 'w', encoding='utf-8').write(html)
subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={stem}.pdf', 'file://' + os.path.abspath(stem + '.html')], check=True, capture_output=True)
print('wrote', stem + '.html', stem + '.pdf')
