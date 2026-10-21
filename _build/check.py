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
PERSON = SITE + '/#person'
MAIN = ['index.html', 'about/index.html', 'projects/index.html', '404.html']
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
    if not redirect and f != '404.html':
        if not re.search(r'<link rel="canonical" href="https://www\.adjiebrotots\.com/', s):
            bad(f, 'no absolute canonical')
        m = re.search(r'<meta name="description" content="([^"]*)"', s)
        if not m and '404' not in f:
            bad(f, 'no meta description')
        elif m and not 50 <= len(html.unescape(m.group(1))) <= 170:
            bad(f, 'meta description is %d characters' % len(m.group(1)))
    # No external scripts, styles or images: every byte a page paints is ours.
    for tag, attr in (('script', 'src'), ('link', 'href'), ('img', 'src'), ('iframe', 'src')):
        for m in re.finditer(r'<%s\b[^>]*\b%s="(https?://[^"]+)"' % (tag, attr), s):
            whole = m.group(0)
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


def main():
    pages = list(MAIN)
    sizes = {}
    for f in pages:
        if not os.path.exists(f):
            bad(f, 'missing')
            continue
        s = check_page(f)
        if f in MAIN[:2]:
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
