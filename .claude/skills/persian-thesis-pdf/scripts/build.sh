#!/bin/bash
# build.sh - compile a Persian XeLaTeX thesis, run all quality checks, make the Overleaf zip.
# usage: build.sh path/to/main.tex            (run from anywhere; images are looked up next to main.tex)
# exit code 0 only if: no LaTeX error, no missing glyph, no undefined reference/citation, no Latin outside \lr.
set -u
TEX=$(readlink -f "${1:?usage: build.sh main.tex}")
DIR=$(dirname "$TEX"); NAME=$(basename "$TEX" .tex); HERE=$(dirname "$(readlink -f "$0")")
cd "$DIR" || exit 1
mkdir -p build

# 0. toolchain (only installs what is missing; Overleaf users skip this)
if ! command -v xelatex >/dev/null || ! kpsewhich xepersian.sty >/dev/null; then
  echo "installing XeLaTeX + xepersian (one time) ..."
  apt-get install -y --no-install-recommends texlive-xetex texlive-lang-arabic texlive-latex-extra \
      texlive-fonts-recommended fonts-farsiweb >/dev/null 2>&1 \
  || { apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends texlive-xetex \
      texlive-lang-arabic texlive-latex-extra texlive-fonts-recommended fonts-farsiweb >/dev/null 2>&1; }
fi

# 1. three passes (TOC, references, labels)
for i in 1 2 3; do
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=build "$NAME.tex" > build/run.txt 2>&1
  if grep -q "^!" "build/$NAME.log"; then
    echo "LATEX ERROR:"; grep -n -A4 "^!" "build/$NAME.log" | head -30; exit 1
  fi
done
LOG="build/$NAME.log"; FAIL=0

# 2. checks
miss=$(grep -c "Missing character" "$LOG"); und=$(grep -ci "undefined" "$LOG"); over=$(grep -c "Overfull" "$LOG")
pages=$(pdfinfo "build/$NAME.pdf" 2>/dev/null | awk '/Pages/{print $2}')
echo "pages: $pages | missing glyphs: $miss | undefined refs/cites: $und | overfull boxes: $over"
[ "$miss" -gt 0 ] && { FAIL=1; grep "Missing character" "$LOG" | sort | uniq -c | head; }
[ "$und" -gt 0 ] && { FAIL=1; grep -i "undefined" "$LOG" | sort -u | head; }
[ "$over" -gt 0 ] && grep "Overfull" "$LOG" | head -5
python3 "$HERE/check_text.py" "$NAME.tex" || FAIL=1

# 3. deliverables: preview PDF + Overleaf zip (tex + every image the source references and that exists)
cp "build/$NAME.pdf" "${NAME}_preview.pdf"
imgs=$(grep -v '^[[:space:]]*%' "$NAME.tex" | grep -o '\\figbox{[^}]*}\|\\includegraphics\(\[[^]]*\]\)\?{[^}]*}' | sed 's/.*{\([^}]*\)}$/\1/' | grep -v '#' | sort -u)
rm -f overleaf_project.zip; files="$NAME.tex"
for f in $imgs; do [ -f "$f" ] && files="$files $f" || echo "note: image not uploaded yet (placeholder box printed): $f"; done
zip -q overleaf_project.zip $files && echo "overleaf_project.zip: $files"
echo "preview: $DIR/${NAME}_preview.pdf"
[ $FAIL -eq 0 ] && echo "ALL CHECKS PASSED" || echo "CHECKS FAILED - fix the items above"
exit $FAIL
