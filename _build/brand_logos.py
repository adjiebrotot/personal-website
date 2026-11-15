"""Draws the Tot Academy and Anthem Madness logos into logos/.

    pip install fonttools brotli
    python3 _build/brand_logos.py

Colours come from _build/core.css (day theme). Words are set in the site's DM Sans and turned
into outlines, so the SVGs look the same on machines without the font.
"""
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "logos"

# Tokens from _build/core.css
INK = "#14203A"
BRAND = "#0052CC"
ROSE = "#E66A6A"
GOLD_SOFT = "#FFD28C"
PAPER = "#FFFFFF"

_font = TTFont(ROOT / "assets/fonts/dm-sans.woff2")
DM = instantiateVariableFont(_font, {"wght": 800, "opsz": 40})
GS = DM.getGlyphSet()
CMAP = DM.getBestCmap()
UPM = DM["head"].unitsPerEm
HMTX = DM["hmtx"]


def word(text, x, y, size, fill, tracking=0.0):
    """One line of DM Sans 800 as a path; (x, y) is the left end of the baseline.
    Returns (svg, width)."""
    s = size / UPM
    pen = SVGPathPen(GS, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cx = 0.0
    for ch in text:
        g = CMAP[ord(ch)]
        GS[g].draw(TransformPen(pen, (s, 0, 0, -s, x + cx, y)))
        cx += HMTX[g][0] * s + tracking * size
    width = cx - tracking * size
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>', width


def width_of(text, size, tracking=0.0):
    return word(text, 0, 0, size, "#000", tracking)[1]


def x_height(size):
    bp = BoundsPen(GS)
    GS[CMAP[ord("x")]].draw(bp)
    return bp.bounds[3] * size / UPM


def svg(w, h, title, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" '
            f'width="{w:g}" height="{h:g}" role="img"><title>{title}</title>{rect}{body}</svg>\n')


# ---------------------------------------------------------------- Tot Academy
def tot_mark():
    """The tot wordmark with the mortarboard and the owl eyes, in a 0 0 400 230 box."""
    t = (f'<path d="M0 0V112Q0 146 38 146" fill="none" stroke="{BRAND}" stroke-width="50" stroke-linecap="round"/>'
         f'<path d="M-30 28H40" fill="none" stroke="{BRAND}" stroke-width="32" stroke-linecap="round"/>')
    left = f'<g transform="translate(70 72)">{t}</g>'
    right = f'<g transform="translate(320 72)">{t}</g>'
    ring = f'<circle cx="200" cy="160" r="49" fill="none" stroke="{BRAND}" stroke-width="44"/>'
    # Cap: the skull first, the board on top, then the cord and tassel hanging off the left.
    cap = (f'<path d="M146 88V118Q200 140 254 118V88Z" fill="{INK}"/>'
           f'<path d="M200 44L294 76L200 106L106 76Z" fill="{INK}"/>'
           f'<path d="M200 76L130 86V114" fill="none" stroke="{GOLD_SOFT}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<rect x="122" y="108" width="16" height="26" rx="7" fill="{GOLD_SOFT}" stroke="{INK}" stroke-width="3"/>'
           f'<circle cx="200" cy="76" r="6" fill="{GOLD_SOFT}"/>')
    eyes = ""
    for ex in (166, 234):
        eyes += (f'<circle cx="{ex}" cy="128" r="20" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>'
                 f'<circle cx="{ex + 5}" cy="124" r="7.5" fill="{INK}"/>')
    return left + ring + right + cap + eyes


def tot_academy():
    size = 62
    tracking = 0.06
    w = width_of("academy", size, tracking)
    # Wide: the mark with "academy" centred under it.
    mark_w, mark_h = 400, 230
    W, H = 440, 330
    mx = (W - mark_w) / 2
    acad, aw = word("academy", (W - w) / 2, 300, size, INK, tracking)
    wide = svg(W, H, "Tot Academy", f'<g transform="translate({mx} 4)">{tot_mark()}</g>{acad}')
    (OUT / "tot-academy.svg").write_text(wide)

    # Square: the same lockup centred on paper, kept inside the circle a profile picture crops to.
    S = 512
    scale = 1.0
    gx = (S - W * scale) / 2
    gy = (S - H * scale) / 2
    sq = svg(S, S, "Tot Academy",
             f'<g transform="translate({gx:.1f} {gy:.1f}) scale({scale})">'
             f'<g transform="translate({mx} 4)">{tot_mark()}</g>{acad}</g>', bg=PAPER)
    (OUT / "tot-academy-square.svg").write_text(sq)


# -------------------------------------------------------------- Anthem Madness
def circled_a(fill):
    """logos/logo.svg drawn in a 680 box, with the circle in another colour."""
    return (f'<circle cx="340" cy="340" r="300" fill="{fill}"/>'
            '<path d="M242 570A250 250 0 0 1 234 113A250 250 0 0 1 446 113A250 250 0 0 1 438 570" '
            f'fill="none" stroke="{PAPER}" stroke-width="46"/>'
            f'<path d="M113 354H567" stroke="{PAPER}" stroke-width="42" stroke-linecap="round"/>')


def anthem_madness():
    # Wide: like the site's .brand, the mark then the two words on one line.
    size = 96
    H = 160
    mark = 136  # the circle's diameter
    k = mark / 600
    mark_svg = f'<g transform="translate({12 - 40 * k:.2f} {12 - 40 * k:.2f}) scale({k:.4f})">{circled_a(ROSE)}</g>'
    gap = 30
    x0 = 12 + mark + gap
    base = H / 2 + x_height(size) / 2 + 2
    a, aw = word("Anthem", x0, base, size, INK, -0.01)
    sp = width_of(" ", size) * 0.9
    m, mw = word("Madness", x0 + aw + sp, base, size, ROSE, -0.01)
    W = round(x0 + aw + sp + mw + 14)
    (OUT / "anthem-madness.svg").write_text(svg(W, H, "Anthem Madness", mark_svg + a + m))

    # Square: the red circled A filling the frame, so a round profile crop keeps all of it.
    k = 512 / 600
    (OUT / "anthem-madness-square.svg").write_text(
        svg(512, 512, "Anthem Madness",
            f'<g transform="translate({-40 * k:.2f} {-40 * k:.2f}) scale({k:.5f})">{circled_a(ROSE)}</g>'))


if __name__ == "__main__":
    tot_academy()
    anthem_madness()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.svg") if p.name != "logo.svg")))
