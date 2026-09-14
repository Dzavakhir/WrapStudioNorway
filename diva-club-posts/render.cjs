/* Playwright renderer.
   Usage:  node render.cjs <port> a:9x16 a:4x5 b:1x1 ...
   Renders each <variant>:<ratio> pair at 2x device scale into out/raw/. */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const RATIOS = { "9x16": [1080, 1920], "4x5": [1080, 1350], "1x1": [1080, 1080] };

(async () => {
  const [port, ...targets] = process.argv.slice(2);
  if (!port || targets.length === 0) {
    console.error("usage: node render.cjs <port> <variant>:<ratio> [...]");
    process.exit(1);
  }
  const outDir = path.join(__dirname, "out", "raw");
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({
    args: [
      "--no-proxy-server",
      "--force-color-profile=srgb",
      "--font-render-hinting=none",
      "--disable-lcd-text",
      "--hide-scrollbars",
    ],
  });

  for (const t of targets) {
    const [variant, ratio] = t.split(":");
    const size = RATIOS[ratio];
    if (!size) { console.error(`unknown ratio: ${ratio}`); process.exit(1); }
    const [W, H] = size;
    const page = await browser.newPage({
      viewport: { width: W, height: H },
      deviceScaleFactor: 2,
    });
    const url = `http://127.0.0.1:${port}/variant-${variant}.html?r=${ratio}`;
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    page.on("requestfailed", (r) => errors.push(`FAILED ${r.url()}`));
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    try {
      await page.waitForFunction("window.DIVA_READY === true", { timeout: 20000 });
    } catch (e) {
      console.error(`  ! ${t}: DIVA_READY never fired (is lib.js included?)`);
    }
    const el = await page.$(".canvas");
    if (!el) { console.error(`  ! ${t}: no .canvas element found`); process.exit(1); }
    const box = await el.boundingBox();
    const out = path.join(outDir, `variant-${variant}-${ratio}.png`);
    await el.screenshot({ path: out });
    const warn = Math.abs(box.width - W) > 1 || Math.abs(box.height - H) > 1
      ? `  <-- WRONG SIZE, expected ${W}x${H}` : "";
    console.log(`  rendered ${t}  canvas=${Math.round(box.width)}x${Math.round(box.height)}${warn}`);
    if (errors.length) console.log("    page issues: " + errors.slice(0, 5).join(" | "));
    await page.close();
  }
  await browser.close();
})();
