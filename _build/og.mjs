// Renders the social preview images from the live pages (Playwright).
//   python3 -m http.server 8411 &      # from the repository root
//   node _build/og.mjs                 # writes assets/img/og.png and og-about.png
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = createRequire('/opt/node22/lib/node_modules/')('playwright'); }
const base = process.env.BASE || 'http://localhost:8411';
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: 'light', reducedMotion: 'reduce' });

await page.goto(base + '/', { waitUntil: 'load' });
await page.addStyleTag({ content: `
  .top, .lede, .hub, .socials, .formal, .ground, .sky .cloud { display: none !important; }
  .stage { min-height: 630px !important; height: 630px; }
  .hello { padding-top: 34px !important; }
  .title { font-size: 92px !important; }
  .roles { font-size: 25px !important; margin-top: 14px !important; white-space: nowrap; }
  .roles li { position: static !important; display: inline !important; }
  .roles li + li::before { content: '·'; padding: 0 .35em; color: var(--muted); }
  .roles ul { display: block !important; }
  .wave { font-size: 28px !important; }
  .scene-wrap { --h: 340px !important; }
  .sun { top: 60px !important; left: 80px !important; width: 70px !important; }
  .plane { transform: translate(700px, -14px) !important; }
  .train { transform: translateX(760px) !important; }
  .bus { transform: translateX(1480px) !important; }
  .roo { transform: translateX(1010px) !important; }
`});
await page.waitForTimeout(500);
await page.screenshot({ path: 'assets/img/og.png' });

await page.goto(base + '/about/', { waitUntil: 'load' });
await page.evaluate(() => {
  const map = document.createElement('div');
  map.className = 'map-card';
  map.appendChild(document.getElementById('map').cloneNode(true));
  document.body.innerHTML = '';
  const wrap = document.createElement('div');
  wrap.className = 'og';
  wrap.innerHTML = '<div class="og-text"><p class="hand og-eyebrow">about me</p><h1>From Bandung<br>to <span>Perth</span>.</h1><p class="og-name">Adjie Brotosukmono</p><p class="og-sub">Energy economics consultant and power system engineer</p></div>';
  wrap.appendChild(map);
  document.body.appendChild(wrap);
  map.querySelector('svg').classList.add('go');
});
await page.addStyleTag({ content: `
  html, body { margin: 0; height: 630px; overflow: hidden; background: linear-gradient(135deg, #D6E6FF, #F3F7FF); }
  .og { display: grid; grid-template-columns: 1fr 560px; gap: 48px; align-items: center; height: 630px; padding: 0 64px; }
  .og h1 { font-size: 84px; line-height: .98; letter-spacing: -.045em; margin: 0 0 22px; }
  .og h1 span { color: #0052CC; }
  .og-eyebrow { font-size: 40px; color: #B45309; margin: 0 0 6px; transform: rotate(-3deg); display: inline-block; }
  .og-name { font-size: 34px; font-weight: 800; margin: 0; }
  .og-sub { font-size: 24px; color: #4C5B76; margin: 4px 0 0; }
  .map-card { width: 560px; } .map-card svg { width: 100%; height: auto; display: block; -webkit-mask-image: radial-gradient(closest-side, #000 76%, transparent); mask-image: radial-gradient(closest-side, #000 76%, transparent); }
`});
await page.waitForTimeout(400);
await page.screenshot({ path: 'assets/img/og-about.png' });
await browser.close();
console.log('wrote assets/img/og.png and assets/img/og-about.png');
