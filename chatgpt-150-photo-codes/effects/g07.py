"""Group g07 — Oq-qora (Black & White): bw_classic, bw_contrast, bw_soft, bw_film, red_pop."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- helpers

def _mono3(l):
    """(H,W) luminance -> 3-channel image."""
    return np.repeat(np.clip(l, 0, 1)[..., None], 3, axis=2).astype(np.float32)


def _red_masks():
    """(sleeve, lips) soft masks. Sleeve = red hue inside the clothing segment, skin excluded aggressively;
    dark folds filled by a morphological closing so the garment stays one solid piece of colour."""
    img = base()
    hsv = rgb2hsv(img)
    h, s = hsv[..., 0], hsv[..., 1]
    d = np.abs(((h - 355.0 + 180.0) % 360.0) - 180.0)          # hue distance from red
    hue_w = smoothstep(34.0, 14.0, d)                          # 1 near red, 0 beyond +-34 deg
    sat_w = smoothstep(0.10, 0.26, s)                          # dark sleeve folds still count
    clothes = np.clip(mask('seg_clothes', feather=2.0, grow=2) * mask('person'), 0, 1)
    face = mask('face', feather=8.0, grow=36)                  # whole face + jaw/neck strip: never colour skin
    raw = hue_w * sat_w * clothes * (1.0 - face)
    hard = (raw > 0.45).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    closed = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(closed, 8)
    keep = np.zeros_like(closed)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 6000:                  # drop speckles; the sleeve is ~180k px
            keep[lab == i] = 1
    sleeve = feather(keep.astype(np.float32), 2.0)
    lips = mask('lips', feather=1.2)
    return np.clip(sleeve, 0, 1).astype(np.float32), np.clip(lips, 0, 1).astype(np.float32)


# ----------------------------------------------------------------------------- #031 classic

@effect('bw_classic')
def bw_classic(img):
    """Balanced, clean classic monochrome: natural tonal range, gentle contrast, crisp detail."""
    out = bw(img, 0.30, 0.59, 0.11)
    # open the deep navy shadows a touch so the hijab folds keep detail, keep highlights natural
    out = curve(out, [(0, 0), (0.06, 0.07), (0.18, 0.215), (0.45, 0.485), (0.75, 0.77), (0.92, 0.925), (1, 1)])
    out = s_curve(out, 0.10)
    out = clarity(out, 0.15, radius=40)
    out = unsharp(out, 1.4, 0.22)
    return clip(out)


# ----------------------------------------------------------------------------- #032 high contrast

@effect('bw_contrast')
def bw_contrast(img):
    """Bold high-contrast monochrome: crushed blacks in the fabric, bright luminous face, punchy detail."""
    out = bw(img, 0.35, 0.50, 0.15)
    out = levels(out, black=0.03, white=0.93)
    # one designed curve instead of stacking: deep toe (fabric folds -> black), fast rise through the
    # skin midtones, rolled-off shoulder so the face stays bright but not paper-white
    out = curve(out, [(0, 0), (0.05, 0.015), (0.14, 0.075), (0.30, 0.30), (0.50, 0.63), (0.68, 0.82), (0.85, 0.93), (1, 1)])
    punchy = clarity(out, 0.35, radius=45)
    skin = clarity(out, 0.18, radius=45)
    out = apply_mask(punchy, skin, mask('face_skin', feather=8))
    out = unsharp(out, 1.2, 0.30)
    # a whisper of vignette to push the eye to the face
    out = vignette(out, strength=0.16, radius=1.0, softness=0.75)
    return clip(out)


# ----------------------------------------------------------------------------- #033 soft high-key

@effect('bw_soft')
def bw_soft(img):
    """Airy high-key monochrome: lifted shadows, light tones, gentle glow, no vignette."""
    out = bw(img, 0.28, 0.54, 0.18)
    # strong high-key lift: blacks become soft grey, midtones float, highlights stay just under white
    out = curve(out, [(0, 0.17), (0.10, 0.36), (0.25, 0.56), (0.45, 0.74), (0.65, 0.86), (0.85, 0.945), (1, 0.985)])
    # let the background dissolve towards white so the subject floats in light
    bgm = mask('background', feather=10)
    out = blend(out, '#ffffff', 'screen', 0.30, bgm)
    # gentle luminous lift on the face (dodge), keeps the skin bright and even
    fx, fy = face_center()
    out = blend(out, '#ffffff', 'soft_light', 0.22, radial(center=(fx, fy - 30), radius=0.55, softness=0.9))
    # soft diffusion glow: bloom around the light areas + a light overall softness
    out = glow(out, sigma=50, strength=0.40, threshold=0.55)
    out = soft_focus(out, sigma=6, mix=0.20)
    # bring back crispness on the eyes / brows / lips so the softness reads as glow, not blur
    detail = unsharp(out, 1.5, 0.40)
    keep = np.clip(mask('eyes', feather=6, grow=12) + mask('lips', feather=6, grow=8) + mask('brows', feather=6, grow=6), 0, 1)
    out = apply_mask(out, detail, keep)
    return clip(out)


# ----------------------------------------------------------------------------- #034 35 mm film

@effect('bw_film')
def bw_film(img):
    """Ilford-style 35 mm: rich midtones, matte toe, visible grain and a soft vignette."""
    out = bw(img, 0.28, 0.60, 0.12)
    out = s_curve(out, 0.18)
    # push midtones up a little so the grain lives in them (film has open shadows)
    out = curve(out, [(0, 0), (0.10, 0.12), (0.25, 0.30), (0.50, 0.55), (0.78, 0.80), (1, 0.985)])
    out = fade(out, 0.06, 0.025)
    out = clarity(out, 0.12, radius=60)
    out = vignette(out, strength=0.34, radius=1.0, softness=0.72)
    out = grain(out, amount=0.11, size=1.7, mono=True, seed=7, shadows=0.9)
    # scanned negatives have a faint softness — take the digital edge off
    out = soft_focus(out, sigma=1.1, mix=0.35)
    return _mono3(luminance(clip(out)))


# ----------------------------------------------------------------------------- #035 red colour pop

@effect('red_pop')
def red_pop(img):
    """Black & white everywhere except the red sleeve and the lips, which stay in full colour."""
    sleeve, lips = _red_masks()
    mono = bw(img, 0.30, 0.59, 0.11)
    mono = s_curve(mono, 0.10)
    mono = clarity(mono, 0.10, radius=40)
    # the sleeve: original colour, richened slightly; the lips: their own natural colour, untouched
    reds = hsl_adjust(img, 355, width=40, sat=1.15, lum=0.0)
    reds = s_curve(reds, 0.08)
    out = apply_mask(mono, reds, sleeve)
    out = apply_mask(out, img, lips)
    return clip(out)
