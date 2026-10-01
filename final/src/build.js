// ساخت نسخه‌ی خودبسنده‌ی مقاله: ارجاع‌ها شماره‌گذاری، فرمول‌ها به SVG، قلم و شکل‌ها جاسازی می‌شوند.
// اجرا:  NODE_PATH=<node_modules با mathjax-full> node build.js
const fs = require('fs');
const path = require('path');
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');

const here = __dirname;
const out = path.join(here, '..', 'maghale_final.html');
const refs = require('./refs.js');
let body = fs.readFileSync(path.join(here, 'article.html'), 'utf8');

// ---------- citations: numbered by first appearance ----------
const order = [];
const num = (k) => {
  if (!refs[k]) throw new Error('unknown reference key: ' + k);
  if (!order.includes(k)) order.push(k);
  return order.indexOf(k) + 1;
};
const compress = (ns) => {
  ns = [...new Set(ns)].sort((a, b) => a - b);
  const parts = [];
  for (let i = 0; i < ns.length; ) {
    let j = i;
    while (j + 1 < ns.length && ns[j + 1] === ns[j] + 1) j++;
    parts.push(j - i >= 2 ? `${ns[i]}–${ns[j]}` : ns.slice(i, j + 1).join(', '));
    i = j + 1;
  }
  return parts.join(', ');
};
body = body.replace(/\{\{([^}|]+)(?:\|([^}]+))?\}\}/g, (_, keys, note) => {
  const ns = keys.split(',').map((k) => num(k.trim()));
  return `<span class="cite">[${compress(ns)}${note ? ', ' + note : ''}]</span>`;
});
const unused = Object.keys(refs).filter((k) => !order.includes(k));
if (unused.length) console.warn('unused references:', unused.join(', '));

const bib = '<ol class="refs">\n' + order.map((k, i) => {
  const html = refs[k].replace(/doi:(\S+)$/, '<span class="doi">doi:$1</span>');
  return `<li id="ref-${i + 1}"><span class="n">[${i + 1}]</span><span>${html}</span></li>`;
}).join('\n') + '\n</ol>';
body = body.replace('<!--BIBLIOGRAPHY-->', bib);

// ---------- keep parentheses glued to inline math (word joiner) ----------
body = body.replace(/\(\\\(/g, '(\u2060\\(').replace(/\\\)\)/g, '\\)\u2060)');

// ---------- figures as data URIs ----------
body = body.replace(/src="fig\/([^"]+)"/g, (_, f) =>
  `src="data:image/png;base64,${fs.readFileSync(path.join(here, 'fig', f)).toString('base64')}"`);

// ---------- styles with embedded font ----------
const fontDir = path.join(here, '..', '..', 'manuscript', 'fonts');
const font = (f) => 'data:font/woff2;base64,' + fs.readFileSync(path.join(fontDir, f)).toString('base64');
const css = fs.readFileSync(path.join(here, 'style.css'), 'utf8')
  .replace('__FONT_REGULAR__', font('Vazirmatn-Regular.woff2'))
  .replace('__FONT_BOLD__', font('Vazirmatn-Bold.woff2'));

const page = `<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>تقویت گسیل خودبه‌خودی نزدیک نانومیله‌ی طلا</title>
<style>${css}</style>
</head>
<body>
<main class="page">
${body}
</main>
</body>
</html>`;

// ---------- math → SVG ----------
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document(page, {
  InputJax: new TeX({
    packages: AllPackages.filter((p) => p !== 'bussproofs'),
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    tags: 'none',
    macros: { nm: ['{#1\\,\\mathrm{nm}}', 1] },
  }),
  OutputJax: new SVG({ fontCache: 'global' }),
});
doc.render();
const errs = adaptor.tags(adaptor.body(doc.document), 'mjx-merror');
if (errs.length) errs.forEach((e) => console.error('TeX error:', adaptor.getAttribute(e, 'data-mjx-error') || adaptor.textContent(e)));

let html = adaptor.doctype(doc.document) + '\n' + adaptor.outerHTML(adaptor.root(doc.document));
const sheet = adaptor.textContent(doc.outputJax.styleSheet(doc));
html = html.replace('</head>', `<style>${sheet}</style>\n</head>`);
fs.writeFileSync(out, html);
console.log(`wrote ${path.relative(process.cwd(), out)}  (${(html.length / 1024).toFixed(0)} KB, ${order.length} references, ${errs.length} TeX errors)`);
