"""Group 12 — Romantik (Romantic): pearl, angelic, love_letter, whisper, blush."""
import math
import numpy as np
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _skin_mask(feather_=5):
    """Face skin + visible body skin (eyes, brows, lips excluded), feathered."""
    return np.clip(mask('face_skin', feather=feather_) + mask('seg_body_skin', feather=feather_), 0, 1)


def _blob(center, rx, ry, angle=0.0, power=1.4):
    """Soft oriented elliptical blob (H, W) in [0, 1]: 1 at the centre, 0 at the ellipse boundary."""
    x, y = coords()
    a = math.radians(angle)
    dx, dy = x - center[0], y - center[1]
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    d = np.sqrt((u / rx) ** 2 + (v / ry) ** 2)
    return ((1 - smoothstep(0.0, 1.0, d)) ** power).astype(np.float32)


def _face_axes():
    """(down, across) unit vectors of the tilted face + eye/mouth landmarks."""
    m = meta()
    el, er = np.array(m['eye_l'], np.float32), np.array(m['eye_r'], np.float32)
    fh, ch = np.array(m['forehead'], np.float32), np.array(m['chin'], np.float32)
    down = ch - fh
    down /= np.linalg.norm(down)
    across = er - el
    across /= np.linalg.norm(across)
    return down, across, el, er


def _crease(img, pos, horizontal=True, strength=0.1):
    """Faint fold crease of an old folded paper: a light ridge with a soft shadow beside it."""
    x, y = coords()
    t = (y if horizontal else x) - pos
    # slight waviness so it does not read as a ruler line
    wave = 3.0 * np.sin((x if horizontal else y) / (W if horizontal else H) * math.pi * 1.7)
    t = t + wave
    light = np.exp(-(t / 1.4) ** 2) * strength
    dark = np.exp(-((t - 3.5) / 3.0) ** 2) * strength * 0.8
    out = clip(img + light[..., None] * (1 - img))
    return clip(out * (1 - dark[..., None]))


def _flourishes(d, inset_=30, size=150, col=None):
    """Delicate faded-ink corner ornaments (double rule + tiny curls) on a letter sheet."""
    col = col or rgba('#6b4636', 0.55)
    col2 = rgba('#6b4636', 0.35)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x0 = inset_ if sx > 0 else W - 1 - inset_
        y0 = inset_ if sy > 0 else H - 1 - inset_
        ex, ey = x0 + sx * size, y0 + sy * size
        d.line([(x0, y0), (ex, y0)], fill=col, width=2)
        d.line([(x0, y0), (x0, ey)], fill=col, width=2)
        # thin inner rule
        o = 7
        d.line([(x0 + sx * o, y0 + sy * o), (ex - sx * 18, y0 + sy * o)], fill=col2, width=1)
        d.line([(x0 + sx * o, y0 + sy * o), (x0 + sx * o, ey - sy * 18)], fill=col2, width=1)
        # tiny curls at the ends of the outer rule
        r = 7
        d.ellipse((ex - r, y0 - r + sy * r, ex + r, y0 + r + sy * r), outline=col, width=2)
        d.ellipse((x0 - r + sx * r, ey - r, x0 + r + sx * r, ey + r), outline=col, width=2)
        # small diamond in the corner
        k = 6
        d.polygon([(x0, y0 - k), (x0 + k, y0), (x0, y0 + k), (x0 - k, y0)], fill=col)


# ----------------------------------------------------------------------------- 056 pearl

@effect('pearl')
def pearl(img):
    """Pearly, luminous skin: refined texture, lifted soft highlights, cool-white nacre sheen on the high points."""
    skin = _skin_mask(5)
    # refined texture (frequency-separation smoothing; pores and freckles stay)
    out = skin_smooth(img, strength=0.45, mask_=skin, radius=14, keep_texture=0.45)
    # brighten the skin: gentle lifting curve, modelling preserved
    lifted = curve(out, [(0, 0), (0.25, 0.262), (0.5, 0.528), (0.8, 0.85), (1, 1)])
    out = apply_mask(out, lifted, skin)
    # nacre sheen only on the high points (forehead, nose bridge, cheekbones, chin): soft cool-white glow
    l = blur(luminance(out), 3)
    hi = blur(smoothstep(0.58, 0.85, l) * skin, 10) * skin
    hi_top = blur(smoothstep(0.72, 0.94, l) * skin, 5) * skin
    out = blend(out, hi[..., None] * color('#eef2fc'), 'screen', 0.6)
    out = blend(out, hi_top[..., None] * color('#e6efff'), 'screen', 0.5)
    # pearl split tone on skin: cool-white highlights, shadows kept neutral-rose so the skin never goes grey
    toned = split_tone(out, shadows='#5c4c55', highlights='#f4f6ff', balance=0.05, strength=0.28)
    out = apply_mask(out, toned, skin)
    # overall luminosity: bloom, calmer colour, surroundings a touch darker so the skin glows
    out = glow(out, sigma=35, strength=0.3, threshold=0.6)
    out = saturation(out, 0.93)
    out = temperature(out, -0.03)
    out = vignette(out, strength=0.24, radius=1.0, softness=0.8, center=face_center())
    return out


# ----------------------------------------------------------------------------- 057 angelic

@effect('angelic')
def angelic(img):
    """Ethereal high-key portrait: airy light, a soft white halo of light behind the head, glowing highlights."""
    fx, fy = face_center()
    person = mask('person')
    person_soft = feather(person, 2.5)
    bgm = 1 - person_soft
    # airy base: lifted blacks, brighter, calmer colour
    out = fade(img, 0.06, 0.0)
    out = brightness(out, 0.06)
    # airy background: lighter, softer pastel greenery (kept coloured so the halo reads as a shape)
    bg_airy = saturation(blend(out, '#ffffff', 'screen', 0.32), 0.75)
    bg_airy = soft_focus(bg_airy, 8, 0.55)
    out = apply_mask(out, bg_airy, bgm)
    # the halo: a bright soft disc of light directly behind the head, fading out into the background
    centre = (fx, fy - 120)
    core = radial(center=centre, radius=0.46, softness=0.7)
    halo = radial(center=centre, radius=0.78, softness=0.92)
    halo_m = np.clip(core * 0.95 + halo * 0.45, 0, 1) * bgm
    out = blend(out, '#ffffff', 'screen', 0.95, mask_=halo_m)
    # faint light rays from above
    ry = rays(center=(fx - 60, -H * 0.25), count=12, seed=57, sharpness=8.0, spread=1.4) * bgm
    out = blend(out, '#fff9f2', 'screen', 0.12, mask_=ry)
    # light wrap: the halo spills onto the edges of the hijab and shoulders and lifts the fabric near the head
    rim = inner_edge(person, width=26, softness=14) * np.clip(core * 1.6, 0, 1)
    out = blend(out, '#fff6ea', 'screen', 0.9, mask_=rim)
    out = blend(out, '#ffffff', 'screen', 0.12, mask_=core * person_soft)
    # glowing highlights + dreamy softness
    out = glow(out, sigma=40, strength=0.42, threshold=0.55)
    out = saturation(out, 0.9)
    out = orton(out, sigma=30, strength=0.15)
    return out


# ----------------------------------------------------------------------------- 058 love_letter

@effect('love_letter')
def love_letter(img):
    """Photo printed on an old love letter: cream paper, warm faded tone, soft worn edges, creases, ink flourishes."""
    mx, my = 64, 80  # paper margin (keeps the 4:5 aspect of the print)
    # --- the print: warm, faded (lighter, lower contrast), a little soft
    ph = tone(img, '#d9bc94', 0.55)
    ph = fade(ph, 0.16, 0.06)
    ph = brightness(ph, 0.04)
    ph = split_tone(ph, shadows='#7a5a44', highlights='#f8e6c8', strength=0.3)
    ph = contrast(ph, 0.9)
    ph = gamma(ph, 1.06)
    ph = temperature(ph, 0.05)
    ph = soft_focus(ph, 6, 0.15)
    ph = vignette(ph, strength=0.5, radius=0.95, softness=0.95, color_='#e0c9a4')
    # --- lay the print on cream letter paper with an irregular, worn edge
    sheet = canvas('#f2e8d4')
    photo_full = sheet.copy()
    photo_full[my:H - my, mx:W - mx] = resize(ph, W - 2 * mx, H - 2 * my)
    area = np.zeros((H, W), np.float32)
    area[my:H - my, mx:W - mx] = 1
    e = feather(area, 10)
    n = fbm(5, seed=21, scale=2.5)
    lo = 0.25 + (n - 0.5) * 0.35
    edge = smoothstep(lo, lo + 0.45, e)
    out = lerp(sheet, photo_full, edge)
    # --- age: gentle uneven yellowing, a few small foxing spots (kept off the face), paper fibres
    yellow = fbm(3, seed=9, scale=0.7)
    out = blend(out, '#dcc7a0', 'multiply', 0.16, mask_=yellow)
    spots = smoothstep(0.74, 0.88, fbm(4, seed=7, scale=6.0)) * (1 - mask('face', feather=60))
    out = blend(out, '#b8905a', 'multiply', 0.22, mask_=spots)
    out = clip(out * paper(seed=3, strength=0.17)[..., None])
    # --- folded-letter creases (away from the face) and faded ink corner ornaments
    out = _crease(out, 1036, horizontal=True, strength=0.11)
    out = _crease(out, 226, horizontal=False, strength=0.09)
    out = draw_shapes(out, lambda d: _flourishes(d, inset_=26, size=210))
    out = grain(out, 0.03, seed=58)
    return out


# ----------------------------------------------------------------------------- 059 whisper

@effect('whisper')
def whisper(img):
    """Very soft, pale and quiet: low contrast, pale cream and pink pastel tones, hushed and delicate."""
    out = brightness(img, 0.06)
    out = contrast(out, 0.8)
    out = saturation(out, 0.75)
    # greens -> pale sage, navy -> dusty mauve-blue
    out = hsl_adjust(out, 100, width=50, sat=0.62, lum=0.06)
    out = hsl_adjust(out, 230, width=40, sat=0.75, lum=0.05, shift=15)
    out = split_tone(out, shadows='#c8a0a8', highlights='#fff0e2', strength=0.45)
    # pale pink-cream wash
    out = blend(out, '#f6d8d4', 'soft_light', 0.45)
    out = blend(out, '#fff0e8', 'screen', 0.15)
    out = temperature(out, 0.05)
    out = fade(out, 0.2, 0.08)
    # dreamy softness
    out = orton(out, sigma=25, strength=0.2)
    out = soft_focus(out, 4, 0.2)
    return out


# ----------------------------------------------------------------------------- 060 blush

@effect('blush')
def blush(img):
    """Natural rosy blush on the apples of the cheeks and a warm pink overall tone."""
    down, across, el, er = _face_axes()
    ang = math.degrees(math.atan2(across[1], across[0]))
    c_l = el + 112 * down - 48 * across
    c_r = er + 112 * down + 48 * across
    skin = mask('face_skin', feather=6)
    # diffused, slightly uneven blush shapes (a real flush is never a perfect gradient)
    blob = _blob(c_l, 120, 92, ang, power=1.8) * 1.15 + _blob(c_r, 122, 94, ang, power=1.8)
    blob = np.clip(blob, 0, 1) * skin * (0.82 + 0.18 * fbm(3, seed=60, scale=3.0))
    # rosy cheeks: warm rose, soft-light lift + a light multiply to deepen
    out = blend(img, '#ff8090', 'soft_light', 0.62, mask_=blob)
    out = blend(out, '#e98494', 'multiply', 0.2, mask_=blob)
    # warm pink overall tone
    out = split_tone(out, shadows='#5a3a45', highlights='#ffd9e0', strength=0.34)
    out = temperature(out, 0.07)
    out = tint(out, 0.04)
    out = blend(out, '#f2bfc9', 'soft_light', 0.3)
    # lips harmonise with the blush
    out = apply_mask(out, saturation(out, 1.12), mask('lips', feather=3))
    return out
