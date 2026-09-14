# Cutouts — background removed, full resolution RGBA

Four files, all **1717 × 2576** (same frame as the source photos, nothing cropped or
resampled), genuine 8-bit alpha channel.

* `*-cut.png` — the normal cutout. Use this everywhere by default.
* `*-cut-soft.png` — same matte with the alpha edge feathered ~2px and an extra
  spill-suppression pass. Use **only** on strongly coloured grounds (maroon, gold)
  where a 1px hard edge can shimmer. On cream/ivory prefer the plain `-cut`.

All numbers below are **measured**, not estimated. Bounding box = the extent of every
pixel with `alpha > 0`, given as inclusive pixel coordinates; the percentages are of
the 1717 × 2576 frame (`left = x/1717`, `right = (x+1)/1717`, likewise for y/2576).
The eye-line is the mean of the two iris centres, fitted as circles on the source.

---

## 1. `mohinur-cut.png` — Mohinur Abdullayeva

| | |
|---|---|
| Size | 1717 × 2576 px · RGBA · 4 219 754 bytes (4.22 MB) |
| Bounding box | L **0** · T **105** · R **1716** · B **2575**  → 1717 × 2471 px |
| Bounding box % | L **0.00%** · T **4.08%** · R **100.00%** · B **100.00%** (w 100.00% · h 95.92%) |
| Eye-line | y = **656.5 px** = **25.49%** from the top of the frame (= 22.32% down the bounding box) |
| Frame bleed | runs off the **left, right and bottom** edges — the bottom row is 100% opaque |

She already fills the frame edge to edge, so no horizontal nudge is needed.

```html
<img class="cut cut--mohinur" src="assets/cutout/mohinur-cut.png" alt="Mohinur Abdullayeva">
```
```css
/* gown bleeds off left/right/bottom by design; eyes land at 25.49% of the image height */
.cut--mohinur{ position:absolute; left:0; bottom:0; width:100%; height:auto; }
```

---

## 2. `sarvinoz-cut.png` — Sarvinoz Alisherovna

| | |
|---|---|
| Size | 1717 × 2576 px · RGBA · 3 796 589 bytes (3.80 MB) |
| Bounding box | L **81** · T **101** · R **1578** · B **2575**  → 1498 × 2475 px |
| Bounding box % | L **4.72%** · T **3.92%** · R **91.96%** · B **100.00%** (w 87.25% · h 96.08%) |
| Eye-line | y = **651.5 px** = **25.29%** from the top of the frame (= 22.24% down the bounding box) |
| Frame bleed | runs off the **bottom** only (82% of the bottom row opaque); clear margins left and right |

She has ~4.7% empty margin on the left and ~8% on the right, so to make her body span a
container exactly, scale by 100/87.25 = 114.61% and pull left by 4.72 × 1.1461 = 5.41%.

```html
<img class="cut cut--sarvinoz" src="assets/cutout/sarvinoz-cut.png" alt="Sarvinoz Alisherovna">
```
```css
/* 114.61% + −5.41% makes the SUBJECT (not the file) span the container edge to edge */
.cut--sarvinoz{ position:absolute; left:-5.41%; bottom:0; width:114.61%; height:auto; }
```

---

## 3. `mohinur-cut-soft.png` — feathered, for coloured grounds

| | |
|---|---|
| Size | 1717 × 2576 px · RGBA · 4 232 681 bytes (4.23 MB) |
| Bounding box | L **0** · T **104** · R **1716** · B **2575**  → 1717 × 2472 px |
| Bounding box % | L **0.00%** · T **4.04%** · R **100.00%** · B **100.00%** (w 100.00% · h 95.96%) |
| Eye-line | y = **656.5 px** = **25.49%** from the top of the frame (= 22.35% down the bounding box) |
| Frame bleed | left, right and bottom; the bleed edges are held hard, only the free edges are feathered |

```html
<img class="cut cut--mohinur-soft" src="assets/cutout/mohinur-cut-soft.png" alt="Mohinur Abdullayeva">
```
```css
/* identical placement to mohinur-cut.png — the matte is 1px softer, the geometry is the same */
.cut--mohinur-soft{ position:absolute; left:0; bottom:0; width:100%; height:auto; }
```

---

## 4. `sarvinoz-cut-soft.png` — feathered, for coloured grounds

| | |
|---|---|
| Size | 1717 × 2576 px · RGBA · 3 798 726 bytes (3.80 MB) |
| Bounding box | L **79** · T **101** · R **1579** · B **2575**  → 1501 × 2475 px |
| Bounding box % | L **4.60%** · T **3.92%** · R **92.02%** · B **100.00%** (w 87.42% · h 96.08%) |
| Eye-line | y = **651.5 px** = **25.29%** from the top of the frame (= 22.24% down the bounding box) |
| Frame bleed | bottom only |

```html
<img class="cut cut--sarvinoz-soft" src="assets/cutout/sarvinoz-cut-soft.png" alt="Sarvinoz Alisherovna">
```
```css
/* 114.39% + −5.26%: same idea as sarvinoz-cut.png, re-derived for the 2px-wider matte */
.cut--sarvinoz-soft{ position:absolute; left:-5.26%; bottom:0; width:114.39%; height:auto; }
```

---

## Hitting a target eye-line

Both women sit at almost the same height in frame (25.49% / 25.29%), so one rule works
for both. To put the eyes at `E` px down a canvas of any size:

```
image height = E / 0.2549   (Mohinur)      image height = E / 0.2529   (Sarvinoz)
image top    = E − 0.2549 × image height   ( = the same thing, expressed as an offset )
```

e.g. eyes at 480px down a 1350px 4:5 canvas → Mohinur rendered 1883px tall, `top: 0`.
Because the two eye-lines are within 0.2% of each other, a pair of portraits scaled to
the **same height** will have their eyes aligned to within ~5px at full resolution.

## Notes for placement

* Both files are the **full original frame**, so `object-fit` / `object-position` from
  `base.css` still behaves exactly as it does on the source JPEGs — the only difference
  is that the studio ground is now transparent.
* Nothing belonging to either subject was removed: Mohinur's earring and the full sweep
  of the gown, Sarvinoz's raised hand, her watch, earring, blouse ties and trousers are
  all intact, along with the detached flyaway strands around both heads.
* No retouching, smoothing or reshaping was done. Pixels at `alpha = 255` are bit-identical
  to the source; only partially-transparent edge pixels were recoloured, and only to
  remove the studio ground's contribution to them.
