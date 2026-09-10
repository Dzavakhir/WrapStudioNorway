"""Group g05 — Kinematik (Cinematic): teal_orange, noir, moody, widescreen, blockbuster."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _skin_mask(feather_=8):
    """Feathered face-skin mask (the body-skin mask is empty for this portrait)."""
    return np.clip(mask('face_skin', feather=feather_), 0, 1)


def _hue_compress(img, center, plateau, falloff, target, k=0.8, sat=1.0, lum=0.0, mask_=None, min_sat=0.1):
    """Pull hues within +-plateau (soft edge of `falloff`) of `center` toward `target` hue by factor k.
    target may be a scalar or an (H,W) array (e.g. luminance-dependent)."""
    hsv = rgb2hsv(img)
    h = hsv[..., 0]
    d = np.abs(((h - center + 180.0) % 360.0) - 180.0)
    w = (1 - smoothstep(plateau, plateau + falloff, d)) * smoothstep(0.0, min_sat * 3, hsv[..., 1])
    if mask_ is not None:
        w = w * mask_
    delta = ((np.asarray(target, np.float32) - h + 180.0) % 360.0) - 180.0
    hsv[..., 0] = (h + k * delta * w) % 360.0
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + (sat - 1) * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] + lum * w, 0, 1)
    return hsv2rgb(hsv)


# ----------------------------------------------------------------------------- 021 teal_orange

@effect('teal_orange')
def teal_orange(img):
    bg = mask('background', feather=3)
    skin = _skin_mask(8)
    lum = blur(luminance(img), 6)

    # foliage: dark leaves -> teal, sunlit leaves -> olive-gold (classic luminance split)
    target = np.interp(lum, [0.18, 0.62], [178.0, 62.0]).astype(np.float32)
    out = _hue_compress(img, center=65, plateau=40, falloff=25, target=target, k=0.82, sat=0.78, lum=-0.02, mask_=bg)
    # sky patch + navy hijab -> teal
    out = _hue_compress(out, center=225, plateau=35, falloff=25, target=187.0, k=0.85, sat=1.25, lum=0.02)
    # skin -> orange side, a touch richer
    out = _hue_compress(out, center=15, plateau=20, falloff=15, target=26.0, k=0.6, sat=1.04, mask_=skin)

    # global Hollywood split: teal shadows, orange highlights
    graded = split_tone(out, shadows='#0f4d5c', highlights='#ff9b45', balance=-0.05, strength=0.58)
    graded = color_balance(graded, shadows=(-0.04, 0.012, 0.05), highlights=(0.03, 0.0, -0.03))
    # skin protect: 30% less of the split on the face
    out = lerp(graded, lerp(out, graded, 0.7), skin)

    out = s_curve(out, 0.17)
    out = clarity(out, 0.15, 40)
    out = vibrance(out, 0.12)
    out = vignette(out, 0.22, color_='#06262e')
    return out


# ----------------------------------------------------------------------------- 022 noir

@effect('noir')
def noir(img):
    fc = face_center()
    out = bw(img, 0.40, 0.50, 0.10)               # red-weighted: luminous skin, dark sky/foliage
    out = levels(out, black=0.03)
    # contrast with a soft highlight shoulder so skin keeps its gradation
    out = curve(out, [(0, 0), (0.22, 0.15), (0.5, 0.55), (0.82, 0.87), (1, 0.955)])

    # key light: one spot on the face, the rest falls off into grey-black
    key = radial(center=(fc[0], fc[1] - 40), radius=1.1, softness=0.8, aspect=0.9)
    out = clip(out * (0.55 + 0.45 * key)[..., None])

    # dramatic diagonal shadow across the bottom-left (sleeve / lower hijab), softly hard edge
    band = linear(135, 0.695, 0.735)
    out = blend(out, '#000000', 'normal', 0.55, mask_=band)
    # a fainter slash from the top-right so the light reads as one hard source
    band2 = 1 - linear(135, 0.12, 0.20)
    out = blend(out, '#000000', 'normal', 0.3, mask_=band2)

    out = glow(out, sigma=26, strength=0.14, threshold=0.75)    # silver-screen diffusion
    out = vignette(out, 0.45, radius=1.0, softness=0.75)
    out = grain(out, 0.06, size=1.3, seed=5)
    return out


# ----------------------------------------------------------------------------- 023 moody

@effect('moody')
def moody(img):
    bg = mask('background', feather=4)
    skin = _skin_mask(8)
    fc = face_center()

    out = exposure(img, -0.42)
    # greens: desaturate, darken, nudge toward teal (world only)
    world = _hue_compress(out, center=70, plateau=40, falloff=25, target=155.0, k=0.4, sat=0.6, lum=-0.07)
    world = saturation(world, 0.6)
    face = saturation(out, 0.82)                       # skin keeps a little life
    out = lerp(world, face, skin)

    out = split_tone(out, shadows='#153d38', highlights='#c9b8a0', strength=0.55)
    out = color_balance(out, shadows=(-0.03, 0.02, 0.02), midtones=(-0.01, 0.0, 0.0))
    out = fade(out, 0.07, 0.05)
    out = clarity(out, 0.14, 40)

    # atmosphere: soft teal-grey mist in the background, denser toward the top (distance)
    mist = fbm(5, seed=23, scale=0.7)
    mist_m = bg * (0.35 + 0.65 * linear(270, 0.15, 0.95)) * (0.6 + 0.4 * mist)   # linear(270) = bottom->top
    out = blend(out, '#5f7a76', 'screen', 0.24, mask_=mist_m)
    # keep the face readable: gentle lift on the subject
    out = blend(out, '#ffffff', 'soft_light', 0.3, mask_=radial(center=fc, radius=0.62, softness=0.8, aspect=0.85))

    out = vignette(out, 0.45, radius=0.98, softness=0.75, color_='#050a0a')
    out = grain(out, 0.035, size=1.4, seed=23)
    return out


# ----------------------------------------------------------------------------- 024 widescreen

@effect('widescreen')
def widescreen(img):
    out = split_tone(img, shadows='#1d3a4a', highlights='#f0b070', strength=0.42)
    out = color_balance(out, shadows=(-0.025, 0.0, 0.03))
    out = s_curve(out, 0.13)
    out = fade(out, 0.035, 0.02)
    out = saturation(out, 0.92)
    out = clarity(out, 0.1, 40)
    out = vignette(out, 0.22, radius=1.0, softness=0.75)
    out = grain(out, 0.05, size=1.2, seed=24)

    ratio = 1.2
    out = letterbox(out, ratio=ratio, color_='#000000')
    pad = (H - int(W / ratio)) // 2
    f = font('lato', 36)
    out = draw_text(out, "— bu yerda hikoya boshlanadi", (W / 2, H - pad - 46), f, '#f6f1e6', anchor='mm', tracking=1.0, opacity=0.96, shadow=(0, 2, 5, '#000000', 0.75))
    return out


# ----------------------------------------------------------------------------- 025 blockbuster

@effect('blockbuster')
def blockbuster(img):
    skin = _skin_mask(12)
    features = np.clip(mask('face', feather=3) - mask('face_skin', feather=3), 0, 1)   # eyes, brows, lips
    bg = mask('background', feather=3)

    # crisp detail (edge-preserving, no halos): moderate off the face, very light on skin
    de = detail_enhance(img, sigma_s=10, sigma_r=0.15)
    out = lerp(lerp(img, de, 0.38), lerp(img, de, 0.08), skin)
    out = lerp(clarity(out, 0.12, 80), out, skin)             # local contrast for the world only (no rim on the face)
    world_tone = levels(s_curve(out, 0.26), black=0.045, white=0.99)
    skin_tone = levels(s_curve(out, 0.15), black=0.02, white=0.99)     # softer contrast on the face
    out = lerp(world_tone, skin_tone, skin)

    # cool, steel-blue world: shadows deep navy, highlights icy
    cool = split_tone(out, shadows='#14283d', highlights='#c4d6e8', balance=-0.05, strength=0.42)
    cool = temperature(cool, -0.14)
    cool = color_balance(cool, highlights=(-0.03, 0.0, 0.05))
    cool = _hue_compress(cool, center=70, plateau=40, falloff=25, target=140.0, k=0.4, sat=0.58, lum=-0.05, mask_=bg)
    cool = _hue_compress(cool, center=230, plateau=30, falloff=20, target=225.0, k=0.3, sat=0.85)   # navy stays navy, not violet
    cool = saturation(cool, 0.92)

    # warm skin, kept separate from the cold grade; tame the reds toward a clean golden warmth
    warm = blend(blur(out, 7), out, 'luminosity', 0.75)         # chroma smoothing: keeps detail, removes red blotches
    warm = _hue_compress(warm, center=0, plateau=22, falloff=15, target=22.0, k=0.5, sat=0.82)
    warm = split_tone(warm, shadows='#3a2a20', highlights='#ffd0a8', strength=0.28)
    warm = temperature(warm, 0.07)
    out = lerp(cool, warm, skin)

    sharp = unsharp(out, 1.0, 0.45, threshold=0.004)
    out = lerp(sharp, lerp(out, sharp, 0.2), skin)          # full sharpening on the world, gentle on skin
    out = lerp(out, sharp, features)                         # eyes, brows, lips fully crisp
    out = grain(out, 0.03, seed=25)
    out = vignette(out, 0.24, radius=1.0, softness=0.7, color_='#040810')
    return out
