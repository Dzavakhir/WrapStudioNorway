// Print book/index.html to dist/<name>.pdf with Chromium. Usage: node book/print.js [out.pdf]
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const root = path.resolve(__dirname, '..');
  const out = process.argv[2] || path.join(root, 'dist', '150-ta-ChatGPT-kod-gayd.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'index.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // layout QA: report overflowing text blocks and pages
  const report = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll('.card, .tip').forEach((el) => {
      if (el.scrollHeight > el.clientHeight + 0.5) bad.push('overflow ' + (el.scrollHeight - el.clientHeight).toFixed(0) + 'px: ' + (el.querySelector('.code') || el.querySelector('.lbl')).textContent);
    });
    document.querySelectorAll('.page').forEach((p, i) => {
      if (p.scrollHeight > p.clientHeight + 1) bad.push('page ' + (i + 1) + ' overflows by ' + (p.scrollHeight - p.clientHeight) + 'px');
    });
    return { pages: document.querySelectorAll('.page').length, bad, fonts: Array.from(document.fonts).filter(f => f.status === 'loaded').length };
  });
  console.log('pages:', report.pages, '| fonts loaded:', report.fonts);
  report.bad.forEach(b => console.log('WARN', b));
  await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
  console.log('written', out);
})();
