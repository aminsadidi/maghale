// Build refs.tex (thebibliography) in order of first \cite in main.tex.
const fs = require('fs');
const R = Object.assign({}, require('../../final/src/refs.js'), require('./refs_extra.js'));
const tex = fs.readFileSync(__dirname + '/main.tex', 'utf8').replace(/^%.*$/mg, '');
const order = [];
for (const m of tex.matchAll(/\\cite[tp]?\{([^}]+)\}/g))
  for (const k of m[1].split(',').map(s => s.trim())) { if (!R[k]) throw new Error('missing ref ' + k); if (!order.includes(k)) order.push(k); }
const conv = s => s.replace(/<i>(.*?)<\/i>/g, '\\textit{$1}').replace(/<b>(.*?)<\/b>/g, '\\textbf{$1}').replace(/&amp;/g, '\\&').replace(/<sub>(.*?)<\/sub>/g, '$_{$1}$')
  .replace(/doi:(\S+)$/, '\\href{https://doi.org/$1}{doi:$1}').replace(/ – /g, ' -- ').replace(/(\d)–(\d)/g, '$1--$2');
const out = '\\begin{thebibliography}{' + order.length + '}\n' + order.map(k => `\\bibitem{${k}} ${conv(R[k])}`).join('\n\n') + '\n\\end{thebibliography}\n';
fs.writeFileSync(__dirname + '/refs.tex', out);
console.log(order.length, 'references; unused:', Object.keys(R).filter(k => !order.includes(k)).join(', '));
