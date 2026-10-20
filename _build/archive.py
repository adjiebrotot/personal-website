#!/usr/bin/env python3
"""Keeps every post of the old Blogger blog alive at its old address.

www.adjiebrotots.com used to be a Blogger blog, so search engines and other
sites still link to addresses like /2017/08/catatan-seorang-mentor.html.
This writes each post as a static page at exactly that path, plus the
/archive/ index and a redirect for the old /p/siapa-adjie.html page.

    python3 _build/archive.py                  # fetch the feed from Blogger
    python3 _build/archive.py posts.json       # or use a saved copy of it

Run it from the repository root. It only ever adds or rewrites the archive
files, so re-running it is safe.
"""
import html
import json
import os
import re
import sys
import urllib.request

SITE = 'https://www.adjiebrotots.com'
FEED = SITE + '/feeds/posts/default?alt=json&max-results=500'
MONTHS = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
          'Agustus', 'September', 'Oktober', 'November', 'Desember']
# Inline styles from the Blogger editor that fight the page's own type and
# colours (and break dark mode). Layout ones such as text-align stay.
DROP_STYLE = re.compile(r'^(font|color|background|line-height|mso-|z-index|position|clip|cursor|white-space|overflow|tab-stops)', re.I)

THEME_INIT = ("<script>(function(){var t=null;try{t=localStorage.getItem('www-theme')}catch(e){}"
              "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)})();</script>")


def load(argv):
    if len(argv) > 1:
        with open(argv[1], encoding='utf-8') as f:
            return json.load(f)
    req = urllib.request.Request(FEED, headers={'User-Agent': 'adjiebrotots-archive/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def clean_style(m):
    keep = []
    for decl in m.group(1).split(';'):
        if ':' not in decl:
            continue
        prop = decl.split(':', 1)[0].strip()
        if prop and not DROP_STYLE.match(prop):
            keep.append(decl.strip())
    return ' style="%s"' % '; '.join(keep) if keep else ''


def clean_body(body):
    body = re.sub(r'\sstyle="([^"]*)"', clean_style, body)
    # One <h1> per page: the post title. Headings inside the post step down one.
    body = re.sub(r'<(/?)h1(\b[^>]*)>', r'<\1h2\2>', body, flags=re.I)
    body = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy" decoding="async"', body, flags=re.I)
    body = re.sub(r'<iframe\b(?![^>]*\bloading=)', '<iframe loading="lazy"', body, flags=re.I)
    body = re.sub(r'\s(imageanchor|border)="[^"]*"', '', body)
    # Old posts link to themselves through http:// and the blogspot host.
    body = body.replace('http://www.adjiebrotots.com/', '/').replace('https://www.adjiebrotots.com/', '/')
    return body


def plain(text, n=158):
    t = re.sub(r'<[^>]+>', ' ', text)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(' ', 1)[0]
    return cut.rstrip(',.;:') + '…'


def tanggal(iso):
    y, m, d = iso[:4], int(iso[5:7]), int(iso[8:10])
    return '%d %s %s' % (d, MONTHS[m - 1], y)


def first_image(body):
    m = re.search(r'<img[^>]+src="(https://blogger\.googleusercontent\.com/[^"]+)"', body)
    if not m:
        return SITE + '/assets/img/og.png'
    return re.sub(r'/(s\d+|w\d+-h\d+)(-[a-z])?/', '/w1200/', m.group(1))


def slug(label):
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')


HEAD = '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Arsip Blog Adjie Brotot</title>
  <meta name="description" content="{desc}">
  <meta name="author" content="Adjie Brotosukmono">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/svg+xml" href="/assets/img/logo.svg">
  <meta property="og:type" content="{ogtype}">
  <meta property="og:site_name" content="Adjie Brotosukmono">
  <meta property="og:locale" content="id_ID">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta name="twitter:card" content="summary_large_image">
  {theme}
  <link rel="stylesheet" href="/assets/css/archive.css">
  <script type="application/ld+json">{jsonld}</script>
</head>
<body>
  <header class="bar">
    <a class="brand" href="/" aria-label="Adjie Brotosukmono, beranda"><img src="/assets/img/logo.svg" alt="" width="28" height="28"><span>Adjie <b>Brotot</b></span></a>
    <nav aria-label="Utama"><a href="/archive/">Arsip</a><a href="https://blog.adjiebrotots.com/id/">Blog baru</a><a href="/about/">Tentang saya</a></nav>
  </header>
'''

FOOT = '''  <footer>
    <nav aria-label="Lainnya"><a href="/">Beranda</a><a href="/about/">Tentang saya</a><a href="https://blog.adjiebrotots.com/">Blog</a><a href="https://tool.adjiebrotots.com/">Tools</a></nav>
    <p>© Adjie Brotosukmono</p>
  </footer>
</body>
</html>
'''


def person_ref():
    return {'@id': SITE + '/#person'}


def write(path, text):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main(argv):
    feed = load(argv)['feed']
    posts = []
    for e in feed['entry']:
        link = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0]
        path = link.split('adjiebrotots.com', 1)[1]
        posts.append({
            'path': path,
            'title': html.unescape(e['title']['$t']),
            'published': e['published']['$t'],
            'updated': e['updated']['$t'],
            'labels': [c['term'] for c in e.get('category', [])],
            'body': clean_body(e['content']['$t']),
        })
    posts.sort(key=lambda p: p['published'], reverse=True)

    for i, p in enumerate(posts):
        url = SITE + p['path']
        desc = plain(p['body'])
        label = p['labels'][0] if p['labels'] else 'Arsip'
        jsonld = {
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            '@id': url + '#article',
            'mainEntityOfPage': url,
            'url': url,
            'headline': p['title'],
            'description': desc,
            'inLanguage': 'id',
            'datePublished': p['published'],
            'dateModified': p['updated'],
            'author': person_ref(),
            'publisher': person_ref(),
            'image': first_image(p['body']),
            'articleSection': label,
            'keywords': p['labels'],
            'isPartOf': {'@type': 'CollectionPage', '@id': SITE + '/archive/', 'name': 'Arsip Blog Adjie Brotot'},
        }
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        pager = []
        if newer:
            pager.append('<a rel="prev" href="%s"><small>Lebih baru</small>%s</a>' % (newer['path'], html.escape(newer['title'])))
        if older:
            pager.append('<a rel="next" class="older" href="%s"><small>Lebih lama</small>%s</a>' % (older['path'], html.escape(older['title'])))
        page = HEAD.format(
            title=html.escape(p['title']), desc=html.escape(desc), url=url, ogtype='article',
            image=html.escape(first_image(p['body'])), theme=THEME_INIT,
            jsonld=json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'))
        page += '''  <main class="post">
    <p class="note">Ini tulisan arsip dari blog lama saya, saya simpan apa adanya supaya tautannya tetap hidup. Tulisan baru ada di <a href="https://blog.adjiebrotots.com/id/">blog.adjiebrotots.com</a>.</p>
    <article>
      <p class="meta"><a href="/archive/#%s">%s</a> · <time datetime="%s">%s</time></p>
      <h1>%s</h1>
      <div class="body">
%s
      </div>
    </article>
    <nav class="pager" aria-label="Tulisan lain">%s</nav>
  </main>
''' % (slug(label), html.escape(label), p['published'][:10], tanggal(p['published']),
           html.escape(p['title']), p['body'], ''.join(pager))
        page += FOOT
        write(p['path'].lstrip('/'), page)

    # The archive index, grouped by year.
    years = {}
    for p in posts:
        years.setdefault(p['published'][:4], []).append(p)
    labels = sorted({l for p in posts for l in p['labels']})
    items = []
    for y in sorted(years, reverse=True):
        rows = ''.join('<li><a href="%s">%s</a> <span>%s · %s</span></li>' % (
            p['path'], html.escape(p['title']), html.escape(', '.join(p['labels']) or 'Arsip'), tanggal(p['published']))
            for p in years[y])
        items.append('<section id="y%s"><h2>%s</h2><ul>%s</ul></section>' % (y, y, rows))
    index_ld = {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        '@id': SITE + '/archive/',
        'url': SITE + '/archive/',
        'name': 'Arsip Blog Adjie Brotot',
        'description': 'Tulisan lama Adjie Brotosukmono dari tahun %s sampai %s, tentang sains, rekayasa, pengetahuan umum dan catatan kehidupan.' % (min(years), max(years)),
        'inLanguage': 'id',
        'author': person_ref(),
        'isPartOf': {'@id': SITE + '/#website'},
        'hasPart': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': SITE + p['path'], 'datePublished': p['published']} for p in posts],
    }
    page = HEAD.format(
        title='Semua tulisan lama', desc=html.escape(index_ld['description']), url=SITE + '/archive/', ogtype='website',
        image=SITE + '/assets/img/og.png', theme=THEME_INIT,
        jsonld=json.dumps(index_ld, ensure_ascii=False).replace('</', '<\\/'))
    page += '''  <main class="post archive">
    <h1>Arsip blog lama</h1>
    <p class="lede">%d tulisan dari blog lama saya, %s sampai %s: catatan sains dan rekayasa, pengetahuan umum, dan cerita kehidupan. Semuanya dalam Bahasa Indonesia, saya biarkan seperti aslinya. Tulisan baru ada di <a href="https://blog.adjiebrotots.com/id/">blog.adjiebrotots.com</a>.</p>
    <p class="labels">%s</p>
    %s
  </main>
''' % (len(posts), min(years), max(years),
       ' '.join('<span id="%s">%s</span>' % (slug(l), html.escape(l)) for l in labels), ''.join(items))
    page += FOOT
    write('archive/index.html', page)

    # The old "Siapa Adjie?" page now lives at /about/.
    write('p/siapa-adjie.html', '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <title>Siapa Adjie? Sekarang di /about/</title>
  <link rel="canonical" href="%s/about/">
  <meta name="robots" content="noindex, follow">
  <meta http-equiv="refresh" content="0; url=/about/">
  <script>location.replace('/about/' + location.hash);</script>
</head>
<body>
  <p>Halaman ini pindah ke <a href="/about/">adjiebrotots.com/about</a>.</p>
</body>
</html>
''' % SITE)

    with open('_build/archive-urls.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join('%s\t%s\t%s' % (p['path'], p['updated'][:10], p['title']) for p in posts) + '\n')
    print('wrote %d posts, /archive/ and /p/siapa-adjie.html' % len(posts))


if __name__ == '__main__':
    main(sys.argv)
