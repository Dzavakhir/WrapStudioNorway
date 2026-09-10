"""Group g02 — Lighting: candle_light, moonlight, sunset_glow, overcast, spotlight."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _rim(dx, dy, soft=5.0, m=None, inset_px=2):
    """Direction-aware rim band just inside the subject silhouette. Shifting the person mask by (dx, dy)
    leaves a band on the edges that face the opposite direction (e.g. dx=dy=+12 -> edges facing top-left).
    The band is built from an eroded mask so it never spills onto the background (no cut-out halo)."""
    m = mask('person') if m is None else m
    if inset_px:
        m = cv2.erode(m, np.ones((inset_px * 2 + 1,) * 2, np.uint8))
    shifted = translate(m, dx, dy, border=cv2.BORDER_REPLICATE)
    band = np.clip(m - shifted, 0, 1)
    # brightest right at the edge, fading inwards
    band = band * (0.55 + 0.45 * feather(band, 2.0))
    return feather(band, soft)


def _glow_spot(center, radius, softness=0.9, aspect=1.0):
    """Soft elliptical light blob (H, W)."""
    return radial(center=center, radius=radius, softness=softness, aspect=aspect)


# ----------------------------------------------------------------------------- 006 candle light

@effect('candle_light')
def candle_light(img):
    """Lit only by a candle held low-left of the face: amber glow on the face, dark soft warm surroundings."""
    person = mask('person', feather=2)
    bg = 1 - person

    # soft, warm surroundings: gentle background blur + brown-amber tone (candlelight carries no green)
    img = blur_background(img, sigma=5)
    warm_bg = tone(img, '#c27a3c', 0.7)
    img = apply_mask(img, warm_bg, feather(bg, 3) * 0.85)

    # tame the sunlit highlights so nothing reads as daylight
    img = curve(img, [(0, 0), (0.6, 0.55), (0.85, 0.74), (1, 0.9)])

    # the candle sits low-left of the face: a broad warm pool of light, dark beyond it
    light = radial(center=(470, 800), radius=0.85, softness=0.72)
    core = radial(center=(450, 860), radius=0.5, softness=0.95)
    key = np.clip(light * 0.8 + core * 0.4, 0, 1)
    dark = img * (2.0 ** -2.1)
    lit = img * 1.1
    img = lerp(dark, lit, key)
    # far corners (away from the flame) sink further into darkness
    img = img * (1 - 0.35 * (1 - linear(60, 0.0, 0.75)))[..., None]

    # amber colour of the flame on the lit area, warm grade overall (amber, not orange: keep some blue)
    img = blend(img, '#ffa452', 'soft_light', 0.45, key)
    img = blend(img, '#ff9a3a', 'screen', 0.08, core)
    img = temperature(img, 0.4)
    img = split_tone(img, shadows='#2a0e05', highlights='#ffb050', strength=0.45)
    img = color_balance(img, shadows=(0.02, -0.01, -0.03), midtones=(0.0, 0.0, 0.02))
    img = apply_mask(img, vibrance(img, 0.12), key)
    # gentle highlight roll-off so the cheeks never clip to flat orange
    img = curve(img, [(0, 0), (0.55, 0.55), (0.8, 0.77), (1, 0.94)])

    # the (off-frame) candle: warm glow bleeding in from the bottom-left corner
    flame = _glow_spot((40, 1430), 0.6, softness=1.0) * (0.85 + 0.3 * fbm(4, 6, 0.6))
    flame = np.clip(flame + 0.9 * _glow_spot((40, 1430), 0.22, softness=1.0), 0, 1.4)
    img = blend(img, np.clip(flame[..., None] * color('#ffb45a'), 0, 1), 'screen', 0.85)

    img = glow(img, sigma=45, strength=0.32, threshold=0.5)
    img = grain(img, 0.06, seed=6)
    img = vignette(img, 0.5, radius=0.95, softness=0.7, color_='#150804')
    return img


# ----------------------------------------------------------------------------- 007 moonlight

@effect('moonlight')
def moonlight(img):
    """Moonlit night: cool blue-silver light from a moon in the top-left, deep soft shadows, desaturated."""
    person = mask('person')

    # night base: dark, cool, desaturated with deep soft shadows; the moon (top-left) lights the face
    key = radial(center=(120, 140), radius=1.7, softness=0.85)          # moon direction (top-left)
    face_key = radial(center=(470, 590), radius=1.0, softness=0.8)      # moonlight falling on the face
    k = np.clip(key * 0.5 + face_key * 0.7, 0, 1)
    dark = exposure(img, -1.7)
    lit = exposure(img, -0.3)
    img = lerp(dark, lit, k)
    # the side away from the moon (bottom-right) falls into deep shadow
    img = img * (1 - 0.4 * linear(35, 0.3, 1.0))[..., None]
    img = temperature(img, -0.5)
    img = saturation(img, 0.45)
    img = split_tone(img, shadows='#0b1a3a', highlights='#cfe0ff', strength=0.55)
    img = curve(img, [(0, 0), (0.15, 0.09), (0.55, 0.55), (1, 0.97)])
    img = color_balance(img, shadows=(-0.02, 0.0, 0.07), midtones=(-0.01, 0.0, 0.04))
    # a little definition on the moonlit face so it does not go muddy
    img = apply_mask(img, clarity(img, 0.18, 50), face_key)

    # silver key light from the top-left + silvery sheen on the lit skin highlights
    img = blend(img, '#dbe8ff', 'screen', 0.25, key)
    sheen = smoothstep(0.3, 0.7, luminance(img)) * face_key
    img = blend(img, '#e2ecff', 'screen', 0.3, sheen)

    # soft moonlight rim on the hijab/shoulder edges that face the moon (inside the silhouette, no halo)
    facing = 1 - linear(45, 0.15, 0.8)  # only edges on the moon side of the frame
    rim = _rim(10, 10, soft=6.0, m=person) * facing
    img = blend(img, '#e4eeff', 'screen', 0.45, rim)
    img = blend(img, '#c8d8ff', 'screen', 0.22, feather(rim, 22))

    # the moon itself: soft bright disc with a wide halo in the top-left sky
    x, y = coords()
    mx, my = 96, 100
    d = np.sqrt((x - mx) ** 2 + (y - my) ** 2)
    disc = feather(1 - smoothstep(40, 46, d), 1.5)
    halo = np.exp(-(d / 150) ** 2) * 0.5 + np.exp(-(d / 480) ** 2) * 0.28
    moon = np.clip(disc * 0.92 + halo, 0, 1)
    img = blend(img, moon[..., None] * color('#e6eeff'), 'screen', 0.95)

    img = glow(img, sigma=40, strength=0.25, threshold=0.45)
    img = grain(img, 0.04, seed=7)
    img = vignette(img, 0.45, radius=0.95, softness=0.7, color_='#05091a')
    return img


# ----------------------------------------------------------------------------- 008 sunset glow

@effect('sunset_glow')
def sunset_glow(img):
    """Sunset backlight: peach-pink/orange light from behind (top-right), warm skin, soft flare, pastel purple shadows."""
    person = mask('person', feather=2)
    bg = 1 - person

    # sky and cool background patches -> peach-pink (background only, hijab keeps its colour)
    bg_col = hsl_adjust(img, hue=210, width=45, sat=1.0, lum=0.08, shift=120)
    img = apply_mask(img, bg_col, feather(bg, 2))

    # peach -> purple gradient, stronger on the background
    grad = linear(90)
    layer = lerp(as_layer('#ffa070'), as_layer('#7a4b8a'), grad)
    img = blend(img, layer, 'screen', 0.5, 0.42 + 0.58 * bg)

    # warm grade, pastel lifted purple shadows (kept gentle so the hijab stays rich)
    img = temperature(img, 0.3)
    img = fade(img, 0.045, 0.015)
    img = split_tone(img, shadows='#4a2a5c', highlights='#ffbe8a', strength=0.45)
    img = color_balance(img, shadows=(0.03, -0.01, 0.06))

    # the sun behind her, top-right: broad wrap light + rim on the edges facing it
    sun = radial(center=(W * 0.93, H * 0.07), radius=1.15, softness=0.9)
    img = blend(img, '#ffb070', 'screen', 0.42, sun * (0.55 + 0.45 * bg))
    rim = _rim(-10, 9, soft=5.0) * (linear(20, 0.2, 0.85))
    img = blend(img, '#ffc890', 'screen', 0.7, rim)
    img = blend(img, '#ffb888', 'screen', 0.3, feather(rim, 18))

    # highlight roll-off: warm, luminous skin without clipping
    img = curve(img, [(0, 0), (0.55, 0.55), (0.8, 0.76), (1, 0.94)])

    # soft flare
    img = lens_flare(img, pos=(W * 0.9, H * 0.08), strength=0.6, color_='#ffd9b0', ghosts=False, streak=False)
    img = glow(img, sigma=45, strength=0.3, threshold=0.6)
    img = grain(img, 0.025, seed=8)
    return img


# ----------------------------------------------------------------------------- 009 overcast

@effect('overcast')
def overcast(img):
    """Overcast daylight: cool, even, low-contrast, muted, soft grey-blue, highlights pulled down."""
    person = mask('person', feather=2)
    bg = 1 - person

    # kill the sun: muted, darker warm-lit foliage, blue sky -> pale grey cloud, background highlights compressed
    bg_col = hsl_adjust(img, hue=55, width=50, sat=0.4, lum=-0.1)
    bg_col = hsl_adjust(bg_col, hue=210, width=40, sat=0.1, lum=0.16)
    bg_col = hsl_adjust(bg_col, hue=120, width=50, sat=0.7, lum=-0.03)
    bg_col = curve(bg_col, [(0, 0), (0.5, 0.48), (0.75, 0.64), (1, 0.84)])
    img = apply_mask(img, bg_col, feather(bg, 2))

    # flat, cool, soft, but still bright daylight
    img = temperature(img, -0.3)
    img = saturation(img, 0.68)
    img = contrast(img, 0.85, pivot=0.55)
    img = fade(img, 0.05, 0.03)
    img = curve(img, [(0, 0), (0.8, 0.74), (1, 0.93)])
    img = gamma(img, 1.06)
    img = color_balance(img, shadows=(-0.02, 0.0, 0.04), midtones=(-0.01, 0.0, 0.02))
    img = clarity(img, -0.12, 60)
    face_m = mask('face', feather=8)
    img = blend(img, '#c4ccd6', 'normal', 0.07, 1 - 0.6 * face_m)

    # skin stays skin: pull the face back from grey-blue to a soft, natural (slightly cool) complexion
    skin = saturation(temperature(img, 0.3), 1.2)
    skin = color_balance(skin, midtones=(0.02, 0.0, -0.01))
    img = apply_mask(img, skin, face_m * 0.9)
    return img


# ----------------------------------------------------------------------------- 010 spotlight

@effect('spotlight')
def spotlight(img):
    """A single theatrical spotlight on the face; everything else sinks into near-black darkness."""
    cx, cy = face_center()
    light = radial(center=(cx, cy - 20), radius=0.77, softness=0.6)
    img_lit = img * 1.06
    img_dark = img * 0.06
    out = lerp(img_dark, img_lit, light)

    # warm stage-lamp tint on the lit area, skin kept lively
    out = blend(out, '#ffe4bc', 'soft_light', 0.3, light)
    out = apply_mask(out, vibrance(out, 0.15), light)

    # faint haze cone from the lamp above
    x, y = coords()
    apex_y = -260.0
    width = 70.0 + 0.55 * (y - apex_y)
    cone = np.exp(-((x - cx) / np.maximum(width, 1)) ** 2) * (1 - smoothstep(cy - 420, cy - 40, y))
    cone = cone * (0.75 + 0.35 * fbm(4, 10, 0.7)) * smoothstep(-150, 250, y)
    out = blend(out, '#ffefd8', 'screen', 0.11, cone)

    out = glow(out, sigma=40, strength=0.2, threshold=0.55)
    out = grain(out, 0.04, seed=10)
    return out
