---
name: maghale-rules
description: Standing rules, preferences and supervisor decisions for the maghale project (gold-nanorod antenna + quantum emitter at 1550 nm, Tamm-plasmon study, Persian thesis, reports, defense deck, lab runs). Read it before any work on simulation, modelling, reports, thesis or article writing in this repository. It updates itself - whenever the user states a new rule, preference, correction or decision about writing or simulation, add it here (see "Self-update protocol").
---

# maghale project rules (self-updating)

This file is the project's memory. It holds everything the users and the supervisor have asked to be respected. **Read all of it before working.** When a rule here conflicts with a generic habit, this file wins. When the user says something new that conflicts with a rule here, the user's newest instruction wins: update the rule (do not keep both).

## Self-update protocol (do this every time, without being asked)

1. **When to update.** The user (or the supervisor through the user) states anything that should hold beyond the current message. Examples: a writing or formatting preference, a physics or modelling decision, a parameter value, a correction of a mistake, a "from now on", a "never do X", how reports or answers should look, and which structures or cases to simulate. One-off requests ("make this plot") are not rules. The decision behind them ("always label curves in English") is.
2. **How.** Add one short line to the right section below, in English, with the date: `- (YYYY-MM-DD) rule ...`. If it replaces an older line, edit or delete the old line instead of adding a contradicting one. If no section fits, add a new `##` section.
3. **Then:** commit with the message `maghale-rules: <what changed>` and the session's attribution footer, then push to the working branch. Mention the update in one line in the reply (in Persian), e.g. «این نکته در اسکیل قوانین پروژه ذخیره شد.»
4. **Keep it lean.** One line per rule. Put details in the project files and link to them here (paths).

## 1. People, language, communication

- Users: Amin Hossain Sadidi and Seyed Mohammad Parsa Molaei Tabari (physics undergraduates, University of Isfahan). Supervisor: Dr. Malek Bagheri Harouni (they say «استاد»). Collaborator: Prof. Giuseppe M. Paternò (Tamm-plasmon study).
- **Always reply in Persian.** When the user says they do not understand, explain in the simplest possible terms: which computer, which folder, what to type, what to send back.
- (2026-11-22) **RTL/LTR in replies:** keep Persian prose right-to-left. Put every equation, code line or formula in its own LTR block (code block in chat; `.eq` block in HTML). Avoid starting a Persian line with a Latin token. In HTML, isolate inline symbols (`<span class="m">` / `unicode-bidi:isolate`).
- When asked to plan, give a step-by-step plan and then carry it out step by step without waiting, unless told otherwise.
- (2026-11-22) **When the user says to finalize the model first or not to compute yet, do not start computations.** Prepare the model or documents and wait for an explicit go («هر موقع گفته شد محاسبات را انجام بده»).
- Be honest: report failures, limitations and uncertain interpretations explicitly. Mark interpretations as proposed, not proven.
- The users' email and personal details are private: never send them to external services.

## 2. Reports for the supervisor (HTML / PDF)

- Deliver reports as a **self-contained HTML** (images embedded as base64) **plus a PDF**, built with the project's `build.py` (`isi/report/build.py`, `tamm/report/build.py`: `{{IMG:name}}` placeholders, headless Chromium). Send both with SendUserFile, commit and push.
- (2026-11-15) Reports for the supervisor must be **very detailed and step by step**: geometry, model, formulas, every number and how it was obtained, method, mechanism, validation. The supervisor must be able to verify every computation. Do not rush.
- (2026-11-22) **Every figure is explained curve by curve:** what each curve or marker is, for which conditions (geometry, position, orientation, mesh, pulse, γ*), and how to read it. Include a table of the simulation conditions.
- Persian reports to be presented in person: give a one-minute summary, a key sentence to say, "how to explain" boxes, limitations stated before the supervisor asks, likely supervisor questions with short answers, and a glossary.
- (2026-11-22) **Plot labels inside figures are in English.** Matplotlib breaks Persian shaping and bidi. Explanations go in Persian in the HTML captions and text.
- Dates in Persian documents use the Persian calendar (e.g. آذر ۱۴۰۵).
- (2026-11-21) English reports for Prof. Paternò are sent only after the supervisor approves them.

## 3. Thesis / Persian article (see also the `persian-thesis-pdf` skill)

- Output: Overleaf code (XeLaTeX + xepersian) plus a PDF preview plus an Overleaf zip. Font **Yas**. Text a little larger and line spacing a little wider than usual, but not bold.
- Add content inside the existing chapters and sections. Do not add new headings unless asked, and keep the text coherent. New references are allowed.
- After every edit, review the text as an examiner would (scientific and writing errors, vague passages) and fix what you are sure of.
- Supervisor's terminology (use these words): سامانه، بسامد، مانند، اتلاف، نظریه، موضعی، روش، ویژگی، تحریک، فروافت، دیک.
- Physics corrections already made (keep them): absorption of gold below ~520 nm comes from **interband** (5d→6sp) transitions, not intraband. The CFL cost grows polynomially (~Δx⁻⁴), not exponentially. The ellipsoid depolarisation factor L_i is only an approximation for a capped cylinder. In the Lumerical runs the rod axis is **z**. Transverse/longitudinal ratios must match the numbers quoted.
- A gold nanosphere is compared with the nanorod under fair conditions (equal volume) throughout the text.

## 4. Defense slides

- Every slide has a number. No Q&A slide.
- (2026-11-08) Use our own results for figures equivalent to those in the papers the supervisor suggested (e.g. LDOS of the rod), with numbers consistent with the text. For the nanosphere, if we have no suitable figure, use the suggested papers' figures with references on the last slide.
- Numbers and labels must not overlap; captions under plots must be large enough to read.

## 5. Running simulations (lab PC, laptop, GitHub)

- (2026-11-04) **Give one comprehensive script that runs everything needed** (all checks, all cases) for days if necessary. Never hand out a series of short runs that each need a new start.
- The lab kit must: download everything at the start and then work fully offline; detect MATLAB, Lumerical and COMSOL and their licences, and use what exists; run smoke tests first; predict the remaining time from measured steps without loading the CPU; resume after a restart; package the results as a zip. The kit lives in `labkit/` and the update zips in the repo root.
- Supervisor's PC: Windows 10, Xeon 6 cores / 12 threads, 64 GB RAM, MATLAB R2018b + MNPBEM, Lumerical v241 (FDTD), no COMSOL. The user may run it for up to a week. Users' laptop: HP ProBook 645 G4, Ryzen 5 Pro 2500U, 32 GB.
- (2026-11-20) Prefer **GitHub Actions** for heavy runs where possible: matrix jobs, a `trigger.txt` push to start them, results committed by the workflow. Use `gh api` REST only.
- Git: work on the session's branch, no pull requests, commit footer as instructed, never put model identifiers in commits.

## 6. Physics and modelling decisions

### Antenna (gold nanorods at 1550 nm, host n = 1.5)
- Final trimer design: `L275_R295_A0_Y160_H3` (dimer arms 275 nm, gap 40 nm, D = 60 nm, R3 295 nm parallel at y = 160 nm). BEM (MNPBEM, retarded), Johnson–Christy gold. Data: `isi/results/bem_extra/tri2_*`. FDTD (Lumerical) is the cross-check.
- Mesh convergence must cover a **wider range of mesh sizes** (supervisor).
- Johnson–Christy gold data has known issues: always check the sensitivity to other gold datasets.
- Geometry studies requested: bring R3 closer (down to ~20-30 nm), then rotate it. Plot g2(0) and indistinguishability against the geometric parameters (R3 distance, angle, gap, ...). Include directional emission and propose a waveguide path for the emitted light.

### Quantum emitter model (decided 2026-11-17 to 2026-11-22)
- Goal: photon statistics (g2(0), indistinguishability, brightness) of a quantum-dot emitter near the designed nanorods, and how the geometric parameters change them.
- The field acting on the emitter = **laser drive + field scattered by the nanorods** (open cavity). Both must be in the model.
- **Purcell effect and the emitter-field coupling both depend on the Green function** and must both enter the quantum mechanics.
- **Final model = macroscopic QED (Dung-Knöll-Welsch quantization) built directly from the Green function.** No quasinormal modes, no Lorentzian fit; the earlier two-mode model is kept only for interpretation. Spec: `isi/report/model_green_final.src.html`.
  - J(ω) = (ω²/πħε₀c²) d·Im G(r₀,r₀;ω)·d gives both the coupling and Purcell. Γ is not a separate input: it emerges from the coupling. Never add Γ D[σ⁻] on top of the explicit field (double counting).
  - Three Green functions: G(r₀,r₀) for rate, Lamb shift and memory kernel. G(r_det,r₀) for detection, radiative fraction and NA collection. G(r₀,r_L) (reciprocity) for the local laser field K(ω).
  - **Do not assume weak coupling or Markovian dynamics.** Compute the regime criteria from G for every geometry (memory time, Γ_peak against the J width, drive against memory).
  - Solution levels: (1) Markov, (2) TCL2 memory kernel, (3) near field discretized in frequency (g_k = √(J(ω_k)Δω)) with the Hilbert space truncated at 2 excitations. Level 3 uses a **non-uniform frequency grid** (fine near ω_e, coarse far away; plan A), with convergence tests.
  - Outside the BEM window (1100-1900 nm), use δ_out from Re G. No extrapolation.
- (2026-11-22) Emitter intrinsic lifetime **τ₀ = 1.5 ns** (in the host), λ_e = 1550 nm, dipole x at the gap centre (other positions for sensitivity). Defaults until changed: pulse 200 fs Gaussian π (local field), laser on the shifted line, γ* = 1 and 10 µeV, NA 0.9 (1.3 for comparison).
- (2026-11-22) **Apply the same model to several structures: the three-rod antenna and a single nanorod** (the dimer as the intermediate case). The single rod needs a full-spectrum BEM run (`job_tri2` with `S_L<L>_H3_c1..c6`). Its length and emitter position are still to be confirmed by the user.
- Emitter material and size: a telecom quantum dot (choose material and size, then report g2(0), indistinguishability and dynamics). The supervisor will send a file with A and Γ to use.

### Tamm-plasmon study (with Prof. Paternò)
- Meep 3D FDTD is the validated tool. Draw conclusions from **full-device runs only**, not the zeroth-order cascade. Use realisation-mean spectra and paired seeds. P = 0.8 µm cells (P = 0.3 µm gives grating artefacts).
- State the grid sensitivity of island films honestly. The round-8 convergence check: dip shift +61 nm vs +66 nm (5 nm vs 3.3 nm grid).
- Lumerical is not needed for the Tamm work. The Lumerical priority is nanorod campaign 3 on the supervisor's PC (`lab_update_c3.zip` → `C3.bat`).

## Change log
- 2026-11-22 Skill created from the full conversation history (sections 1-6).
