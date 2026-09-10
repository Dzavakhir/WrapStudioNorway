"""Group g08 - Oq-qora (Black & White): silver, bw_matte, bw_glow, bw_infrared, bw_warm."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- helpers

def _hue_weight(h, center, width):
    """1 near `center` hue (deg), fading to 0 at +-width."""
    d = np.abs(((h - center + 180.0) % 360.0) - 180.0)
    return smoothstep(width, width * 0.35, d)


def _shoulder(x, knee=0.78):
    """Soft highlight roll-off: linear below `knee`, asymptotic to 1.0 above it (no hard clipping)."""
    over = np.maximum(x - knee, 0.0)
    return np.where(x > knee, knee + (1.0 - knee) * (1.0 - np.exp(-over / (1.0 - knee))), x)


def _mono(l):
    """(H,W) luminance -> (H,W,3) grey image."""
    return np.repeat(np.clip(l, 0, 1)[..., None].astype(np.float32), 3, axis=2)


# Print curve for the classic looks: open toe (the navy hijab keeps its folds), luminous mids,
# highlights stretched to paper white.
_PRINT_CURVE = [(0.0, 0.0), (0.05, 0.055), (0.16, 0.19), (0.35, 0.41), (0.55, 0.63), (0.8, 0.88), (0.92, 0.97), (1.0, 1.0)]


# ----------------------------------------------------------------------------- #036 silver

@effect('silver')
def silver(img):
    """Silver-gelatin print: cool silvery tones, rich midtones, paper-white highlights, deep detailed blacks."""
    g = bw(img, 0.34, 0.55, 0.11)                       # panchromatic, slightly red-weighted (luminous skin)
    g = curve(g, _PRINT_CURVE)
    g = clarity(g, 0.15, radius=60)                      # 'rich midtones': micro-contrast of a glossy print
    # cold-tone paper: luminance-matched blue-grey stops (tone changes, tonal values stay)
    g = gradient_map(g, [(0.0, '#0c1119'), (0.3, '#3f4b5b'), (0.65, '#9ea9b8'), (1.0, '#f6f8fc')], strength=0.75)
    g = grain(g, 0.025, size=1.0, seed=36)               # very fine silver grain
    return g


# ----------------------------------------------------------------------------- #037 bw_matte

@effect('bw_matte')
def bw_matte(img):
    """Matte B&W: lifted, faded blacks, softened whites, neutral modern editorial feel."""
    g = bw(img, 0.32, 0.57, 0.11)
    g = clarity(g, 0.12, radius=50)                      # editorial structure so the flat tone is not muddy
    # lifted blacks (0.17), softened whites (0.93), gentle S in the mids
    g = curve(g, [(0.0, 0.17), (0.2, 0.30), (0.5, 0.58), (0.8, 0.80), (1.0, 0.93)])
    g = grain(g, 0.03, size=1.15, seed=37)
    return g


# ----------------------------------------------------------------------------- #038 bw_glow

@effect('bw_glow')
def bw_glow(img):
    """Glowing high-key B&W: bright airy tones with a soft bloom bleeding from the highlights."""
    g = bw(img, 0.38, 0.52, 0.10)
    # high-key curve: lift everything, especially the mids/upper mids, keep a soft toe
    g = curve(g, [(0.0, 0.08), (0.2, 0.35), (0.5, 0.72), (0.75, 0.88), (1.0, 1.0)])
    bloom = glow(g, sigma=60, strength=0.8, threshold=0.55)   # wide bloom from the highlights
    face = mask('face_skin', feather=12)
    g = lerp(bloom, g, 0.4 * face)                       # keep 60 % of the bloom on the face (skin texture survives)
    g = orton(g, sigma=25, strength=0.25)                # dreamy softness
    g = contrast(g, 0.95, pivot=0.6)
    g = grain(g, 0.02, seed=38)
    return g


# ----------------------------------------------------------------------------- #039 bw_infrared

@effect('bw_infrared')
def bw_infrared(img):
    """Infrared B&W: foliage renders bright white, blue sky goes dark, skin turns milky and luminous."""
    hsv = rgb2hsv(img)
    h, s = hsv[..., 0], hsv[..., 1]
    bg = mask('background', feather=2)
    sat_w = smoothstep(0.08, 0.30, s)

    w_veg = _hue_weight(h, 65.0, 65.0) * sat_w * bg               # yellow-green vegetation (background only)
    w_sky = _hue_weight(h, 215.0, 45.0) * smoothstep(0.10, 0.30, s) * bg   # blue sky
    clothes = mask('seg_clothes', feather=3)
    w_red = _hue_weight(h, 0.0, 25.0) * smoothstep(0.25, 0.60, s) * clothes  # red sleeve: light in IR (lips excluded)
    w_skin = np.clip(mask('face_skin', feather=2) + mask('seg_body_skin', feather=2), 0, 1)

    # IR-ish luminance: chlorophyll reflects strongly -> big multiplicative gain (keeps leaf texture),
    # sky absorbs -> strong darkening, red dye reflects -> lighter, skin slightly luminous.
    l = bw(img, 0.25, 0.62, 0.13)[..., 0]
    gain = 1.0 + 1.9 * w_veg - 0.8 * w_sky + 2.0 * w_red + 0.12 * w_skin
    l = _shoulder(l * gain, knee=0.78)
    g = _mono(l)

    # porcelain skin: smooth, then soft halo (Kodak HIE style bloom)
    g = skin_smooth(g, strength=0.4, mask_=w_skin, radius=12, keep_texture=0.5)
    g = s_curve(g, 0.08)
    g = glow(g, sigma=35, strength=0.4, threshold=0.62)
    g = grain(g, 0.045, size=1.1, seed=39)
    return g


# ----------------------------------------------------------------------------- #040 bw_warm

@effect('bw_warm')
def bw_warm(img):
    """Warm-toned B&W: selenium / brown print tone, deep brown-black shadows, creamy highlights, soft vignette."""
    g = bw(img, 0.36, 0.54, 0.10)
    g = curve(g, _PRINT_CURVE)
    g = clarity(g, 0.10, radius=60)
    # brown tone curve with luminance-matched stops (tone changes, tonal values stay)
    g = gradient_map(g, [(0.0, '#120c09'), (0.28, '#5a4335'), (0.62, '#b39d86'), (1.0, '#fbf3e6')], strength=0.85)
    g = vignette(g, strength=0.18, radius=1.0, softness=0.75, color_='#120c09')
    g = grain(g, 0.03, size=1.0, seed=40)
    return g
