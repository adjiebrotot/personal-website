#!/usr/bin/env python3
"""Writes sitemap.xml: the pages of www, then every archived Blogger post.

    python3 _build/sitemap.py      # from the repository root

Bump a page's date in PAGES when its content changes.
"""
SITE = 'https://www.adjiebrotots.com'
PAGES = [
    ('/', '2026-10-20', '1.0'),
    ('/about/', '2026-10-20', '0.9'),
    ('/archive/', '2026-10-20', '0.4'),
]

rows = ['<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, mod, pri in PAGES:
    rows.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (SITE, path, mod, pri))
with open('_build/archive-urls.txt', encoding='utf-8') as f:
    for line in f:
        path, mod = line.split('\t')[:2]
        rows.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>0.3</priority></url>' % (SITE, path, mod))
rows.append('</urlset>')
with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('sitemap.xml: %d urls' % (len(rows) - 3))
