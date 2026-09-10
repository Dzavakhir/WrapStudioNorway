"""Group g25 — Mavsum & ob-havo (Season & Weather): autumn, winter, spring, summer, rain."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _person(feather_=1.5):
    """Cleaned person mask: the stored mask sits at ~0.988 inside the subject, remap to a solid core + soft edge."""
    p = smoothstep(0.03, 0.97, mask('person'))
    return feather(p, feather_) if feather_ else p


def _foliage(img, lo=36.0, hi=180.0, soft=8.0, min_sat=0.10, protect_face=True):
    """Soft weight (H,W) of the green / yellow-green vegetation, chosen by hue and gated by saturation.
    Skin (hue 4-16), lips, the red sleeve (~355) and the navy hijab (~240) all fall outside the window."""
    hsv = rgb2hsv(img)
    h, s = hsv[..., 0], hsv[..., 1]
    w = smoothstep(lo - soft, lo + soft, h) * (1 - smoothstep(hi - soft, hi + soft, h)) * smoothstep(min_sat, min_sat * 3, s)
    if protect_face:
        w = w * (1 - mask('face', 6, grow=4))
    return w.astype(np.float32)


def _skin_guard(img, ref, amount=0.5, feather_=6, grow=-6):
    """Pull the face-skin hue & saturation back towards the ungraded reference (luminance keeps the new grade)."""
    m = mask('face_skin', feather_, grow=grow) * amount
    hsv = rgb2hsv(img)
    hsv0 = rgb2hsv(ref)
    dh = ((hsv[..., 0] - hsv0[..., 0] + 180.0) % 360.0) - 180.0
    hsv[..., 0] = (hsv0[..., 0] + dh * (1 - m)) % 360.0
    hsv[..., 1] = hsv[..., 1] * (1 - m) + hsv0[..., 1] * m
    return hsv2rgb(hsv)


def _bloom(img, sigma=40, strength=0.3, threshold=0.55, color_='#ffe6c0', dark_protect=(0.1, 0.42)):
    """Tinted highlight bloom kept off the dark areas (plain glow() smears the bright face onto the navy hijab)."""
    l = luminance(img)
    hi = smoothstep(threshold, 1.0, l)[..., None] * img
    b = blur(hi, sigma) * color(color_)
    wgt = smoothstep(dark_protect[0], dark_protect[1], l)
    return blend(img, b, 'screen', strength, mask_=wgt)


def _dots(count, radius, seed, alpha=(0.5, 1.0), area=None, elong=(1.0, 1.0), tilt=(-8, 8)):
    """Random anti-aliased discs / soft ellipses -> (H,W) float layer. area: optional (H,W) probability mask."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    n = 0
    tries = 0
    while n < count and tries < count * 30:
        tries += 1
        x, y = r.uniform(0, W), r.uniform(0, H)
        if area is not None and r.random() > area[int(y), int(x)]:
            continue
        rad = r.uniform(*radius)
        e = r.uniform(*elong)
        cv2.ellipse(m, (int(round(x)), int(round(y))), (max(1, int(round(rad))), max(1, int(round(rad * e)))),
                    float(r.uniform(*tilt)), 0, 360, float(r.uniform(*alpha)), -1, cv2.LINE_AA)
        n += 1
    return m


def _streak_blur(layer, length, dx, dy):
    """Motion blur of a layer along the unit direction (dx, dy) over `length` px."""
    L = int(length) | 1
    k = np.zeros((L, L), np.float32)
    c = L / 2 - 0.5
    cv2.line(k, (int(round(c - dx * L / 2)), int(round(c - dy * L / 2))),
             (int(round(c + dx * L / 2)), int(round(c + dy * L / 2))), 1.0, 1, cv2.LINE_AA)
    k /= max(k.sum(), 1e-6)
    return cv2.filter2D(layer, -1, k, borderType=cv2.BORDER_REFLECT)


def _rgba_layer(draw_fn, blur_=0.0):
    """Draw with PIL onto a transparent layer -> (rgb (H,W,3), alpha (H,W)), optionally defocused (premultiplied blur)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    a = np.array(layer).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3]
    if blur_:
        pm = blur(rgb * alpha[..., None], blur_)
        alpha = blur(alpha, blur_)
        rgb = pm / np.maximum(alpha[..., None], 1e-4)
    return rgb, alpha


def _composite(img, rgb, alpha, opacity=1.0):
    return clip(lerp(img, rgb, np.clip(alpha * opacity, 0, 1)))


def _ellipse_pts(cx, cy, a, b, rot_deg, n=28):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = math.radians(rot_deg)
    x = cx + a * np.cos(t) * math.cos(r) - b * np.sin(t) * math.sin(r)
    y = cy + a * np.cos(t) * math.sin(r) + b * np.sin(t) * math.cos(r)
    return list(zip(x.tolist(), y.tolist()))


def _flower(d, cx, cy, size, col, rot=0.0, centre_col='#fff1c9', alpha=235):
    """Five-petal blossom drawn as rotated petal ellipses + a pale centre."""
    for i in range(5):
        ang = rot + i * 72.0
        a = math.radians(ang)
        px, py = cx + math.cos(a) * size * 0.40, cy + math.sin(a) * size * 0.40
        d.polygon(_ellipse_pts(px, py, size * 0.40, size * 0.25, ang), fill=color255(col) + (alpha,))
    rc = size * 0.15
    d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=color255(centre_col) + (alpha,))


# ----------------------------------------------------------------------------- 121 autumn

@effect('autumn')
def autumn(img):
    """Golden autumn: every green turns amber/orange (deep greens -> red-orange), low warm sun from the left."""
    orig = img
    p = _person()
    w = _foliage(img, lo=36, hi=180)
    hsv = rgb2hsv(img)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    t = np.clip((h - 36.0) / (180.0 - 36.0), 0, 1)
    target = 40.0 - 26.0 * t                                    # yellow-greens -> amber, deep greens -> red-orange
    hsv[..., 0] = h * (1 - w) + target * w
    hsv[..., 1] = np.clip(s * (1 + 0.30 * w) + 0.08 * w, 0, 1)
    hsv[..., 2] = np.clip(v + 0.04 * w, 0, 1)
    img = hsv2rgb(hsv)
    img = temperature(img, 0.22)
    img = split_tone(img, shadows='#4a2a14', highlights='#ffcf7a', strength=0.35)
    # warm low sun coming through the trees on the left
    sun_c = (-W * 0.08, H * 0.28)
    sun = radial(center=sun_c, radius=1.25, softness=0.95)
    img = blend(img, '#ffc673', 'screen', 0.55, mask_=sun)
    ry = rays(center=sun_c, count=12, seed=25, sharpness=8, spread=1.3)
    img = blend(img, '#ffe0a0', 'screen', 0.35, mask_=ry * (1 - 0.5 * p))
    img = _bloom(img, sigma=45, strength=0.25, threshold=0.55, color_='#ffe2b4')
    img = s_curve(img, 0.06)
    img = _skin_guard(img, orig, amount=0.45)
    return vignette(img, strength=0.28, radius=1.0, softness=0.8, color_='#2a1408')


# ----------------------------------------------------------------------------- 122 winter

def _snow_layer(seed=25):
    face_soft = mask('face', 40, grow=20)
    far = _dots(1100, (1.2, 2.6), seed, alpha=(0.4, 0.9), elong=(1.2, 1.8))
    far = blur(far, 0.7)
    mid = _dots(280, (2.5, 5.5), seed + 1, alpha=(0.5, 1.0), elong=(1.1, 1.6))
    mid = blur(mid, 1.1)
    near = _dots(55, (7, 16), seed + 2, alpha=(0.25, 0.55), area=1 - 0.8 * face_soft)
    near = blur(near, 5)
    return np.clip(far * 0.9 + mid + near, 0, 1)


@effect('winter')
def winter(img):
    """Cold winter: frosted, desaturated foliage, overcast white sky, silver-blue grade, mist and falling snow."""
    orig = img
    p = _person()
    w = _foliage(img, lo=36, hi=180)
    hsv = rgb2hsv(img)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    sky = smoothstep(185, 200, h) * (1 - smoothstep(250, 265, h)) * smoothstep(0.08, 0.25, s) * (1 - p)
    hsv[..., 1] = np.clip(s * (1 - 0.85 * w) * (1 - 0.7 * sky), 0, 1)
    l = luminance(img)
    hp = smoothstep(0.0, 0.10, l - blur(l, 5))                   # leaf highlights = snow dusting on top
    frost = w * (0.10 + 0.32 * smoothstep(0.25, 0.85, v) + 0.25 * hp)
    hsv[..., 2] = np.clip(v + frost + 0.14 * sky, 0, 1)
    img = hsv2rgb(hsv)
    img = temperature(img, -0.30)
    img = saturation(img, 0.78)
    img = split_tone(img, shadows='#2b3d5c', highlights='#e4eef8', strength=0.4)
    img = brightness(img, 0.04)
    lin = linear(90)
    haze_m = np.clip((1 - p) * (0.22 + 0.2 * (1 - lin)) * (0.75 + 0.5 * fbm(4, 25, 0.7)) + p * 0.05, 0, 1)
    img = blend(img, '#dde6f0', 'normal', 1.0, mask_=haze_m)
    snow = _snow_layer()
    img = blend(img, '#f6f9ff', 'screen', 0.92, mask_=snow)
    img = _skin_guard(img, orig, amount=0.55)
    return vignette(img, 0.2, color_='#1f2b3c')


# ----------------------------------------------------------------------------- 123 spring

def _blossoms(seed=25):
    """Three blossom layers: defocused foreground clusters in the top corners, blossom dots on the trees behind,
    and drifting petals. Returns [(rgb, alpha, opacity), ...] to composite in order."""
    r = rng(seed)
    p = _person()
    face_zone = mask('face', 30, grow=30)
    pinks = ['#ffb7c5', '#ffc9d6', '#f7a3b6', '#ffd6df', '#fbbcc9']
    layers = []

    # background blossom on the trees behind (upper background)
    bg_top = (1 - p) * (1 - linear(90, 0.12, 0.72))

    def draw_bg(d):
        n = 0
        tries = 0
        while n < 170 and tries < 6000:
            tries += 1
            x, y = r.uniform(0, W), r.uniform(0, H * 0.8)
            if r.random() > bg_top[int(y), int(x)]:
                continue
            sz = r.uniform(14, 34)
            _flower(d, x, y, sz, pinks[r.integers(len(pinks))], r.uniform(0, 72), alpha=int(r.uniform(150, 230)))
            n += 1
    layers.append(_rgba_layer(draw_bg, 2.2) + (0.8,))

    # defocused foreground clusters (shooting through a blossoming branch)
    def draw_fg(d):
        for (cx, cy, count, spread) in ((110, 120, 9, 120), (1040, 110, 8, 110), (560, -10, 5, 110), (1120, 420, 4, 80)):
            for _ in range(count):
                x, y = cx + r.normal(0, spread * 0.55), cy + r.normal(0, spread * 0.5)
                sz = r.uniform(60, 120)
                _flower(d, x, y, sz, pinks[r.integers(len(pinks))], r.uniform(0, 72), alpha=int(r.uniform(200, 245)))
    layers.append(_rgba_layer(draw_fg, 9.0) + (0.9,))

    # drifting petals
    def draw_petals(d):
        n = 0
        tries = 0
        while n < 70 and tries < 4000:
            tries += 1
            x, y = r.uniform(0, W), r.uniform(0, H * 0.85)
            if face_zone[int(y), int(x)] > 0.15:
                continue
            L = r.uniform(7, 17)
            d.polygon(_ellipse_pts(x, y, L, L * r.uniform(0.35, 0.6), r.uniform(0, 180)),
                      fill=color255(pinks[r.integers(len(pinks))]) + (int(r.uniform(190, 255)),))
            n += 1
    layers.append(_rgba_layer(draw_petals, 1.2) + (0.95,))
    return layers


@effect('spring')
def spring(img):
    """Fresh spring: vivid lush greens, pink blossom on and in front of the trees, drifting petals, airy light."""
    orig = img
    w = _foliage(img, lo=36, hi=180)
    hsv = rgb2hsv(img)
    hsv[..., 0] = (hsv[..., 0] + 12.0 * w) % 360.0
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + 0.35 * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] + 0.08 * w, 0, 1)
    img = hsv2rgb(hsv)
    img = brightness(img, 0.04)
    img = split_tone(img, shadows='#4a5a3a', highlights='#ffe0ea', strength=0.35)
    for rgb, alpha, op in _blossoms():
        img = _composite(img, rgb, alpha, op)
    img = blend(img, '#fff6f0', 'screen', 0.16, mask_=1 - linear(90, 0.0, 0.7))
    img = _bloom(img, sigma=50, strength=0.25, threshold=0.6, color_='#fff4ec')
    img = vibrance(img, 0.15)
    return _skin_guard(img, orig, amount=0.4)


# ----------------------------------------------------------------------------- 124 summer

@effect('summer')
def summer(img):
    """Bright sunny summer: vivid colours, deeper blue sky, warm bright light and a sun glow top-right."""
    orig = img
    p = _person()
    img = vibrance(img, 0.45)
    img = hsl_adjust(img, 210, width=40, sat=1.5, lum=-0.02)   # deeper blue sky
    img = hsl_adjust(img, 95, width=50, sat=1.2, lum=0.04)     # lush greens
    img = temperature(img, 0.16)
    img = brightness(img, 0.04)
    img = s_curve(img, 0.08)
    sun_pos = (W * 0.90, H * 0.07)
    corner = radial(center=sun_pos, radius=1.05, softness=0.95)
    img = blend(img, '#fff1c4', 'screen', 0.6, mask_=corner)
    ry = rays(center=(W * 0.92, H * 0.05), count=10, seed=7, sharpness=8, spread=1.4)
    img = blend(img, '#fff0c0', 'screen', 0.35, mask_=ry)
    rim = inner_edge(p, 12, 6) * radial(center=sun_pos, radius=1.3, softness=0.9) * (1 - mask('face', 10, grow=6))
    img = blend(img, '#ffe6b0', 'screen', 0.5, mask_=rim)
    img = lens_flare(img, pos=sun_pos, strength=0.45, ghosts=False, streak=False)
    img = _bloom(img, 30, 0.3, 0.6, '#fff0d0')
    return _skin_guard(img, orig, 0.35)


# ----------------------------------------------------------------------------- 125 rain

def _rain_lines(count, length, thickness, seed, alpha, d):
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(count):
        L = r.uniform(*length)
        x0, y0 = r.uniform(-50, W + 50), r.uniform(-100, H + 50)
        x1, y1 = x0 + d[0] * L, y0 + d[1] * L
        cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), float(r.uniform(*alpha)), thickness, cv2.LINE_AA)
    return m


def _lens_droplets(img, sharp, seed=27, count=130):
    """Water drops on the lens: each is a small inverted-refracting lens with a bright rim and a specular dot."""
    r = rng(seed)
    x, y = coords()
    mx, my = x.copy(), y.copy()
    inside = np.zeros((H, W), np.float32)
    shade = np.zeros((H, W), np.float32)
    eyes_zone = mask('eyes', 25, grow=30)
    drops = []
    n = 0
    tries = 0
    while n < count and tries < count * 40:
        tries += 1
        cx, cy = r.uniform(12, W - 12), r.uniform(12, H - 12)
        rad = 4 + 18 * r.random() ** 2
        if rad > 9 and eyes_zone[int(cy), int(cx)] > 0.3:
            continue
        if any((cx - a) ** 2 + (cy - b) ** 2 < (rad + c + 8) ** 2 for a, b, c in drops):
            continue
        drops.append((cx, cy, rad))
        n += 1
        e = r.uniform(1.0, 1.5) if rad > 8 else r.uniform(0.9, 1.2)
        rx, ry = rad, rad * e
        x0, x1 = int(max(0, cx - rx - 3)), int(min(W, cx + rx + 4))
        y0, y1 = int(max(0, cy - ry - 3)), int(min(H, cy + ry + 4))
        xs, ys = x[y0:y1, x0:x1], y[y0:y1, x0:x1]
        dx, dy = (xs - cx) / rx, (ys - cy) / ry
        dsq = dx * dx + dy * dy
        d = np.sqrt(dsq)
        core = 1 - smoothstep(0.90, 1.0, d)
        s = 1 - 1.8 * np.sqrt(np.clip(1 - dsq, 0, 1))              # -0.8 at the centre (inverted), 1 at the rim
        sel = core > 0
        mx[y0:y1, x0:x1] = np.where(sel, cx + (xs - cx) * s, mx[y0:y1, x0:x1])
        my[y0:y1, x0:x1] = np.where(sel, cy + (ys - cy) * s + 0.12 * ry * (1 - dsq), my[y0:y1, x0:x1])
        ang = np.arctan2(dy, dx)
        light = 0.5 + 0.5 * np.cos(ang - math.radians(-130))       # side facing the top-left light
        rim = smoothstep(0.55, 0.95, d) * (1 - smoothstep(0.95, 1.0, d))
        sh = rim * (0.35 * light - 0.22 * (1 - light))
        spec = np.exp(-((dx + 0.38) ** 2 + (dy + 0.42) ** 2) / (2 * 0.13 ** 2)) * 0.5
        inside[y0:y1, x0:x1] = np.maximum(inside[y0:y1, x0:x1], core)
        shade[y0:y1, x0:x1] += (sh + spec) * core
    refr = cv2.remap(sharp, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    refr = clip(refr * 1.06 + 0.02)
    out = lerp(img, refr, inside)
    return clip(out + shade[..., None])


@effect('rain')
def rain(img):
    """Rain: cool blue-grey damp grade, misty distance, two depths of slanted rain streaks, drops on the lens."""
    p = _person()
    img = exposure(img, -0.18)
    img = temperature(img, -0.28)
    img = saturation(img, 0.72)
    img = split_tone(img, shadows='#243449', highlights='#b9c7d6', strength=0.4)
    img = fade(img, 0.06, 0.03)
    mist = (1 - p) * (0.18 + 0.12 * (1 - linear(90)))
    img = blend(img, '#93a2b3', 'normal', 1.0, mask_=mist)
    sharp = img
    img = blur(img, 0.9)
    d = (-math.sin(math.radians(12)), math.cos(math.radians(12)))
    far = _rain_lines(700, (30, 70), 1, seed=25, alpha=(0.25, 0.6), d=d)
    near = _rain_lines(220, (80, 170), 2, seed=26, alpha=(0.35, 0.8), d=d)
    near = blur(near, 0.8)
    face_soft = mask('face', 30, grow=10)
    streaks = np.clip(far + near, 0, 1) * (1 - 0.45 * face_soft)
    img = blend(img, '#dfe8f2', 'screen', 0.45, mask_=streaks)
    img = _lens_droplets(img, sharp, seed=27)
    return vignette(img, 0.3, color_='#141c26')
