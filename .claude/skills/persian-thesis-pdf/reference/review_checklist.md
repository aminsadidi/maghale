# Persian thesis: review checklist (run before every delivery)

Work as an examiner would. Read the whole source in order, chapter by chapter, and fix what you find. Tick each item.

## A. Consistency of numbers (most frequent examiner complaint)
- [ ] Every number in abstract, results text, figure captions, tables and conclusion is identical (peak wavelength, Fp, η, ratios).
- [ ] Numbers in text match the figures. If the user has a plot, read values from it (or from a data-cursor screenshot), never from memory.
- [ ] Derived numbers are recomputed (e.g. Γrad/Γ0 = η·Fp, ratios, volumes, CFL Δt), and the arithmetic is shown when it is not obvious.
- [ ] Every value in a table was actually computed or simulated. If a data point does not exist (e.g. a gap that was never simulated), remove it everywhere, or mark it clearly as future work. Never fill it in by interpolation.
- [ ] Symmetry checks: if the geometry is symmetric about an axis, the corresponding monitor or face results must be equal, and the text must name that axis correctly.

## B. Physics and mathematics
- [ ] Scaling words are correct: "exponential" only for evanescent and absorbing decay; near-field and Purcell laws are power laws (1/d³); CFL cost is polynomial (∝Δx⁻⁴), not exponential.
- [ ] Interband (5d→6sp, gold below about 550 nm) versus intraband (free-electron Drude absorption) are not mixed up.
- [ ] Rate versus efficiency: Γrad/Γ0 is the maximum photon rate (saturation), η is the photon probability per pulse. "Photons per 10 excitations", not "per 10 photons".
- [ ] Fp (total) ≠ radiative rate. Do not call Fp the "emission speed of photons".
- [ ] Equations: prefactors and units are checked against a textbook (Novotny & Hecht, Maier, Bohren & Huffman, Taflove). Ellipsoid-only formulas (depolarisation factors Lᵢ) are flagged as approximations for other shapes.
- [ ] Driving force versus restoring force, near field versus far field, TE versus TM: the standard confusions are checked.
- [ ] Limitations are stated honestly: bulk dielectric data versus size-dependent surface damping, mesh uncertainty at the smallest gaps, intrinsic quantum yield assumed equal to 1.
- [ ] No claim of a verification that was not done (e.g. "agrees with theory" when only one quantity was compared).

## C. Citations
- [ ] Every claim with a date or name is correct (who, what, year). Example: Purcell 1946 was a prediction, not an experiment.
- [ ] Every citation supports the sentence it is attached to. No book from 2005 cited for a "2020+" trend.
- [ ] New references are real, with full IEEE details. Do not invent volume or page numbers; drop a reference whose details are uncertain.
- [ ] No citations in the abstract.

## D. Persian writing
- [ ] Persian ی/ک, not Arabic ي/ك. Correct ZWNJ (می‌شود، ساختارها، پیچیده‌ای).
- [ ] Word traps: مجاز (allowed) ≠ مجازی (virtual); فلزات نجیب not «اصیل»; «گذار» not «ترانزیشن».
- [ ] Neutral academic tone. Remove: بی‌نقص، خیره‌کننده، شگرف، بی‌رقیب، شگفت‌انگیز، کورکورانه، بی‌ارزش، نجومی، «اثبات کرد» (for a simulation use «نشان داد»), exclamation marks.
- [ ] No incomplete sentences (each sentence has its verb), no doubled words, no paragraph that repeats the previous one.
- [ ] Foreign names transliterated correctly (Drexhage → درکسهاگه, Lavinia Rogobete → لاوینیا روگوبته).
- [ ] Use «پایان‌نامه», not «رساله» (رساله = PhD).

## E. Typesetting (checked automatically by scripts/build.sh)
- [ ] 0 LaTeX errors, 0 missing glyphs, 0 undefined references, 0 Latin letters outside \lr{}.
- [ ] Decimal separator «/» in Persian text (۵۴/۵). Latin "." is fine inside $...$ math.
- [ ] Percent written as «درصد». No en dash; "--" only inside \begin{latin} (bibliography).
- [ ] Each figure and table is referenced in the text. Captions are self-contained. Table captions go above the table, figure captions below.
- [ ] Chapter numbering: \chapter, \section (never shows "۱.۰"). Bibliography heading is right-aligned and Persian.
- [ ] Visually inspect the PDF: render the pages that have figures or tables and check layout, placeholders and overflows.
