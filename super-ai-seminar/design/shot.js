const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const jobs = [
    { file: 'story.html', out: '../out/story_1080x1920.png', w: 1080, h: 1920 },
    { file: 'post.html', out: '../out/post_1080x1080.png', w: 1080, h: 1080 },
  ].filter(j => require('fs').existsSync(path.join(__dirname, j.file)));

  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.join(__dirname, j.file));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    await page.locator('.stage').screenshot({ path: path.join(__dirname, j.out) });
    console.log('rendered', j.out);
    await page.close();
  }
  await browser.close();
})();
