"""Group 13 — Estetika (Aesthetic Trends): dark_academia, light_academia, cottagecore, y2k, clean_girl."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- helpers

def _face_back(graded, milder, amount=0.5, feather_=14):
    """Blend the face region part-way back towards a milder version (keeps skin natural)."""
    m = mask('face_skin', feather=feather_)
    return lerp(graded, milder, m * amount)


def _mask_centroid(m, thresh=0.5):
    ys, xs = np.where(m > thresh)
    if len(xs) == 0:
        return face_center()
    return float(xs.mean()), float(ys.mean())


def _brightest_in(img, m, sigma=4.0):
    """Position of the brightest (blurred) pixel inside mask m."""
    l = blur(luminance(img), sigma) * (m > 0.5)
    idx = int(np.argmax(l))
    return float(idx % W), float(idx // W)


def _face_saturation(img, factor, feather_=10):
    """Saturation change restricted to the face skin."""
    return lerp(img, saturation(img, factor), mask('face_skin', feather=feather_))


# ----------------------------------------------------------------------------- 061 dark academia

@effect('dark_academia')
def dark_academia(img):
    """Moody brown tones, darker exposure, vintage grain, old-library feel."""
    # foliage greens -> brown / amber-olive, sky & navy -> muted
    img = hsl_adjust(img, hue=85, width=60, sat=0.6, lum=-0.04, shift=-55)
    img = hsl_adjust(img, hue=215, width=45, sat=0.45, lum=-0.04)
    # darker exposure with brown (not black) shadows
    img = exposure(img, -0.32)
    img = s_curve(img, 0.14)
    img = curve(img, [(0, 0.03), (0.5, 0.48), (1, 0.97)])
    img = saturation(img, 0.75)
    pre = img
    img = split_tone(img, shadows='#2a1a10', highlights='#c8a878', strength=0.5)
    img = tone(img, '#8a6248', 0.3)
    img = _face_back(img, pre, 0.6)            # skin keeps some of its own pink
    img = lerp(img, clarity(img, 0.12, 30), mask('face_skin', feather=10))
    img = temperature(img, 0.14)
    img = color_balance(img, shadows=(0.05, 0.025, 0.0), highlights=(0.02, 0.0, -0.03))
    # warm reading-lamp light on the face keeps her the bright point of the frame
    lamp = radial(center=face_center(), radius=0.85, softness=0.85)
    img = blend(img, '#f4cfa0', 'soft_light', 0.5, lamp)
    img = blend(img, '#f4cfa0', 'screen', 0.16, lamp)
    # vintage grain (coarse but restrained) + heavy dark vignette
    img = grain(img, 0.04, size=1.6, seed=13)
    img = vignette(img, 0.45, radius=1.05, softness=0.85, color_='#140b06')
    return img


# ----------------------------------------------------------------------------- 062 light academia

@effect('light_academia')
def light_academia(img):
    """Creamy beige tones, bright soft light, low saturation, warm elegance."""
    # greens -> soft sage/beige, blues -> muted warm slate
    img = hsl_adjust(img, hue=85, width=60, sat=0.5, lum=0.02, shift=-25)
    img = hsl_adjust(img, hue=220, width=45, sat=0.55, lum=0.06)
    # brighter, softer tone
    img = curve(img, [(0, 0.0), (0.25, 0.29), (0.6, 0.67), (1, 1)])
    img = contrast(img, 0.9, pivot=0.55)
    img = fade(img, 0.06, 0.02)
    img = saturation(img, 0.78)
    img = split_tone(img, shadows='#7a6a58', highlights='#fff2dc', strength=0.45)
    img = tone(img, '#d8c2a0', 0.28)
    # creamy wash + soft daylight from above
    img = blend(img, '#f4e4cc', 'soft_light', 0.4)
    img = blend(img, '#fff4e2', 'screen', 0.06)
    top = 1 - linear(90, 0.0, 0.8)
    img = blend(img, '#fff3df', 'screen', 0.10, top)
    # skin stays warm and alive inside the low-saturation grade
    img = _face_saturation(img, 1.2)
    img = _face_back(img, temperature(img, 0.1), 0.6)
    # bloom + a whisper of softness outside the face
    img = glow(img, sigma=50, strength=0.25, threshold=0.55)
    soft = soft_focus(img, 8, 0.2)
    img = lerp(soft, img, mask('face', feather=20))
    img = grain(img, 0.025, seed=13)
    return img


# ----------------------------------------------------------------------------- 063 cottagecore

@effect('cottagecore')
def cottagecore(img):
    """Soft warm greens, gentle sunlight, light haze, nostalgic film feel."""
    src = img
    # soft warm greens, softer sky
    img = hsl_adjust(img, hue=80, width=60, sat=0.85, lum=0.07, shift=16)
    img = hsl_adjust(img, hue=215, width=40, sat=0.6, lum=0.05, shift=-10)
    img = temperature(img, 0.2)
    img = _face_back(img, temperature(src, 0.09), 0.5)
    # nostalgic film tone
    img = fade(img, 0.07, 0.03)
    img = s_curve(img, 0.08)
    img = split_tone(img, shadows='#4a5a3e', highlights='#ffe6b8', strength=0.3)
    # gentle sunlight from the top-right (mostly on the foliage, softly over her)
    sun_c = (W * 1.02, -H * 0.06)
    sun = radial(center=sun_c, radius=1.4, softness=0.9)
    img = blend(img, '#ffe0a8', 'screen', 0.55, sun)
    person = mask('person', feather=25)
    ray_m = rays(center=sun_c, count=11, seed=13, sharpness=8.0, spread=1.3)
    ray_m = ray_m * (1 - linear(90, 0.05, 0.85)) * (1 - 0.6 * person)
    img = blend(img, '#fff0c8', 'screen', 0.35, ray_m)
    # sun-kissed rim on the hijab / shoulder facing the light
    rim = inner_edge(mask('person'), width=16, softness=8) * radial(center=sun_c, radius=1.6, softness=0.95)
    img = blend(img, '#ffdca0', 'screen', 0.4, rim)
    # light haze (top-weighted) + bloom
    haze = 0.3 + 0.7 * (1 - linear(90, 0.0, 0.9))
    img = blend(img, '#fff0d0', 'screen', 0.2, haze)
    img = glow(img, sigma=45, strength=0.25, threshold=0.5)
    # film grain, soft warm vignette
    img = grain(img, 0.04, size=1.2, seed=13)
    img = vignette(img, 0.15, radius=1.0, softness=0.8, color_='#3a2a18')
    return img


# ----------------------------------------------------------------------------- 064 y2k

@effect('y2k')
def y2k(img):
    """Glossy high saturation, magenta and cyan tints, sparkles and a lens flare."""
    src = img
    # glossy, punchy, saturated (skin gets vibrance only)
    img = vibrance(img, 0.35)
    mild = glow(s_curve(src, 0.1), sigma=25, strength=0.25, threshold=0.6)
    img = saturation(img, 1.25)
    img = s_curve(img, 0.18)
    img = split_tone(img, shadows='#2a1a60', highlights='#ff9ad0', strength=0.4)
    # magenta (top-left) -> cyan (bottom-right) tint wash
    g = linear(35, 0.1, 0.9)
    tint_layer = lerp(as_layer('#ff3fd0'), as_layer('#30e8ff'), g)
    img = blend(img, tint_layer, 'soft_light', 0.5)
    img = blend(img, tint_layer, 'screen', 0.14)
    img = _face_back(img, split_tone(mild, shadows='#3a2a60', highlights='#ffc4e0', strength=0.12), 0.88)
    # gloss: bloom + shiny highlights, lip-gloss specular
    img = glow(img, sigma=25, strength=0.3, threshold=0.65)
    img = curve(img, [(0, 0), (0.7, 0.71), (0.9, 0.93), (1, 1)])
    lips = mask('lips', feather=3)
    spec = smoothstep(0.45, 0.8, blur(luminance(img), 3)) * lips
    img = blend(img, '#fff0f8', 'screen', 0.45, spec)
    img = chromatic_aberration(img, 4)
    # sparkles: catchlights in both eyes, one on the smile, a scatter over bright spots
    r = rng(13)
    pts, sizes = [], []
    for n in ('iris_l', 'iris_r'):
        cx, cy = _mask_centroid(mask(n))
        pts.append((cx - 7, cy - 8)); sizes.append(26)
    tx, ty = _brightest_in(src, mask('mouth'))
    pts.append((tx, ty)); sizes.append(40)
    fx0, fy0, fx1, fy1 = face_box()
    l = blur(luminance(src), 3) * (mask('background') > 0.5)
    cand = np.argwhere(l > 0.5)
    r.shuffle(cand)
    for y, x in cand:
        if fx0 - 40 < x < fx1 + 40 and fy0 - 40 < y < fy1 + 60:
            continue
        if x < 70 or x > W - 70 or y < 70 or y > H - 70:
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 170 ** 2 for px, py in pts):
            continue
        pts.append((float(x), float(y))); sizes.append(float(r.uniform(34, 78)))
        if len(pts) >= 3 + 9:
            break
    sp = sparkle_layer(pts, sizes, '#ffffff', seed=13, glow_=True)
    sp = sp * lerp(as_layer('#ffe4fb'), as_layer('#e0fbff'), g)   # holographic tint
    img = blend(img, np.clip(sp, 0, 1), 'screen', 1.0)
    # lens flare in the top-left sky
    img = lens_flare(img, pos=(W * 0.13, H * 0.075), strength=0.6, color_='#ffd8f4', ghosts=False, seed=13)
    return img


# ----------------------------------------------------------------------------- 065 clean girl

@effect('clean_girl')
def clean_girl(img):
    """Bright clean light, natural glowing skin, neutral whites, minimal and fresh."""
    # neutral whites: gently white-balance on the teeth
    teeth = mask('mouth')
    ref = img[teeth > 0.5].mean(0)
    gains = np.clip(ref.mean() / np.maximum(ref, 1e-3), 0.96, 1.04)
    gains = 1 + 0.5 * (gains - 1)
    img = clip(img * gains.astype(np.float32))
    img = temperature(img, -0.02)
    # bright clean light: lift mids, keep highlights clean
    img = curve(img, [(0, 0), (0.3, 0.37), (0.7, 0.77), (1, 1)])
    top = 1 - linear(90, 0.0, 0.7)
    img = blend(img, '#ffffff', 'screen', 0.08, top)
    # skin: professional smoothing + dewy glow on the natural highlights, healthy colour kept
    img = skin_smooth(img, 0.42, radius=14, keep_texture=0.4)
    fs = mask('face_skin', feather=6)
    dew = smoothstep(0.55, 0.85, blur(luminance(img), 6)) * fs
    img = blend(img, '#fff6ec', 'screen', 0.22, dew)
    img = _face_saturation(img, 1.18)
    img = _face_back(img, temperature(img, 0.08), 0.6)
    img = lerp(img, clarity(img, 0.14, 30), fs)
    # eyes a touch brighter and crisper
    eyes = mask('eyes', feather=3)
    img = lerp(img, unsharp(exposure(img, 0.18), 1.5, 0.5), eyes * 0.7)
    # fresh minimal background: softly blurred, lighter, calmer colour
    person = mask('person')
    img = blur_background(img, sigma=11, person=person)
    bg_m = 1 - mask('person', feather=2)
    bg_style = contrast(brightness(saturation(img, 0.72), 0.10), 0.85, pivot=0.6)
    bg_style = blend(bg_style, '#ffffff', 'screen', 0.10)
    img = lerp(img, bg_style, bg_m)
    # global polish
    img = glow(img, sigma=35, strength=0.2, threshold=0.65)
    img = clarity(img, 0.1, 40)
    return img
