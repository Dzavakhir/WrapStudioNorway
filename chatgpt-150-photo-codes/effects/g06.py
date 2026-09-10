"""Group g06 — Cinematic: pastel_film, neo_noir, bleach_bypass, anamorphic, epic_dark."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- helpers

def _oval_kernel(rx, ry, rim=0.0):
    """Elliptical (anamorphic) bokeh kernel, optionally with a brighter rim ("cat-eye" ring)."""
    rx, ry = int(rx), int(ry)
    y, x = np.mgrid[-ry:ry + 1, -rx:rx + 1].astype(np.float32)
    d = np.sqrt((x / rx) ** 2 + (y / ry) ** 2)
    k = 1 - smoothstep(0.92, 1.0, d)
    if rim:
        k = k * (1 + rim * smoothstep(0.55, 0.95, d))
    return (k / k.sum()).astype(np.float32)


def _oval_bokeh(img, exclude, count=30, rx=24, ry=40, seed=29, min_lum=0.5, spacing=70):
    """Vertical-oval bokeh discs at the brightest background peaks -> (H,W,3) layer to screen-blend.
    Disc colour is sampled from the image so the bokeh belongs to the scene."""
    lum = luminance(img)
    lb = blur(lum, 5) * (1 - exclude)
    dil = cv2.dilate(lb, np.ones((spacing * 2 + 1, spacing * 2 + 1), np.uint8))
    peaks = np.argwhere((lb >= dil - 1e-6) & (lb > min_lum) & (exclude < 0.5))
    if len(peaks) == 0:
        return np.zeros((H, W, 3), np.float32)
    vals = lb[peaks[:, 0], peaks[:, 1]]
    order = np.argsort(-vals)[:count]
    soft = blur(img, 8)
    r = rng(seed)
    x, y = coords()
    layer = np.zeros((H, W, 3), np.float32)
    for i in order:
        cy, cx = peaks[i]
        bright = smoothstep(min_lum, 0.95, float(lb[cy, cx]))
        s = r.uniform(0.6, 1.0) + 0.45 * bright          # brighter gaps = bigger, brighter discs
        d = np.sqrt(((x - cx) / (rx * s)) ** 2 + ((y - cy) / (ry * s)) ** 2)
        disc = (1 - smoothstep(0.82, 1.0, d)) * (0.65 + 0.45 * smoothstep(0.45, 0.95, d))
        col = np.clip(soft[cy, cx] * 1.3 + 0.12, 0, 1) * 0.75 + color('#fff1cf') * 0.25
        a = 0.22 + 0.6 * bright
        layer += disc[..., None] * col * a
    return np.clip(layer, 0, 1)


def _eye_level():
    m = meta()
    return (m['eye_l'][1] + m['eye_r'][1]) / 2.0


# ----------------------------------------------------------------------------- #026 pastel film

@effect('pastel_film')
def pastel_film(img):
    bg = mask('background', feather=3)
    clothes = mask('seg_clothes', feather=4)
    face = mask('face_skin', feather=8)

    # foliage (olive / yellow-green, hue ~45-70) -> pale seafoam mint; sky blue -> pastel pink. Background only.
    bgc = hsl_adjust(img, hue=60, width=48, sat=0.6, lum=0.2, shift=88)
    bgc = hsl_adjust(bgc, hue=215, width=40, sat=0.55, lum=0.12, shift=80)
    bgc = blend(bgc, '#bfeedd', 'soft_light', 0.5)
    img = apply_mask(img, bgc, bg)
    # red sleeve -> soft coral, navy hijab -> pastel lavender-blue (clothes only, skin untouched)
    cl = hsl_adjust(img, hue=0, width=28, sat=0.55, lum=0.22, shift=8)
    cl = hsl_adjust(cl, hue=235, width=35, sat=0.9, lum=0.24, shift=14)
    img = apply_mask(img, cl, clothes)

    # high key: lifted shadows, low contrast, bright midtones
    img = fade(img, 0.13, 0.03)
    img = contrast(img, 0.86)
    img = gamma(img, 1.14)
    img = brightness(img, 0.03)
    # pink shadows / buttery highlights
    img = split_tone(img, shadows='#e2a6bd', highlights='#fff1b4', balance=-0.05, strength=0.55)
    img = color_balance(img, shadows=(0.06, -0.01, 0.03), highlights=(0.02, 0.01, -0.03))
    img = vibrance(img, 0.12)
    # keep skin peachy rather than grey
    img = apply_mask(img, color_balance(img, midtones=(0.035, 0.0, 0.01)), face)
    # a gentle milky bloom (not a haze)
    img = glow(img, sigma=60, strength=0.22, threshold=0.55)
    img = blend(img, '#f7dbe3', 'soft_light', 0.2)
    img = grain(img, 0.025, size=1.5, seed=26)
    return img


# ----------------------------------------------------------------------------- #027 neo noir

@effect('neo_noir')
def neo_noir(img):
    person_hard = mask('person')
    person = feather(person_hard, 2)
    lum = luminance(img)

    # night base: dark, desaturated, cool; background sinks further than the subject
    dark = temperature(saturation(exposure(img, -1.35), 0.45), -0.25)
    dark = apply_mask(exposure(dark, -0.9), dark, person)

    # two neon sources. left = magenta, right = cyan. "shade" = how much a surface catches light
    xw = linear(0)
    left = 1 - smoothstep(0.38, 0.72, xw)
    right = smoothstep(0.28, 0.66, xw)
    shade = smoothstep(0.03, 0.85, lum) ** 0.85
    albedo = saturation(img, 0.55)
    mag = color('#ff3a92'); cyn = color('#2ab4ff')
    key = (left * (0.12 + 0.88 * shade))[..., None] * mag * 0.88 + (right * (0.12 + 0.88 * shade))[..., None] * cyn * 0.85
    # background catches less light (it is further from the signs)
    key = key * (0.45 + 0.55 * person)[..., None]
    lit = clip(dark + albedo * key)

    # glossy specular sheen: the brightest surfaces flash the neon colour
    spec = smoothstep(0.66, 0.97, lum)
    lit = blend(lit, (spec * left)[..., None] * mag, 'screen', 0.45)
    lit = blend(lit, (spec * right)[..., None] * cyn, 'screen', 0.45)

    # coloured rim light along the silhouette
    rim = inner_edge(person_hard, width=16, softness=7)
    lit = blend(lit, (rim * left)[..., None] * mag, 'screen', 0.9)
    lit = blend(lit, (rim * right)[..., None] * cyn, 'screen', 0.9)

    # neon bloom, punchy contrast, a little grain
    lit = glow(lit, sigma=35, strength=0.35, threshold=0.5)
    lit = s_curve(lit, 0.2)
    lit = vignette(lit, 0.35, radius=1.05, softness=0.7)
    lit = grain(lit, 0.04, seed=27)
    return lit


# ----------------------------------------------------------------------------- #028 bleach bypass

@effect('bleach_bypass')
def bleach_bypass(img):
    face = mask('face_skin', feather=8)
    # roll the highlights off first so the silver contrast never clips the skin
    src = curve(img, [(0, 0), (0.5, 0.5), (0.75, 0.71), (0.9, 0.8), (1, 0.88)])
    g = gray(src)
    # silver retained in the film: luminance overlaid on itself = hard, dense contrast
    out = blend(src, g, 'overlay', 0.42)
    out = saturation(out, 0.24)
    # the face keeps a touch more colour so she does not go corpse-grey
    out = apply_mask(out, saturation(blend(src, g, 'overlay', 0.36), 0.4), face)
    out = s_curve(out, 0.1)
    # gritty detail (wide-radius local contrast only: no edge halos)
    out = clarity(out, 0.3, 70)
    out = unsharp(out, 0.9, 0.25)
    # cool silvery tint: steel shadows, pale silver highlights
    out = temperature(out, -0.1)
    out = split_tone(out, shadows='#1b2431', highlights='#dfe6ee', strength=0.35)
    out = grain(out, 0.08, size=1.25, seed=28)
    out = vignette(out, 0.3, radius=1.0, softness=0.7)
    return out


# ----------------------------------------------------------------------------- #029 anamorphic

@effect('anamorphic')
def anamorphic(img):
    person_hard = mask('person')
    person = feather(person_hard, 2)
    face = mask('face', feather=10)
    eyes = mask('eyes', feather=10, grow=14)
    x, y = coords()

    # --- background: vertical-oval bokeh (anamorphic squeeze), sky gaps blooming into oval discs
    k = _oval_kernel(11, 19, rim=0.5)
    bgm = (1 - person_hard)[..., None]
    boosted = np.clip(img, 0, 1) ** 2.4
    num = cv2.filter2D(boosted * bgm, -1, k, borderType=cv2.BORDER_REFLECT)
    den = cv2.filter2D(np.repeat(bgm, 3, 2), -1, k, borderType=cv2.BORDER_REFLECT)
    bgb = np.clip(num / np.maximum(den, 1e-3), 0, 1) ** (1 / 2.4)
    bgb = blur(bgb, 1.5)
    discs = _oval_bokeh(img, person_hard, count=28, rx=22, ry=38, seed=29, min_lum=0.6, spacing=55)
    bgb = blend(bgb, discs, 'screen', 0.85)
    out = lerp(img, bgb, 1 - person)

    # --- subtle cinematic grade: teal shadows, warm highlights
    out = split_tone(out, shadows='#1d4a58', highlights='#f2c28a', strength=0.4)
    out = s_curve(out, 0.12)
    out = saturation(out, 0.9)

    # --- horizontal blue lens-flare streak at eye level, source off to the right
    y0 = _eye_level()
    sx = W * 0.94
    core = np.exp(-((y - y0) / 4.5) ** 2)
    mid = np.exp(-((y - y0) / 18.0) ** 2)
    wide = np.exp(-((y - y0) / 80.0) ** 2)
    prof = 0.6 + 0.4 * np.exp(-((x - sx) / (W * 0.6)) ** 2)
    streak = (core[..., None] * color('#dcecff') * 1.0
              + mid[..., None] * color('#3e8cff') * 0.7
              + wide[..., None] * color('#3e8cff') * 0.3) * prof[..., None]
    d = np.sqrt((x - sx) ** 2 + (y - y0) ** 2)
    hot = ((1 - smoothstep(0, 34, d)) ** 2)[..., None] * color('#ffffff') + (np.exp(-(d / 150) ** 2) * 0.6)[..., None] * color('#5aa0ff')
    # thin secondary streak a little below (multi-element anamorphic flare)
    sec = np.exp(-((y - y0 - 48) / 3.0) ** 2) * (0.35 + 0.65 * smoothstep(0.2, 1.0, x / W))
    streak = streak + sec[..., None] * color('#8ab8ff') * 0.45
    # translucent over the face, nearly gone over the eyes: the flare must not mask her
    streak = streak * (1 - 0.6 * face)[..., None] * (1 - 0.75 * eyes)[..., None] + hot
    streak = np.clip(streak, 0, 1)
    out = blend(out, streak, 'screen', 0.92)
    out = blend(out, blur(streak, 30) * 0.6, 'screen', 0.5)

    out = vignette(out, 0.28, radius=1.05, softness=0.7)
    out = grain(out, 0.03, seed=29)
    return out


# ----------------------------------------------------------------------------- #030 epic dark fantasy

@effect('epic_dark')
def epic_dark(img):
    person = mask('person', feather=3)
    face = mask('face_skin', feather=8)

    out = saturation(img, 0.58)
    out = apply_mask(out, saturation(img, 0.8), face)           # keep her alive
    graded = split_tone(out, shadows='#0e1a2e', highlights='#dca055', balance=-0.05, strength=0.55)
    # the face takes the gold more gently, and a touch of magenta keeps the skin from going sallow
    face_g = tint(split_tone(out, shadows='#0e1a2e', highlights='#e0a060', balance=-0.05, strength=0.38), 0.12)
    out = apply_mask(graded, face_g, face)
    out = s_curve(out, 0.22)
    # background sinks into cold darkness
    bgd = temperature(exposure(out, -0.55), -0.18)
    out = apply_mask(bgd, out, person)
    # warm golden key light from the top-right (gentle on the skin)
    keym = radial(center=(W * 0.68, H * 0.28), radius=0.85, softness=0.85)
    out = blend(out, '#eaa662', 'soft_light', 0.35, keym)
    # god rays from the top-right corner + glow at the source (rays stay off the face)
    r = rays(center=(W * 1.05, -H * 0.05), count=16, seed=6, sharpness=8.0, spread=1.3)
    r = r * (1 - 0.35 * person) * (1 - 0.8 * face)
    out = blend(out, r[..., None] * color('#f0b860'), 'screen', 0.36)
    src = radial(center=(W * 1.02, -H * 0.02), radius=0.75, softness=1.0)
    out = blend(out, src[..., None] * color('#f2c070'), 'screen', 0.35)
    # crisp detail (a little softer on the skin)
    crisp = unsharp(clarity(out, 0.42, 40), 1.3, 0.3)
    out = apply_mask(crisp, unsharp(clarity(out, 0.22, 40), 1.3, 0.2), face)
    # dramatic vignette
    out = vignette(out, 0.55, radius=1.0, softness=0.75, color_='#050810')
    out = grain(out, 0.04, seed=30)
    return out
