# assets/ground — index

Reusable, frameless, modern grounds for large cutout/fade portraits (BRIEF.md
§0). Nothing here depends on anything outside this folder. Load it either way:

```html
<link rel="stylesheet" href="base.css">
<link rel="stylesheet" href="assets/ground/ground.css">
```
```css
/* or, inside your variant's own <style> block: */
@import url("assets/ground/ground.css");
```

Apply one ground class to `.canvas` itself, or to a full-bleed `.layer` div
sitting behind your photo/type layers — both work, every class only touches
`background-*`.

## Files

| File | What it is | Notes |
|---|---|---|
| `ground.css` | 5 ground classes + 3 optional overlay classes | self-contained: CSS gradients + the two files below only |
| `grain-fine.png` | 256×256 RGBA seamless fine-grain dither | tiles with zero seam (FFT-synthesised, not edge-blended); low-contrast gray, alpha baked low. Used by every `.g-*` class already; also the source for `.tex-grain` / `.tex-soft-noise` |
| `bloom.png` | 1200×1200 RGBA soft radial light bloom | transparent well before the edge, warm ivory-gold tint; source for `.tex-bloom`, or use it directly with `mix-blend-mode: screen` / `soft-light` |
| `INDEX-ground.md` | this file | |

Regenerate the two PNGs any time with `python3 scratch/ground.py` — fixed
seeds, byte-for-byte reproducible, writes only into this folder.

## Classes

| Class | For | Direction | Grain |
|---|---|---|---|
| `.g-maroon-deep` | rich general-purpose dark ground, warm light from upper-centre | **A** — modern maroon | baked in (`overlay`, tuned for a saturated dark ground) |
| `.g-maroon-spot` | maroon with a soft spotlight where a figure stands — cutout reads lit from behind | **A**, also suits **C** for a dramatic backlit portrait | baked in (`overlay`) |
| `.g-cream-soft` | airy ivory/cream, barely-there blush in one corner | **B** — ivory & blush | baked in (`soft-light`, gentle so nothing muddies) |
| `.g-cream-wash` | cream with a soft blush wash sweeping across ~half the frame | **B**, the one with more movement | baked in (`soft-light`) |
| `.g-duo-split` (+ `.is-flip`, `.is-horizontal`) | two clean fields, cream + maroon, on one seam — for a figure planted across the join | **C** — editorial asymmetry; also works as a single graphic accent inside an A or B layout | baked in (`soft-light`, uniform across both fields) |
| `.tex-grain` | optional standalone overlay: crisp fine dither | any direction | *is* the grain — see "layering more grain" below |
| `.tex-soft-noise` | optional standalone overlay: softer/larger-tile dither, gentler blend | any direction, safest over cream/blush | *is* the grain, softer |
| `.tex-bloom` | optional standalone overlay: warm screen-blended light bloom | **A** / **C** (needs a dark ground to read against) | not grain — see notes below |

Every `.g-*` class **already has its own grain baked in** — you do not need to
add `.tex-grain` on top of a `.g-*` class just to be safe from banding. Reach
for the three `.tex-*` classes only when you want *more* texture than a
`.g-*` class already carries, or you're applying grain/bloom to a custom
background of your own that isn't one of the five above.

## Usage — one snippet per class

```html
<!-- A — rich ambient maroon, light glows in from upper-centre -->
<div class="canvas g-maroon-deep">…your cutout + type…</div>

<!-- A — maroon spotlight behind a standing figure; slide the light to match -->
<div class="canvas g-maroon-spot" style="--spot-x:50%; --spot-y:58%">…</div>

<!-- B — airy cream, blush tucked in one corner -->
<div class="canvas g-cream-soft">…</div>

<!-- B — cream with a diagonal blush sweep, more movement -->
<div class="canvas g-cream-wash">…</div>

<!-- C — cream/maroon split; default is vertical, cream-left/maroon-right -->
<div class="canvas g-duo-split">…figure standing across the seam…</div>
<!-- swap which side is which colour: -->
<div class="canvas g-duo-split is-flip">…</div>
<!-- split top/bottom instead of left/right (combine with is-flip too): -->
<div class="canvas g-duo-split is-horizontal">…</div>
<!-- slide the seam off-centre: -->
<div class="canvas g-duo-split" style="--duo-pos:58%">…</div>
```

```html
<!-- optional overlays: apply to an element that already has
     position:relative/absolute (.canvas and .layer both do) -->
<div class="layer tex-grain"></div>       <!-- extra crisp dither -->
<div class="layer tex-soft-noise"></div>  <!-- extra soft dither, gentler -->
<div class="layer tex-bloom"
     style="--bloom-x:38%; --bloom-y:32%; --bloom-size:90%; --bloom-opacity:.8"></div>
```
Each `.tex-*` is a single `::after`, so use one per element — stack a second
`.layer` div if you want two of these in the same spot (e.g. grain **and**
bloom together over one ground).

## Layering more grain

- `.g-maroon-deep` / `.g-maroon-spot`: baked-in grain already uses
  `mix-blend-mode: overlay` (the stronger mode, tuned for saturated dark
  reds). If a layout stacks a translucent panel or a wide flat area on top
  and *that* starts banding, add `.tex-grain` to that panel too — don't
  double it directly onto the `.g-*` div itself.
- `.g-cream-soft` / `.g-cream-wash` / `.g-duo-split`: baked-in grain uses
  `soft-light` (gentler, won't grey out the cream). If you build a *custom*
  light gradient elsewhere that isn't one of the five classes, reach for
  `.tex-soft-noise` on it rather than `.tex-grain` — same reasoning, safer
  over light colour.
- Building a gradient from scratch that isn't any of the five `.g-*`
  presets? Add `.tex-grain` (dark backgrounds) or `.tex-soft-noise` (light
  backgrounds) directly to that element — that's exactly what they're for.

## Verified

`scratch/ground-check.html` → `scratch/ground-check.png` (rendered via
`./preview.sh`) checks all five `.g-*` classes at 644×800 against a real
`assets/cutout/*-cut-soft.png` figure + Playfair Display type, all four
`g-duo-split` orientation modifiers, and a direct before/after of
`.tex-grain` / `.tex-soft-noise` against a deliberately shallow banding-prone
gradient. Verified at native render resolution (not just thumbnail): no
visible banding in any gradient, no seam at the grain tile's repeat boundary
in either axis, maroon stays in the brand family (never toward grey),
cream stays warm (never blue/dingy), and cream/maroon text stays legible
over every ground.
