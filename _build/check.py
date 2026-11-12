#!/usr/bin/env python3
"""Static checks for adjiebrotots.com. Run from the repository root:

    python3 _build/check.py

Fails (exit 1) on anything that would hurt a reader or a crawler.
"""
import glob
import gzip
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

SITE = 'https://www.adjiebrotots.com'
ADSENSE = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8730116101825381'
PERSON = SITE + '/#person'
MAIN = ['index.html', 'about/index.html', 'id/about/index.html', '404.html']
# Notes drawn from data-note attributes: never part of the page text.
NOTES = ['not that important', 'as words', 'hope it can help you too']
problems = []


def bad(f, msg):
    problems.append('%s: %s' % (f, msg))


class Text(HTMLParser):
    """Visible text, without scripts, styles or SVG titles."""
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'title', 'svg'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'title', 'svg') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def target(href):
    """The file a site-relative link lands on, or None when it can't exist."""
    path = href.split('#')[0].split('?')[0]
    if not path:
        return 'index.html'
    path = path.lstrip('/')
    if path == '' or path.endswith('/'):
        return path + 'index.html'
    return path


def check_page(f):
    s = open(f, encoding='utf-8').read()
    redirect = 'http-equiv="refresh"' in s
    h1 = len(re.findall(r'<h1[\s>]', s))
    if h1 != 1 and not redirect:
        bad(f, '%d <h1> elements' % h1)
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            data = json.loads(b)
        except ValueError as e:
            bad(f, 'JSON-LD does not parse: %s' % e)
            continue
        ids = re.findall(r'"@id":\s*"([^"]*#person)"', b)
        for i in set(ids):
            if i != PERSON:
                bad(f, 'person @id %s is not %s' % (i, PERSON))
    # AdSense: never on a screen without content of its own (the homepage is a signpost to
    # about, blog and tools; 404 is an error page), and a page that loads it links to the
    # privacy policy that says so.
    ads = ADSENSE in s
    if ads and f in ('index.html', '404.html'):
        bad(f, 'loads AdSense on a page without content of its own')
    if ads and 'rel="privacy-policy"' not in s:
        bad(f, 'loads AdSense but has no privacy policy link')
    if not redirect and f != '404.html':
        if not re.search(r'<link rel="canonical" href="https://www\.adjiebrotots\.com/', s):
            bad(f, 'no absolute canonical')
        m = re.search(r'<meta name="description" content="([^"]*)"', s)
        if not m and '404' not in f:
            bad(f, 'no meta description')
        elif m and not 50 <= len(html.unescape(m.group(1))) <= 170:
            bad(f, 'meta description is %d characters' % len(m.group(1)))
    # No external scripts, styles or images: every byte a page paints is ours. The one
    # exception is the AdSense loader, async so it never holds up the first paint.
    for tag, attr in (('script', 'src'), ('link', 'href'), ('img', 'src'), ('iframe', 'src')):
        for m in re.finditer(r'<%s\b[^>]*\b%s="(https?://[^"]+)"' % (tag, attr), s):
            whole = m.group(0)
            if tag == 'script' and m.group(1).startswith(ADSENSE) and ' async ' in whole:
                continue
            if tag == 'link' and not re.search(r'rel="(stylesheet|preload|modulepreload)"', whole):
                continue
            bad(f, 'external %s: %s' % (tag, m.group(1)))
    for m in re.finditer(r'<img\b[^>]*>', s):
        tagtxt = m.group(0)
        if 'alt=' not in tagtxt:
            bad(f, 'img without alt: %s' % tagtxt[:80])
        if not ('width=' in tagtxt and 'height=' in tagtxt):
            bad(f, 'img without width/height: %s' % tagtxt[:80])
    for m in re.finditer(r'\bhref="(/[^"]*)"', s):
        t = target(m.group(1))
        if t and not os.path.exists(t):
            bad(f, 'broken link %s' % m.group(1))
    for m in re.finditer(r'\b(?:src|srcset)="([^"]+)"', s):
        for part in m.group(1).split(','):
            u = part.strip().split(' ')[0]
            if u.startswith('/') and not os.path.exists(u.lstrip('/')):
                bad(f, 'missing file %s' % u)
    if f in MAIN:
        p = Text()
        p.feed(s)
        text = ' '.join(p.out)
        if '—' in text:
            bad(f, 'em-dash in page text')
        for n in NOTES:
            if n in text:
                bad(f, 'hover note "%s" leaked into the page text' % n)
    return s


def style_of(s):
    return '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', s, re.S))


def check_design(f, s):
    """The design system (DESIGN.md): pages build on the shared tokens instead of drifting from them."""
    css = style_of(s)
    own = re.sub(r'/\* @sync (\w+) \*/.*?/\* @end \1 \*/', '', css, flags=re.S)
    # Hard offset shadows come from the --pop scale, so every sticker lifts the same way in both themes.
    for m in re.finditer(r'box-shadow:[^;}]*?\b\d+px \d+px 0 (?:var\(--line\)|#[0-9A-Fa-f]{3,8})', own):
        bad(f, 'hand-written offset shadow, use var(--pop-N): %s' % m.group(0))
    # A token defined in core.css is never redefined by a page, or the three sites drift apart again.
    core = set(re.findall(r'(--[\w-]+)\s*:', ''.join(re.findall(r'/\* @sync core \*/.*?/\* @end core \*/', css, re.S))))
    for m in re.finditer(r':root[^{]*\{([^}]*)\}', own):
        for name in re.findall(r'(--[\w-]+)\s*:', m.group(1)):
            if name in core:
                bad(f, 'page redefines the shared token %s (change it in _build/core.css)' % name)
    # Night is written twice (the reader's pick, and the system setting when there is no script): keep the two the same.
    norm = lambda t: ' '.join(t.split())
    pick = dict((norm(k), norm(v)) for k, v in re.findall(r':root\[data-theme="dark"\]([^{]*)\{([^}]*)\}', own))
    system = dict((norm(k), norm(v)) for k, v in re.findall(r':root:not\(\[data-theme="light"\]\)([^{]*)\{([^}]*)\}', own))
    for sel in sorted(set(pick) | set(system)):
        if pick.get(sel) != system.get(sel):
            bad(f, 'night rule ":root%s" differs between data-theme and prefers-color-scheme' % (' ' + sel if sel else ''))
    # Every var() names a token that exists (a typo paints nothing, silently).
    defined = set(re.findall(r'(--[\w-]+)\s*:', s)) | set(re.findall(r"setProperty\(\s*'(--[\w-]+)'", s))
    for name in sorted(set(re.findall(r'var\((--[\w-]+)\)', s))):
        if name not in defined:
            bad(f, 'var(%s) is used but never defined' % name)


def main():
    pages = list(MAIN)
    sizes = {}
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import core
    problems.extend(core.sync(check=True))
    for f in pages:
        if not os.path.exists(f):
            bad(f, 'missing')
            continue
        s = check_page(f)
        check_design(f, s)
        if f in MAIN[:3]:
            sizes[f] = (len(s.encode()), len(gzip.compress(s.encode(), 9)))
    # Sitemap: every URL is a real page.
    sm = open('sitemap.xml', encoding='utf-8').read()
    for loc in re.findall(r'<loc>([^<]+)</loc>', sm):
        t = target(loc.replace(SITE, ''))
        if not os.path.exists(t):
            bad('sitemap.xml', 'lists %s, which does not exist' % loc)
    for f, (raw, gz) in sizes.items():
        print('%-20s %6.1f kB, %5.1f kB gzipped' % (f, raw / 1024, gz / 1024))
        if gz > 60 * 1024:
            bad(f, 'over the 60 kB gzipped budget')
    fonts = sum(os.path.getsize(p) for p in glob.glob('assets/fonts/*.woff2'))
    print('%-20s %6.1f kB' % ('fonts', fonts / 1024))
    if problems:
        print('\n'.join(problems))
        print('%d problem(s)' % len(problems))
        sys.exit(1)
    print('all checks passed (%d pages)' % len(pages))


if __name__ == '__main__':
    main()
