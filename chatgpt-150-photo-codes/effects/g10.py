"""Group 10 — Colour grading: earthy, peach, rose_gold, emerald, lavender.

All five are full-frame colour grades of the same portrait, so they are built to be
unmistakable from each other at thumbnail size:
  earthy    - warm brown / olive / terracotta / sand, matte and organic
  peach     - bright, airy, warm peach highlights, rosy skin, faded blacks
  rose_gold - dusty-rose midtones + golden glowing highlights, mauve hijab
  emerald   - deep saturated emerald foliage, teal shadows, luxurious contrast
  lavender  - cool dreamy lilac tint in shadows and highlights, soft glow

Skin is protected in every grade: the tonal part of the grade applies everywhere,
the colour part is blended back on the face so the skin stays natural.
The face mask is the precise segmentation (`seg_face_skin`), which encloses eyes,
brows and lips and does not spill onto the hijab (the landmark `face` oval does).
"""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- helpers

def _face(feather_=2.5, shrink=1):
    """Precise face region (skin + eyes + brows + lips), barely eroded so the feather never reaches the hijab."""
    m = mask('seg_face_skin', grow=-shrink) if shrink else mask('seg_face_skin')
    return feather(m, feather_) if feather_ else m


def _face_wide():
    """Face grown outward: for ops that only touch hues the hijab does not have (the red sleeve)."""
    return mask('seg_face_skin', feather=3, grow=4)


def _person():
    """Subject alpha: foliage ops are restricted to the background with this, so skin hues are never touched."""
    return mask('person', feather=1.0)


def _hue_w(hsv, hue, width, plateau=0.5, min_sat=0.08):
    """Weight 1 inside +-width*plateau of `hue`, tapering to 0 at +-width; gated on saturation."""
    d = np.abs(((hsv[..., 0] - hue + 180.0) % 360.0) - 180.0)
    w = smoothstep(width, width * plateau, d)
    return w * smoothstep(0.0, min_sat * 3, hsv[..., 1])


def _sel(img, hue, width, sat=1.0, lum=0.0, shift=0.0, plateau=0.5, min_sat=0.08, protect=None,
         sat_gate=None, target=None, converge=0.0, ref=None):
    """Selective colour like hsl_adjust, with a flat plateau, a protection mask (1 = leave alone), an
    optional saturation gate (s0, s1) and optional hue convergence toward `target` (0..1)."""
    hsv = rgb2hsv(img)
    hsv_ref = rgb2hsv(ref) if ref is not None else hsv
    w = _hue_w(hsv_ref, hue, width, plateau, min_sat)
    if sat_gate is not None:
        w = w * smoothstep(sat_gate[0], sat_gate[1], hsv_ref[..., 1])
    if protect is not None:
        w = w * (1 - protect)
    h = hsv[..., 0]
    if target is not None and converge:
        dh = ((target - h + 180.0) % 360.0) - 180.0
        h = h + dh * converge * w
    hsv[..., 0] = (h + shift * w) % 360
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + (sat - 1) * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] + lum * w, 0, 1)
    return hsv2rgb(hsv)


def _hue_mask(ref, hue, width, plateau=0.6, protect=None, sat_gate=None):
    """(H,W) weight of pixels of `ref` near a hue (for masked blends)."""
    hsv = rgb2hsv(ref)
    w = _hue_w(hsv, hue, width, plateau)
    if sat_gate is not None:
        w = w * smoothstep(sat_gate[0], sat_gate[1], hsv[..., 1])
    if protect is not None:
        w = w * (1 - protect)
    return w


def _protect(graded, before, amount, m):
    """Blend `before` back into `graded` on the face by `amount` (0..1)."""
    return clip(lerp(graded, before, m * amount))


def _tinted_glow(img, colour, sigma=40, strength=0.3, threshold=0.6, mask_=None):
    """Bloom whose light carries a colour (gold, peach, lavender...)."""
    l = luminance(img)
    hi = smoothstep(threshold, 1.0, l)
    if mask_ is not None:
        hi = hi * mask_
    layer = blur(hi[..., None] * img, sigma) * (0.5 + 0.5 * color(colour))
    return blend(img, np.clip(layer, 0, 1), 'screen', strength)


def _band(img, lo, hi, soft=0.12):
    """Soft luminance band mask (H,W) between lo and hi."""
    l = luminance(img)
    return smoothstep(lo - soft, lo + soft, l) * (1 - smoothstep(hi - soft, hi + soft, l))


def _cheeks():
    """Approximate cheek centres from the landmarks, following the tilt of the face."""
    m = meta()
    fh, ch = np.array(m['forehead']), np.array(m['chin'])
    down = ch - fh
    down = down / np.linalg.norm(down)
    side = np.array([down[1], -down[0]])  # perpendicular, points to viewer's right
    el, er = np.array(m['eye_l']), np.array(m['eye_r'])
    left = el + down * 150 - side * 30
    right = er + down * 150 + side * 30
    return tuple(left), tuple(right)


def _blush(img, colour='#ff8f86', strength=0.3, radius=0.22):
    """Soft rosy warmth on both cheeks, restricted to face skin."""
    cl, cr = _cheeks()
    m = np.maximum(radial(cl, radius, 0.85, aspect=1.15), radial(cr, radius, 0.85, aspect=1.15))
    m = m * feather(mask('seg_face_skin', grow=-6), 8)
    return blend(img, colour, 'soft_light', strength, m)


# ----------------------------------------------------------------------------- 046 earthy

@effect('earthy')
def earthy(img):
    """Terracotta, olive, sand and warm brown: a natural, organic palette."""
    face = _face()
    face_wide = _face_wide()
    person = _person()

    # tone: matte but with body
    img = fade(img, 0.05, 0.03)
    img = s_curve(img, 0.12)
    before = img.copy()
    ref = before

    # foliage -> olive (a touch greener than the yellow-green source, deeper, still coloured)
    img = _sel(img, 60, 60, sat=0.95, lum=-0.09, shift=10, plateau=0.5, protect=person, ref=ref)
    img = blend(img, '#6f7332', 'color', 0.5, _hue_mask(ref, 60, 60, 0.5, person))
    # sleeve red -> terracotta (toward orange, less neon, a little deeper)
    img = _sel(img, 355, 30, sat=0.8, lum=-0.02, shift=18, plateau=0.6, protect=face_wide, sat_gate=(0.45, 0.7), ref=ref)
    img = blend(img, '#b8552f', 'color', 0.35, _hue_mask(ref, 355, 30, 0.6, face_wide, (0.45, 0.7)))
    # navy hijab -> warm dark brown; sky -> sand
    navy = _hue_mask(ref, 235, 50, 0.6)
    img = _sel(img, 235, 50, sat=0.3, lum=0.03, plateau=0.6, ref=ref)
    img = blend(img, '#5a3d2b', 'color', 0.55, navy * (1 - _band(ref, 0.45, 1.3, 0.1)))
    img = blend(img, '#e0c9a0', 'color', 0.6, navy * _band(ref, 0.45, 1.3, 0.1))

    # global warmth: sand highlights, warm brown shadows
    img = temperature(img, 0.1)
    img = split_tone(img, shadows='#3d2b1f', highlights='#d9b48a', strength=0.4)
    img = blend(img, '#e8cfa6', 'soft_light', 0.4, _band(img, 0.62, 1.3))
    img = blend(img, '#4a3323', 'multiply', 0.22, 1 - _band(img, 0.35, 1.3))
    img = saturation(img, 0.95)

    # skin: warm and natural (not orange, not dull)
    skin_v = temperature(before, 0.1)
    skin_v = split_tone(skin_v, shadows='#4a3326', highlights='#e8c9a0', strength=0.2)
    img = _protect(img, skin_v, 0.45, face)

    img = vignette(img, 0.22, color_='#2e2118')
    img = grain(img, 0.02, size=1.4, seed=46)
    return img


# ----------------------------------------------------------------------------- 047 peach

@effect('peach')
def peach(img):
    """Peachy warm tones: soft peach highlights, rosy warmth on the skin, gentle fade."""
    face = _face()
    face_wide = _face_wide()
    person = _person()

    # tone: brighter, airy, gentle fade
    img = brightness(img, 0.02)
    img = fade(img, 0.05, 0.03)
    img = curve(img, [(0, 0.05), (0.5, 0.55), (1, 0.985)])
    before = img.copy()
    ref = before

    # foliage -> golden peach
    img = _sel(img, 60, 60, sat=0.62, lum=0.08, shift=-24, plateau=0.5, protect=person, ref=ref)
    img = blend(img, '#f5b08e', 'color', 0.45, _hue_mask(ref, 60, 60, 0.5, person))
    # navy hijab -> soft muted navy (kept for contrast); sky -> pale peach
    navy = _hue_mask(ref, 235, 50, 0.6)
    img = _sel(img, 235, 50, sat=0.85, lum=0.05, shift=-4, plateau=0.6, ref=ref)
    img = blend(img, '#ffd2b0', 'color', 0.7, navy * _band(ref, 0.5, 1.3, 0.1))
    # red sleeve -> coral
    img = _sel(img, 355, 30, sat=0.85, lum=0.07, shift=14, plateau=0.6, protect=face_wide, sat_gate=(0.45, 0.7), ref=ref)

    # global peach: warm, slightly magenta, peach highlights, peach glow
    img = temperature(img, 0.13)
    img = tint(img, 0.09)
    img = split_tone(img, shadows='#7a4a4c', highlights='#ffc4a8', strength=0.55)
    img = blend(img, '#ffbca0', 'soft_light', 0.5, _band(img, 0.5, 1.3))
    img = blend(img, '#ffd2b8', 'screen', 0.12, _band(img, 0.55, 1.3))
    img = _tinted_glow(img, '#ffc9a8', sigma=40, strength=0.28, threshold=0.58)
    # keep the hijab a soft navy rather than grey
    img = lerp(img, before, navy * (1 - _band(ref, 0.5, 1.3, 0.1)) * 0.5)

    # skin: rosy warmth, kept natural
    skin_v = s_curve(before, 0.06)
    skin_v = split_tone(skin_v, shadows='#7a4448', highlights='#ffd2bc', strength=0.4)
    skin_v = temperature(skin_v, 0.08)
    skin_v = tint(skin_v, 0.08)
    img = _protect(img, skin_v, 0.55, face)
    img = _blush(img, '#ff7f8a', 0.45)

    img = vignette(img, 0.1, color_='#6a4038')
    return img


# ----------------------------------------------------------------------------- 048 rose_gold

@effect('rose_gold')
def rose_gold(img):
    """Rose-gold: pink midtones, golden shimmering highlights, soft glow."""
    face = _face()
    face_wide = _face_wide()
    person = _person()
    bg = mask('background', feather=3)

    # tone
    img = fade(img, 0.04, 0.02)
    img = s_curve(img, 0.08)
    before = img.copy()
    ref = before

    # foliage -> warm gold base (the shadows will go rose, the sunlit leaves gold)
    img = _sel(img, 60, 60, sat=0.6, lum=0.05, shift=-26, plateau=0.5, protect=person, ref=ref)
    # navy hijab -> dusty mauve
    navy = _hue_mask(ref, 235, 50, 0.6)
    img = _sel(img, 235, 50, sat=0.45, lum=0.07, shift=30, plateau=0.6, ref=ref)
    img = blend(img, '#9a6478', 'color', 0.5, navy)
    # red sleeve -> rose
    img = _sel(img, 355, 30, sat=0.8, lum=0.06, shift=-10, plateau=0.6, protect=face_wide, sat_gate=(0.45, 0.7), ref=ref)

    # dusty-rose midtones
    mid = _band(img, 0.18, 0.5, 0.14)
    img = blend(img, '#d99aa6', 'soft_light', 0.55, mid)
    img = blend(img, '#c9808f', 'color', 0.25, mid * (1 - face))
    img = color_balance(img, midtones=(0.04, -0.01, 0.02))
    img = split_tone(img, shadows='#6b2f45', highlights='#ffd8a8', strength=0.5)

    # golden highlights + golden glow
    hi = _band(img, 0.48, 1.3, 0.12)
    img = blend(img, '#f2c47a', 'soft_light', 0.8, hi)
    img = blend(img, '#e6b266', 'color', 0.5, hi * (1 - face))
    img = blend(img, '#ffe0a0', 'screen', 0.2, _band(img, 0.62, 1.3, 0.1) * (1 - face))
    img = _tinted_glow(img, '#ffd28a', sigma=45, strength=0.45, threshold=0.5)
    img = _tinted_glow(img, '#ffe6b0', sigma=12, strength=0.25, threshold=0.6, mask_=bg)
    img = vibrance(img, 0.12)

    # shimmer: tiny gold sparkles on the brightest sun-lit leaves
    l = blur(luminance(img) * bg, 1.5)
    local = np.clip(l - blur(l, 12), 0, 1)  # leaf glints = local peaks, not the flat sky
    r = rng(48)
    thr = np.percentile(local[bg > 0.5], 99.3)
    ys, xs = np.where((local > thr) & (bg > 0.6))
    pts, sizes = [], []
    if len(xs):
        for i in r.permutation(len(xs)):
            x, y = float(xs[i]), float(ys[i])
            if all((x - px) ** 2 + (y - py) ** 2 > 60 ** 2 for px, py in pts):
                pts.append((x, y)); sizes.append(float(r.uniform(7, 15)))
            if len(pts) >= 22:
                break
    if pts:
        sp = sparkle_layer(pts, sizes, color_='#fff2cc', seed=48)
        img = blend(img, sp, 'screen', 0.42)

    # skin: rosy-gold but natural
    skin_v = split_tone(before, shadows='#6b3a45', highlights='#ffd8b8', strength=0.35)
    skin_v = color_balance(skin_v, midtones=(0.03, 0, 0.015))
    img = _protect(img, skin_v, 0.45, face)

    img = vignette(img, 0.18, color_='#4a2430')
    return img


# ----------------------------------------------------------------------------- 049 emerald

@effect('emerald')
def emerald(img):
    """Deep emerald: rich saturated greens, dark teal shadows, luxurious contrast."""
    face = _face()
    face_wide = _face_wide()
    person = _person()

    # tone: luxurious contrast
    img = s_curve(img, 0.18)
    img = clarity(img, 0.15, 40)
    before = img.copy()
    ref = before

    # foliage yellow-green -> emerald (all leaf hues converge on ~140, deeper and richer)
    fol = _hue_mask(ref, 60, 64, 0.55, person)
    img = _sel(img, 60, 64, sat=1.4, lum=-0.07, plateau=0.55, protect=person, target=140, converge=0.85, ref=ref)
    # tame the sunlit leaves (no neon lime): darken and deepen the brightest greens
    img = blend(img, '#0f6b46', 'multiply', 0.45, fol * _band(ref, 0.45, 1.3, 0.12))
    img = blend(img, '#1f9a62', 'color', 0.3, fol)
    # sky / navy hijab -> deep teal-navy
    img = _sel(img, 235, 50, sat=1.1, lum=0.04, shift=-38, plateau=0.6, ref=ref)
    # sleeve red -> deep rich red (complement of emerald)
    img = _sel(img, 355, 30, sat=1.0, lum=-0.06, shift=-4, plateau=0.6, protect=face_wide, sat_gate=(0.45, 0.7), ref=ref)

    # dark teal shadows, clean warm-neutral highlights
    img = split_tone(img, shadows='#0a3328', highlights='#f0e6cc', strength=0.45)
    img = color_balance(img, shadows=(-0.05, 0.02, 0.03))
    img = blend(img, '#06261f', 'multiply', 0.25, 1 - _band(img, 0.3, 1.3, 0.15))

    # skin: protected, only the contrast curve and a whisper of the grade
    img = _protect(img, before, 0.65, face)

    img = vignette(img, 0.26, color_='#04120f')
    return img


# ----------------------------------------------------------------------------- 050 lavender

@effect('lavender')
def lavender(img):
    """Dreamy lavender tint: soft purple in shadows and highlights, cool and romantic."""
    face = _face()
    face_wide = _face_wide()
    person = _person()

    # tone: soft, lifted, dreamy
    img = brightness(img, 0.03)
    img = fade(img, 0.08, 0.03)
    before = img.copy()
    ref = before

    # foliage -> soft lilac / mauve-grey (coloured, not grey)
    fol = _hue_mask(ref, 60, 60, 0.5, person)
    img = _sel(img, 60, 60, sat=0.5, lum=0.04, shift=30, plateau=0.5, protect=person, ref=ref)
    img = blend(img, '#a894d6', 'color', 0.5, fol)
    # navy hijab & sky -> dusty violet
    navy = _hue_mask(ref, 235, 50, 0.6)
    img = _sel(img, 235, 50, sat=0.7, lum=0.08, shift=18, plateau=0.6, ref=ref)
    img = blend(img, '#7a66b0', 'color', 0.35, navy)
    # red sleeve -> cool mauve-raspberry
    img = _sel(img, 355, 30, sat=0.6, lum=0.06, shift=-22, plateau=0.6, protect=face_wide, sat_gate=(0.45, 0.7), ref=ref)

    # lavender everywhere: purple shadows, pale lavender highlights, cool
    img = temperature(img, -0.1)
    img = split_tone(img, shadows='#3a2a6a', highlights='#e6d8ff', strength=0.5)
    img = blend(img, '#b8a4e6', 'color', 0.22, 1 - face)
    img = blend(img, '#6e58b0', 'soft_light', 0.38, 1 - _band(img, 0.4, 1.3, 0.15))
    img = blend(img, '#4a3a80', 'color', 0.2, (1 - _band(img, 0.32, 1.3, 0.12)) * (1 - face))
    img = blend(img, '#ece2ff', 'soft_light', 0.5, _band(img, 0.5, 1.3, 0.12))
    img = blend(img, '#e6dcff', 'screen', 0.1, _band(img, 0.55, 1.3, 0.1))
    img = saturation(img, 0.92)

    # dreamy glow
    img = orton(img, sigma=22, strength=0.25)
    img = _tinted_glow(img, '#e6d8ff', sigma=45, strength=0.35, threshold=0.5)

    # skin: cool but alive
    skin_v = temperature(before, -0.02)
    skin_v = split_tone(skin_v, shadows='#4a3a6a', highlights='#f0e4ff', strength=0.2)
    skin_v = blend(skin_v, '#e8a8b8', 'soft_light', 0.3)
    skin_v = s_curve(skin_v, 0.05)
    img = _protect(img, skin_v, 0.62, face)

    img = vignette(img, 0.14, color_='#3a2a5a')
    return img
