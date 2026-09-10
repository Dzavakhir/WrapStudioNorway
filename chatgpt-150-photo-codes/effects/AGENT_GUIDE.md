# Designer-agent guide — 150 ChatGPT photo codes

You are one of 30 graphic designers producing the example images for a premium PDF guide
("150 ChatGPT photo-editing codes", romantic-classic style, burgundy & cream). Each code (e.g. `/golden_hour`)
is a prompt a reader sends to ChatGPT together with their photo. **Your job: make the photo of the
guide's model look exactly like the result that code promises**, implemented as Python image code.

Your 5 codes: `python3 tools/brief.py gNN` (NN = your group number) prints them with the Uzbek title,
the English prompt the reader will use, and implementation hints. The hints are a starting point —
you are the designer; the promise in the prompt is the spec.

## Files

* `source/crop.jpg` — the base portrait, 1152 x 1440 (4:5). A daylight park selfie: young woman in a navy
  hijab and red sleeve, smiling, green foliage and a bit of blue sky behind, face centre-left.
* `source/masks/*.png` — ready masks (see `lib.mask`): person, background, face, face_skin, eyes, iris, lips,
  mouth (teeth), brows, seg_hair, seg_clothes … `source/meta.json` — landmark points (eye_l, eye_r, mouth, nose, chin, forehead).
* `effects/lib.py` — the shared helper library (read it once, fully; it has tone/colour, blend modes, blur/glow,
  masks, procedural textures, frames, text). **Do not edit lib.py, registry.py, render.py or codes.json.**
* `effects/gNN.py` — **the only file you create/edit** (NN = your group).
* `render.py` — `python3 render.py gNN` renders your 5 codes to `renders/` and writes the contact sheet
  `previews/gNN.jpg` (original + your 5 results). `python3 render.py some_code` renders one code (-> previews/custom.jpg).

## Contract

```python
from effects.lib import *          # numpy as np, cv2, PIL Image/ImageDraw..., all helpers
from effects.registry import effect

@effect('golden_hour')             # exactly the code name from the brief, no slash
def golden_hour(img):              # img: float32 RGB (1440, 1152, 3) in [0, 1] — a fresh copy, mutate freely
    ...
    return img                     # same shape, float32 in [0,1] (a PIL image of the same size is also accepted)
```

* One function per code, all five in your file. Private helpers are fine (prefix with `_`).
* Deterministic: any randomness must use a fixed seed (`rng(seed)` / `np.random.default_rng(seed)`).
* Keep each effect under ~25 s on 4 CPU cores. No network, no new pip packages, no extra asset files.
* Output must stay 1152 x 1440. Frames/cards must be composited onto a same-size canvas (see `paste`, `inset`, `canvas`).

## Quality bar (this is what gets you a "pass")

1. **Obvious at thumbnail size.** On the contact sheet the result must be instantly distinguishable from the
   original and from the other codes. A subtle nudge is a fail. A garish, clipped mess is also a fail.
2. **Delivers the prompt's promise.** If the prompt says "orange foliage", the foliage is orange. If it says
   "rim light", a rim light is visible along the hijab/shoulders. Read your prompt literally.
3. **Flattering and respectful.** Never alter the face shape, expression, body, hijab or clothing. Skin stays
   natural (no orange, grey or plastic skin) unless the effect is explicitly a stylisation (pop art, thermal…).
   Retouch codes must look like a professional retoucher's work: visible improvement, still real.
4. **Technically clean.** No hard mask edges/halos around the subject (feather masks, use `blur_background`,
   `replace_background`), no banding, no clipped-to-white skin, no 1-px artefacts, no visible seams in tiled work.
5. **Tasteful.** Romantic-classic guide: results should look premium. Text/frames use `font()` (Playfair,
   Cormorant, Lato) — never PIL's default bitmap font. Palette constants in lib (BURGUNDY, CREAM…) are there if a frame or text needs colour.

## Workflow

1. `cat effects/AGENT_GUIDE.md`, `cat effects/lib.py`, `python3 tools/brief.py gNN`.
2. Write `effects/gNN.py` with all five effects.
3. `python3 render.py gNN` → fix any error → **look at `previews/gNN.jpg`** (Read tool) and, for anything you are
   unsure about, the full-size `renders/NNN_code.jpg`.
4. Critique your own sheet as an art director: is each look unmistakable, on-brief, flattering, clean? Adjust and
   re-render. Expect 2–4 iterations; stop when every code passes the bar above.
5. Final answer: one line per code — `/code — what it does now (1 sentence) — any caveat`. Nothing else is needed.

## Tips

* Build looks in layers: tone (curves/levels) → colour (split_tone, hsl_adjust, temperature) → light
  (radial/linear masks with `blend(...,'screen'|'soft_light')`) → texture (grain, paper, scratches) → vignette.
* `blend(img, layer, mode, opacity, mask_)` takes a colour string, a (H,W) mask or an (H,W,3) layer.
* Region work: `apply_mask(original, edited, mask('face_skin', feather=4))`.
* Light sources: `radial(center=(x,y), radius, softness)`, `linear(angle)`, `rays()`, `lens_flare()`, `light_leak()`.
* Cut-out/backgrounds: `blur_background`, `replace_background(img, colour_or_layer)`, `inner_edge(mask('person'))` for rim light.
* Frames: `canvas(CREAM, paper())` + `paste(canvas_img, img, (w,h), rotate_=…, border=…, border_bottom=…, radius=…)`.
* Text: `draw_text(img, "…", (x,y), font('playfair-bold', 120), '#F7F1E8', anchor='mm', tracking=8)`.
* Painterly: `cv_oil`, `cv_stylization`, `cv_pencil`, `xdog`, `halftone`, `posterize`, `gradient_map`.
* Landmarks: `meta()['eye_l']`, `face_center()`, `face_box()`; cheeks ≈ between eye and mouth, 90 px outward.
