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
    Skin (hue 4-16), lips, the red sleeve (~355) and the navy hijab (~240) all fall outside the window, so the
    weight can be used over the whole frame and also cleans the green fringe along the subject outline."""
    hsv = rgb2hsv(img)
    h, s = hsv[..., 0], hsv[..., 1]
    w = smoothstep(lo - soft, lo + soft, h) * (1 - smoothstep(hi - soft, hi + soft, h)) * smoothstep(min_sat, min_sat * 3, s)
    if protect_face:
        w = w * (1 - mask('face', 6, grow=4))
    return w.astype(np.float32)


def _skin_guard(img, ref, amount=0.5, feather_=6, grow=-6, lips=True):
    """Pull the face-skin (and lips) hue & saturation back towards the ungraded reference; luminance keeps the grade."""
    m = mask('face_skin', feather_, grow=grow)
    if lips:
        m = np.clip(m + mask('lips', 3), 0, 1)
    m = m * amount
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


def _ellipse_pts(cx, cy, a, b, rot_deg, n=28, pointed=0.0):
    """Polygon points of a rotated ellipse; pointed>0 pinches the ends (leaf / petal shapes)."""
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = math.radians(rot_deg)
    ex, ey = a * np.cos(t), b * np.sin(t)
    if pointed:
        ey = ey * (1 - np.abs(np.cos(t))) ** pointed
    x = cx + ex * math.cos(r) - ey * math.sin(r)
    y = cy + ex * math.sin(r) + ey * math.cos(r)
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

def _falling_leaves(seed=25):
    """A handful of drifting autumn leaves (pointed leaf shapes), a few big defocused ones, none over the face."""
    r = rng(seed)
    face_zone = mask('face', 30, grow=40)
    cols = ['#e8862a', '#f0a030', '#c8541c', '#f2b93a', '#d9732a']

    def draw(d, count, size, alpha):
        n = 0
        tries = 0
        while n < count and tries < 3000:
            tries += 1
            x, y = r.uniform(0, W), r.uniform(0, H * 0.9)
            if face_zone[int(y), int(x)] > 0.12:
                continue
            L = r.uniform(*size)
            col = color255(cols[r.integers(len(cols))]) + (int(r.uniform(*alpha)),)
            d.polygon(_ellipse_pts(x, y, L, L * r.uniform(0.38, 0.55), r.uniform(0, 180), pointed=0.35), fill=col)
            n += 1
    mid = _rgba_layer(lambda d: draw(d, 14, (12, 24), (200, 255)), 1.3)
    near = _rgba_layer(lambda d: draw(d, 4, (34, 52), (170, 220)), 6.0)
    return [mid + (0.95,), near + (0.85,)]


@effect('autumn')
def autumn(img):
    """Golden autumn: every green turns orange/amber (deep greens -> red-orange), warm low sun from the left,
    golden haze, a few drifting leaves."""
    orig = img
    p = _person()
    w = _foliage(img, lo=36, hi=180)
    hsv = rgb2hsv(img)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    t = np.clip((h - 36.0) / (180.0 - 36.0), 0, 1)
    target = 37.0 - 21.0 * t                                    # yellow-greens -> orange-amber, deep greens -> red-orange
    hsv[..., 0] = h * (1 - w) + target * w
    hsv[..., 1] = np.clip(s * (1 + 0.45 * w) + 0.12 * w, 0, 1)
    hsv[..., 2] = np.clip(v + 0.06 * w, 0, 1)
    img = hsv2rgb(hsv)
    img = temperature(img, 0.22)
    img = split_tone(img, shadows='#4a2a14', highlights='#ffcf7a', strength=0.35)
    # warm low sun coming through the trees on the left + golden haze over the background
    sun_c = (-W * 0.08, H * 0.26)
    sun = radial(center=sun_c, radius=1.3, softness=0.95)
    img = blend(img, '#ffb45c', 'screen', 0.75, mask_=sun)
    haze = (1 - p) * (0.10 + 0.14 * (1 - linear(0, 0.0, 1.0)))
    img = blend(img, '#ffb060', 'normal', 1.0, mask_=haze)
    ry = rays(center=sun_c, count=12, seed=25, sharpness=8, spread=1.3)
    img = blend(img, '#ffe0a0', 'screen', 0.45, mask_=ry * (1 - 0.5 * p))
    for rgb, alpha, op in _falling_leaves():
        img = _composite(img, rgb, alpha, op)
    img = _bloom(img, sigma=45, strength=0.25, threshold=0.55, color_='#ffe2b4')
    img = s_curve(img, 0.06)
    img = _skin_guard(img, orig, amount=0.5)
    return vignette(img, strength=0.2, radius=1.0, softness=0.8, color_='#2a1408')


# ----------------------------------------------------------------------------- 122 winter

def _snow_layer(seed=25):
    face_soft = mask('face', 35, grow=25)
    far = blur(_dots(480, (1.3, 2.6), seed, alpha=(0.35, 0.8), elong=(1.2, 1.7), area=1 - 0.85 * face_soft), 0.8)
    mid = blur(_dots(130, (2.6, 5.0), seed + 1, alpha=(0.5, 1.0), elong=(1.1, 1.5), area=1 - 0.9 * face_soft), 1.4)
    near = blur(_dots(32, (7, 15), seed + 2, alpha=(0.25, 0.5), area=1 - 0.95 * face_soft), 5)
    return np.clip(far + mid + near, 0, 1)


def _settled_snow(p, seed=33):
    """Light dusting of snow on the upward-facing edges of the subject (top of the hijab, shoulders, sleeve)."""
    mb = blur(p, 6)
    gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
    up = np.clip(gy / (np.sqrt(gx * gx + gy * gy) + 1e-5), 0, 1)     # mask grows downward = edge faces up
    band = inner_edge(p, 7, 2.5)
    tex = smoothstep(0.30, 0.70, fbm(5, seed, 3.0))
    return np.clip(band * up ** 2 * tex * 1.3, 0, 1)


@effect('winter')
def winter(img):
    """Cold winter: frozen foggy background with snow-laden foliage and snowy ground, overcast sky, silver-blue
    grade, falling snow; the face keeps its natural colour."""
    orig = img
    p = _person()
    bg = 1 - _person(3.0)
    w = _foliage(img, lo=36, hi=180)
    hsv = rgb2hsv(img)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    sky = smoothstep(185, 200, h) * (1 - smoothstep(250, 265, h)) * smoothstep(0.08, 0.25, s) * bg
    # snow clumps = the locally brightest spots of the foliage
    l = luminance(img)
    lm = blur(l, 20)
    lsd = np.sqrt(np.maximum(blur((l - lm) ** 2, 20), 1e-4))
    clumps = blur(smoothstep(0.35, 1.3, (l - lm) / (lsd + 0.03)), 1.2) * w
    hsv[..., 1] = s * (1 - 0.88 * w) * (1 - 0.75 * sky)
    hsv[..., 2] = np.clip(v * (1 - bg) + (0.20 + 0.62 * v) * bg + 0.16 * sky, 0, 1)
    wb = hsv2rgb(hsv)
    wb = clip(wb * np.array([0.90, 0.95, 1.06], np.float32))
    wb = lerp(wb, as_layer('#f3f7fb'), clumps * 0.85)
    ground = w * smoothstep(H * 0.62, H * 0.80, coords()[1]) * bg           # grass -> snow-covered ground
    snow_tex = (0.9 + 0.1 * fbm(5, 31, 2.0))[..., None]
    wb = lerp(wb, as_layer('#eef3f8') * snow_tex, ground * 0.85)
    num = blur(wb * bg[..., None], 2.2)
    den = blur(bg, 2.2)[..., None]
    wb = lerp(wb, num / np.maximum(den, 1e-3), bg)                            # misty softness on the background only
    img = lerp(img, wb, np.clip(bg + w * (1 - bg), 0, 1))
    img = temperature(img, -0.22)
    img = split_tone(img, shadows='#2b3d5c', highlights='#e6eef8', strength=0.35)
    img = saturation(img, 0.85)
    lin = linear(90)
    haze_m = np.clip(bg * (0.16 + 0.20 * (1 - lin)) * (0.8 + 0.4 * fbm(4, 25, 0.7)) + p * 0.04, 0, 1)
    img = blend(img, '#e3eaf1', 'normal', 1.0, mask_=haze_m)
    img = blend(img, '#f4f8ff', 'screen', 0.8, mask_=_settled_snow(p))
    img = blend(img, '#f6f9ff', 'screen', 0.92, mask_=_snow_layer())
    skin = np.clip(mask('face_skin', 6, grow=-4) + mask('lips', 3), 0, 1)
    img = blend(img, orig, 'color', 0.8, mask_=skin)
    return vignette(img, 0.18, color_='#1f2b3c')


# ----------------------------------------------------------------------------- 123 spring

def _blossoms(seed=25):
    """Three blossom layers: blossom dots on the trees behind, defocused clusters in the top corners (shooting through
    a blossoming branch) and a few drifting petals. Returns [(rgb, alpha, opacity), ...] to composite in order."""
    r = rng(seed)
    p = _person()
    face_zone = mask('face', 30, grow=30)
    pinks = ['#ffb7c5', '#ffc9d6', '#f7a3b6', '#ffd6df', '#fbbcc9']
    layers = []
    bg_top = (1 - p) * (1 - linear(90, 0.12, 0.72))

    def draw_bg(d):
        n = 0
        tries = 0
        while n < 210 and tries < 8000:
            tries += 1
            x, y = r.uniform(0, W), r.uniform(0, H * 0.8)
            if r.random() > bg_top[int(y), int(x)]:
                continue
            sz = r.uniform(12, 30)
            _flower(d, x, y, sz, pinks[r.integers(len(pinks))], r.uniform(0, 72), alpha=int(r.uniform(150, 230)))
            n += 1
    layers.append(_rgba_layer(draw_bg, 2.0) + (0.8,))

    def draw_fg(d):
        for (cx, cy, count, spread) in ((70, 70, 7, 90), (1090, 60, 6, 80), (1130, 330, 3, 60)):
            for _ in range(count):
                x, y = cx + r.normal(0, spread * 0.55), cy + r.normal(0, spread * 0.5)
                sz = r.uniform(48, 90)
                _flower(d, x, y, sz, pinks[r.integers(len(pinks))], r.uniform(0, 72), alpha=int(r.uniform(200, 245)))
    layers.append(_rgba_layer(draw_fg, 5.0) + (0.85,))

    petal_area = np.clip((1 - face_zone) * (1 - 0.7 * p), 0, 1)

    def draw_petals(d):
        n = 0
        tries = 0
        while n < 38 and tries < 4000:
            tries += 1
            x, y = r.uniform(0, W), r.uniform(0, H * 0.9)
            if r.random() > petal_area[int(y), int(x)]:
                continue
            L = r.uniform(5, 11)
            d.polygon(_ellipse_pts(x, y, L, L * r.uniform(0.4, 0.65), r.uniform(0, 180), pointed=0.2),
                      fill=color255(pinks[r.integers(len(pinks))]) + (int(r.uniform(190, 255)),))
            n += 1
    layers.append(_rgba_layer(draw_petals, 1.0) + (0.95,))
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
    img = blend(img, '#fff6f0', 'screen', 0.18, mask_=1 - linear(90, 0.0, 0.7))
    img = _bloom(img, sigma=50, strength=0.28, threshold=0.6, color_='#fff4ec')
    img = vibrance(img, 0.15)
    return _skin_guard(img, orig, amount=0.4)


# ----------------------------------------------------------------------------- 124 summer

@effect('summer')
def summer(img):
    """Bright sunny summer: vivid colours, deeper blue sky, warm bright light, sun rays and a sun glow top-right."""
    orig = img
    p = _person()
    facez = mask('face', 12, grow=4)
    img = lerp(vibrance(img, 0.45), vibrance(img, 0.15), facez)
    img = hsl_adjust(img, 210, width=40, sat=1.5, lum=-0.02)   # deeper blue sky
    img = hsl_adjust(img, 95, width=50, sat=1.2, lum=0.04)     # lush greens
    img = temperature(img, 0.16)
    img = brightness(img, 0.05)
    img = s_curve(img, 0.08)
    sun_pos = (W * 0.90, H * 0.07)
    corner = radial(center=sun_pos, radius=1.05, softness=0.95)
    img = blend(img, '#fff1c4', 'screen', 0.7, mask_=corner)
    ry = rays(center=(W * 0.92, H * 0.05), count=10, seed=7, sharpness=8, spread=1.4)
    img = blend(img, '#fff0c0', 'screen', 0.4, mask_=ry)
    rim = inner_edge(p, 12, 6) * radial(center=sun_pos, radius=1.3, softness=0.9) * (1 - mask('face', 10, grow=6))
    img = blend(img, '#ffe6b0', 'screen', 0.55, mask_=rim)
    img = lens_flare(img, pos=sun_pos, strength=0.55, ghosts=False, streak=False)
    img = _bloom(img, 30, 0.3, 0.6, '#fff0d0')
    return _skin_guard(img, orig, 0.4)


# ----------------------------------------------------------------------------- 125 rain

def _rain_lines(count, length, thickness, seed, alpha, d):
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(count):
        L = r.uniform(*length)
        x0, y0 = r.uniform(-50, W + 50), r.uniform(-150, H + 50)
        x1, y1 = x0 + d[0] * L, y0 + d[1] * L
        cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), float(r.uniform(*alpha)), thickness, cv2.LINE_AA)
    return m


def _stamp_drop(mx, my, inside, shade, x, y, cx, cy, rx, ry, spec=True):
    """One water drop: inverted/shrunk refraction of the scene inside, thin glassy rim, small specular."""
    x0, x1 = int(max(0, cx - rx - 3)), int(min(W, cx + rx + 4))
    y0, y1 = int(max(0, cy - ry - 3)), int(min(H, cy + ry + 4))
    if x1 <= x0 or y1 <= y0:
        return
    xs, ys = x[y0:y1, x0:x1], y[y0:y1, x0:x1]
    dx, dy = (xs - cx) / rx, (ys - cy) / ry
    dsq = dx * dx + dy * dy
    d = np.sqrt(dsq)
    core = 1 - smoothstep(0.93, 1.0, d)
    s = 1 - 1.7 * np.sqrt(np.clip(1 - dsq, 0, 1))              # -0.7 at the centre (inverted), 1 at the rim
    sel = core > 0
    mx[y0:y1, x0:x1] = np.where(sel, cx + (xs - cx) * s, mx[y0:y1, x0:x1])
    my[y0:y1, x0:x1] = np.where(sel, cy + (ys - cy) * s, my[y0:y1, x0:x1])
    rim = smoothstep(0.80, 0.94, d) * (1 - smoothstep(0.94, 1.0, d))
    ang = np.arctan2(dy, dx)
    light = 0.5 + 0.5 * np.cos(ang - math.radians(-125))
    sh = rim * (0.22 * light - 0.10 * (1 - light)) - 0.05 * smoothstep(0.55, 0.85, d) * (1 - smoothstep(0.85, 0.95, d))
    if spec:
        sh = sh + np.exp(-((dx + 0.35) ** 2 + (dy + 0.40) ** 2) / (2 * 0.10 ** 2)) * 0.30
    inside[y0:y1, x0:x1] = np.maximum(inside[y0:y1, x0:x1], core)
    shade[y0:y1, x0:x1] += sh * core


def _lens_droplets(img, sharp, seed=27, count=90, avoid=None):
    """Water drops on the wet glass in front of the lens, some running with small trails; none over the face."""
    r = rng(seed)
    x, y = coords()
    mx, my = x.copy(), y.copy()
    inside = np.zeros((H, W), np.float32)
    shade = np.zeros((H, W), np.float32)
    drops = []
    n = 0
    tries = 0
    while n < count and tries < count * 60:
        tries += 1
        cx, cy = r.uniform(14, W - 14), r.uniform(14, H - 14)
        rad = 5 + 20 * r.random() ** 1.8
        if avoid is not None and avoid[int(cy), int(cx)] > 0.15:
            continue
        if any((cx - a) ** 2 + (cy - b) ** 2 < (rad + c + 10) ** 2 for a, b, c in drops):
            continue
        drops.append((cx, cy, rad))
        n += 1
        run = rad > 9 and r.random() < 0.45
        e = r.uniform(1.15, 1.6) if run else r.uniform(0.9, 1.15)
        _stamp_drop(mx, my, inside, shade, x, y, cx, cy, rad, rad * e, spec=rad > 7)
        if run:
            ty, tx = cy - rad * e, cx
            for _ in range(int(r.integers(2, 5))):
                ty -= r.uniform(rad * 0.9, rad * 1.8)
                tx += r.uniform(-rad * 0.25, rad * 0.25)
                rr = rad * r.uniform(0.25, 0.45)
                _stamp_drop(mx, my, inside, shade, x, y, tx, ty, rr, rr * 1.2, spec=False)
    refr = cv2.remap(sharp, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    refr = clip((refr - 0.5) * 1.15 + 0.53)
    out = lerp(img, refr, inside)
    return clip(out + shade[..., None])


@effect('rain')
def rain(img):
    """Rain: cool blue-grey damp grade, misty distance, two depths of slanted rain streaks, drops on the lens."""
    p = _person()
    img = exposure(img, -0.1)
    img = temperature(img, -0.28)
    img = saturation(img, 0.72)
    img = split_tone(img, shadows='#243449', highlights='#b9c7d6', strength=0.4)
    img = fade(img, 0.06, 0.03)
    mist = (1 - p) * (0.18 + 0.12 * (1 - linear(90)))
    img = blend(img, '#93a2b3', 'normal', 1.0, mask_=mist)
    sharp = img
    img = blur(img, 1.0)
    d = (-math.sin(math.radians(12)), math.cos(math.radians(12)))
    far = _streak_blur(_rain_lines(520, (40, 110), 1, seed=25, alpha=(0.25, 0.55), d=d), 13, *d) * 1.6
    near = blur(_streak_blur(_rain_lines(170, (120, 260), 2, seed=26, alpha=(0.3, 0.7), d=d), 25, *d), 1.0) * 1.7
    face_soft = mask('face', 30, grow=10)
    streaks = np.clip(far + near, 0, 1) * (1 - 0.4 * face_soft)
    img = blend(img, '#e4ecf4', 'screen', 0.5, mask_=streaks)
    img = _lens_droplets(img, sharp, seed=27, avoid=mask('face', 12, grow=28))
    return vignette(img, 0.3, color_='#141c26')
