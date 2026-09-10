"""Group g01 — Yorug'lik (Lighting): golden_hour, soft_light, studio_light, rim_light, window_light."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _person(feather_=1.5):
    """Cleaned person mask: the stored mask sits at ~0.988 inside the subject (with a faint ring), so
    remap it to a solid 1.0 core while keeping the soft edge, then feather a little."""
    p = mask('person')
    p = smoothstep(0.03, 0.97, p)
    return feather(p, feather_) if feather_ else p


def _decontaminate_edge(img, p, width=7):
    """Kill the green foliage fringe that hugs the subject outline once the background is replaced/darkened."""
    band = edge_band(p, width, 3)
    fixed = hsl_adjust(img, 105, width=55, sat=0.2, lum=-0.02)
    return apply_mask(img, fixed, band)


def _skin(feather_=6.0, grow=0):
    """Face-skin mask minus the hijab: the stored face_skin oval overlaps the hijab's inner edge at the temple,
    so the clothes segmentation is subtracted before any grow/feather."""
    m = mask('face_skin') * (1 - smoothstep(0.2, 0.6, mask('seg_clothes', 2)))
    if grow:
        k = np.ones((abs(grow) * 2 + 1,) * 2, np.uint8)
        m = cv2.dilate(m, k) if grow > 0 else cv2.erode(m, k)
    return feather(m, feather_) if feather_ else m


def _skin_protect(img, ref, amount=0.5, feather_=5):
    """Pull face-skin hue & saturation back towards a reference so grades never turn the skin orange/grey.
    The skin mask excludes the hijab and is eroded so the correction never spills onto the fabric."""
    m = _skin(feather_, grow=-6)
    hsv = rgb2hsv(img)
    hsv0 = rgb2hsv(ref)
    t = m * amount
    dh = ((hsv[..., 0] - hsv0[..., 0] + 180.0) % 360.0) - 180.0          # circular hue difference
    hsv[..., 0] = (hsv0[..., 0] + dh * (1 - t)) % 360.0
    hsv[..., 1] = hsv[..., 1] * (1 - t) + hsv0[..., 1] * t
    return hsv2rgb(hsv)


def _rim_mask(p, lights, core=6.0, skirt=22.0, skirt_amount=0.45, wrap=0.12):
    """Physically-motivated rim light mask (H,W) along the subject outline.
    Intensity falls off with the distance from the edge (bright core + soft skirt) and depends on how much the
    local edge faces each light: lights = [((lx, ly), strength), ...] with (lx, ly) the unit direction TOWARDS
    the light in image coordinates (y down), e.g. (0.7, -0.7) = light at the top-right."""
    hard = (p > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(hard, cv2.DIST_L2, 5)
    profile = (np.exp(-dist / core) + skirt_amount * np.exp(-dist / skirt)) * (hard > 0)
    mb = blur(p, 10.0)
    gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
    mag = np.sqrt(gx * gx + gy * gy) + 1e-5
    nx, ny = -gx / mag, -gy / mag                                           # outward normal
    facing = np.zeros((H, W), np.float32)
    for (lx, ly), s in lights:
        facing += s * smoothstep(-0.05, 0.6, nx * lx + ny * ly)
    facing = np.clip(wrap + facing, 0, 1)
    return np.clip(profile * facing, 0, 1).astype(np.float32)


def _bloom(img, sigma=40, strength=0.35, threshold=0.55, color_='#ffe2b4', dark_protect=(0.1, 0.42)):
    """Warm highlight bloom that is kept off the dark areas: plain glow() screens the blurred bright face onto the
    navy hijab next to it and turns that band purple, so the bloom is weighted by local luminance and gold-tinted."""
    l = luminance(img)
    hi = smoothstep(threshold, 1.0, l)[..., None] * img
    b = blur(hi, sigma) * color(color_)
    w = smoothstep(dark_protect[0], dark_protect[1], l)
    return blend(img, b, 'screen', strength, mask_=w)


def _light_direction(angle_deg):
    """Unit vector towards a light at compass angle (0 = right, 90 = top, 180 = left), y down."""
    a = math.radians(angle_deg)
    return (math.cos(a), -math.sin(a))


# ----------------------------------------------------------------------------- 001 golden hour

@effect('golden_hour')
def golden_hour(img):
    """Warm low sun from the top-right, golden skin glow, haze, warm brown shadows."""
    orig = img
    p = _person()
    skin = _skin(8)
    skin_in = _skin(6, grow=-6)                                                     # eroded: never touches the hijab
    face = mask('face', 40)
    sun_c = (W * 1.04, -H * 0.04)
    sun = radial(center=sun_c, radius=1.55, softness=0.92)                          # sun glow off-frame, top-right
    side = linear(-45, 0.05, 0.95)                                                  # 0 bottom-left -> 1 top-right

    # foliage goes golden, base warmth, warm-brown shadows
    img = hsl_adjust(img, 100, width=50, sat=1.12, shift=-26)                         # greens -> yellow-gold
    img = temperature(img, 0.30)
    img = split_tone(img, shadows='#5a3626', highlights='#ffd27a', strength=0.42)
    img = curve(img, [(0, 0.04), (0.25, 0.25), (0.65, 0.70), (1, 0.98)])            # gentle haze in the blacks, open mids

    # low sun from the side: directional warm light, haze towards the sun, soft rays through the trees
    img = blend(img, '#ffb15a', 'screen', 0.42, mask_=side * (0.35 + 0.65 * sun) * (1 - skin * 0.7))
    img = blend(img, '#f5c98c', 'normal', 0.22, mask_=sun ** 1.4 * (1 - face * 0.5))
    img = blend(img, '#fff0c8', 'screen', 0.55, mask_=radial(center=sun_c, radius=0.75, softness=1.0))
    beams = blur(rays(center=sun_c, count=9, seed=4, sharpness=8.0, spread=1.3), 22) * sun
    img = blend(img, '#ffc46e', 'screen', 0.35, mask_=beams * (1 - face * 0.7))

    # sun-kissed edge on the hijab / shoulder facing the sun
    rim = _rim_mask(p, [(_light_direction(48), 1.0)], core=7, skirt=26, skirt_amount=0.5, wrap=0.0)
    img = blend(img, '#ffd48a', 'screen', 0.75, mask_=rim)

    # golden glow on the skin, bloom
    img = blend(img, '#ffd2ae', 'soft_light', 0.3, mask_=skin_in)
    img = _bloom(img, sigma=40, strength=0.4, threshold=0.55)

    # keep the skin natural: pull hue/saturation back towards a gently warmed, peachy original
    img = _skin_protect(img, tint(temperature(orig, 0.2), 0.05), 0.72)
    img = vignette(img, strength=0.22, radius=1.0, softness=0.75, color_='#2a1608', center=(W * 0.4, H * 0.45))
    return img


# ----------------------------------------------------------------------------- 002 soft light

@effect('soft_light')
def soft_light(img):
    """Diffused, shadowless, airy relight: lifted shadows, low contrast, even creamy skin, no vignette."""
    orig = img
    skin = _skin(5, grow=-4)
    fill_m = _skin(14)                                                              # skin only: no halo on the hijab

    # open up the shadows everywhere, extra fill on the face
    img = curve(img, [(0, 0.06), (0.3, 0.36), (0.7, 0.76), (1, 0.97)])
    fill = curve(img, [(0, 0.12), (0.25, 0.40), (0.6, 0.70), (1, 0.97)])
    img = apply_mask(img, fill, fill_m * 0.85)
    img = contrast(img, 0.9, pivot=0.55)
    img = exposure(img, 0.08)

    # even, smooth skin (keep pores)
    img = skin_smooth(img, strength=0.45, mask_=skin, radius=12, keep_texture=0.5)
    img = apply_mask(img, brightness(img, 0.03), skin)

    # airy, creamy ambience: skylight from above + gentle diffusion
    img = blend(img, '#fff6ea', 'screen', 0.16, mask_=1 - linear(90, 0.0, 1.0) * 0.6)
    img = orton(img, sigma=20, strength=0.3)
    img = saturation(img, 0.92)
    img = tint(img, 0.04)
    img = temperature(img, 0.06)
    img = curve(img, [(0, 0.05), (0.5, 0.52), (0.9, 0.9), (1, 0.965)])             # matte toe, no clipped skin
    img = _skin_protect(img, orig, 0.35)
    return img


# ----------------------------------------------------------------------------- 003 studio light

def _catchlights(img, strength=0.55):
    """Soft round studio catchlight in the upper-left of each iris."""
    layer = np.zeros((H, W), np.float32)
    x, y = coords()
    for name in ('iris_l', 'iris_r'):
        m = mask(name)
        pts = np.argwhere(m > 0.5)
        if len(pts) == 0:
            continue
        cy, cx = pts.mean(0)
        r = math.sqrt(len(pts) / math.pi)
        d = np.sqrt((x - (cx - r * 0.38)) ** 2 + (y - (cy - r * 0.42)) ** 2)
        layer = np.maximum(layer, (1 - smoothstep(r * 0.16, r * 0.34, d)) * mask('eyes', 0.5))
    return blend(img, '#ffffff', 'screen', strength, mask_=layer)


@effect('studio_light')
def studio_light(img):
    """Dark-grey seamless backdrop, key light on the face, crisp detail, clean colours."""
    p = _person(1.2)
    fx, fy = face_center()

    # seamless backdrop: soft background-light pool behind the head, darker towards the edges (dithered)
    pool = radial(center=(fx + 60, fy - 140), radius=1.15, softness=0.85, aspect=0.9)
    backdrop = lerp(as_layer('#1b1919'), as_layer('#3d3839'), pool)
    backdrop = clip(backdrop + ((noise(3) - 0.5) * 0.012)[..., None])

    # subject: neutralise the green park bounce, crisp, clean
    subj = tint(img, 0.06)
    subj = temperature(subj, 0.04)
    subj = s_curve(subj, 0.08)
    subj = clarity(subj, 0.3, 40)
    subj = unsharp(subj, 1.5, 0.35)

    # key light on the face (+ soft falloff away from it)
    key = radial(center=(fx - 40, fy - 40), radius=0.62, softness=0.7, aspect=1.05)
    subj = blend(subj, '#fff5e8', 'soft_light', 0.45, mask_=key)
    subj = clip(subj * (1 + 0.06 * key)[..., None])
    subj = curve(subj, [(0, 0), (0.55, 0.55), (0.85, 0.83), (1, 0.965)])          # highlight roll-off: no clipped skin
    falloff = linear(90, 0.5, 1.0) * (1 - key)
    subj = clip(subj * (1 - 0.28 * falloff)[..., None])

    # hair light / separation along the top of the hijab, catchlights in the eyes
    hair = _rim_mask(p, [(_light_direction(75), 1.0)], core=6, skirt=18, skirt_amount=0.35, wrap=0.0)
    subj = blend(subj, '#ffffff', 'screen', 0.45, mask_=hair)
    subj = blend(subj, '#ffffff', 'screen', 0.07, mask_=mask('iris', 1.0))
    subj = _catchlights(subj, 0.55)

    img = replace_background(subj, backdrop, person=p, feather_=0)
    img = _decontaminate_edge(img, p, 7)
    return img


# ----------------------------------------------------------------------------- 004 rim light

@effect('rim_light')
def rim_light(img):
    """Backlight: bright warm-white edge tracing the hijab and shoulders, background darker and cooler."""
    p = _person(1.2)
    bg = 1 - p

    # background: darker, slightly cool, with the warm backlight source glowing behind the head at the top-right
    dark = temperature(exposure(img, -0.95), -0.2)
    dark = saturation(dark, 0.78)
    img = apply_mask(img, dark, bg)
    src = radial(center=(W * 0.9, H * 0.1), radius=0.6, softness=0.95)
    img = blend(img, '#ffdcae', 'screen', 0.5, mask_=src * bg)
    img = _decontaminate_edge(img, p, 6)

    # subject: a touch more contrast so the rim sings
    img = apply_mask(img, s_curve(img, 0.06), p)

    # rim: main backlight top-right, a weaker kicker top-left so the whole outline is traced
    rim = _rim_mask(p, [(_light_direction(55), 1.0), (_light_direction(125), 0.4)],
                    core=8.5, skirt=30, skirt_amount=0.55, wrap=0.10)
    img = blend(img, '#ffe9c4', 'screen', 1.0, mask_=np.clip(rim * 1.25, 0, 1))
    img = blend(img, '#ffffff', 'add', 0.45, mask_=rim ** 1.5)

    # lens bloom: soft, modest, both sides of the edge
    bloom = blur(rim, 16)
    img = blend(img, '#ffd9a6', 'screen', 0.42, mask_=bloom)
    img = vignette(img, strength=0.18, radius=1.05, softness=0.7, color_='#08080c')
    return img


# ----------------------------------------------------------------------------- 005 window light

@effect('window_light')
def window_light(img):
    """Bright, calm window light: warm soft daylight from the left with a gentle hint of venetian-blind bands."""
    orig = img
    p = _person(1.5)
    face = mask('face', 30)
    bulge = blur(mask('face'), 45)
    from_left = 1 - linear(0, 0.05, 1.0)                                              # 1 at the left edge -> 0 right

    # base: a touch brighter than the original, warm, gentle contrast, open shadows
    img = exposure(img, 0.10)
    img = temperature(img, 0.14)
    img = contrast(img, 0.96, pivot=0.5)
    img = curve(img, [(0, 0.04), (0.3, 0.34), (0.7, 0.73), (1, 0.985)])
    lum_w = 0.45 + 0.55 * smoothstep(0.08, 0.4, luminance(img))                     # sunny wash lands on skin/background, keeps the navy clean

    # blind bands: wide, soft, horizontal-ish; the pattern jumps at the subject outline (she is closer to the
    # blind) and bends over the face so it reads as light on a 3-D form rather than an overlay
    x, y = coords()
    a = math.radians(-6)
    t = x * math.sin(a) + y * math.cos(a) + 60
    t = t + p * (40 + 60 * bulge)
    period, duty = 240, 0.42
    u = t % period
    soft_bg, soft_p = 44.0, 30.0
    band_bg = smoothstep(0, soft_bg, u) * (1 - smoothstep(period * duty - soft_bg, period * duty, u))
    band_p = smoothstep(0, soft_p, u) * (1 - smoothstep(period * duty - soft_p, period * duty, u))
    bands = band_bg * (1 - p) + band_p * p                                            # 1 = shade band
    reach = 0.6 + 0.4 * from_left                                                     # bands fade away from the window
    region = (1 - p) * 1.0 + p * (1 - face) * 0.6 + p * face * 0.5                    # bg 100% / body 60% / face 50%
    shade_w = bands * reach * region
    img = lerp(img, img * as_layer('#cfd2da'), shade_w)                               # <= ~18% darkening on the background, ~9% on the face
    lit = (1 - bands) * reach
    img = blend(img, '#ffe6b8', 'screen', 0.22, mask_=lit * lum_w)                    # the lit bands are the warm, sunny part

    # the window: warm soft daylight sweeping in from the left, soft fall-off to the right
    img = blend(img, '#fff0d0', 'screen', 0.26, mask_=from_left ** 1.2 * lum_w)
    img = blend(img, '#fff2d8', 'screen', 0.24, mask_=radial(center=(-W * 0.1, H * 0.35), radius=0.9, softness=1.0) * lum_w)
    img = clip(img * (1 - 0.06 * linear(0, 0.4, 1.0))[..., None])

    # gentle fill on the face, small bloom, natural skin
    img = apply_mask(img, curve(img, [(0, 0.05), (0.3, 0.35), (1, 0.985)]), mask('face', 20))
    img = _bloom(img, sigma=30, strength=0.22, threshold=0.62, color_='#fff0d8')
    img = _skin_protect(img, orig, 0.3)
    return img
