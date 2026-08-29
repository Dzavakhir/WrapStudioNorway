// Render each poster HTML to a pixel-exact PNG at its native artboard size,
// then report where every text block actually landed so the Instagram safe
// zones can be checked against measurements instead of guesses.
import { chromium } from 'playwright';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = path.join(root, 'out');

const TARGETS = [
  {
    html: 'story-9x16.html',
    png: 'super-ai-seminar-story-1080x1920.png',
    w: 1080,
    h: 1920,
    // Stories chrome. Text and write-on fields must stay inside this band.
    safe: [250, 1620],
  },
  {
    html: 'post-1x1.html',
    png: 'super-ai-seminar-post-1080x1080.png',
    w: 1080,
    h: 1080,
    safe: [24, 1056],
  },
];

const only = process.argv[2];

fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
let violations = 0;
try {
  for (const t of TARGETS) {
    if (only && !t.html.includes(only)) continue;
    const src = path.join(root, t.html);
    if (!fs.existsSync(src)) continue;

    const page = await browser.newPage({
      viewport: { width: t.w, height: t.h },
      deviceScaleFactor: 1,
    });
    await page.goto(pathToFileURL(src).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);

    const board = page.locator('.board');
    await board.screenshot({ path: path.join(outDir, t.png), type: 'png' });

    // Measure the blocks that carry meaning; the diptych may bleed past the
    // safe band on purpose, so it is reported but not policed.
    const boxes = await page.evaluate(() => {
      const top = document.querySelector('.board').getBoundingClientRect().top;
      const pick = [
        ['hero', '.hero'],
        ['names', '.frame .name'],
        ['kicker', '.kicker'],
        ['pitch', '.pitch'],
        ['ticket', '.ticket'],
        ['diptych', '.duo'],
      ];
      const out = [];
      for (const [label, sel] of pick) {
        for (const el of document.querySelectorAll(sel)) {
          const r = el.getBoundingClientRect();
          out.push({
            label,
            top: Math.round(r.top - top),
            bottom: Math.round(r.bottom - top),
            left: Math.round(r.left),
            right: Math.round(r.right),
          });
        }
      }
      return out;
    });

    console.log(`\n${t.png}  ${t.w}x${t.h}   safe band y ${t.safe[0]}-${t.safe[1]}`);
    for (const b of boxes) {
      const bleeds =
        b.label !== 'diptych' && (b.top < t.safe[0] || b.bottom > t.safe[1]);
      if (bleeds) violations++;
      console.log(
        `  ${b.label.padEnd(9)} y ${String(b.top).padStart(4)}-${String(b.bottom).padStart(4)}` +
          `  x ${String(b.left).padStart(4)}-${String(b.right).padStart(4)}` +
          (bleeds ? '   <-- OUTSIDE SAFE BAND' : '')
      );
    }
    await page.close();
  }
} finally {
  await browser.close();
}

if (violations) {
  console.error(`\n${violations} block(s) outside the safe band.`);
  process.exitCode = 1;
}
