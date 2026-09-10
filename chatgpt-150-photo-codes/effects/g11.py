"""Group 11 - Romantik (Romantic): soft_glow, dreamy_haze, bloom, rose_tint, vintage_romance."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _highlights(img, threshold=0.5, knee=1.0):
    """Highlight-weighted copy of the image (H,W,3): 0 below threshold, ramping to full at white."""
    l = luminance(img)
    return smoothstep(threshold, knee, l)[..., None] * img


def _multi_bloom(img, threshold=0.5, sigmas=(12, 45, 110), weights=(0.35, 0.55, 0.4), tint_='#fff3dc'):
    """Multi-scale bloom layer (H,W,3) computed in linear light so bright sources dominate.
    Returns a layer meant to be screen-blended."""
    hi = _highlights(img, threshold)
    hi_lin = np.clip(hi, 0, 1) ** 2.2
    acc = np.zeros_like(img)
    for s, w in zip(sigmas, weights):
        acc += w * blur(hi_lin, s)
    acc = np.clip(acc, 0, 1) ** (1 / 2.2)
    return np.clip(acc * color(tint_), 0, 1)


def _skin_protect(layer, amount=0.35, feather_=12):
    """Reduce a light layer over the face so the skin never blows out to white."""
    f = mask('face_skin', feather=feather_)
    return layer * (1 - amount * f)[..., None]


def _crisp_features():
    """Mask of eyes, brows and lips (feathered) - used to keep them sharp under diffusion."""
    return np.clip(mask('eyes', feather=6, grow=6) + mask('lips', feather=6, grow=4) + mask('brows', feather=6, grow=3), 0, 1)


# ----------------------------------------------------------------------------- 051 soft_glow

@effect('soft_glow')
def soft_glow(img):
    """Soft dreamy glow: gentle bloom on skin and highlights, slightly softened detail."""
    out = orton(img, sigma=30, strength=0.45)
    # gentle bloom on the highlights
    out = glow(out, sigma=40, strength=0.4, threshold=0.55)
    # a whisper of extra bloom on the skin itself (romantic skin glow), kept from clipping
    face_light = blur(_highlights(out, 0.45) * mask('face', feather=16)[..., None], 28)
    out = blend(out, face_light * color('#fff1e4'), 'screen', 0.35)
    # slightly softened detail (diffusion filter look), eyes / brows / lips stay crisp
    soft = soft_focus(out, sigma=5, mix=0.4)
    out = apply_mask(soft, out, _crisp_features())
    out = brightness(out, 0.02)
    out = temperature(out, 0.06)
    out = vignette(out, strength=0.14, radius=1.0, softness=0.8, color_='#1a1014')
    return out


# ----------------------------------------------------------------------------- 052 dreamy_haze

@effect('dreamy_haze')
def dreamy_haze(img):
    """Dreamy haze: soft white mist, lowered contrast, glowing light, ethereal atmosphere."""
    out = img
    person = mask('person', feather=10)
    top = 1 - linear(90)                                   # 1 at top -> 0 at bottom
    cloud = 0.8 + 0.4 * fbm(4, seed=11, scale=0.6)         # gentle unevenness like real mist
    mist = (0.32 * top + 0.15) * cloud
    mist = mist * (1 - 0.3 * person)                       # subject stays a touch clearer (depth haze)
    mist = np.clip(mist, 0, 1)
    out = blend(out, '#fff6ec', 'screen', 1.0, mask_=mist)
    # lowered contrast + lifted blacks, but luminous whites
    out = contrast(out, 0.85, pivot=0.55)
    out = fade(out, 0.06, 0.0)
    out = levels(out, 0.0, 0.94)
    # glowing light: bloom + soft light pouring in from the sky (top-left)
    out = glow(out, sigma=50, strength=0.4, threshold=0.45)
    sky = radial(center=(W * 0.12, -H * 0.02), radius=1.0, softness=0.95)
    out = blend(out, sky[..., None] * color('#fff8ee'), 'screen', 0.5)
    out = temperature(out, 0.06)
    out = soft_focus(out, sigma=3, mix=0.2)
    return out


# ----------------------------------------------------------------------------- 053 bloom

@effect('bloom')
def bloom(img):
    """Strong highlight bloom: bright areas glow and spill soft light into their surroundings."""
    # lift the light sources first so they truly glow
    src = curve(img, [(0, 0), (0.45, 0.45), (0.72, 0.8), (1, 1)])
    layer = _multi_bloom(src, threshold=0.42, sigmas=(10, 40, 100, 200), weights=(0.5, 0.8, 0.7, 0.5), tint_='#fff0d0')
    layer = _skin_protect(layer, amount=0.35, feather_=14)
    out = blend(src, layer, 'screen', 0.9)
    # tight core glow right on the brightest pixels
    out = glow(out, sigma=15, strength=0.5, threshold=0.65)
    # keep the underlying detail crisp so it reads as bloom, not haze
    out = unsharp(out, radius=1.5, amount=0.3)
    out = s_curve(out, 0.06)
    return out


# ----------------------------------------------------------------------------- 054 rose_tint

@effect('rose_tint')
def rose_tint(img):
    """Delicate rose-pink tint over the whole image, warm and romantic."""
    out = fade(img, 0.03, 0.02)
    out = brightness(out, 0.05)
    out = temperature(out, 0.05)
    pre = out
    # rose veil weighted towards mids/highlights: sky, foliage and light go pink, the navy hijab
    # only takes a plum cast instead of turning grey or violet
    w = smoothstep(0.08, 0.45, luminance(out))
    out = lerp(out, tint(out, 0.20), 0.45 + 0.55 * w)     # magenta cast = the rose over the greens & sky
    out = hsl_adjust(out, 120, width=45, sat=0.85, shift=-8)
    tinted = blend(out, '#ffb0c8', 'soft_light', 0.55)
    tinted = blend(tinted, '#f0a0c0', 'color', 0.10)
    tinted = color_balance(tinted, midtones=(0.05, -0.02, 0.03), highlights=(0.06, -0.01, 0.03))
    out = lerp(out, tinted, 0.35 + 0.65 * w)
    # skin keeps a gentle natural rose (never magenta); teeth and eye whites stay clean
    skin = np.clip(mask('face_skin', feather=12, grow=6) + mask('seg_body_skin', feather=12, grow=4), 0, 1)
    natural = blend(pre, '#ffc0c8', 'soft_light', 0.35)
    natural = color_balance(natural, highlights=(0.04, 0.0, 0.02))
    out = lerp(out, natural, 0.6 * skin)
    clean = np.clip(mask('mouth', feather=3, grow=2) + mask('eyes', feather=3, grow=2), 0, 1)
    out = lerp(out, pre, 0.8 * clean)
    # romantic soft pink light from the top-right corner + gentle glow
    pink_light = radial(center=(W * 0.9, H * 0.05), radius=1.0, softness=0.95)
    out = blend(out, pink_light[..., None] * color('#ffc0d8'), 'screen', 0.4)
    out = glow(out, sigma=45, strength=0.2, threshold=0.6)
    return out


# ----------------------------------------------------------------------------- 055 vintage_romance

@effect('vintage_romance')
def vintage_romance(img):
    """Vintage romantic film: warm faded tones, soft glow, gentle vignette, nostalgic."""
    out = exposure(img, 0.12)
    out = fade(out, 0.14, 0.05)
    out = saturation(out, 0.85)
    out = temperature(out, 0.16)
    out = split_tone(out, shadows='#5a3040', highlights='#ffd6b8', strength=0.45)
    out = orton(out, sigma=30, strength=0.3)
    out = light_leak(out, '#ffb070', side='right', strength=0.22, seed=3, size=0.5)
    out = vignette(out, strength=0.3, radius=1.05, softness=0.75, color_='#2a1418')
    out = grain(out, amount=0.04, size=1.4, seed=5)
    return out
