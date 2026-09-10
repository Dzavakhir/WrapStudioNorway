"""Group 15 - Portrait retouch: skin_smooth, bright_eyes, white_teeth, dodge_burn, soft_focus."""
import math
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _blob(cx, cy, sx, sy, angle=0.0, inner=0.10):
    """Soft elliptical blob (H,W) in [0,1]: 1 at the centre, fading to 0 at the semi-axes sx (along `angle`, deg,
    image coords / y down) and sy (across)."""
    x, y = coords()
    a = math.radians(angle)
    dx, dy = x - cx, y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    d = np.sqrt((u / sx) ** 2 + (v / sy) ** 2)
    return (1 - smoothstep(inner, 1.0, d)).astype(np.float32)


def _iris_centres():
    out = []
    for n in ('iris_l', 'iris_r'):
        m = mask(n)
        ys, xs = np.where(m > 0.5)
        out.append((float(xs.mean()), float(ys.mean()), float(np.sqrt((m > 0.5).sum() / math.pi))))
    return out


def _even_chroma(img, m, sigma=12.0, amount=0.5):
    """Colour evening: blur the a/b (chroma) channels in Lab inside mask m, keep luminance detail."""
    lab = cv2.cvtColor(np.ascontiguousarray(clip(img), dtype=np.float32), cv2.COLOR_RGB2LAB)
    ab = lab[..., 1:].copy()
    w = np.asarray(m, np.float32)[..., None]
    num = blur(ab * w, sigma)                      # masked blur: hijab / lip colours do not bleed into the skin
    den = blur(w, sigma)[..., None]
    ab_b = num / np.maximum(den, 1e-3)
    lab[..., 1:] = lerp(ab, ab_b, amount * w)
    return clip(cv2.cvtColor(np.ascontiguousarray(lab, dtype=np.float32), cv2.COLOR_LAB2RGB))


def _teeth_mask(img):
    """Soft mask of the visible teeth only (bright, low-saturation pixels inside the mouth mask)."""
    hsv = rgb2hsv(img)
    lum = luminance(img)
    mouth_m = mask('mouth', feather=0.8)
    t = mouth_m * smoothstep(0.22, 0.36, lum) * (1 - smoothstep(0.40, 0.55, hsv[..., 1]))
    t = t * (1 - mask('lips', grow=-2, feather=1.0) * (1 - mask('mouth')))   # never touch the lips
    return feather(np.clip(t, 0, 1), 1.5)


# ----------------------------------------------------------------------------- 071 skin_smooth

@effect('skin_smooth')
def skin_smooth_(img):
    skin = mask('face_skin', feather=5)
    # keep a little distance from the eyes / brows / lips so lashes and lip edges stay crisp
    protect = np.clip(mask('eyes', grow=6, feather=4) + mask('brows', grow=2, feather=3) + mask('lips', grow=3, feather=3), 0, 1)
    skin = np.clip(skin * (1 - protect), 0, 1)

    # 1) two gentle bilateral passes: flatten low-contrast unevenness (noise, blotches) while freckles,
    #    smile lines and the nose contour (higher contrast) are preserved
    low = bilateral(img, d=11, sigma_color=0.062, sigma_space=9)
    low = bilateral(low, d=11, sigma_color=0.05, sigma_space=9)
    # 2) add back the finest texture (pores / grain) so the skin never goes plastic
    high = img - blur(img, 1.5)
    smooth = clip(low + 0.45 * high)
    out = lerp(img, smooth, 0.9 * skin)

    # 3) even out the tone: soften redness / blotches in the chroma only (luminance detail untouched)
    out = _even_chroma(out, skin, sigma=12, amount=0.5)

    # 4) a hair brighter, cleaner skin
    out = clip(out + 0.022 * skin[..., None])
    return out


# ----------------------------------------------------------------------------- 072 bright_eyes

@effect('bright_eyes')
def bright_eyes(img):
    lum = luminance(img)
    eye = mask('eyes', feather=1.5)
    iris = mask('iris', feather=1.5)
    iris_core = mask('iris', grow=-5, feather=2.5)
    whites = np.clip(eye - mask('iris', grow=2, feather=2.0), 0, 1)
    out = img.copy()

    # --- eye whites: gently brighten & clean (weighted towards the sclera, not the lash line)
    w_w = whites * smoothstep(0.06, 0.40, lum)
    hsv = rgb2hsv(out)
    hsv[..., 1] = hsv[..., 1] * (1 - 0.35 * w_w)
    hsv[..., 2] = np.clip(hsv[..., 2] * (1 + 0.30 * w_w) + 0.04 * w_w, 0, 0.82)
    out = hsv2rgb(hsv)

    # --- iris: clean the JPEG mottling first, then lift the midtones so the brown shows,
    #     a little more saturation / contrast, and a slightly darker limbal ring for definition
    ir = bilateral(out, d=7, sigma_color=0.07, sigma_space=5)
    ir = clip(ir * 1.18)                          # multiplicative: the pupil stays black
    ir = saturation(ir, 1.18)
    ir = contrast(ir, 1.08, pivot=0.20)
    out = lerp(out, ir, iris)
    ring = np.clip(iris - iris_core, 0, 1)
    out = blend(out, '#000000', 'soft_light', 0.35, ring)

    # --- sharpen the eye area (lashes, liner, lids) a touch - but not the iris itself
    region = mask('eyes', grow=26, feather=12) * (1 - mask('iris', grow=2, feather=2))
    sh = unsharp(out, 1.3, 0.5)
    out = lerp(out, sh, region)

    # --- gentle lift of the eye zone so the eyes read brighter (lids / under-eye)
    zone = mask('eyes', grow=45, feather=26) * mask('face_skin', feather=3)
    out = blend(out, '#ffffff', 'soft_light', 0.18, zone)

    # --- small catchlight sparkle at the upper-left of each iris (the existing light direction)
    layer = np.zeros((H, W), np.float32)
    x, y = coords()
    for cx, cy, r in _iris_centres():
        px, py = cx - 0.30 * r, cy - 0.34 * r
        d = np.sqrt((x - px) ** 2 + (y - py) ** 2)
        layer = np.maximum(layer, (1 - smoothstep(0.0, 2.6, d)) ** 1.3)              # bright core
        layer = np.maximum(layer, 0.30 * (1 - smoothstep(1.5, 7.0, d)))              # soft glow
        layer = np.maximum(layer, 0.25 * star(px, py, size=9, thickness=0.10, rays=4, rotation=8))
    out = blend(out, layer[..., None] * color('#fff8e6'), 'screen', 0.65)
    return out


# ----------------------------------------------------------------------------- 073 white_teeth

@effect('white_teeth')
def white_teeth(img):
    t = _teeth_mask(img)
    hsv = rgb2hsv(img)
    # remove most of the yellow cast, keep a whisper of natural warmth
    hsv[..., 1] = hsv[..., 1] * (1 - 0.55 * t)
    # brighten multiplicatively so the shading and the gaps between the teeth stay defined
    hsv[..., 2] = np.clip(hsv[..., 2] * (1 + 0.16 * t) + 0.02 * t, 0, 1)
    out = hsv2rgb(hsv)
    # clean, very slightly cool white
    out = blend(out, '#f3f6ff', 'screen', 0.06, t)
    out = temperature(out, -0.06) * t[..., None] + out * (1 - t[..., None])
    # a touch of definition on the (upscaled, soft) teeth
    out = lerp(out, unsharp(out, 1.5, 0.35), t)
    return clip(lerp(img, out, t))


# ----------------------------------------------------------------------------- 074 dodge_burn

@effect('dodge_burn')
def dodge_burn(img):
    skin = mask('face_skin', feather=4)
    face = mask('face', feather=2)

    # --- dodge: soft highlights on the high points of the face
    D = np.zeros((H, W), np.float32)
    D += 1.00 * _blob(470, 395, 110, 55, angle=-27)     # forehead centre
    D += 0.55 * _blob(487, 605, 62, 28, angle=99)       # nose bridge
    D += 0.30 * _blob(476, 676, 20, 15)                 # nose tip
    D += 0.85 * _blob(368, 685, 68, 36, angle=-35)      # cheekbone (image left, under the eye)
    D += 0.95 * _blob(690, 595, 92, 46, angle=-35)      # cheekbone (image right, under the eye)
    D += 0.65 * _blob(632, 905, 52, 34, angle=-27)      # chin
    D = np.clip(D, 0, 1) * skin

    # --- burn: face edges + jaw (ring inside the hole-free face mask), cheek hollows, nose sides
    ring = inner_edge(face, width=70, softness=36)
    B = 0.95 * ring
    B += 0.30 * _blob(805, 770, 115, 58, angle=-45)     # under the cheekbone, merging into the jaw (image right)
    B += 0.28 * _blob(340, 785, 75, 36, angle=-45)      # under the cheekbone (image left)
    B += 0.22 * _blob(458, 632, 44, 15, angle=99)       # nose side (left)
    B += 0.22 * _blob(513, 634, 44, 15, angle=99)       # nose side (right)
    B = np.clip(B, 0, 1) * skin
    B = B * (1 - 0.85 * D)                              # never burn where we dodge

    out = blend(img, '#ffffff', 'soft_light', 0.60, D)
    out = blend(out, '#000000', 'soft_light', 0.60, B)  # neutral burn (no muddy colour cast)
    out = blend(out, '#8a6a58', 'multiply', 0.12, B)    # ... with just a hint of warm shadow
    # a whisper of midtone contrast on the skin so the sculpting reads as light, not paint
    out = lerp(out, clarity(out, 0.12, 60), skin * 0.8)
    # pure redistribution of light: keep the average face brightness exactly where it was
    sel = skin > 0.5
    delta = float(luminance(img)[sel].mean() - luminance(out)[sel].mean())
    out = clip(out + delta * skin[..., None])
    return out


# ----------------------------------------------------------------------------- 075 soft_focus

@effect('soft_focus')
def soft_focus_(img):
    # sharp core with a gentle diffusion (classic soft-focus filter)
    b = blur(img, 12)
    out = lerp(img, b, 0.35)
    # keep the eyes readable: less diffusion around them
    eyes_zone = mask('eyes', grow=40, feather=28)
    out = lerp(out, lerp(img, b, 0.15), eyes_zone)
    # luminous bloom: the highlights spread softly into their surroundings
    l = luminance(img)
    hi = smoothstep(0.42, 1.0, l)[..., None] * img
    bloom = blur(hi, 36)
    out = blend(out, bloom, 'screen', 0.55)
    # keep the blacks and the overall contrast so it does not go milky
    out = contrast(out, 1.06, pivot=0.45)
    out = brightness(out, 0.015)
    # a hint of romantic warmth in the highlights (kept light so the skin stays natural)
    out = split_tone(out, shadows='#2f2a3a', highlights='#ffe2c8', strength=0.10)
    return clip(out)
