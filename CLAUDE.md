# adjiebrotots.com

Static personal site at www.adjiebrotots.com, published by GitHub Pages. Sister sites:
`../tool` (tool.adjiebrotots.com, design tokens in its `dark.css` / `light.css`) and `../blog`
(blog.adjiebrotots.com). See `README.md` for the files.

## Published URLs are permanent

- `/`, `/about/`, `/archive/` and every archived Blogger post (`/YYYY/MM/slug.html`, listed in
  `_build/archive-urls.txt`) are live and linked from elsewhere. Never delete or rename one.
- `p/siapa-adjie.html` redirects to `/about/`; `404.html` forwards old Blogger label, year and
  feed URLs. Keep both.

## One identity across www, tool and blog

The Person node `https://www.adjiebrotots.com/#person` is the same `@id` in the tool's and the
blog's JSON-LD. Change the facts in it on all three sites at once (and in `llms.txt` and the
about page's text), or not at all.

## Keep it fast

- Each page inlines its own CSS, SVG and JS. No frameworks, no external scripts or fonts.
- Animate only `transform` and `opacity`; honour `prefers-reduced-motion`; pause the skyline
  when it's off screen.
- Images are WebP with `width`/`height`, `loading="lazy"` below the fold.

## Page text

- No em-dashes in page text. No years or dates in the about story.
- The homepage notes on the About / Blog / Tools buttons live in `data-note` attributes drawn by
  CSS (`aria-hidden`, `data-nosnippet`), so jokes never become facts in search results. Keep
  them out of the page text.
- Both themes (day and night) must work; check at 390px wide that nothing scrolls sideways.
