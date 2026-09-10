"""Group g04 — Plyonka & Vintage (Film & Vintage).

Codes: faded_film, cinestill, sepia, old_photo, light_leak.
Note: `sepia` and `light_leak` shadow the lib helpers of the same name inside this
module, so the helpers are called through the module alias `L`.
"""
from effects.lib import *
from effects import lib as L
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _skin(feather_=6):
    """Face + body skin, feathered."""
    return np.clip(mask('face_skin', feather_) + mask('seg_body_skin', feather_), 0, 1)


def _blob(center, size, seed=0, power=1.5):
    """Soft organic light blob mask (H,W): centre in px, size=(rx, ry) in px, fbm-modulated."""
    x, y = coords()
    cx, cy = center
    rx, ry = size
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    m = (1 - smoothstep(0.0, 1.0, d)) ** power
    return (m * (0.8 + 0.4 * fbm(4, seed, 0.5))).astype(np.float32)


# ----------------------------------------------------------------------------- #016 faded film

@effect('faded_film')
def faded_film(img):
    """Matte faded film: milky lifted blacks, softened whites, pastel muted colours, gentle warmth."""
    out = fade(img, amount=0.18, highlight=0.07)            # lifted milky blacks, softened whites
    out = contrast(out, 0.93)                                # flatter, matte
    out = lerp(saturation(out, 0.70), saturation(out, 0.86), _skin(8))  # pastel, muted colours; skin keeps some life
    out = temperature(out, 0.08)                             # gentle warmth
    out = split_tone(out, shadows='#6e566a', highlights='#fff1dc', strength=0.28)  # mauve shadows, cream lights
    out = color_balance(out, shadows=(0.03, 0.0, 0.015))     # a touch of rose in the shadows
    out = glow(out, sigma=35, strength=0.15, threshold=0.7)  # soft, dreamy highlights
    out = grain(out, 0.04, size=1.3, seed=16)
    return out


# ----------------------------------------------------------------------------- #017 CineStill 800T

@effect('cinestill')
def cinestill(img):
    """CineStill 800T: tungsten-balanced cool tones, warm highlights, red-orange halation, night feel."""
    fc = face_center()
    l0 = luminance(img)
    face_m = mask('face', 12)
    # 1. night exposure: background drops a stop; the face keeps its light (street-lamp / flash feel)
    dark = exposure(img, -1.0)
    lit = exposure(img, -0.15)
    spot = radial(center=(fc[0], fc[1] + 80), radius=0.85, softness=0.75)
    out = lerp(dark, lit, np.clip(spot + 0.4 * face_m, 0, 1))
    # 2. tungsten balance: cool cast, greens drift to cyan, teal shadows / warm highlights
    out = temperature(out, -0.32)
    out = hsl_adjust(out, 100, width=55, sat=0.75, shift=35)
    out = split_tone(out, shadows='#16233f', highlights='#ffd9a0', strength=0.45)
    out = contrast(out, 1.08)
    # 3. skin: bring most of the warmth back so the face reads healthy under the cool grade
    out = lerp(out, temperature(out, 0.28), _skin(8) * 0.65)
    out = vignette(out, 0.35, radius=1.0, softness=0.8, color_='#040914')
    # 4. bright highlights stay blown as warm 'lamps' and bloom red-orange halation (damped on the face)
    core = smoothstep(0.64, 0.92, l0) * (1 - 0.85 * face_m)
    halo = np.clip(blur(core, 55) * 2.4, 0, 1)
    out = lerp(out, as_layer('#ff4a1a'), halo * 0.55)          # pull the hue to red-orange even over blue sky
    out = blend(out, halo[..., None] * color('#ff3b1f'), 'screen', 0.85)
    out = blend(out, np.clip(blur(core, 18) * 1.3, 0, 1)[..., None] * color('#ff7a30'), 'screen', 0.75)
    out = blend(out, blur(core, 2)[..., None] * color('#fff1d2'), 'screen', 0.9)   # cores stay warm white
    # 5. film finish
    out = grain(out, 0.05, size=1.3, seed=17)
    return out


# ----------------------------------------------------------------------------- #018 sepia

@effect('sepia')
def sepia(img):
    """Classic sepia: warm brown monochrome, soft contrast, gentle vignette."""
    out = s_curve(img, 0.12)
    out = gradient_map(out, [(0.0, '#241609'), (0.25, '#573c22'), (0.5, '#a37d4f'),
                             (0.75, '#dabf95'), (1.0, '#f7ecd6')], 1.0)
    out = fade(out, 0.05, 0.03)
    out = glow(out, sigma=30, strength=0.12, threshold=0.7)
    out = vignette(out, 0.3, radius=1.05, softness=0.85, color_='#1a0e06')
    out = grain(out, 0.04, size=1.2, seed=18)
    return out


# ----------------------------------------------------------------------------- #019 old photo

@effect('old_photo')
def old_photo(img):
    """Decades-old print: yellowed faded tones, paper texture, stains, scratches, dust, worn soft corners."""
    face_m = mask('face', 15)
    corner = 1 - radial(radius=1.2, softness=0.65)
    # faded, yellowed low-contrast print
    out = soft_focus(img, 8, 0.3)
    out = gradient_map(out, [(0.0, '#3a2a18'), (0.25, '#705838'), (0.5, '#b39a66'),
                             (0.75, '#dccb98'), (1.0, '#f6efd0')], 1.0)
    out = s_curve(out, 0.06)
    out = color_balance(out, highlights=(0.02, 0.01, -0.06))              # yellowed paper whites
    out = lerp(out, blur(out, 6), corner * 0.8)                           # worn soft corners
    out = clip(out * paper(seed=3, strength=0.3)[..., None])              # paper texture
    # uneven yellowing, brown stains and cream fog at the corners
    out = blend(out, '#d9ad55', 'multiply', 0.3, smoothstep(0.35, 0.8, fbm(3, seed=19, scale=0.45)))
    stain = np.clip(corner * 0.8 + 0.25, 0, 1) * smoothstep(0.45, 0.8, fbm(4, seed=29, scale=0.55))
    out = blend(out, '#6a4a22', 'multiply', 0.5, stain)
    fog = corner * smoothstep(0.4, 0.85, fbm(4, seed=23, scale=0.45))
    out = blend(out, '#f4e8c8', 'screen', 0.7, fog)
    # scratches (lighter over the face) and dust
    sc = scratches(18, seed=4, length=(180, 800), thickness=(1, 2), vertical=True)
    sc = np.maximum(sc, scratches(6, seed=8, length=(150, 500), thickness=(1, 2), vertical=False))
    out = blend(out, '#fff6e0', 'screen', 0.5, sc * (1 - 0.6 * face_m))
    out = blend(out, '#3a2810', 'multiply', 0.35, scratches(5, seed=12, length=(120, 400), thickness=(1, 1), vertical=False))
    out = blend(out, '#fff8ea', 'screen', 0.5, dust(500, seed=5, size=(1, 4)))
    out = blend(out, '#2a1a08', 'multiply', 0.4, dust(150, seed=6, size=(1, 3)))
    out = vignette(out, 0.4, radius=1.05, softness=0.9, color_='#4a3618')
    out = fade(out, 0.06, 0.02)
    out = grain(out, 0.06, size=1.6, seed=7)
    return out


# ----------------------------------------------------------------------------- #020 light leak

@effect('light_leak')
def light_leak(img):
    """Analog light leak: orange-red light bleeding in from the right edge, faded film colours."""
    out = fade(img, 0.1, 0.03)
    out = saturation(out, 0.95)
    out = temperature(out, 0.06)
    x, y = coords()
    # main leak: broad orange glow bleeding from the right edge, hottest at the top-right corner
    main = _blob((W * 1.12, H * 0.42), (W * 0.62, H * 0.75), seed=20)
    out = blend(out, main[..., None] * color('#ff6a2a'), 'screen', 0.85)
    hot = _blob((W * 1.05, H * 0.05), (W * 0.55, H * 0.5), seed=25)
    out = blend(out, hot[..., None] * color('#ffb347'), 'screen', 0.5)
    # hot saturated red rim right at the edge
    rim = smoothstep(W * 0.7, W * 1.02, x) ** 1.8 * (0.8 + 0.2 * fbm(4, 21, 0.6))
    out = blend(out, rim[..., None] * color('#ff2a10'), 'screen', 0.75)
    # thin yellow-white burn at the very edge
    streak = smoothstep(W * 0.93, W * 1.0, x) ** 2
    out = blend(out, streak[..., None] * color('#ffd08a'), 'screen', 0.5)
    # secondary, smaller pink leak top-left
    pink = _blob((-W * 0.08, -H * 0.02), (W * 0.5, H * 0.45), seed=22)
    out = blend(out, pink[..., None] * color('#ff9ac0'), 'screen', 0.45)
    out = grain(out, 0.04, size=1.3, seed=24)
    return out
