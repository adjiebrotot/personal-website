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
    """The tot wordmark, measured off the original artwork (a 431 x 329 frame; the mark spans
    x 50 to 373, y 62 to 255). One flat silhouette: the eyes are holes, and every part laid over
    another keeps a small gap, as in the original. Letters in brand blue, the cap in ink."""
    eyes = ((171, 154), (247, 153))   # hole radius 21; the o is cut back to 25.5 around them
    # The t is drawn from arcs only: a round top, a crossbar with round ends and small fillets
    # into the stem, and a foot that bends right out of a fillet and turns under in two arcs.
    t = ("M68 115A18.5 18.5 0 0 1 105 115V123A4 4 0 0 0 109 127H117A12 12 0 0 1 117 151H109"
         "A4 4 0 0 0 105 155V215.06A10 10 0 0 0 111.8 224.54A15 15 0 0 1 102.9 253.2"
         "A48 48 0 0 1 68 207V155A4 4 0 0 0 64 151H62"
         "A12 12 0 0 1 62 127H64A4 4 0 0 0 68 123Z")
    letter = f'<path d="{t}"/>'
    ring = ('<path fill-rule="evenodd" d="M142 186a69 69 0 1 0 138 0a69 69 0 1 0-138 0Z'
            'M178 192a33.5 33.5 0 1 0 67 0a33.5 33.5 0 1 0-67 0Z"/>')
    skull = "M162.5 109.6L213.5 125.5L265.5 109.6V149.5H162.5Z"  # flat bottom; the eyes bite its corners
    tassel = ("M143 90H149V113C152 118 158 124 158 134V162H139Q134 162 134 157V134"
              "C134 124 138 118 143 113Z")
    board = "M128 91L213 62L299 90L213.5 118Z"
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="21"/>' for x, y in eyes)
    ring_cut = (f'<path d="{skull}" stroke="#000" stroke-width="15" stroke-linejoin="round"/>'
                f'<path d="{tassel}" stroke="#000" stroke-width="6" stroke-linejoin="round"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="25.5"/>' for x, y in eyes)
                + '<rect x="186" y="150" width="54" height="16"/>')  # between the eyes the o opens into the cap's gap
    return (
        '<defs>'
        f'<mask id="tot-o" maskUnits="userSpaceOnUse" x="0" y="0" width="431" height="329">'
        f'<rect width="431" height="329" fill="#fff"/><g fill="#000">{ring_cut}</g></mask>'
        f'<mask id="tot-cap" maskUnits="userSpaceOnUse" x="0" y="0" width="431" height="329">'
        f'<rect width="431" height="329" fill="#fff"/><g fill="#000">{holes}</g></mask>'
        '</defs>'
        f'<g fill="{BRAND}">{letter}<g transform="translate(243.5 0)">{letter}</g>'
        f'<g mask="url(#tot-o)">{ring}</g></g>'
        f'<g fill="{INK}"><path d="{board}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        f'<g mask="url(#tot-cap)"><path d="{skull}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><path d="{tassel}"/></g>'
        '<circle cx="184" cy="156" r="10.5"/><circle cx="248.5" cy="166" r="10.5"/></g>'
    )


def ink_box(text, size, tracking=0.0):
    """Bounds (x0, y0, x1, y1) of a word set at the origin, y up being negative."""
    s = size / UPM
    bp = BoundsPen(GS)
    cx = 0.0
    for ch in text:
        g = CMAP[ord(ch)]
        GS[g].draw(TransformPen(bp, (s, 0, 0, -s, cx, 0)))
        cx += HMTX[g][0] * s + tracking * size
    return bp.bounds


MARK = (50, 60.5, 373, 255)  # the tot mark's left, top, right, bottom in its own frame


def tot_lockup(pad):
    """The mark with "academy" centred under it. Returns (body, width, height)."""
    size, tracking = 62, 0.06
    x0, y0, x1, y1 = MARK
    mw, mh = x1 - x0, y1 - y0
    ax0, ay0, ax1, ay1 = ink_box("academy", size, tracking)
    aw = ax1 - ax0
    W = max(mw, aw) + 2 * pad
    gap = 22
    base = pad + mh + gap - ay0
    H = base + ay1 + pad
    acad, _ = word("academy", (W - aw) / 2 - ax0, base, size, INK, tracking)
    body = f'<g transform="translate({(W - mw) / 2 - x0:.2f} {pad - y0:.2f})">{tot_mark()}</g>{acad}'
    return body, W, H


def tot_side(pad):
    """The mark with "academy" to its right, sitting on the letters' baseline."""
    size, tracking = 104, 0.0
    x0, y0, x1, y1 = MARK
    mw, mh = x1 - x0, y1 - y0
    ax0, ay0, ax1, ay1 = ink_box("academy", size, tracking)
    gap = 30
    base = pad + mh                      # the bottom of the t's and the o
    top = min(pad, base + ay0)
    bottom = max(pad + mh, base + ay1)
    shift = pad - top                    # room for anything that rises above the mark
    W = pad + mw + gap + (ax1 - ax0) + pad
    H = bottom + shift + pad
    acad, _ = word("academy", pad + mw + gap - ax0, base + shift, size, INK, tracking)
    body = f'<g transform="translate({pad - x0:.2f} {pad + shift - y0:.2f})">{tot_mark()}</g>{acad}'
    return body, W, H


def framed(body, W, H):
    """An SVG of whole-pixel size with the drawing centred in it."""
    w, h = round(W), round(H)
    return w, h, f'<g transform="translate({(w - W) / 2:.2f} {(h - H) / 2:.2f})">{body}</g>'


def tot_academy():
    # Wide: "academy" on the right. Stacked: "academy" underneath.
    (OUT / "tot-academy.svg").write_text(svg(*framed(*tot_side(16))[:2], "Tot Academy", framed(*tot_side(16))[2]))
    (OUT / "tot-academy-stacked.svg").write_text(svg(*framed(*tot_lockup(16))[:2], "Tot Academy", framed(*tot_lockup(16))[2]))

    # Square: the stacked lockup centred on paper, inside the circle a profile picture crops to.
    body, W, H = tot_lockup(0)
    S = 512
    k = 380 / W
    sq = svg(S, S, "Tot Academy",
             f'<g transform="translate({(S - W * k) / 2:.2f} {(S - H * k) / 2:.2f}) scale({k:.4f})">{body}</g>', bg=PAPER)
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

    # Square: the circled A over the name on two lines, for profile pictures.
    S = 512
    size = 74
    words = [("Anthem", INK), ("Madness", ROSE)]
    boxes = [ink_box(t, size, -0.01) for t, _ in words]
    cap = -boxes[0][1]          # "A" and "M" set the cap height
    lead = 1.12 * size
    disc = 228
    gap = 30
    block = disc + gap + cap + lead
    top = (S - block) / 2
    k = disc / 600
    body = f'<g transform="translate({(S - disc) / 2 - 40 * k:.2f} {top - 40 * k:.2f}) scale({k:.5f})">{circled_a(ROSE)}</g>'
    base = top + disc + gap + cap
    for (t, fill), (x0, _, x1, _) in zip(words, boxes):
        path, _ = word(t, (S - (x1 - x0)) / 2 - x0, base, size, fill, -0.01)
        body += path
        base += lead
    (OUT / "anthem-madness-square.svg").write_text(svg(S, S, "Anthem Madness", body, bg=PAPER))


if __name__ == "__main__":
    tot_academy()
    anthem_madness()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.svg") if p.name != "logo.svg")))
