#!/usr/bin/env python3
"""Copies the shared design system from _build/core.css into every page.

    python3 _build/core.py            # rewrite the synced blocks in each page
    python3 _build/core.py --check    # exit 1 if a page has drifted (check.py runs this too)

A page opts into a block by carrying its markers inside its <style>:

    /* @sync core */ ... /* @end core */

Everything between them is replaced, so never edit there: edit core.css.
"""
import re
import sys

SOURCE = '_build/core.css'
# Which blocks each page carries. The 404 has no top bar, so no chrome.
PAGES = {
    'index.html': ['core', 'chrome'],
    'about/index.html': ['core', 'chrome'],
    'id/about/index.html': ['core', 'chrome'],
    '404.html': ['core'],
}
INDENT = '    '
BLOCK = r'/\* @sync %s \*/\n(.*?)/\* @end %s \*/'


def expand_dark(css):
    """One @dark { } becomes the system-setting rule and the reader's-pick rule."""
    def both(m):
        body = m.group(1).rstrip()
        inner = '\n'.join('  ' + l if l.strip() else l for l in body.split('\n'))
        return ('@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {%s\n  }\n}\n'
                ':root[data-theme="dark"] {%s\n}' % (inner, body))
    return re.sub(r'@dark \{(.*?)\n\}', both, css, flags=re.S)


def blocks():
    src = open(SOURCE, encoding='utf-8').read()
    out = {}
    for name in sorted(set(n for names in PAGES.values() for n in names)):
        m = re.search(BLOCK % (name, name), src, re.S)
        if not m:
            sys.exit('%s: no "@sync %s" block' % (SOURCE, name))
        body = expand_dark(m.group(1)).rstrip('\n')
        out[name] = '\n'.join(INDENT + l if l.strip() else '' for l in body.split('\n'))
    return out


def render(name, body):
    return ('/* @sync %s */ /* from _build/core.css: edit it there, then run _build/core.py */\n%s\n%s/* @end %s */'
            % (name, body, INDENT, name))


def sync(check=False):
    """Returns the list of problems; writes the pages unless check is set."""
    src = blocks()
    problems = []
    page_re = r'/\* @sync %s \*/.*?/\* @end %s \*/'
    for page, names in PAGES.items():
        s = open(page, encoding='utf-8').read()
        new = s
        for name in names:
            pat = page_re % (name, name)
            if not re.search(pat, new, re.S):
                problems.append('%s: no "@sync %s" block' % (page, name))
                continue
            new = re.sub(pat, lambda m, n=name: render(n, src[n]), new, count=1, flags=re.S)
        if new != s:
            if check:
                problems.append('%s: differs from _build/core.css (run python3 _build/core.py)' % page)
            else:
                open(page, 'w', encoding='utf-8').write(new)
                print('updated', page)
    return problems


if __name__ == '__main__':
    found = sync(check='--check' in sys.argv)
    for p in found:
        print(p)
    sys.exit(1 if found else 0)
