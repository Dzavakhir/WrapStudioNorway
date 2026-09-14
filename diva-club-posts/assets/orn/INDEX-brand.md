# Brand-derived ornaments — index

Hand-drawn from the club's own logo (`assets/logo.png`): the pomegranate the
goddess holds, its crown of sepals, and the spiral inside it. Plain SVG line
art, `fill="#000"` / `stroke="#000"` only, meant to be used as CSS masks:

```css
.orn { -webkit-mask: url("assets/orn/pomegranate.svg") center/contain no-repeat;
       background: var(--gold); }
```

| File | viewBox | Intended use | Recommended on-canvas size |
|---|---|---|---|
| `pomegranate.svg` | `0 0 200 240` | Single standalone accent — a small mark beside a date/label, a title's flourish, or scattered once near a corner. Survives down to 60px tall (tested). | 70–120px tall |
| `pomegranate-sprig.svg` | `0 0 220 340` | Two fruit on an asymmetric branch — a corner piece, or run up the side of a title block. Reads best with more room than the single fruit. | 160–260px tall |
| `spiral-rule.svg` | `0 0 600 60` | Horizontal divider between two text blocks (e.g. under the event title, above the date line). Mirrored spiral curls at both ends; hairline weight throughout. | 240–420px wide |
| `sparkle.svg` | `0 0 120 120` | Small scattered accent — a single glint near a headline word or a corner of a photo frame. Designed to be reused at a few sizes/rotations, not as one big feature mark. | 18–44px |
| `monogram-d.svg` | `0 0 240 240` | Standalone club mark / watermark — a footer seal, a small badge near the logo, or a subtle corner mark on a photo. Hand-built serif "D" (bezier paths, no `<text>`) inside a thin laurel-tied oval. | 80–160px square |

## Usage note — current brief direction

`BRIEF.md`'s client-redirect section caps ornament use hard: **at most one or
two deliberate accents per post, or none**, and explicitly steers away from
filigree/wreaths toward frameless, photo-led, modern layouts. Treat this set
as a sparing-use library under that rule, not as a decorating kit:

- `spiral-rule.svg`, `sparkle.svg` and `monogram-d.svg` read as one clean,
  restrained accent each — the easiest fits for the current direction (a
  single hairline divider, one small glint near a headline, a small watermark
  seal).
- `pomegranate.svg` works the same way as a single small mark.
- `pomegranate-sprig.svg` is the most botanical/branch-like piece of the set —
  closest to the "wreath" look the redirect asks to avoid. Reach for it only
  if a post specifically wants that fuller accent, and still keep it as the
  post's *one* ornament, not layered with the others.

All five were checked by eye against the logo (`assets/logo.png`) and the
official cream lockup (`assets/logo-cream-trim.png`) on both a maroon-deep +
gold pairing and a cream/blush + maroon pairing before being finalized.
