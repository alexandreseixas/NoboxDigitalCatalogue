import puppeteer from 'puppeteer';
import { mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, 'pdf_export');
const W = 1080, H = 720;
const URL = 'http://localhost:7788/10_jogo';

if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });

// ── Size helpers ──────────────────────────────────────────────────────────
async function setSize(page, w, h) {
  await page.evaluate((w, h) => {
    DPR = 1; W = w; H = h;
    canvas.width = w; canvas.height = h;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    var wrap = document.getElementById('gameWrap');
    wrap.style.width = w + 'px'; wrap.style.height = h + 'px';
    if (typeof c1Layout === 'function') c1Layout();
  }, w, h);
}

async function shot(page, name) {
  await new Promise(r => setTimeout(r, 180));
  const path = join(OUT, name + '.png');
  // Paint the (i) badge onto the appropriate canvas if refs are available.
  await page.evaluate(() => {
    if (typeof window.__paintRefsBadge !== 'function') return;
    const screen = (typeof st !== 'undefined' && st && st.screen) ? st.screen : '';
    const isCh = screen === 'c1' || screen === 'c2' || screen === 'c3';
    const isDb = screen && screen[0] === 'd';
    if (!isCh && !isDb) return;
    if (isCh && (!window.CHALLENGE_REFS || !window.CHALLENGE_REFS[screen] || !window.CHALLENGE_REFS[screen].length)) return;
    if (isDb && (typeof DEBRIEF_REFS === 'undefined' || !(DEBRIEF_REFS[_debriefN] || {})[_debriefSlide] || !(DEBRIEF_REFS[_debriefN] || {})[_debriefSlide].length)) return;
    const cv = isDb ? document.getElementById('debriefCanvas') : document.getElementById('gameCanvas');
    window.__paintRefsBadge(cv);
  });
  await new Promise(r => setTimeout(r, 50));
  // Clip to the actual gameWrap dimensions (canvas area only).
  const rect = await page.evaluate(() => {
    const r = document.getElementById('gameWrap').getBoundingClientRect();
    return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) };
  });
  await page.screenshot({ path, clip: rect });
  console.log('✓', name);
}

// ── Boot ──────────────────────────────────────────────────────────────────
const browser = await puppeteer.launch({
  headless: false,
  args: [`--window-size=${W},${H}`, '--start-maximized'],
  defaultViewport: { width: W, height: H }
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H });
await page.goto(URL, { waitUntil: 'networkidle2' });
await new Promise(r => setTimeout(r, 1500));
// Pin gameWrap to top-left so the screenshot clip aligns with the canvas
// regardless of the body's flexbox centring.
await page.addStyleTag({ content: `
  html, body { display: block !important; align-items: initial !important; justify-content: initial !important; }
  #gameWrap { position: absolute !important; top: 0 !important; left: 0 !important; }
` });

// Helper exposed to the page: paint the (i) refs badge directly into a
// canvas at the same screen position the HTML button would occupy.
// Puppeteer's screenshot doesn't always pick up HTML elements layered on
// top of a canvas (compositing layer mismatch), so we burn the badge in.
await page.evaluate(() => {
  window.__paintRefsBadge = function(targetCanvas){
    const cv = targetCanvas || document.getElementById('gameCanvas');
    const c = cv.getContext('2d');
    if (!c) return;
    const cw = cv.width, ch = cv.height;
    // Place the badge at bottom-right of whichever canvas, with a safe inset.
    // Sized comparable to the live HTML button (~7% of canvas height).
    const btnH = Math.round(ch * 0.07);
    const r = btnH / 2;
    const cx = cw - r - Math.round(cw * 0.025);
    const cy = ch - r - Math.round(ch * 0.030);
    c.save();
    c.beginPath();
    c.arc(cx, cy, r, 0, Math.PI * 2);
    c.fillStyle   = 'rgba(29,92,98,0.12)';
    c.fill();
    c.lineWidth   = 1.5;
    c.strokeStyle = 'rgba(29,92,98,0.28)';
    c.stroke();
    c.fillStyle   = '#1D5C62';
    c.font        = '700 ' + Math.round(btnH * 0.46) + 'px Inter, Arial, sans-serif';
    c.textAlign   = 'center';
    c.textBaseline= 'middle';
    c.fillText('\u2139', cx, cy);
    c.restore();
  };
});
await setSize(page, W, H);

// ═════════════════════════════════════════════════════════════════════════
// 01 — Privacy / consent screen
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => { st.screen = 'privacy'; draw(); });
await shot(page, '01_privacy');

// ═════════════════════════════════════════════════════════════════════════
// 02 — Identification / register screen  (HTML inputs visible + filled)
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.screen = 'register';
  draw();
  if (typeof showReg === 'function') showReg();
});
await new Promise(r => setTimeout(r, 300));
// Fill the HTML inputs with realistic sample data
await page.evaluate(() => {
  // Find all visible select / input elements inside the register overlay
  var selects = document.querySelectorAll('#regOverlay select, #regOverlay input');
  selects.forEach(function(el) {
    if (el.tagName === 'SELECT' && el.options.length > 1) {
      el.selectedIndex = 1;
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  draw();
});
await new Promise(r => setTimeout(r, 300));
await shot(page, '02_register');

// ═════════════════════════════════════════════════════════════════════════
// 03 — Intro
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => { if (typeof hideReg === 'function') hideReg(); st.screen = 'intro'; draw(); });
await shot(page, '03_intro');

// ═════════════════════════════════════════════════════════════════════════
// 04–07 — Challenge 1: Escada Analgésica
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => { st.c1 = mkC1(); st.screen = 'c1'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen(); });
await shot(page, '04_c1_select');

await page.evaluate(() => {
  st.c1 = mkC1();
  st.c1.cards[0].slot = 0; st.c1.cards[1].slot = 1; st.c1.cards[2].slot = 2;
  st.c1.slots = [0, 1, 2];
  st.c1.correct = true; st.c1.tries = 1; st.c1.score = 100;
  st.c1.phase = 'result'; st.c1.resultT = 1; st.c1.revealT = 1;
  st.screen = 'c1'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '05_c1_correct');

await page.evaluate(() => {
  st.c1 = mkC1();
  st.c1.cards[0].slot = 2; st.c1.cards[1].slot = 0; st.c1.cards[2].slot = 1;
  st.c1.slots = [2, 0, 1];
  st.c1.correct = false; st.c1.wrong = [0, 1, 2]; st.c1.tries = 1; st.c1.score = 0;
  st.c1.phase = 'result'; st.c1.resultT = 1; st.c1.revealT = 1;
  st.screen = 'c1'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '06_c1_wrong');

// ═════════════════════════════════════════════════════════════════════════
// 07 — Debrief 1 (single slide now) — at NATURAL size so PNG renders correctly
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.scores[0] = 100; st.totalScore = 100;
  st.screen = 'd1'; draw();
  showDebrief(1);
  _debriefSlide = 1; _updateDebriefContent();
  if (typeof _positionRefsBtn === 'function') _positionRefsBtn();
  _refsBtn.style.display = 'flex';
  _refsBtn.style.zIndex = '50';
});
await new Promise(r => setTimeout(r, 2000));
await shot(page, '07_debrief1');

await page.evaluate(() => { hideDebrief(); });

// ═════════════════════════════════════════════════════════════════════════
// 09–12 — Challenge 2: Farmacovigilância
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => { st.c2 = mkC2(); st.screen = 'c2'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen(); });
await shot(page, '09_c2_select');

await page.evaluate(() => {
  st.c2 = mkC2(); st.c2.val = 1.3; st.c2.guessVal = 1.3;
  st.c2.score = 100; st.c2.phase = 'result'; st.c2.resultT = 1;
  st.screen = 'c2'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '10_c2_exact');

await page.evaluate(() => {
  st.c2 = mkC2(); st.c2.val = 2.0; st.c2.guessVal = 2.0;
  st.c2.score = Math.max(0, Math.round(100 * Math.pow(1 - Math.abs(2.0 - 1.3) / 52, 2)));
  st.c2.phase = 'result'; st.c2.resultT = 1;
  st.screen = 'c2'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '11_c2_close');

await page.evaluate(() => {
  st.c2 = mkC2(); st.c2.val = 35; st.c2.guessVal = 35;
  st.c2.score = Math.max(0, Math.round(100 * Math.pow(1 - Math.abs(35 - 1.3) / 52, 2)));
  st.c2.phase = 'result'; st.c2.resultT = 1;
  st.screen = 'c2'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '12_c2_wrong');

// ═════════════════════════════════════════════════════════════════════════
// 13 — Debrief 2 — at NATURAL size
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.screen = 'd2'; draw();
  showDebrief(2);
  _debriefSlide = 1; _updateDebriefContent();
  if (typeof _positionRefsBtn === 'function') _positionRefsBtn();
  _refsBtn.style.display = 'flex';
  _refsBtn.style.zIndex = '50';
});
await new Promise(r => setTimeout(r, 2000));
await shot(page, '13_debrief2');

await page.evaluate(() => { hideDebrief(); });

// ═════════════════════════════════════════════════════════════════════════
// 14–16 — Challenge 3: Via Metabólica
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => { st.c3 = mkC3(); st.screen = 'c3'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen(); });
await shot(page, '14_c3_select');

await page.evaluate(() => {
  st.c3 = mkC3();
  var ph = c3PillHome();
  st.c3.pill.x = ph.x + 300; st.c3.pill.y = ph.y - 80;
  st.c3.pill.placed = true; st.c3.pill.dragging = false;
  st.c3.dropZone = 'p2'; st.c3.correct = true;
  st.c3.phase = 'result'; st.c3.resultT = 1; st.c3.drugT = 1; st.c3.score = 100;
  st.screen = 'c3'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '15_c3_correct');

await page.evaluate(() => {
  st.c3 = mkC3();
  var ph = c3PillHome();
  st.c3.pill.x = ph.x - 120; st.c3.pill.y = ph.y - 80;
  st.c3.pill.placed = true; st.c3.pill.dragging = false;
  st.c3.dropZone = 'p1'; st.c3.correct = false;
  st.c3.phase = 'result'; st.c3.resultT = 1; st.c3.drugT = 1; st.c3.score = 0;
  st.screen = 'c3'; draw(); if (typeof _updateRefsBtnForScreen === 'function') _updateRefsBtnForScreen();
});
await shot(page, '16_c3_wrong');

// ═════════════════════════════════════════════════════════════════════════
// 17 — Debrief 3 — now 2 slides — at NATURAL size
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.screen = 'd3'; draw();
  showDebrief(3);
  _debriefSlide = 1; _updateDebriefContent();
  if (typeof _positionRefsBtn === 'function') _positionRefsBtn();
  _refsBtn.style.display = 'flex';
  _refsBtn.style.zIndex = '50';
});
await new Promise(r => setTimeout(r, 2000));
await shot(page, '17_debrief3_slide1');

await page.evaluate(() => { _debriefSlide = 2; _updateDebriefContent(); if (typeof _positionRefsBtn === 'function') _positionRefsBtn(); });
await new Promise(r => setTimeout(r, 2000));
await shot(page, '17_debrief3_slide2');

await page.evaluate(() => { hideDebrief(); });

// ═════════════════════════════════════════════════════════════════════════
// 18 — Finale (with simulated online ranking)
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.scores = [100, 78, 55];
  st.totalScore = 233;
  st.institution = 'USF Boa Saúde';
  st.rankState = 'loaded';
  st.rankData = { position: 3, avg_score: 187, participants: 24 };
  st.screen = 'finale';
  draw();
});
await shot(page, '18_finale_ranked');

// ═════════════════════════════════════════════════════════════════════════
// 19 — IEC (Informação Essencial Conforme — regulatory compliance page)
// ═════════════════════════════════════════════════════════════════════════
await page.evaluate(() => {
  st.screen = 'iec';
  showIEC();
});
await new Promise(r => setTimeout(r, 2000));   // wait for IEC PNG to load
await shot(page, '19_iec');

await page.evaluate(() => {
  if (typeof hideIEC === 'function') hideIEC();
});

// ═════════════════════════════════════════════════════════════════════════
// Done — compile PDF
// ═════════════════════════════════════════════════════════════════════════
await browser.close();
console.log('\nAll screenshots saved to', OUT);
console.log('Compiling PDF...');

const { readdirSync, createWriteStream } = await import('fs');
const { default: PDFDocument } = await import('pdfkit');

const files = readdirSync(OUT)
  .filter(f => f.endsWith('.png'))
  .sort()
  .map(f => join(OUT, f));

const doc = new PDFDocument({ autoFirstPage: false, margin: 0 });
const pdfPath = join(__dirname, 'RantuGuesser_Training_Screens.pdf');
const stream = createWriteStream(pdfPath);
doc.pipe(stream);

for (const f of files) {
  // Debrief pages were captured at 1920×1080 too (game centred in teal bg)
  doc.addPage({ size: [W, H], margin: 0 });
  doc.image(f, 0, 0, { width: W, height: H });
}

doc.end();
await new Promise(resolve => stream.on('finish', resolve));
console.log('✅ PDF saved to', pdfPath);
