"""Group g09 — Colour grading: warm_tone, cool_tone, pastel, vibrant, muted."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _hue_weight(hsv, center, width, min_sat=0.08):
    """(H,W) weight 1 near `center` hue (deg), fading to 0 at +-width; ignores near-grey pixels."""
    d = np.abs(((hsv[..., 0] - center + 180.0) % 360.0) - 180.0)
    return smoothstep(width, width * 0.4, d) * smoothstep(0.0, min_sat * 3, hsv[..., 1])


def _hue_remap(img, center, width, target, sat=1.0, lum=0.0, min_sat=0.08):
    """Pull hues near `center` toward `target` (shortest path), with sat multiplier / lum offset."""
    hsv = rgb2hsv(img)
    w = _hue_weight(hsv, center, width, min_sat)
    delta = ((target - hsv[..., 0] + 180.0) % 360.0) - 180.0
    hsv[..., 0] = (hsv[..., 0] + delta * w) % 360.0
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + (sat - 1) * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] + lum * w, 0, 1)
    return hsv2rgb(hsv)


def _skin_protect(graded, reference, keep=0.5, feather_=8, color_only=False):
    """Pull the face skin `keep` of the way back toward `reference` (feathered face_skin mask).
    color_only: take only the reference's colour, keeping the graded luminance (tonality of the grade stays)."""
    m = mask('face_skin', feather=feather_)
    ref = blend(graded, reference, 'color') if color_only else reference
    return apply_mask(graded, lerp(graded, ref, keep), m)


def _skin_recolor(graded, reference, mix=0.85, feather_=8):
    """Face skin takes hue+saturation from `reference` and keeps the graded luminance (HSV V);
    `mix` blends that recoloured skin over the graded skin."""
    m = mask('face_skin', feather=feather_)
    hv = rgb2hsv(reference)
    hv[..., 2] = rgb2hsv(graded)[..., 2]
    return apply_mask(graded, lerp(graded, hsv2rgb(hv), mix), m)


# ----------------------------------------------------------------------------- 041 warm_tone

@effect('warm_tone')
def warm_tone(img):
    """Cosy warm grade: golden highlights, soft brown shadows, gentle warmth on the skin."""
    src = levels(img, 0.0, 1.0, gamma_=1.10)                                          # slight lift so the gold glows
    out = temperature(src, 0.28)
    out = hsl_adjust(out, hue=75, width=45, sat=1.05, lum=0.03, shift=-12)          # foliage -> golden
    out = split_tone(out, shadows='#5a3a26', highlights='#ffd9a0', strength=0.38)
    out = color_balance(out, shadows=(0.03, 0.01, -0.02), highlights=(0.03, 0.01, -0.03))
    out = vibrance(out, 0.12)
    out = s_curve(out, 0.05)
    out = glow(out, sigma=45, strength=0.22, threshold=0.60)                          # soft golden bloom
    out = vignette(out, strength=0.18, radius=1.0, softness=0.75, color_='#2a1a10')
    out = _skin_recolor(out, temperature(src, 0.08), mix=0.85)                       # gentle warmth, no orange
    return out


# ----------------------------------------------------------------------------- 042 cool_tone

@effect('cool_tone')
def cool_tone(img):
    """Clean cool grade: blue-tinted shadows, silvery highlights, modern calm."""
    src = levels(img, 0.0, 1.0, gamma_=1.08)
    out = temperature(src, -0.28)
    out = hsl_adjust(out, hue=75, width=45, sat=0.85, shift=22)                       # foliage -> cool teal-green
    out = split_tone(out, shadows='#1a3050', highlights='#dfeeff', strength=0.40)
    out = saturation(out, 0.90)
    # silvery highlights: desaturate the top tones and tint them faintly cool
    l = luminance(out)
    wh = smoothstep(0.55, 0.95, l)
    silver = lerp(out, gray(out) * np.array([0.97, 0.99, 1.03], np.float32), 0.45)
    out = clip(lerp(out, silver, wh))
    out = color_balance(out, shadows=(-0.03, -0.01, 0.05), highlights=(0.0, 0.01, 0.03))
    out = s_curve(out, 0.06)
    out = fade(out, 0.03, 0.0)                                                        # keep hijab folds out of pure black
    out = _skin_protect(out, src, keep=0.72, color_only=True)                         # natural skin colour, cool tonality
    return out


# ----------------------------------------------------------------------------- 043 pastel

@effect('pastel')
def pastel(img):
    """Soft pastel: light pink and mint tints, lifted shadows, low contrast, dreamy."""
    lifted = fade(levels(img, 0.0, 1.0, gamma_=1.25), 0.10, 0.04)                    # tonal lift, no colour
    out = contrast(lifted, 0.87, pivot=0.58)
    out = saturation(out, 0.92)
    out = _hue_remap(out, center=72, width=48, target=150, sat=1.30, lum=0.06)      # yellow-greens -> mint
    out = hsl_adjust(out, hue=205, width=30, sat=0.8, lum=0.10)                      # sky -> baby blue
    out = hsl_adjust(out, hue=240, width=35, sat=0.7, lum=0.08, shift=10)           # navy -> dusty lavender
    out = hsl_adjust(out, hue=0, width=18, sat=0.75, lum=0.08, min_sat=0.2)         # red sleeve -> rose
    out = split_tone(out, shadows='#c0b4d4', highlights='#ffd8e4', strength=0.42)   # lavender-grey / pink
    out = color_balance(out, shadows=(0.0, 0.0, 0.015), midtones=(0.02, 0.0, 0.015), highlights=(0.05, -0.005, 0.02))
    out = glow(out, sigma=40, strength=0.22, threshold=0.5)                          # dreamy bloom
    haze = 1 - radial(radius=1.1, softness=0.9)
    out = blend(out, '#f9d3e0', 'screen', 0.14, mask_=haze)                          # faint pink haze at the edges
    out = _skin_protect(out, lifted, keep=0.55)
    return out


# ----------------------------------------------------------------------------- 044 vibrant

@effect('vibrant')
def vibrant(img):
    """Punchy summer grade: boosted saturation, clarity and contrast; skin gets half the gain."""
    out = levels(img, 0.0, 1.0, gamma_=1.10)
    out = curve(out, [(0, 0.008), (0.05, 0.048), (0.25, 0.235), (0.5, 0.52), (0.75, 0.79), (0.95, 0.96), (1, 1)])
    out = clarity(out, 0.22, radius=40)
    out = temperature(out, 0.06)
    full = saturation(vibrance(out, 0.55), 1.05)
    full = hsl_adjust(full, hue=80, width=50, sat=1.15, lum=0.02, shift=6)          # greens fresher / punchier
    full = hsl_adjust(full, hue=210, width=35, sat=1.08, lum=0.02)                   # sky richer, navy keeps detail
    half = vibrance(out, 0.12)
    out = apply_mask(full, half, mask('face_skin', feather=8))
    out = sharpen(out, 0.25)
    return out


# ----------------------------------------------------------------------------- 045 muted

@effect('muted')
def muted(img):
    """Quiet-luxury mute: low saturation, soft contrast, warm brownish shadows."""
    src = levels(img, 0.0, 1.0, gamma_=1.12)
    out = saturation(src, 0.58)
    out = contrast(out, 0.92, pivot=0.5)
    out = fade(out, 0.07, 0.05)
    out = split_tone(out, shadows='#3a2a22', highlights='#e8dcc8', strength=0.35)
    out = color_balance(out, shadows=(0.035, 0.015, -0.02), midtones=(0.012, 0.004, -0.008))
    out = temperature(out, 0.05)
    out = hsl_adjust(out, hue=52, width=32, sat=0.85, lum=0.01, shift=16)            # khaki foliage -> soft sage
    out = vignette(out, strength=0.12, radius=1.05, softness=0.8, color_='#2a1c14')
    out = grain(out, 0.02, size=1.2, seed=9)
    out = _skin_protect(out, src, keep=0.40)
    return out
