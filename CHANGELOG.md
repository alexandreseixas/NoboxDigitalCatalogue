# CATÁLOGO NOBOX — Changelog

All notable changes to the Nobox interactive catalogue (forked from the Bial Rantudil® CLM game), in reverse chronological order.

**Versioning convention:** date-based — `vYYYY-MM-DD` for each distinct shipping build.

Convention loosely follows [Keep a Changelog](https://keepachangelog.com/) — sections are **Added**, **Changed**, **Fixed**, **Removed**.

---

## [v2026-05-28b] — Carry the menu's polish through the rest of the app

Three signature moves from the menu modal extended into the canvas-drawn surfaces, so the catalogue and the modal read as one product instead of an overlay-over-canvas.

### Added — canvas chrome
- **Amber gradient underline below the canvas top bar.** A 2 px horizontal gradient (`#F5A800 → #FDD47B → transparent`) drawn just below the white top-bar strip in `drawTopBar()`. Same gradient that anchors the modal header. Appears on every challenge and debrief screen (c1 · c2 · c3 · d1 · d2 · d3 · finale), so wherever the top bar is, the brand band is.

### Added — finale screen
- **Finale cards now mirror the menu modal's `.cm-card.active` vocabulary.** Each of the three score breakdown cards picks up:
  - An eyebrow band — `DESAFIO 01 / 02 / 03` in tracked uppercase — exactly the same eyebrow language the modal uses on its section labels.
  - An **amber active state** (border, tinted background, amber-tinted eyebrow + shadow) on the card(s) with the highest score. Ties are handled correctly — if two challenges tie for top, both light up. If everything's at zero, nothing lights up (catalogue/demo state).
  - Slightly tightened layout to make room for the new eyebrow.

### Added — privacy screen
- **Amber gradient accent under `Aviso de Privacidade`** — the same short fading line the modal uses under its title, now anchoring the privacy notice too.

### Result
Every page the user lands on carries the same signature: gradient navy/teal element + amber underline + clean card grid + numbered or labelled badges. The transition from canvas screen → menu modal → UL-250 sample feels like moving between views of one product, not opening separate prototypes.

---

## [v2026-05-28] — Esc key fix + cross-surface polish for continuity

### Fixed
- **`Esc` kbd in the menu footer rendered as `=Esc=`** — at 10 px font-size with a 1 px border, the rounded rectangle borders read as two vertical strokes flanking the text. Rebuilt as a proper key-cap component: 22 px tall, 8 px horizontal padding, SF Mono/Menlo, subtle linear-gradient fill, 2 px bottom border for the "physical key" depth cue. Now reads cleanly as `Esc`.

### Polished — cross-surface continuity
The menu modal sets the polish bar for the rest of the HTML UI; brought the menu trigger and the UL-250 sample into the same family.

- **UL-250 slide topbar** now carries the menu modal's signature amber gradient underline (`linear-gradient(90deg, #B58858 → #D8B388 → transparent)`) below the eyebrow + lockup row, so the slide reads as a continuation of the modal's header pattern.
- **UL-250 slide bottom-strip** picked up a subtle 1 px top divider (`rgba(255,255,255,0.08)`) above the slide-meta + `Powered by Biocodex` row, mirroring the menu footer's separation pattern.
- **Menu trigger button (`#catMenuBtn`)** — amber disc bumped from 20 → 22 px with an inset shadow for depth; padding/letter-spacing tightened to echo the modal's eyebrow typography. Hover transitions slowed from 180 ms → 220 ms for a softer feel.

### Result
All three HTML surfaces (catalogue chrome, menu modal, UL-250 sample) share the same family of design moves: gradient navy backgrounds, amber underline accents, subtle border separators, rounded pills with consistent corner radii. A presenter clicking through reads them as one product, not three separate prototypes.

---

## [v2026-05-27h] — Real debriefs restored + "Powered by" label

### Changed
- **`An endorsement of` → `Powered by`** in the UL-250 sample's bottom strip. Simpler, clearer for a proposal context.

### Restored (from the Bial source project)
After confirming each PNG has no `Rantudil` logo visible, swapped the placeholder debriefs back to the original Bial content. These are real, polished clinical slides — they reference `Acemetacina` (the generic active ingredient name) and real comparator drugs (Naproxeno, Diclofenac, Etodolac, Ibuprofeno, Etorixocib) but carry no brand mark, so they read as plausible debrief content during a catalogue demo without leaking the Bial brand:

- **`d1.png` ←** original Bial slide. Left side: WHO analgesic ladder + "26.4 % da população portuguesa sofre de lombalgia". Right side: "Acemetacina é o AINE com melhor perfil de segurança multissistémica" with anatomy icons (liver / GI / kidneys). Visually richer than the placeholder I built — earns the "this is what a real debrief looks like" moment.
- **`d3_1.png` ←** original. "Acemetacina é o único AINE com metabolização hepática de fase II" with the four-attribute cascade and the comparator binding-rate table (Acemetacina 87.6 % vs Naproxeno/Etodolac/Ibuprofeno 99 %, Diclofenac 99.7 %, Etorixocib 92 %).
- **`d3_2.png` ←** original. "Acemetacina é o AINE com menor risco de interação medicamentosa" interaction matrix — anti-hypertensives × anti-inflammatories × anti-coagulants.

### Kept as placeholder
- **`d2.png`** — the original Bial pharmacovigilance slide has the **Rantudil® shield** dead center, so it stays as my Comparador A–D + Medicamento X bar-chart placeholder. Reuse this slot if Biocodex ever ships a Rantudil-free pharmacovigilance variant.

### Backups
- The Nobox placeholder versions of `d1.png`, `d3_1.png`, `d3_2.png` are kept under `game_assets/debriefs/_placeholder_backup/` in case the catalogue needs to ship to a non-pharma audience and the Acemetacina references become inappropriate.

### Audit
- Re-rendered every catalogue screen + the UL-250 slide states via Playwright. Everything reads clean: menu pill mirrors the UL-250 back button, debriefs flow naturally from the challenges, the "Powered by Biocodex" footer is balanced. No fixes needed beyond what's listed above.

---

## [v2026-05-27g] — Catalogue menu button moved to mirror UL-250 back button

### Changed
- **`#catMenuBtn` now `position: fixed; top: 16px; left: 16px;`** — same exact viewport coordinates as the UL-250 sample's `.back-btn`. Previously the menu sat absolute-positioned inside `#gameWrap` at top-right, just below the canvas top bar.
- **Visual treatment matched** to the UL-250 back button: 7px padding, 12px font, 20px disc icon, identical shadow `0 6px 18px rgba(8,18,22,0.20)`. The amber disc accent (Nobox) versus the gold disc (UL-250/Biocodex) is the only intentional differentiator — same component, two brand worlds.
- **Removed `positionCatMenuBtn()` helper.** Fixed positioning means the button no longer depends on canvas top-bar height to stay clear of the score pill; one less moving part on resize.

### Why
The two surfaces (the catalogue and the UL-250 sample) now share an identical "floating navigation pill" UI primitive at the same viewport coordinate. A presenter clicking from one to the other sees the affordance land in the same spot, which sells the impression that they're inside one product, not two separate prototypes.

---

## [v2026-05-27f] — UL-250 slide matched to catalogue dimensions + real Biocodex logo

### Changed
- **Slide canvas now 1080×720 (3:2)** — same dimensions and aspect as the catalogue's gameWrap. Previously 1920×1080 (16:9), which made the transition from the catalogue to the sample feel like jumping between two different products.
- **Cream-teal surround** (`#D6E8E6`) and rounded-corner navy frame with the catalogue's signature shadow (`0 12px 48px rgba(29,92,98,0.22)`), so the sample sits in the exact same staging as every catalogue screen.
- **All internal proportions scaled** to fit the smaller canvas: padding 80→48 px, question font 68→38 px, options padding 22→14 px, label font 34→22 px, feedback panel font 22→14 px. Density matches the catalogue's information density.

### Added
- **Real Biocodex logo embedded** (`samples/biocodex_logo.svg` + `biocodex_logo_white.svg`). The white variant has the dark-gray wordmark recolored to white while preserving the magenta `#B51E84` dot and gold `#D2CF60` accent on the right of the mark — the original brand identity stays intact on the navy canvas. Embedded via `<img>` for crisp scaling.

### Verified
- Clicked through the menu link end-to-end (`Menu → Exemplos por cliente → UL-250 · Biocodex`) and the destination slide sits at exactly the same scale as the catalogue screens. Visual frame is preserved; only the brand world changes.

---

## [v2026-05-27e] — UL-250 slide spacing audit + restructure

Rendered the slide at 1920×1080 via Playwright and the bottom 1/3 was a mess: the peach speech bubble's upward-pointing triangle was piercing into the option row, the bubble + status/reset row + slide meta were stacked too tightly (content sum exceeded the 920 px available canvas height), and the slide-meta was absolutely-positioned right under the actions row.

### Restructured
- **Old:** `[options] → footer-band {explanation bubble + actions row} → endorsement` with absolutely-positioned `slide-meta` at the bottom. Three vertical layers fighting for ~150 px of space.
- **New:** `[options] → feedback (single horizontal panel) → bottom-strip {slide-meta · endorsement}`. The peach panel now holds the status pill, explanation text and reset button in a single row.
- **Triangle pointer removed.** It was pointing up at nothing meaningful and clipping into the option above. The feedback panel reads as a standalone callout now.
- **Status pill polished.** Small filled pill — green for "Resposta correta", red for "Não exatamente" (via `.feedback.is-wrong .status-pill`), with a tiny white dot for affordance.
- **Reset button moved inside the bubble**, restyled as a navy block ("Tentar outra vez") at the right edge.

### Tightened vertical rhythm
- Question font 78 → 68 px so it fits on two lines without UL-250® wrapping.
- Question top margin 80 → 56 px.
- Options grid top margin 64 → 48 px; gap 24 → 20 px; option padding 28×36 → 22×30; letter circle 58 → 52 px; label font 38 → 34 px.
- Feedback panel top margin: 32 px clear above the options grid.

### Result
Both correct and wrong states now render cleanly with daylight between every element. Bottom-strip lives on its own baseline with proper separation from the feedback panel.

---

## [v2026-05-27d] — UL-250 / Biocodex sample wired into the catalogue

Sets up the "tell + show" pitch: tell the prospect we can brand this for them, then show them an actual Biocodex-skinned example one click away.

### Added
- **`samples/ul250_pergunta.html`** — fully interactive multiple-choice slide in the UL-250/Biocodex design language (navy canvas, gold underline, peach explanation bubble, serif italic emphasis on *S. boulardii*). Options are clickable buttons with three states (neutral, correct = green/check, wrong = red/X). On wrong answer, the correct option auto-reveals 350 ms later so the lesson lands. A peach speech bubble + status label slide in with the explanation, and a "Tentar outra vez" reset button restores neutral state. Keyboard accessible (Enter/Space) with `role="radio"` semantics.
- **Floating "Voltar ao catálogo" pill** (top-left) on the sample slide — navy text on white, gold arrow disc, points to `../01_jogo.html`.
- **New "Exemplos por cliente" section** in the catalogue's menu modal. Tinted background (subtle navy gradient) distinguishes it from the regular nav. Single card uses Biocodex navy for the badge and a green arrow disc on the right — reads as a wink to UL-250's product color without leaving the catalogue's design language.

### Wiring
- The menu card is an `<a href="samples/ul250_pergunta.html">` instead of a `<button data-screen>`. The existing menu JS handler checks for `data-screen` and returns early when absent, so the link's native navigation fires normally.

### How to demo it
1. Open the catalogue, click the top-right `Menu`.
2. Scroll to **Exemplos por cliente** at the bottom.
3. Click the **UL-250 · Biocodex** card → lands on the interactive slide.
4. Click any option → answer revealed + explanation. Reset to try again.
5. Click **Voltar ao catálogo** to return to the generic catalogue.

---

## [v2026-05-27c] — Real visual audit + polish pass

Set up Playwright + headless Chromium inside the sandbox to actually render every screen and the menu modal, then fixed everything that looked wrong.

### Fixed (menu modal)
- **Header eyebrow/title overlap.** `CATÁLOGO INTERATIVO` and `Mapa de Navegação` were sitting on the same baseline. Added explicit `display: block` and `line-height` on `#catMenuEyebrow` and `#catMenuTitle` so they stack cleanly.
- **`&geacute;` literal in Desafio 1 description.** Typo — should have been `&eacute;`. Renders as "Escada analgésica da OMS" now.
- **Debrief ⓘ glyph rendered as an empty box** on browsers without that Unicode codepoint. Replaced with a serif italic `i` so it's bulletproof.
- **Active-card checkmark misplaced.** `.cm-card` was missing `position: relative`, so the `::after` checkmark was positioning relative to the panel instead of the card — visible as a stray amber dot in the top-right of the modal header. Added `position: relative` to `.cm-card` and re-styled the checkmark as a small amber filled circle in the card's top-right corner.

### Fixed (canvas)
- **Privacy screen shield emoji rendered as an empty box** on browsers without the 🛡 codepoint. Replaced with a path-drawn teal shield + white checkmark inside — same visual intent, zero font dependency.

### Fixed (debrief PNGs)
- **Double Nobox logo** on every debrief screen (one in the canvas top bar, one baked into the PNG). Regenerated `d1.png`, `d2.png`, `d3_1.png`, `d3_2.png` without the embedded logo since the top bar already provides the brand frame.
- **`d2.png` upgraded to a real comparator histogram** instead of just a title card — five horizontal bars showing Comparadores A–D + Medicamento X with their data values, so the debrief reads as a credible clinical-evidence slide.
- **`d3_1.png` upgraded to a two-column pathway visual** — CYP450 in red ("partilhada", "risco elevado de interações") next to Glucoronoconjugação in teal with the Medicamento X pill embedded ("menor probabilidade de interações"). Mirrors the in-game C3 mechanic.
- **`d3_2.png` upgraded to a real interaction matrix** — 3 therapeutic classes (α/β/γ) × 5 columns (Medicamento X + Comparadores A–D) with color-coded cells (`Sem int.` / `Minor` / `Mod.` / `Major`) showing Medicamento X's favourable profile.

### Build tooling
- Installed Playwright + chromium-headless-shell in the workspace so every future change can be visually verified end-to-end. Screenshot script in `/tmp/snap_all.py` (kept locally) renders all 13 screen states in ~25 s.

---

## [v2026-05-27b] — Polished customer-facing menu modal

The dev panel was debug furniture — fine for QA, wrong for proposals. This build adds a proper branded modal aimed at prospects and live sales demos.

### Added
- **`#catMenu` modal** — a centered card-style HTML overlay with the Nobox palette: a teal gradient header with an amber underline accent, three labelled sections (`Início`, `Desafios clínicos`, `Encerramento`), and one card per screen. Each card has a numbered/lettered badge (01/02/03 for setup, D1/D2/D3 for challenges, ⓘ for debriefs, 04 amber for the finale, 05 for credits), a screen title, and a one-line description (e.g. *Escada analgésica da OMS*, *Notificações adversas*, *Doente polimedicado*). Cards have hover lift, an amber active state, and a check glyph on the current screen.
- **Open/close animations** — backdrop blurs in over 220 ms, panel rises with a subtle scale/translate via `cmRise`.
- **Dismissal paths** — close × button, backdrop click, and Esc key all close the modal.
- **Card click → close → navigate** — a 60 ms delay lets the modal start closing before the canvas screen-flash fires, keeping transitions smooth.
- **Active-screen highlight** — `_updateCatMenuActive()` runs on open to add an amber border to whichever card matches `st.screen`.
- **Responsive collapse** — `@media (max-width: 720px)` drops the grids to a single column.
- **Polished trigger button** — `#catMenuBtn` is now a white pill with a teal label and an amber-disc icon, hover state flips to solid teal. Matches the rest of the brand chrome.

### Changed
- Click on `#catMenuBtn` now opens the new modal instead of the dev panel. The dev panel stays accessible behind `?dev=1` + 5 taps on the bottom-right for engineering/QA use.
- `draw()` hides `#catMenuBtn` when **either** the customer modal **or** the dev panel is open.

### Build
- New standalone preview file: `menu_preview.html` — open in any browser to see the modal in its open state without launching the full game.

---

## [v2026-05-27] — Quick-access menu + visual audit pass

### Added
- **Quick-access menu button** (`#catMenuBtn`) — small dark-teal "☰ Menu" pill in the top-right of the canvas, just below the top bar. Click opens the existing screen-jump panel (renamed `DEV MODE` → `MENU DE NAVEGAÇÃO`), which lists every screen for one-tap navigation during a sales demo. The button auto-positions on resize via `positionCatMenuBtn()`, mirroring the same JS-driven sizing pattern the debrief/refs buttons use.
- **Menu auto-close on navigation** — picking a screen in the panel now sets `DEV.open = false` before `go()` so the panel dismisses cleanly instead of staying open over the new screen.
- **Menu button hides while panel is open** — `draw()` toggles `#catMenuBtn` display each frame so the bright HTML button doesn't sit on top of the dimmed canvas overlay.

### Changed
- **Dev panel rows reflowed** — the lonely `Credits` row left behind by the IEC removal is gone; `Credits` joined row 2 (`C2 · D2 · C3 · D3 · Finale · Credits`).
- **`#catMenuBtn` z-index = 23** so the white screen-flash transition (z-index 25) covers the menu button cleanly between screens.

### Fixed
- **Top-bar product placeholder clipped off-canvas at finale.** With `scoreW = 0` on the finale screen, the previous formula `scoreRightX - scoreW + W*0.030` put the pill's right edge at `W*1.005` (about 6 px past the canvas). Clamped via `Math.min(scoreRightX, ...)` so the pill stays fully on-canvas on every screen.

### Audited (no change needed)
- Credits screen — pure Nobox logo + "Sair →" button, no brand leakage.
- C1 ladder rendering with restored WHO labels — the in-game card layout's auto-fit logic handles "AINEs + Opióides fortes" without truncation.
- C2 chart axis — "Comparador A/B/C/D" labels fit comfortably in the label column at any canvas size.
- C3 cards — `Medicamento A/B/C` labels share the same auto-fit path as the original drug names.
- Top-bar geometry on regular screens — verified ~15 px gap between product placeholder and score pill.

---

## [v2026-05-26c] — C1 restored to WHO analgesic ladder

### Changed
- **C1 cards reverted** to the original WHO analgesic ladder labels: `AINEs / Paracetamol`, `AINEs + Opióides fracos`, `AINEs + Opióides fortes` (correct steps 1–3) with `Paracetamol` and `Opióides fortes` as distractors. The ladder is a public clinical reference (Organização Mundial da Saúde, 1986) — not Bial IP — so genericizing it added no privacy value while making the puzzle abstract.
- **C1 victory text restored** to `1º AINEs / Paracetamol → 2º AINEs + Opióides fracos → 3º AINEs + Opióides fortes¹.`
- **C1 reference** (challenge `(i)` button) updated to cite the WHO ladder explicitly: `World Health Organization. WHO's pain ladder for adults. WHO, 1986. Adaptado por APMGF — Escada Analgésica.`
- **DEBRIEF_REFS[1][1]** first entry also updated to the WHO citation.
- **`d1.png` rebuilt** with a ladder-centric layout: three stacked rounded bars (AINEs / Paracetamol → AINEs + Opióides fracos → AINEs + Opióides fortes), a `POSICIONAMENTO DO PRODUTO` footer with a `Medicamento X` placeholder pill, and the same Nobox brand frame as the other debriefs.

---

## [v2026-05-26b] — IEC removal + debrief placeholders

### Changed
- **IEC step bypassed.** The finale screen now navigates directly to `credits` instead of `iec` (`01_jogo.html` line 2185). The `showIEC()` / `hideIEC()` helpers stay in place as dead code so per-client builds can re-enable them by changing one line.
- **Dev menu IEC entry commented out** (line 1448) — the screen is no longer reachable through the dev shortcut either.
- **`game_assets/iec.png` replaced** by a 2160×1620 brand-safe placeholder document (`Informação Essencial Conforme — conteúdo a definir por produto`). Original Rantudil IEC removed.

### Removed
- All four debrief PNGs (`d1.png`, `d2.png`, `d3_1.png`, `d3_2.png`) replaced with 1920×1080 Nobox-branded placeholder slides. Each shows the Nobox logo, an amber `Medicamento X` pill, a topic-specific subtitle (posicionamento / farmacovigilância / via metabólica / interações) and a footer note (`Placeholder de debrief · conteúdo final a definir por produto`). Original images contained explicit Acemetacina / Rantudil® content and have been overwritten.

### Build
- Asset payload dropped from ~6.3 MB to ~0.4 MB across the five replaced PNGs.

---

## [v2026-05-26] — Catalogue fork (Nobox demo build)

Forked from the Bial Rantudil® CLM build (v2026-05-22) and genericized for use as a Nobox sales-demo catalogue. The game mechanics, animations, register flow, analytics pipeline and post-event reporting are unchanged; only branding, product names and clinical content have been stripped.

### Changed
- **Title** → `Catálogo Nobox` (was `Rantudil Quiz`).
- **House logo** → Nobox blue logo (`Logo_Azul_Nobox.png`) replaces the Bial SVG in every screen (top-left corner of canvas + top bar). Image natural-aspect ratio is now read from `naturalWidth/naturalHeight` so any logo fits cleanly.
- **Product mark** → A `Medicamento X` text pill, rendered by the new `drawProductPlaceholder()` helper, sits where the Rantudil product logo used to. Per-client builds can swap this for a bitmap.
- **Intro screen** is now rendered programmatically (Nobox logo + `Medicamento X` placeholder + subtitle + CTA). The original `cover_rantudil.jpg` is no longer loaded.
- **C1 cards** → `Medicamento X`, `Medicamento X + Medicamento Y`, `Medicamento X + Medicamento Z` (correct slots 0/1/2), with `Medicamento Y` and `Medicamento Z` as distractors. Victory text updated accordingly.
- **C2 comparator labels** → `Comparador A/B/C/D` (was Ibuprofeno/Diclofenac/Etoricoxib/Naproxeno). Numerical data preserved so the histogram still looks credible. Interactive row labelled `Medicamento X` (was Acemetacina). Result-popup copy and chart subtitle updated.
- **C3 patient drugs** → `Medicamento A/B/C` with abstract therapeutic classes (`Classe terapêutica α/β/γ`). Question copy now refers to `Medicamento X` instead of "AINE". Pill label and result text genericized.
- **References** → `DEBRIEF_REFS` and `CHALLENGE_REFS` blocks fully rewritten as plausible-looking placeholder citations (e.g. `Laboratório Exemplo, S.A.`, `Sociedade Científica de Referência`, `Base de dados de farmacovigilância (demonstração)`). Real Bial product-info URLs removed.
- **Privacy notice** → Copy rewritten to read as a Nobox-run demo; tap-through link points to `https://www.nobox.pt/privacidade`; footer reads `Informação Sobre Proteção de Dados | nobox.pt`.
- **localStorage keys** → `rantudil_*` → `catalogo_nobox_*` for scores, ranking cache and event queue, so the demo can't collide with any live Bial event stream.

### Removed
- `game_assets/cover_rantudil.jpg`, `game_assets/Logo-Rantudil.svg`, `game_assets/logos/bial_logo.svg` are no longer referenced (file deletion requires manual step — assets remain on disk for now).
- `pdf_export/` snapshots and the shipping `.zip` builds were not copied into the catalogue fork.

### Known follow-ups
- **Debrief PNGs** (`game_assets/debriefs/d1.png`, `d2.png`, `d3_1.png`, `d3_2.png`) and the IEC document (`game_assets/iec.png`) still contain the original Bial/Rantudil clinical content. For a pure-demo catalogue these should be swapped for placeholder slides ("Debrief — conteúdo a definir por produto"). Tracked as task #12.
- Internal variable names (`bialLogo`, `rantudilLogo`) and function names (`drawBialLogoCorner`, `drawRantudilMark`) intentionally left in place to keep this diff focused on user-visible content. Rename in a future refactor when extracting the engine.

### Provenance
- Original game-only build documented below remains the authoritative production code for the Bial client.

---

## [v2026-05-22] — Label refresh + new thumbnail

### Changed
- **C1 card labels reordered to lead with "AINEs"** (line 2063–2065 of `01_jogo.html`). All three correct cards now read as `AINEs / Paracetamol`, `AINEs + Opióides fracos`, `AINEs + Opióides fortes`. Distractor cards (`Paracetamol`, `Opióides fortes`) unchanged.
- C1 victory popup text updated to match new label order: `1º AINEs / Paracetamol → 2º AINEs + Opióides fracos → 3º AINEs + Opióides fortes¹.`
- Analytics prompt (`analytics/REPORT_PROMPT.md`) — C1 reference labels updated so future LLM-generated reports align.
- **New CLM-manager thumbnail** (`01_thumbnail.jpg`) — 800×600, generated from `game_assets/cover_rantudil.jpg`. Adds an amber "RantuGuesser" title pill positioned where the in-game "Começar →" button appears. Previous thumbnail (309×232) replaced.

### Notes
- Historical analytics events store **card IDs** (`slots: [0, 1, 2]`), not labels — so label changes don't break prior data. Only the human-readable mapping changes.

---

## [v2026-05-21] — Analytics dashboard + C2 fix

### Added
- **Analytics report generator** (`analytics/generate_report.py`) — pulls events from Supabase, computes 10+ analyses, emits self-contained HTML report. Includes funnel, first-try accuracy, wrong-answer distributions, time-per-screen, register friction, device breakdown, top-institutions table, restart rate.
- **LLM-based report prompt** (`analytics/REPORT_PROMPT.md`) — alternative to the Python script. Paste into Claude/ChatGPT with `events.csv` attached.
- **Real-data report** generated from production events: `analytics/report.html` (26 KB) + `analytics/report.pdf` (610 KB).
- **Date-window filter** in the analysis script (`DATE_FROM_FILTER` constant) — current default = `2026-05-14` onward.
- **C2 histogram staggered labels** — reference comparators (Naproxeno 11.9, Etoricoxib 16.4, Diclofenac 31.0) placed at alternating vertical positions to prevent overlap.
- **PDF print styles** — `@page A4`, `break-inside: avoid` on cards/sections/tables, `-webkit-print-color-adjust: exact` so brand colors survive Chrome's print rendering.
- `analytics/requirements.txt` — Pillow, requests, matplotlib.

### Fixed
- **C2 analytics tracking bug** (`01_jogo.html` line 3082) — was `correct: c.guessVal === 28` (never matched, slider is continuous + real answer is 1.3). Now uses `correct: c.score >= 80`, matching the game's own celebration threshold (~±1.07 of target).
- C2 histogram x-axis label clipping ("50" was rendered half-off the SVG viewBox).
- C2 histogram bars overlapping reference labels at top of chart.

### Changed
- Headline C2 framing in reports: **HCPs overestimate** (median guess 4.1 vs. correct 1.3) — was previously mis-framed as underestimation because of the `=== 28` bug.

---

## [v2026-05-15] — Game-only deck

### Changed
- **Deck restructured to game-only**: the CLM now opens directly into the game. No cover slide, no presentation chain.
- `10_jogo.html` → `01_jogo.html` (renumbered to be the deck's only slide).
- `10_thumbnail.jpg` → `01_thumbnail.jpg`.
- `exitToDeck()` simplified to just `go('privacy')` — restarts the game for the next HCP rather than trying to navigate to a non-existent cover slide.
- Canvas-failure fallback link updated: `"Voltar à apresentação"` → `"Tentar novamente"` (`javascript:location.reload()`).

### Removed
- Slides 02–09 (educational HTML files + their thumbnails) — content was delivered separately, no longer needed in this CLM.
- `assets/`, `css/`, `js/` folders — only the old slides referenced them.
- The minimal cover slide created on 2026-05-15 was also removed once the client confirmed no cover was wanted.

### Build
- Resulting zip: 7.1 MB / 18 files (down from 13 MB / 84 files in the previous build).

---

## [v2026-05-11b] — Analytics event stream

### Added
- **Append-only event-stream layer** in `01_jogo.html`. Captures: `session_start`, `screen_enter`, `c1_answer`, `c2_answer`, `c3_answer`, `register_complete`, `session_complete`.
- **Offline-resilient queue** — events buffer to localStorage (`rantudil_pending_events_v1`), capped at 500 entries, auto-flush on `online` event + on visibility change. Mirrors the existing `submitScore` pattern.
- **Device fingerprinting at session start** — os/form/screen dimensions/viewport/DPR/touch/UA (no PII).
- **Register field friction tracking** — per-field focus duration + count + keystroke count on the institution-search input.
- **Per-screen timing** — `screen_enter` includes `prev_screen_ms` (time on previous screen).
- **Supabase `events` table schema + RLS policy** documented inline in the analytics scaffolding comment.

### Notes
- Privacy contract preserved: only `institution` (already collected with consent) and aggregate technical data; no IPs, no user names, no identifiers beyond a per-session UUID.

---

## [v2026-05-11a] — Register screen polish + ship readiness

### Added
- **`_centerRegCard()`** — JS-managed register-card centering via dynamic `padding-top`. Replaced the `align-items: center → flex-start` snap that couldn't be CSS-transitioned.
- **RAF throttle to ~10 fps** on the register screen — saves CPU and avoids competing with iOS keyboard animation on iPad.
- **`<select>` focus guard** — ULS/Tipo dropdowns no longer trigger the `.kb-open` keyboard-anticipation logic (iPad picker wheel doesn't shrink `visualViewport`, so the previous logic caused a false snap).
- **`window.resize` → `_centerRegCard()`** — orientation-change safety for older iPads where `visualViewport.resize` may not fire.

### Changed
- Register card CSS: `align-items: flex-start` always (was `center`). `transition` now covers both `padding-top` and `padding-bottom`.
- `.kb-open` class no longer overrides `align-items` — only sets `padding-bottom: 280px`.
- Keep `lastTime` fresh during throttled frames so the first frame after exiting register has `dt ≈ 1` (no visible jump).
- Top bar logo width clamped (`Math.min(...)` against W*0.32) so very wide screens don't overflow.
- Privacy-link tap target widened.

### Fixed
- C1 Verify button hidden during result phase (line 2716–2718).
- C2 Confirm button hidden during result phase + requires `c2.touched` to enable.
- C3 pill always visible on placement.
- C3 wrong-result: pill **hidden entirely** (was previously shown at 45% opacity).
- C1 victory popup: "+ AINEs" added after "Opióides fracos" and "Opióides fortes".
- C2 subtitle: removed redundant "de *reports*" phrase.

### Build
- First polished zip shipped: `rantudil-clm-260511.zip` — 13 MB, 84 files.

---

## [v2026-05-11] — Final clinical-copy review (git-tracked)

From git history; pre-this-session polish.

- C2: tagline `'mais seguro'` → `'com menos reports'`, italic `<i>reports</i>` everywhere.
- C3 victory popup: `'não interage'` → `'tem menor probabilidade de interagir'`.
- C3 defeat popup: `'a via correta'` → `'a via preferencial'`.
- Finale: removed `'o AINE com melhor perfil de segurança GI'` tagline.

---

## [v2026-05-07] — Register redesign + PDF export

From git history.

### Added
- PDF export: include IEC compliance page (page 19).
- PDF export: burn-in (i) badge + uniform 1080×720 page sizing.
- PDF export: trigger `_updateRefsBtnForScreen()` on every challenge capture.
- Register: `'tap to change'` chevron on filled search row.

### Changed
- Debriefs: updated reference lists for D1, D3.1, D3.2.
- Register: card properly centred — keyboard padding only when needed.
- Register: equalised card top/bottom white space.
- Register: light polish — mint check badge, breathing room, hint colour.
- Register: dropdown polish — touch-friendly items, cleaner alignment.
- Register: full redesign — debrief-aligned, icon-led, progressive disclosure.
- C3 victory popup: `'Acertaste!'` → `'Correto!'` for professional tone.
- C3: renumber reference markers per state — both lists fully consistent.
- Refs: render markers as smaller raised digits — consistent typography.
- C3: split refs into separate victory/defeat lists with clean marker scheme.
- Refs button: only show during the result popup, not during play.

### Removed
- Unused asset files.

---

## [v2026-05-06] — Reference markers + debrief refresh

From git history.

### Added
- C3: ¹ marker to "Sem interação" (Sinvastatina) for completeness.
- C3: reference markers ¹/²/³ across drug effects and popup messages.
- C2: ¹ reference marker on all three result-popup info variants.
- C1: superscript ¹ reference markers in the question header.
- References: clickable URLs + reposition result-popup CTA.

### Changed
- Debriefs: refreshed artwork for D1, D2, D3.1, D3.2 with new layouts.
- Finale: replaced text glyph icons with branded mint-teal illustrations.
- Debriefs: D1 collapsed to 1 slide, D3 expanded to 2 slides.
- References: replaced `CHALLENGE_REFS` with Bial-supplied citation list.
- C2: shrunk chart area so result popup never covers the Acemetacina bar.
- C2: capitalised "acemetacina" → "Acemetacina" in title question.
- C2: restored full date range in chart subtitle, kept ¹ at end.
- C2: replaced `(2001–2024)` with ¹ in the chart-source subtitle.
- C1: replaced `(OMS)` with ¹ in the victory popup info text.

---

## [v2026-05-05] — C2/C3 core mechanics

From git history.

### Added
- References: surface the (i) modal on C1/C2/C3 challenge screens.

### Changed
- C3: rename `Glucuronoconjugação` → `Glucoronoconjugação` (per client spec).
- C3: drag hint → `'Arraste para a via metabólica preferencial'`.
- C3: all-title header with surgical bold emphasis.
- C3: title/subtitle replaced with new clinical-scenario phrasing.
- C2: lowercase "acemetacina" in title question.
- C2: enlarge "A SUA ESTIMATIVA" pill.
- C2: rework — taller card header, Acemetacina label, restored pill.
- C2: cap scale at 50, widen bar area for iPad precision.
- C2: new title/subtitle, EudraVigilance source label, slider `?` on initial state.

---

## Asset inventory at current build

```
01_jogo.html          198 KB   — the game (CLM opens here)
01_thumbnail.jpg      114 KB   — CLM-manager thumbnail (800×600 with title pill)
game_assets/
├── cover_rantudil.jpg          1.4 MB  — intro hero
├── iec.png                     731 KB  — IEC compliance doc
├── Logo-Rantudil.svg           9.6 KB
├── debriefs/                   6.3 MB  — d1/d2/d3_1/d3_2 illustrations
├── icons/                      158 KB  — challenge breakdown icons
└── logos/                       35 KB  — Bial + Nobox logos
```

## Repository layout

```
250923-RANTUDIL-Nobox/
├── 01_jogo.html              — the game
├── 01_thumbnail.jpg          — CLM thumbnail
├── CHANGELOG.md              — this file
├── game_assets/              — all imagery the game uses
├── analytics/                — analytics tooling (not in shipped zip)
│   ├── generate_report.py
│   ├── REPORT_PROMPT.md
│   ├── requirements.txt
│   ├── report.html           — latest generated report
│   └── report.pdf
└── rantudil-clm-260511.zip   — current shipping build
```

## Versioning the zip going forward (recommendation)

The current workflow overwrites `rantudil-clm-260511.zip` on every change. Consider switching to date-tagged builds so historical versions remain on disk:

```bash
zip -r "rantudil-clm-$(date +%y%m%d).zip" 01_jogo.html 01_thumbnail.jpg game_assets
```

That keeps any previous build retrievable without needing git checkout.
