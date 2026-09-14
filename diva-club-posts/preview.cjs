/* Screenshot any page in this folder — for previewing ornaments / WIP.
   node preview.cjs <port> <path> <width> <height> <outPng> */
const { chromium } = require("playwright");
(async () => {
  const [port, p, w, h, out] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ["--no-proxy-server", "--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text", "--hide-scrollbars"] });
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
  page.on("requestfailed", r => console.log("FAILED " + r.url()));
  await page.goto(`http://127.0.0.1:${port}/${p}`, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(400);
  await page.screenshot({ path: out });
  console.log("wrote " + out);
  await browser.close();
})();
