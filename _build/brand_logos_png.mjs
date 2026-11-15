// Renders PNG copies of the brand logos drawn by brand_logos.py (Playwright).
//   node _build/brand_logos_png.mjs
// Squares come out at 1024 x 1024; wide logos at 4x their SVG size. Transparent where the SVG is.
import { createRequire } from 'module';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = createRequire('/opt/node22/lib/node_modules/')('playwright'); }
const dir = fileURLToPath(new URL('../logos/', import.meta.url));
const names = ['tot-academy', 'tot-academy-stacked', 'tot-academy-square', 'anthem-madness', 'anthem-madness-square'];
const browser = await pw.chromium.launch();
for (const name of names) {
  const svg = readFileSync(dir + name + '.svg', 'utf8');
  const [, w, h] = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/).map(Number);
  const scale = name.endsWith('-square') ? 1024 / w : 4;
  const page = await browser.newPage({ viewport: { width: Math.round(w), height: Math.round(h) }, deviceScaleFactor: scale });
  await page.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block}</style>${svg}`);
  writeFileSync(dir + name + '.png', await page.screenshot({ omitBackground: true }));
  await page.close();
  console.log(name + '.png', Math.round(w * scale) + 'x' + Math.round(h * scale));
}
await browser.close();
