#!/usr/bin/env python3
"""Short links: www.adjiebrotots.com/<slug> sends the reader on to a longer URL.

Add a line to LINKS, then run from the repository root:

    python3 _build/links.py

Each slug becomes a tiny static page, <slug>/index.html, that redirects at once (meta
refresh plus one line of JS, with a plain link as the fallback). GitHub Pages can't send a
real 301 from a static site, but search engines treat an instant meta refresh as a
permanent redirect, and the canonical points at the target. adjiebrotots.com/<slug> works
too: GitHub Pages sends the bare domain on to www with the path kept.

A short link is a published URL like any other: once it is shared, never reuse its slug for
something else. Removing a line here deletes its page on the next run.
"""
import html
import os
import re
import shutil
import sys

LINKS = {
    'pns': 'https://blog.adjiebrotots.com/id/pensiun-tanpa-jadi-pns/',
}

# Paths the site already uses (or may): a short link can never take one of them.
RESERVED = {'about', 'id', 'en', 'assets', 'logos', 'blog', 'tool', 'tools', 'privacy',
            '404', 'index', 'sitemap', 'robots', 'llms', 'ads'}
MARK = '<!-- short link: made by _build/links.py -->'

PAGE = '''<!DOCTYPE html>
%(mark)s
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Redirecting</title>
  <meta name="robots" content="noindex, follow">
  <meta http-equiv="refresh" content="0; url=%(url)s">
  <script>location.replace(%(js)s + location.hash);</script>
  <style>body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 16px; font: 1.05rem system-ui, sans-serif; color: #14203A; background: #F3F7FF; } a { color: #0052CC; overflow-wrap: anywhere; } @media (prefers-color-scheme: dark) { body { color: #EAF1FF; background: #0F1728; } a { color: #8DBBFF; } }</style>
</head>
<body>
  <p>Taking you to <a href="%(url)s">%(url)s</a></p>
</body>
</html>
'''


def main():
    problems = []
    for slug, url in LINKS.items():
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
            problems.append('%s: use lowercase letters, digits and hyphens' % slug)
        if slug in RESERVED or slug.startswith(('_', '.')):
            problems.append('%s: reserved path' % slug)
        if not url.startswith('https://'):
            problems.append('%s: target must be https://' % slug)
        page = os.path.join(slug, 'index.html')
        if os.path.exists(page) and MARK not in open(page, encoding='utf-8').read():
            problems.append('%s: %s is a real page, not a short link' % (slug, page))
    if problems:
        print('\n'.join(problems))
        sys.exit(1)

    for slug, url in sorted(LINKS.items()):
        os.makedirs(slug, exist_ok=True)
        with open(os.path.join(slug, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(PAGE % {'mark': MARK, 'url': html.escape(url), 'js': repr(url).replace('<', '\\x3c')})
        print('/%s/ -> %s' % (slug, url))

    # Pages of links that were taken out of LINKS.
    for d in sorted(os.listdir('.')):
        page = os.path.join(d, 'index.html')
        if d not in LINKS and os.path.isfile(page) and MARK in open(page, encoding='utf-8').read():
            shutil.rmtree(d)
            print('removed /%s/' % d)


if __name__ == '__main__':
    main()
