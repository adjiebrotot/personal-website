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
  one exception is the async AdSense loader in the about pages' `<head>`, the same tag the tool
  site and the blog use.
- Animate only `transform` and `opacity`; honour `prefers-reduced-motion`; pause the skyline
  when it's off screen.
- Images are WebP with `width`/`height`, `loading="lazy"` below the fold.

## Ads

- AdSense runs on the about pages only: one hand-placed unit each (Display 5, `1821351030`),
  after the story and before the badges, labelled by CSS. Never on the homepage (a signpost
  to about, blog and tools, which AdSense counts as a screen without content of its own) or
  the 404 (an error page); `_build/check.py` fails if either loads AdSense.
- A page with ads links to the privacy policy (`tool.adjiebrotots.com/privacy/`, which covers
  all three sites) with `rel="privacy-policy"`.
- The slot map for all three sites is in the tool repo, `shared.css`, above `.ad-slot`.

## Page text

- No em-dashes in page text. No years or dates in the about story.
- The homepage notes on the About / Blog / Tools buttons live in `data-note` attributes drawn by
  CSS (`aria-hidden`, `data-nosnippet`), so jokes never become facts in search results. Keep
  them out of the page text.
- Both themes (day and night) must work; check at 390px wide that nothing scrolls sideways.
