---
name: persian-thesis-pdf
description: Build, fix or review a Persian (Farsi) thesis, report or article as a PDF plus Overleaf code - XeLaTeX + xepersian, Yas font, RTL typesetting, equations, figures from Lumerical/MATLAB plots, tables, IEEE references. Use whenever the user asks for a پایان‌نامه / پروژه / گزارش / مقاله in Persian as PDF or "کد اورلیف", wants changes to such a document, or asks to proofread it for scientific and writing errors.
---

# Persian thesis PDF (XeLaTeX + xepersian)

**Output.** Always deliver three things:
1. `main.tex`: one self-contained file. The user pastes it into Overleaf with the compiler set to **XeLaTeX**.
2. `overleaf_project.zip`: main.tex plus every image it uses (Overleaf: New Project → Upload Project).
3. `main_preview.pdf`: compiled locally so the user can check before uploading.

Send all three with SendUserFile, commit them, and answer in Persian.

## Workflow
1. **Start from the template** `template/main.tex`. It is the proven preamble: Yas font chain, Scale 1.12, line spacing 1.55, report class with \chapter, fancy header, \figbox placeholders, and a right-aligned Persian bibliography heading. Do not rebuild the preamble from scratch.
2. **If the input is an existing PDF**, convert it to text:
   ```
   pdftotext in.pdf - | python3 -c "import sys,unicodedata;print(unicodedata.normalize('NFKC',sys.stdin.read()))"
   ```
   Then also *look* at every page with Read (pages=…). Equations, figures and the true RTL order are only visible in the images. Rewrite the LaTeX by hand. Never paste the extracted text: it has mirrored brackets, lost ZWNJ and Arabic ي/ك.
3. **Write the content** following the rules below. Keep the user's structure. Add material inside existing sections unless they ask for new headings.
4. **Build and check:**
   ```
   bash .claude/skills/persian-thesis-pdf/scripts/build.sh path/to/main.tex
   ```
   The script installs TeX if missing, runs 3 XeLaTeX passes, and fails on any of these: LaTeX errors, missing glyphs, undefined references or citations, Latin text outside `\lr{}`, dashes, `\%`, Arabic letters, or "." decimals in Persian. It also warns about overstated words, suspicious "نمایی", citations in the abstract and unreferenced figures or tables. Then it writes the preview PDF and the zip. Fix the cause until it prints `ALL CHECKS PASSED`.
5. **Inspect visually.** Read the pages of the PDF that have the title, TOC, figures, tables and bibliography.
6. **Review as an examiner** using `reference/review_checklist.md`. Do this pass before every delivery, not only when the user asks. Fix everything you are sure of. List what needs the user's data (exact plot values, missing simulations, images) instead of guessing.

## Typesetting rules (each one fixes a bug seen in real theses)
- **Latin text.** Every Latin word in Persian text goes in `\lr{...}`: abbreviations, English terms, names, file names. The Yas font has no Latin glyphs, so anything outside `\lr{}` prints as empty boxes.
- **Math.** Latin subscripts use `\sub{rad}` (= \mathrm). Never `\text{}` inside math, because it switches to the Persian font. Use `\Imag`, `\Real` for Im and Re.
- **Numbers in text.** Use Persian digits with «/» as the decimal separator (۵۴/۵). Write «درصد», never %. Use "-" for ranges and compounds (درود-لورنتز), never "–" or "--". Units are written in Persian (نانومتر); inside math, write `\mathrm{nm}`.
- **Numbering.** Chapters are `\chapter{...}` and sections are `\section{...}`, so the TOC never shows "۱.۰". Equations are numbered (chapter.n). Cite them as «رابطه‌ی (\ref{eq:x})».
- **Figures.** Use `\figbox{file.png}{width}`. It includes the image if present, otherwise prints a labelled placeholder. Put side-by-side panels in two minipages with «(آ)»/«(ب)» sublabels. Use the user's real plots: copy them from the images folder with the expected names.
- **Tables.** Use booktabs plus `\resizebox{\textwidth}{!}{...}` for wide tables, `\arraystretch` 1.3, and put the caption above the table.
- **Bibliography.** Use `thebibliography` inside `\begin{latin}`, preceded by a Persian `\chapter*{منابع و مآخذ}`, `\addcontentsline` and `\markboth`. Inside latin, set `\renewcommand{\bibname}{\rl{منابع و مآخذ}}` and `\renewcommand{\chapter}[2]{}`. Use IEEE style. Keys are short (novotny, maier, ...). Number references in order of the list.
- **Size and spacing.** Use 12pt, the font at Scale 1.12 and \setstretch 1.55. These are larger and airier than common templates, as users asked. If they want bigger still, raise Scale and stretch, not \textbf.
- **Font.** The chain is: BYas.ttf (project file) → BYas → B Yas → XB Yas → Yas → XB Niloofar → Vazirmatn → Nazli → Amiri. If the user's old preamble has its own `\settextfont`, theirs wins (add Scale).
- **Avoid in Persian mode:** `\text{}` in math, `%` and `--` in text, Arabic presentation-form characters, `.` decimals, and English letters outside `\lr`.

## Content rules
- Do not invent data. New numbers must come from the user's plots or files, or from a calculation you actually ran. Add the calculation script to the repo and say in the text how it was obtained, for example "حل تحلیلی دقیق" versus "شبیه‌سازی FDTD".
- When adding a comparison (for example a nanosphere next to a nanorod), keep the conditions identical (same volume, material data, medium, orientation, distance and wavelength) and state them. Add the supporting theory in the theory chapter, the results in the results chapter, and update the abstract and conclusion so the document stays coherent.
- Abstract: no citations. Conclusion: no new results. Every number in the abstract must also appear in the results chapter.
- Use a neutral academic tone (see checklist D).

## Files
- `template/main.tex`: full skeleton (title page, abstract, TOC, chapter, equation, figure, table, bibliography).
- `scripts/build.sh`: compile, checks, preview and zip.
- `scripts/check_text.py`: source checks; can be run alone: `python3 check_text.py main.tex`.
- `reference/review_checklist.md`: examiner-style review list (numbers, physics, citations, Persian writing, typesetting).
- Worked example: `thesis_tex/main.tex` in this repo (54-page thesis built with this skill).
