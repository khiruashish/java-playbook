// Screenshot each HTML file (1920x1080) to a PNG next to it; warn when content overflows the slide.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  let bad = 0;
  for (const f of process.argv.slice(2)) {
    await page.goto('file://' + f);
    await page.evaluate(() => document.fonts.ready);
    const o = await page.evaluate(() => {
      const m = document.querySelector('.main'); const r = m.getBoundingClientRect();
      let worst = 0;
      for (const e of m.querySelectorAll('*')) {
        const b = e.getBoundingClientRect();
        worst = Math.max(worst, b.bottom - r.bottom, b.right - r.right);
        if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible') worst = Math.max(worst, e.scrollWidth - e.clientWidth);
      }
      return Math.round(worst);
    });
    if (o > 0) { bad++; console.log(`OVERFLOW ${o}px  ${f.split('/').pop()}`); }
    await page.screenshot({ path: f.replace(/\.html$/, '.png') });
  }
  await browser.close();
  if (bad) process.exitCode = 3;
})();
