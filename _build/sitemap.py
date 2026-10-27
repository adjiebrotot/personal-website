#!/usr/bin/env python3
"""Writes sitemap.xml for www. Run from the repository root:

    python3 _build/sitemap.py

Bump a page's date in PAGES when its content changes.
"""
SITE = 'https://www.adjiebrotots.com'
PAGES = [
    ('/', '2026-10-27', '1.0'),
    ('/about/', '2026-10-27', '0.9'),
    ('/id/about/', '2026-10-27', '0.9'),
]

rows = ['<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, mod, pri in PAGES:
    rows.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (SITE, path, mod, pri))
rows.append('</urlset>')
with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('sitemap.xml: %d urls' % (len(rows) - 3))
