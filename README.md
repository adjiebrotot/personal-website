# adjiebrotots.com

The personal site of Adjie Brotosukmono at **https://www.adjiebrotots.com**: a homepage, the
story at `/about/` and the projects at `/projects/`. Static files only, published by GitHub Pages. Sister sites:
[Adjie Brotools](https://tool.adjiebrotots.com/) and the
[Adjie Brotot Blog](https://blog.adjiebrotots.com/).

## Files

| Path | What it is |
| --- | --- |
| `index.html` | Homepage: the Jakarta, energy and Perth skyline, links to about, blog and tools |
| `about/index.html` | The story so far, as a five-stop trail with the projects at each stop |
| `projects/index.html` | The power system and economics projects in detail, by role |
| `404.html` | Not found |
| `llms.txt` | Who Adjie is, written for answer engines |
| `robots.txt`, `sitemap.xml`, `site.webmanifest`, `CNAME` | Crawling, install and domain |
| `assets/` | Fonts (DM Sans, Caveat, subset) and images |
| `logos/` | The favicon (`logo.svg`), the app icons and the Apple touch icon, wired the way the tool site does it |
| `_build/` | Checks, the sitemap and the social images (never published) |

Everything a page needs to paint is inline in it (CSS, SVG, a few lines of JS), so each page
is one request plus two small font files.

## Check and regenerate

```sh
python3 _build/check.py        # one h1 per page, JSON-LD, links, images, page weight
python3 _build/sitemap.py      # after adding a page or changing one (bump its date in PAGES)
python3 -m http.server 8411 &  # then
node _build/og.mjs             # social preview images, after the homepage or map changes
```

## Going live (one time)

The domain still points at the old Blogger blog, which is retired.

1. Merge into `main`. In GitHub, **Settings → Pages**: Source **Deploy from a branch**, branch
   `main`, folder `/ (root)`. Custom domain `www.adjiebrotots.com` (the `CNAME` file says so).
2. In Blogger, **Settings → Publishing → Custom domain**: remove `www.adjiebrotots.com` (or
   delete the blog).
3. At the DNS provider (Cloudflare): `CNAME www → adjiebrotot.github.io`, and for the bare
   domain the four GitHub Pages `A` records (185.199.108.153, .109.153, .110.153, .111.153), so
   `adjiebrotots.com` redirects to `www`. Turn on **Enforce HTTPS** in GitHub once the
   certificate is issued.
4. In Google Search Console (Domain property for `adjiebrotots.com`) and Bing Webmaster Tools,
   submit `https://www.adjiebrotots.com/sitemap.xml`. Old Blogger addresses will drop out of
   the index on their own once they return 404.
