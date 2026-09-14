# assets/derived — photo treatments index

Derived from `assets/mohinur.jpg` and `assets/sarvinoz.jpg` by `scratch/treat.py`. Source photos are untouched; every file below is full source resolution (no downscale), so it stays sharp once the renderer's 2x supersample + LANCZOS downscale is applied.

| File | Size (px) | Ground it's for | Example usage |
|---|---|---|---|
| `mohinur-fade-dark.png` | 1717×2576 | Dark maroon ground (#5A0413 / #93061F) | `<img class="ph-fade" src="assets/derived/mohinur-fade-dark.png" style="background:#5A0413">` |
| `mohinur-fade-light.png` | 1717×2576 | Cream / blush ground (#FBF4EA / #F4E3DD) | `<img class="ph-fade" src="assets/derived/mohinur-fade-light.png" style="background:#FBF4EA">` |
| `mohinur-duotone.jpg` | 1717×2576 | Any ground -- self-contained maroon image | `<img class="ph-duotone" src="assets/derived/mohinur-duotone.jpg">` |
| `mohinur-warm.jpg` | 1717×2576 | Any ground -- full-colour photo, cropped/framed as usual | `<img class="ph ph--mohinur" src="assets/derived/mohinur-warm.jpg">` |
| `sarvinoz-fade-dark.png` | 1717×2576 | Dark maroon ground (#5A0413 / #93061F) | `<img class="ph-fade" src="assets/derived/sarvinoz-fade-dark.png" style="background:#5A0413">` |
| `sarvinoz-fade-light.png` | 1717×2576 | Cream / blush ground (#FBF4EA / #F4E3DD) | `<img class="ph-fade" src="assets/derived/sarvinoz-fade-light.png" style="background:#FBF4EA">` |
| `sarvinoz-duotone.jpg` | 1717×2576 | Any ground -- self-contained maroon image | `<img class="ph-duotone" src="assets/derived/sarvinoz-duotone.jpg">` |
| `sarvinoz-warm.jpg` | 1717×2576 | Any ground -- full-colour photo, cropped/framed as usual | `<img class="ph ph--sarvinoz" src="assets/derived/sarvinoz-warm.jpg">` |

## Notes for layout

- `-fade-dark.png` / `-fade-light.png` are RGBA with a soft elliptical alpha falloff (~13-18% of the frame). Place directly over the named ground -- no clipping shape, drop shadow, or extra vignette needed; the PNG edge pixels are already colour-matched toward that ground so there is no grey halo. `-fade-dark` is tuned for `--maroon-deep #5A0413` (also reads fine on `--maroon-ink #34020C` / `--maroon #93061F`); `-fade-light` is tuned for `--cream #FBF4EA` (also reads fine on `--blush #F4E3DD`). Don't cross them: `-fade-light` on a dark ground (or `-fade-dark` on a light one) brings back a visible edge because the edge pixels were colour-lifted the other way.
- `-duotone.jpg` is a flat maroon-ink/maroon/blush duotone (opaque JPEG, own rectangle) -- works on any ground in the palette; use where a graphic, single-colour-family photo treatment fits variant A's ceremonial mood.
- `-warm.jpg` is a normal full-colour photo (opaque JPEG) with a gentle romantic grade -- drop it into the existing `.ph .ph--mohinur` / `.ph .ph--sarvinoz` face-safe crop classes exactly like the source jpgs; only use where the source's rectangular crop is already the intended look (editorial insets, cover frames), not where a soft photo edge is needed.
