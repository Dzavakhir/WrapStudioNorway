"""g16 — Portrait retouch: /clarity, /sharpen, /glow_skin, /matte_skin, /portrait_pro."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- landmarks / geometry

_M = meta()
_EL = np.array(_M['eye_l'], np.float32)      # image-left eye  (396, 601)
_ER = np.array(_M['eye_r'], np.float32)      # image-right eye (587, 503)
_NOSE = np.array(_M['nose'], np.float32)     # nose tip        (472, 687)
_MOUTH = np.array(_M['mouth'], np.float32)
_CHIN = np.array(_M['chin'], np.float32)
_FC = np.array(_M['face_center'], np.float32)
_U = (_ER - _EL) / (np.linalg.norm(_ER - _EL) + 1e-6)          # along the eye line, towards image-right
_V = np.array([-_U[1], _U[0]], np.float32)                     # "down" the face (towards the chin)
_TILT = math.degrees(math.atan2(_U[1], _U[0]))                 # ~ -27 deg (head tilted)


def _blob(center, r_along, r_across, angle_deg=_TILT, power=1.0):
    """Soft elliptical dome (H,W): 1 at centre, 0 at the ellipse edge; r_along lies along angle_deg."""
    x, y = coords()
    a = math.radians(angle_deg)
    dx, dy = x - center[0], y - center[1]
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    d = np.sqrt((u / r_along) ** 2 + (v / r_across) ** 2)
    return ((1 - smoothstep(0.0, 1.0, d)) ** power).astype(np.float32)


def _skin_mask(img, feather_=3.0):
    """Face skin only: the segmentation skin mask (hugs the hijab edge) minus eyes/brows/lips/teeth,
    gated to non-dark pixels so nothing leaks onto the navy fabric."""
    m = mask('seg_face_skin')
    feat = np.clip(mask('eyes', grow=8) + mask('brows', grow=5) + mask('lips', grow=4) + mask('mouth', grow=4), 0, 1)
    m = m * (1 - feather(feat, 3))
    m = m * smoothstep(0.10, 0.22, luminance(img))
    return np.clip(feather(m, feather_), 0, 1)


# highlight / contour zones (all multiplied by the skin mask when used, so spill onto the hijab is harmless)
def _zones():
    z = {}
    z['cheek_r'] = _blob((740, 612), 105, 72)            # image-right cheekbone (her left, towards camera)
    z['cheek_l'] = _blob((372, 706), 62, 68)             # image-left cheekbone (foreshortened side)
    mid = (_EL + _ER) / 2
    bridge_c = (mid + _NOSE) / 2 + np.array([4, 10], np.float32)
    ang = math.degrees(math.atan2(_NOSE[1] - mid[1], _NOSE[0] - mid[0]))
    z['bridge'] = _blob(bridge_c, 72, 20, ang)           # nose bridge, elongated along the nose
    z['nose_tip'] = _blob(_NOSE + np.array([6, -4], np.float32), 30, 26)
    z['forehead'] = _blob((445, 425), 95, 62)
    z['chin'] = _blob((612, 905), 52, 42)
    z['under_l'] = _blob(_EL + 50 * _V, 70, 34)          # under-eye areas
    z['under_r'] = _blob(_ER + 50 * _V, 76, 36)
    z['cheek_r_hi'] = _blob((762, 566), 68, 34)          # cheekbone lines (highlighter placement)
    z['cheek_l_hi'] = _blob((364, 690), 40, 44)
    z['brow_r'] = _blob(_ER - 34 * _V + 8 * _U, 62, 15)  # brow bone under the image-right brow
    return z


# ----------------------------------------------------------------------------- tonal helpers

def _local_contrast(img, amount, radius, eps=0.03, protect=None):
    """Edge-aware local contrast (clarity): detail = luminance - guided-filter base, so strong edges
    (hijab against sky) get no halo while midtone structure is boosted."""
    l = luminance(img)
    base_l = cv2.ximgproc.guidedFilter(l, l, int(radius), float(eps))
    d = l - base_l
    w_pos = 1 - 0.9 * smoothstep(0.62, 0.95, l)            # don't push highlights into clipping
    w_neg = 0.55 + 0.45 * smoothstep(0.0, 0.15, l)         # don't crush deep shadows
    w = np.where(d > 0, w_pos, w_neg)
    if protect is not None:
        w = w * (1 - protect)
    return clip(img + (amount * d * w)[..., None])


def _lum_sharpen(img, radius, amount, threshold=0.0, limit=0.22, mask_=None):
    """Luminance-only unsharp mask with coring (threshold) and a soft limiter against overshoot halos."""
    l = luminance(img)
    d = l - blur(l, radius)
    if threshold:
        d = np.sign(d) * np.maximum(np.abs(d) - threshold, 0)
    d = np.tanh(d / limit) * limit
    d = np.where(d > 0, d * (1 - 0.9 * smoothstep(0.78, 0.98, l)), d)   # no overshoot into clipping
    a = amount if mask_ is None else amount * mask_
    return clip(img + (a * d)[..., None])


def _even_tone(img, m, strength=0.5, sigma=14):
    """Even out skin colour: chroma is pulled towards the local (skin-only) average, luminance untouched."""
    l = luminance(img)[..., None]
    chroma = img - l
    mm = m[..., None]
    avg = blur(chroma * mm, sigma) / np.maximum(blur(m, sigma), 1e-3)[..., None]
    return clip(l + lerp(chroma, avg, strength * m))


def _scale_lum(img, new_l, old_l):
    ratio = new_l / np.maximum(old_l, 1e-3)
    return clip(img * ratio[..., None])


# ----------------------------------------------------------------------------- 076 /clarity

@effect('clarity')
def clarity_fx(img):
    skin = _skin_mask(img, 4)
    soft = np.clip(skin * 0.65 + feather(mask('lips', grow=3), 3) * 0.5, 0, 1)  # skin -65%, lips -50%
    out = _local_contrast(img, 0.85, 40, 0.03, protect=soft)                    # midtone detail
    out = _local_contrast(out, 0.42, 130, 0.06, protect=skin * 0.35)            # larger-scale "dimensional" structure
    out = _lum_sharpen(out, 1.6, 0.35, 0.004, mask_=1 - 0.5 * skin)
    out = lerp(vibrance(out, 0.16), out, np.clip(skin * 0.5 + soft * 0.4, 0, 0.8))  # colour punch, gentle on skin & lips
    out = curve(out, [(0, 0), (0.25, 0.222), (0.75, 0.765), (1, 1)])                  # punch, mostly in the shadows
    return out


# ----------------------------------------------------------------------------- 077 /sharpen

@effect('sharpen')
def sharpen_fx(img):
    skin = _skin_mask(img, 4)
    eyes = feather(mask('eyes', grow=12), 6)
    w = np.clip(1 - 0.55 * skin + 0.45 * eyes, 0, 1.45)
    out = _lum_sharpen(img, 1.2, 1.15, 0.006, limit=0.16, mask_=w)       # fine detail
    out = _lum_sharpen(out, 2.8, 0.5, 0.004, limit=0.16, mask_=w)        # slightly coarser edges
    out = _lum_sharpen(out, 6.0, 0.22, 0.004, limit=0.12, mask_=1 - 0.6 * skin)   # edge acutance visible even when small
    de = detail_enhance(out, 10, 0.15)
    out = lerp(out, de, 0.3 * (1 - 0.7 * skin))
    return out


# ----------------------------------------------------------------------------- 078 /glow_skin

@effect('glow_skin')
def glow_skin(img):
    skin = _skin_mask(img, 3)
    z = _zones()
    out = skin_smooth(img, 0.35, mask_=skin, radius=12, keep_texture=0.45)
    l = luminance(out)
    ls = blur(l, 6)
    lit = smoothstep(0.42, 0.60, ls)                                         # only where the light already falls
    zone = np.clip(z['cheek_r'] ** 1.3 + z['cheek_l'] ** 1.3 + z['bridge'] + 0.6 * z['nose_tip'] + 0.6 * z['forehead'] ** 1.3 + 0.6 * z['chin'], 0, 1)
    # broad radiance: planes brighter than the surrounding skin, concentrated on cheekbones / nose / forehead
    rel = ls - cv2.ximgproc.guidedFilter(l, l, 60, 0.05)
    hl = smoothstep(0.0, 0.05, rel) * lit
    glowmap = np.clip(hl * (0.3 + 0.9 * zone) + 0.35 * zone * smoothstep(0.30, 0.55, ls), 0, 1)
    glowmap = np.clip(feather(glowmap, 8), 0, 1) * skin
    out = clip(out * (1 + 0.19 * glowmap)[..., None])                       # luminance gain keeps the skin colour
    # dewy sheen: smooth highlighter shapes on the cheekbone lines, nose bridge/tip, brow bone and chin
    hi_shape = np.clip(z['cheek_r_hi'] + 0.8 * z['cheek_l_hi'] + 0.9 * z['bridge'] + 0.6 * z['nose_tip'] + 0.5 * z['chin'] + 0.45 * z['brow_r'], 0, 1)
    l3 = blur(luminance(out), 3.0)
    organic = smoothstep(0.01, 0.045, l3 - cv2.ximgproc.guidedFilter(l3, l3, 25, 0.02)) * smoothstep(0.56, 0.72, l3)
    sheen = (hi_shape * lit * (0.55 + 0.45 * organic) + 0.2 * organic * (0.3 + zone)) * skin
    sheen = np.clip(feather(sheen, 3), 0, 1)
    out = blend(out, '#ffffff', 'screen', 1.0, mask_=sheen * 0.48)
    # soft bloom around the highlights
    hi = smoothstep(0.66, 0.95, luminance(out))[..., None] * out * skin[..., None]
    out = blend(out, blur(hi, 12), 'screen', 0.35, mask_=feather(skin, 10))
    # healthy colour: barely warmer, a little more vibrant, rosy blush on the cheek apples
    warm = vibrance(temperature(out, 0.03), 0.08)
    out = apply_mask(out, warm, skin)
    blush = np.clip(z['cheek_r'] + z['cheek_l'], 0, 1) * skin
    out = blend(out, '#e0787e', 'soft_light', 1.0, mask_=blush * 0.25)
    return out


# ----------------------------------------------------------------------------- 079 /matte_skin

@effect('matte_skin')
def matte_skin(img):
    skin = _skin_mask(img, 3)
    out = skin_smooth(img, 0.55, mask_=skin, radius=14, keep_texture=0.35)
    out = _even_tone(out, skin, 0.5)
    l = luminance(out)
    # kill specular shine: bright local bumps are pulled back to the local skin level
    local = cv2.ximgproc.guidedFilter(l, l, 22, 0.02)
    bump = l - local
    shine = smoothstep(0.56, 0.70, blur(l, 3)) * smoothstep(0.0, 0.05, bump)
    new_l = l - shine * bump * 0.85
    # compress the highlight end of the skin tones (powdered finish)
    new_l = np.interp(new_l, [0, 0.2, 0.45, 0.6, 0.72, 0.85, 1.0], [0, 0.21, 0.462, 0.59, 0.68, 0.755, 0.85]).astype(np.float32)
    matte = _scale_lum(out, new_l, l)
    matte = saturation(matte, 0.92)
    matte = blend(matte, '#e6cbb6', 'soft_light', 0.2)
    return apply_mask(out, matte, skin)


# ----------------------------------------------------------------------------- 080 /portrait_pro

@effect('portrait_pro')
def portrait_pro(img):
    skin = _skin_mask(img, 3)
    z = _zones()
    # --- skin: frequency-separation smoothing + colour evening
    out = skin_smooth(img, 0.7, mask_=skin, radius=14, keep_texture=0.45)
    out = _even_tone(out, skin, 0.45)
    # --- under-eye brightening
    ue = np.clip(z['under_l'] + z['under_r'], 0, 1) * skin
    out = blend(out, '#ffffff', 'soft_light', 1.0, mask_=ue * 0.4)
    # --- eyes: cleaner whites, crisper & brighter iris, boosted catchlights, defined lashes
    eyes_m = feather(mask('eyes', grow=1), 1.0)
    iris_m = feather(mask('iris', grow=1), 1.0)
    whites = np.clip(eyes_m - feather(mask('iris', grow=3), 1.5), 0, 1)
    e = clip(saturation(out, 0.6) + 0.07)
    out = apply_mask(out, e, whites * 0.9)
    e = unsharp(clip(saturation(contrast(out, 1.2), 1.2) + 0.03), 1.2, 0.5)
    out = apply_mask(out, e, iris_m)
    cl = smoothstep(0.6, 0.9, blur(luminance(out), 1.0)) * eyes_m
    out = blend(out, '#ffffff', 'screen', 1.0, mask_=cl * 0.35)
    out = _lum_sharpen(out, 1.5, 0.6, mask_=feather(mask('eyes', grow=14), 6))
    # --- teeth: whiten (remove yellow, lift) only the bright tooth pixels
    teeth = feather(mask('mouth', grow=1), 1.2) * smoothstep(0.30, 0.50, blur(luminance(out), 1.5))
    t = clip(saturation(hsl_adjust(out, 45, width=45, sat=0.35), 0.75) + 0.08)
    out = apply_mask(out, t, teeth)
    # --- lips & brows: a little definition
    lips_m = feather(mask('lips'), 1.5)
    lp = unsharp(vibrance(out, 0.08), 1.5, 0.4)
    out = apply_mask(out, lp, lips_m * 0.8)
    br = clip(unsharp(out, 1.5, 0.5) * 0.94)
    out = apply_mask(out, br, feather(mask('brows', grow=1), 1.5) * 0.8)
    # --- subtle contouring (dodge & burn): lift the centre planes, deepen the face edges
    dodge = np.clip(0.8 * z['forehead'] + z['bridge'] + 0.6 * z['chin'] + 0.5 * z['cheek_r'] + 0.5 * z['cheek_l'], 0, 1)
    dodge = dodge * skin
    burn = (1 - radial(center=tuple(_FC), radius=0.56, softness=0.75)) * skin
    out = blend(out, '#ffffff', 'soft_light', 1.0, mask_=dodge * 0.35)
    out = blend(out, '#000000', 'soft_light', 1.0, mask_=burn * 0.2)
    out = clip(out * (1 + 0.04 * skin)[..., None])                         # keep the face luminous after the burn
    # --- refined colour: gentle clarity, warm split tone, vibrance, contrast, vignette
    out = _local_contrast(out, 0.18, 50, 0.03, protect=skin * 0.6)
    out = split_tone(out, shadows='#3a3f5c', highlights='#ffd9a8', strength=0.14)
    out = lerp(vibrance(out, 0.07), out, lips_m * 0.7)        # keep the lips natural
    out = s_curve(out, 0.04)
    out = vignette(out, 0.18, radius=1.0, softness=0.75)
    return out
