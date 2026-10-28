# adjiebrotots.com

Static personal site at www.adjiebrotots.com, published by GitHub Pages. Sister sites:
`../tool` (tool.adjiebrotots.com, design tokens in its `dark.css` / `light.css`) and `../blog`
(blog.adjiebrotots.com). See `README.md` for the files.

## Published URLs are permanent

- `/` and `/about/` are linked from the tool site, the blog and elsewhere. Never rename either;
  a new page gets its own path and a line in `_build/sitemap.py`.
- The old Blogger blog that used to live on this domain is retired on purpose. Don't bring its
  posts back.

## One identity across www, tool and blog

The Person node `https://www.adjiebrotots.com/#person` is the same `@id` in the tool's and the
blog's JSON-LD. Change the facts in it on all three sites at once (and in `llms.txt` and the
about page's text), or not at all.

## Keep it fast

- Each page inlines its own CSS, SVG and JS. No frameworks, no external scripts or fonts. The
  one exception is the async AdSense loader in each `<head>`, the same tag the tool site and the
  blog use; ad placement is set in AdSense (Auto ads), not in the pages.
- Animate only `transform` and `opacity`; honour `prefers-reduced-motion`; pause the skyline
  when it's off screen.
- Images are WebP with `width`/`height`, `loading="lazy"` below the fold.

## Page text

- No em-dashes in page text. No years or dates in the about story.
- The homepage notes on the About / Blog / Tools buttons live in `data-note` attributes drawn by
  CSS (`aria-hidden`, `data-nosnippet`), so jokes never become facts in search results. Keep
  them out of the page text.
- Both themes (day and night) must work; check at 390px wide that nothing scrolls sideways.
