# Design system

A hand-drawn sticker book: flat colour, a 2px ink outline, a hard offset shadow, a slight tilt,
and a handwritten note on top. Everything below exists to keep that look the same on every page,
in both themes.

The shared part lives in `_build/core.css` and is copied into each page's `<style>` between
`/* @sync core */` markers by `python3 _build/core.py`. Never edit between the markers.
`python3 _build/check.py` fails when a page drifts.

## Tokens (`_build/core.css`)

| Group | Tokens | Use |
| --- | --- | --- |
| Ink and paper | `--ink` `--muted` `--line` `--card` `--card-2` | Text, outlines, card fills |
| Brand | `--brand` `--accent` `--accent-soft` `--teal` `--teal-soft` `--gold` `--gold-soft` `--rose` `--hl` | Links, handwriting (gold or accent), the marker highlight (`--hl`) |
| Sticker fills | `--gold-soft` `--mint-soft` `--sky-soft`, text in `--on-soft` | Pastel fills that stay the same day and night, so the text on them is always dark |
| Pop | `--pop-0` to `--pop-4`, colour `--pop-c` | The offset shadow: 0 pressed, 1 small bits (notes, badges, bubbles), 2 round buttons and pins, 3 cards and big buttons, 4 hover |
| Corners | `--r-sm` `--r-md` `--r-lg` `--r-xl` | Chips and bubbles, buttons and quiet cards, sticker cards, dashed regions |
| Handwriting | `--hand-s` `--hand-m` `--hand-l` | Caveat sizes: asides, kickers, the page eyebrow |
| Headings | `--fs-h2` `--fs-h2-s` | A stop on the trail, and every other section heading (tracking `-.025em`) |
| Measure | `--measure` `--measure-wide` | Reading blocks, and rows of cards or photos |
| Motion | `--t-fast` `--ease-pop` | Hover and press |

A page keeps its own tokens (its sky, the paint for its drawings) in its own `:root` block after
the synced one. It never redefines a shared token.

## Parts

- **Sticker** (button, card, pin): `background: var(--card)`, `border: 2px solid var(--line)`,
  a `--pop` shadow, a radius from the scale. Hover lifts one step: small ones
  `translate(-1px, -1px)` to `--pop-3`, cards and big buttons `translate(-2px, -2px)` to
  `--pop-4`. Pressed is `translate(2px, 2px)` with `--pop-0`.
- **Quiet card** (project rows, quick answers): `border: 2px solid var(--rule)`, no shadow,
  `--r-md`. It becomes a sticker on hover or when open. Use it for lists, so a page has few
  loud things.
- **Handwriting** (`.hand`): short, lower case, tilted a few degrees, gold for kickers and
  accent for place names. Never for facts a reader needs.
- **Marker highlight**: a `linear-gradient` band of `--hl` under a few words of a heading.
- **Tape, polaroids, the boarding pass**: props. They keep their own soft shadows and paper
  colours, because they are objects on the page, not stickers.

## Night

`--line` stays bright, and `--pop-c` steps back to a deeper blue, so a card reads as an outline
with depth instead of a double border. Write night values once in `core.css` inside
`@dark { }`; the script expands it for the reader's pick (`data-theme`) and the system setting.
A page's own night tokens are written twice by hand, and the check compares the two.

## Adding a page or a part

1. Copy the two marker pairs into the new page's `<style>`, add the page to `PAGES` in
   `_build/core.py` and `MAIN` in `_build/check.py`, then run `core.py`.
2. Build parts from the tokens. If a value is missing from a scale, add a step to `core.css`
   instead of writing a one-off.
3. Look at it in both themes and at 390px wide, then run `check.py`.
