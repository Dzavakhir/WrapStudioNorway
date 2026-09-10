"""Group g26 — Mavsum & ob-havo (Season & Weather): fog, golden_leaves, frost, sunrays, night."""
import math
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- shared helpers

def _norm(m):
    m = np.asarray(m, np.float32)
    return (m - m.min()) / (m.max() - m.min() + 1e-6)


def _rejection_points(r, n, density, tries_mult=25, y_max=None):
    """Sample ~n (x, y) points with probability proportional to `density` (H,W)."""
    pts = []
    tries = 0
    ymax = H if y_max is None else y_max
    while len(pts) < n and tries < n * tries_mult:
        tries += 1
        px, py = r.uniform(0, W - 1), r.uniform(0, ymax - 1)
        if r.random() < density[int(py), int(px)]:
            pts.append((px, py))
    return pts


def _ellip_dist():
    """Elliptical distance from the frame centre: 0 centre, 1 at the edge mid-points, ~1.41 at the corners."""
    x, y = coords()
    return np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2).astype(np.float32)


# ----------------------------------------------------------------------------- 126 fog

@effect('fog')
def fog(img):
    """Soft fog: the background dissolves into white mist with distance; the subject stays crisp in front."""
    person_hard = mask('person')
    person = mask('person', feather=2.5)
    bg_w = 1 - person
    face_zone = mask('face', feather=40, grow=30)

    # background as seen through mist: softer, paler, desaturated, a touch cooler
    bg = blur_background(img, sigma=3.5, person=person_hard)
    bg = saturation(bg, 0.45)
    bg = contrast(bg, 0.80, pivot=0.62)
    bg = fade(bg, 0.10, 0.0)
    bg = temperature(bg, -0.08)
    img = apply_mask(img, bg, bg_w)

    # fog density: thicker with distance (top of frame), drifting horizontal wisps, slow cloud variation
    depth = 0.50 + 0.50 * (1 - linear(90, 0.0, 1.0))            # 1 at the top -> 0.5 at the bottom
    wisp = fbm(4, seed=26, scale=1.0)
    wisp = _norm(cv2.GaussianBlur(wisp, (0, 0), sigmaX=70, sigmaY=9))
    cloud = fbm(3, seed=7, scale=0.6)
    density = depth * (0.66 + 0.34 * wisp) * (0.80 + 0.20 * cloud)
    ground = linear(90, 0.50, 1.0)                                # low mist only over the lower body
    fog_a = bg_w * density * 0.95 + person * (1 - face_zone) * 0.07 * ground * (0.6 + 0.4 * wisp)
    img = blend(img, '#eef0f2', 'screen', 1.0, mask_=np.clip(fog_a, 0, 1))

    # light scattering: gentle bloom, whisper of cool neutral tone
    img = glow(img, sigma=50, strength=0.14, threshold=0.7)
    img = temperature(img, -0.03)
    return img


# ----------------------------------------------------------------------------- 127 golden_leaves

_LEAF_COLOURS = [('#f2c65a', '#d49a2c'), ('#e8a33a', '#c07a1c'), ('#d97a2b', '#a85614'), ('#e9b445', '#bd8322'),
                 ('#cf6a2a', '#9c4a15'), ('#f0d070', '#cfa030'), ('#e08a30', '#b0611a'), ('#c65a22', '#8f3d12')]
_VEIN = '#7a4210'
_LEAF_HI = '#fff0b8'


def _fp(pts, S=16):
    """Float (N,2) points -> int32 (N,1,2) fixed-point for cv2 shift=4."""
    return np.round(np.asarray(pts, np.float64) * S).astype(np.int32).reshape(-1, 1, 2)


def _draw_leaf(col, alp, cx, cy, L, wd, th, light, dark, r, S):
    """One autumn leaf (pointed ellipse, gentle curl, two-tone fold, midrib + side veins, sunlit edge, stem)."""
    n = 26
    u = np.linspace(0.0, 1.0, n)
    x = (u - 0.5) * L
    p_top, p_bot = r.uniform(1.0, 1.5), r.uniform(1.0, 1.5)
    top = (wd / 2) * np.sin(np.pi * u) ** p_top
    bot = -(wd / 2) * np.sin(np.pi * u) ** p_bot
    bend = r.uniform(-1, 1) * 0.12 * L * ((u - 0.5) * 2) ** 2      # slight curl of the blade
    c, s = math.cos(th), math.sin(th)

    def world(px, py):
        return np.stack([cx + px * c - py * s, cy + px * s + py * c], 1)

    top_w = world(x, top + bend)
    bot_w = world(x, bot + bend)
    mid_w = world(x, bend)
    full = np.concatenate([top_w, bot_w[::-1]])
    lit = np.concatenate([top_w, mid_w[::-1]])
    cv2.fillPoly(col, [_fp(full)], color255(dark), cv2.LINE_AA, 4)
    cv2.fillPoly(alp, [_fp(full)], 255, cv2.LINE_AA, 4)
    cv2.fillPoly(col, [_fp(lit)], color255(light), cv2.LINE_AA, 4)
    # midrib and side veins
    k = int(n * 0.94)
    cv2.polylines(col, [_fp(mid_w[1:k])], False, color255(_VEIN), S, cv2.LINE_AA, 4)
    for uv in (0.26, 0.40, 0.54, 0.68, 0.80):
        i = int(uv * (n - 1))
        hw = (wd / 2) * math.sin(math.pi * uv) * 0.8
        for sign in (1, -1):
            a = math.radians(38) * sign
            ex, ey = x[i] + hw * math.cos(a) * 1.1, bend[i] + hw * math.sin(a)
            p0 = world(np.array([x[i]]), np.array([bend[i]]))[0]
            p1 = world(np.array([ex]), np.array([ey]))[0]
            cv2.line(col, tuple(_fp(p0)[0, 0]), tuple(_fp(p1)[0, 0]), color255(_VEIN), 1, cv2.LINE_AA, 4)
    # sunlit edge highlight along the upper blade
    cv2.polylines(col, [_fp(top_w[2:-2])], False, color255(_LEAF_HI), max(1, S // 2), cv2.LINE_AA, 4)
    # stem
    p0 = world(np.array([x[0]]), np.array([bend[0]]))[0]
    p1 = world(np.array([x[0] - 0.14 * L]), np.array([bend[0] - 0.02 * L]))[0]
    cv2.line(col, tuple(_fp(p0)[0, 0]), tuple(_fp(p1)[0, 0]), color255(_VEIN), S + 1, cv2.LINE_AA, 4)
    cv2.line(alp, tuple(_fp(p0)[0, 0]), tuple(_fp(p1)[0, 0]), 255, S + 1, cv2.LINE_AA, 4)


def _leaf_layer(r, count, size_rng, area=None, avoid=None, aspect=(0.38, 0.62), S=2):
    """Draw leaves at S x supersampling -> premultiplied colour (H,W,3) and alpha (H,W), both float32."""
    col = np.zeros((H * S, W * S, 3), np.uint8)
    alp = np.zeros((H * S, W * S), np.uint8)
    n = tries = 0
    while n < count and tries < count * 60:
        tries += 1
        cx, cy = r.uniform(-0.04, 1.04) * W, r.uniform(-0.04, 1.04) * H
        ix, iy = int(np.clip(cx, 0, W - 1)), int(np.clip(cy, 0, H - 1))
        if area is not None and r.random() > area[iy, ix]:
            continue
        if avoid is not None and r.random() < avoid[iy, ix]:
            continue
        L = r.uniform(*size_rng)
        wd = L * r.uniform(*aspect)
        light, dark = _LEAF_COLOURS[r.integers(len(_LEAF_COLOURS))]
        _draw_leaf(col, alp, cx * S, cy * S, L * S, wd * S, r.uniform(0, 2 * math.pi), light, dark, r, S)
        n += 1
    colf = cv2.resize(col, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    alpf = cv2.resize(alp, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return colf, alpf


def _composite_premul(img, colf, alpf, sigma=0.0, opacity=1.0, occlusion=None, shadow=0.0):
    """Composite a premultiplied layer; optional defocus (sigma), occlusion mask and soft contact shadow."""
    if occlusion is not None:
        colf = colf * occlusion[..., None]
        alpf = alpf * occlusion
    if sigma > 0:
        colf = blur(colf, sigma)
        alpf = blur(alpf, sigma)
    if shadow > 0:
        sh = blur(translate(np.repeat(alpf[..., None], 3, 2), 5, 9, border=cv2.BORDER_CONSTANT)[..., 0], 6)
        img = img * (1 - shadow * sh)[..., None]
    a = (alpf * opacity)[..., None]
    return clip(img * (1 - a) + colf * opacity)


@effect('golden_leaves')
def golden_leaves(img):
    """Falling golden leaves at three depths, drifting through warm autumn light."""
    r = rng(27)
    person_hard = mask('person')
    person = mask('person', feather=2.0)
    bg_w = 1 - person
    face_zone = mask('face', feather=45, grow=70)

    # warm autumn light: the park turns golden-orange, the subject only gets a gentle warmth
    bg = blur_background(img, sigma=2.0, person=person_hard)
    bg = hsl_adjust(bg, 95, width=55, sat=1.25, lum=0.04, shift=-62)
    bg = hsl_adjust(bg, 40, width=30, sat=1.15, lum=0.02)
    bg = temperature(bg, 0.22)
    bg = exposure(bg, 0.10)
    bg = split_tone(bg, shadows='#5a3a20', highlights='#ffd08a', strength=0.35)
    per = temperature(img, 0.08)
    per = exposure(per, 0.05)
    per = split_tone(per, shadows='#4a3020', highlights='#ffd9a0', strength=0.15)
    img = lerp(bg, per, person)

    # low autumn sun from the top-left sky, soft haze of warm light
    sun = radial(center=(W * 0.06, -H * 0.04), radius=1.0, softness=1.0) ** 1.6
    img = blend(img, '#ffd89a', 'screen', 1.0, mask_=sun * (0.55 * bg_w + 0.25 * person))
    img = blend(img, '#ffc070', 'soft_light', 1.0, mask_=linear(135, 0.0, 1.0) * 0.3 * bg_w)

    # leaves: far (small, slightly soft, hidden behind the subject) / mid (crisp) / near (large, defocused)
    far_c, far_a = _leaf_layer(r, 40, (22, 42), area=np.clip(bg_w - 0.2, 0, 1) / 0.8)
    img = _composite_premul(img, far_c, far_a, sigma=1.2, opacity=0.92, occlusion=bg_w)
    mid_c, mid_a = _leaf_layer(r, 26, (46, 90), avoid=face_zone)
    img = _composite_premul(img, mid_c, mid_a, sigma=0.35, opacity=1.0, shadow=0.16)
    near_c, near_a = _leaf_layer(r, 7, (110, 175), avoid=np.clip(face_zone + mask('face', feather=90, grow=160) * 0.8, 0, 1))
    img = _composite_premul(img, near_c, near_a, sigma=5.5, opacity=0.9)

    img = glow(img, sigma=40, strength=0.25, threshold=0.65)
    img = vignette(img, strength=0.18, color_='#3a2210')
    return img


# ----------------------------------------------------------------------------- 128 frost

def _fern(m, x, y, ang, length, depth, r, thick, val, step=5.0, every=2):
    """Recursive feathery ice dendrite: a wandering stem with alternating side branches that shrink toward the tip."""
    steps = max(3, int(length / step))
    px, py, a = x, y, ang
    for i in range(steps):
        a += r.normal(0, 0.06)
        nx, ny = px + step * math.cos(a), py + step * math.sin(a)
        v = float(val * (1.0 - 0.4 * i / steps))
        t = thick if i < steps * 0.5 else max(thick - 1, 1)
        cv2.line(m, (int(px * 16), int(py * 16)), (int(nx * 16), int(ny * 16)), v, t, cv2.LINE_AA, 4)
        if depth > 0 and i % every == 1 and i < steps - 1:
            side = 1 if (i // every) % 2 == 0 else -1
            bl = length * 0.42 * (1.0 - i / steps) ** 0.9 * r.uniform(0.7, 1.1)
            if bl > 6:
                _fern(m, nx, ny, a + side * r.uniform(0.8, 1.15), bl, depth - 1, r, max(thick - 1, 1), val * 0.85, step, every)
        px, py = nx, ny


def _frost_ferns(r):
    """Dendrites growing inward from all four frame edges (denser and longer at the corners) -> (H,W) mask."""
    m = np.zeros((H, W), np.float32)
    starts = []
    for _ in range(12):   # top / bottom edges
        t = r.uniform(0, 1); starts.append(((t * W, -4.0), math.pi / 2, t))
        t = r.uniform(0, 1); starts.append(((t * W, H + 4.0), -math.pi / 2, t))
    for _ in range(13):   # left / right edges
        t = r.uniform(0, 1); starts.append(((-4.0, t * H), 0.0, t))
        t = r.uniform(0, 1); starts.append(((W + 4.0, t * H), math.pi, t))
    for (x, y), a, t in starts:
        corner_w = 1.0 - 0.6 * math.sin(math.pi * t)                     # 1 at the corners, 0.4 mid-edge
        length = r.uniform(90, 200) * (0.6 + 0.9 * corner_w)
        _fern(m, x, y, a + r.uniform(-0.55, 0.55), length, 2, r, 3, r.uniform(0.75, 1.0))
    # small seed crystals scattered in the edge band
    d = _ellip_dist()
    band = smoothstep(0.55, 1.25, d)
    for (px, py) in _rejection_points(r, 80, band):
        _fern(m, px, py, r.uniform(0, 2 * math.pi), r.uniform(24, 60), 1, r, 2, r.uniform(0.5, 0.9))
    return np.clip(m, 0, 1)


@effect('frost')
def frost(img):
    """Cold blue grade; ice crystals creep in from the frame edges: milky frost front, veins, dendrites, glints."""
    r = rng(28)
    original = img
    # cold grade (skin keeps a little life)
    g = temperature(img, -0.3)
    g = saturation(g, 0.85)
    g = split_tone(g, shadows='#1c3b66', highlights='#d6e9ff', strength=0.35)
    g = contrast(g, 1.05)
    skin = mask('face_skin', feather=8)
    img = apply_mask(g, lerp(g, temperature(original, -0.08), 0.4), skin)
    # darken and cool the rim so the white crystals read
    img = vignette(img, strength=0.32, radius=1.0, softness=0.75, color_='#0f2545')

    d = _ellip_dist()
    band = smoothstep(0.74, 1.16, d)                                     # 0 centre -> 1 at the frame edge
    corner = smoothstep(0.90, 1.40, d)
    face_zone = mask('face', feather=50, grow=50)

    # milky frost body with an irregular growth front, crystalline veins and ice grain inside
    front = fbm(5, seed=13, scale=1.6)
    body = smoothstep(0.34, 0.72, band * (0.45 + 1.0 * front) + 0.24 * corner)
    v1 = smoothstep(0.62, 0.96, 1 - np.abs(2 * fbm(6, seed=3, scale=3.0) - 1))
    v2 = smoothstep(0.70, 0.98, 1 - np.abs(2 * fbm(6, seed=17, scale=6.0) - 1))
    grain_ = smoothstep(0.55, 0.95, noise(seed=9, sigma=1.2))
    milk = 0.32 + 0.28 * fbm(4, seed=21, scale=2.5)
    tex = milk + 0.5 * v1 + 0.35 * v2 + 0.2 * grain_
    frost_body = np.clip(body * tex, 0, 1)
    # feathery dendrites reaching past the front toward the centre
    ferns = _frost_ferns(r) * smoothstep(0.58, 0.98, d)
    layer = np.clip(frost_body + ferns * 0.95 + blur(ferns, 8) * 0.5 * band, 0, 1) * (1 - face_zone)
    layer = layer * (1 - 0.55 * mask('person', feather=6))   # the subject only lightly frosted
    img = blend(img, '#e8f4ff', 'screen', 0.88, mask_=layer)

    # glints and sparkles where the frost is thick
    specks = dust(count=450, seed=28, size=(0.8, 2.0)) * np.clip(body + ferns, 0, 1)
    img = blend(img, '#f6fbff', 'screen', 0.85, mask_=specks)
    pts = _rejection_points(r, 30, np.clip(frost_body * 1.2 + ferns, 0, 1) * band)
    sizes = [r.uniform(6, 15) for _ in pts]
    img = blend(img, sparkle_layer(pts, sizes, color_='#ffffff', seed=5), 'screen', 0.8)
    return img


# ----------------------------------------------------------------------------- 129 sunrays

def _beam_mask(center, angles, widths, gains):
    x, y = coords()
    ang = np.arctan2(y - center[1], x - center[0])
    m = np.zeros((H, W), np.float32)
    for a0, wdt, g in zip(angles, widths, gains):
        d = np.abs(((ang - a0 + math.pi) % (2 * math.pi)) - math.pi)
        m += np.exp(-(d / wdt) ** 2) * g
    dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) / math.hypot(W, H)
    return m, dist


@effect('sunrays')
def sunrays(img):
    """God rays streaming diagonally from the top-right corner across the whole scene, with warm haze and bloom."""
    r = rng(29)
    src = (W * 1.06, -H * 0.06)
    n = 17
    angles = list(r.uniform(math.radians(104), math.radians(170), n)) + [math.radians(a) for a in (118, 137, 155)]
    widths = list(r.uniform(0.012, 0.045, n)) + [0.07, 0.09, 0.075]
    gains = list(r.uniform(0.35, 1.0, n)) + [0.35, 0.4, 0.3]
    m, dist = _beam_mask(src, angles, widths, gains)
    broad, _ = _beam_mask(src, [math.radians(135)], [0.30], [1.0])
    m = _norm(m) + 0.35 * broad
    m *= (1 - smoothstep(0.12, 1.15, dist)) ** 1.1
    m *= 0.6 + 0.4 * fbm(4, seed=9, scale=0.9)                      # volumetric variation along the beams
    m = np.clip(m / max(m.max(), 1e-6), 0, 1)

    img = temperature(img, 0.15)
    haze = radial(center=src, radius=1.3, softness=1.0) ** 1.4
    img = blend(img, '#ffe0b0', 'screen', 1.0, mask_=haze * 0.32)      # atmospheric haze toward the sun
    skin = mask('face_skin', feather=10)
    features = np.clip(mask('eyes', feather=14, grow=14) + mask('brows', feather=10, grow=6) + mask('lips', feather=12, grow=8), 0, 1)
    strength = 0.82 * (1 - 0.42 * skin) * (1 - 0.55 * features)        # rays cross the face but never wash the eyes
    img = blend(img, '#ffe9b0', 'screen', 1.0, mask_=m * strength)
    sun = radial(center=src, radius=0.6, softness=1.0) ** 2.2
    img = blend(img, '#fff1d0', 'screen', 1.0, mask_=sun * 0.85)

    # dust motes glinting inside the beams
    dots = np.zeros((H, W), np.float32)
    face_zone = mask('face', feather=30, grow=20)
    for (px, py) in _rejection_points(r, 65, np.clip(m * 1.2, 0, 1) * (1 - face_zone), y_max=int(H * 0.9)):
        rad = r.uniform(1.0, 3.0)
        cv2.circle(dots, (int(px * 16), int(py * 16)), int(rad * 16), float(r.uniform(0.35, 0.9)), -1, cv2.LINE_AA, 4)
    img = blend(img, '#fff4d8', 'screen', 1.0, mask_=blur(dots, 1.0) * 0.7)

    img = glow(img, sigma=45, strength=0.35, threshold=0.6)
    return img


# ----------------------------------------------------------------------------- 130 night

@effect('night')
def night(img):
    """Night scene: deep blue darkness with a starry sky; the subject softly lit by a warm light, cool moon rim."""
    r = rng(30)
    original = img
    person_hard = mask('person')
    person = mask('person', feather=2.0)
    bg_w = 1 - person

    # --- background: deep blue night (moonlit silhouettes of the trees stay faintly readable)
    bg = exposure(img, -2.0)
    bg = temperature(bg, -0.5)
    bg = hsl_adjust(bg, 100, width=50, sat=0.45)
    bg = split_tone(bg, shadows='#0b1a3f', highlights='#3a5a9a', balance=-0.15, strength=0.45)
    bg = blend(bg, '#0c2050', 'screen', 1.0, mask_=0.22 + 0.30 * (1 - linear(90)))

    # --- person: dimmer and cooler, then relit by a warm key light from the upper left
    per = exposure(img, -0.75)
    per = temperature(per, -0.12)
    per = saturation(per, 0.92)
    fx, fy = face_center()
    key = radial(center=(fx - 60, fy - 80), radius=0.66, softness=0.9)
    warm_gain = np.array([0.78, 0.55, 0.26], np.float32)
    per = clip(per * (1 + key[..., None] * warm_gain))
    img = lerp(bg, per, person)
    # light spill onto the background right next to the subject, soft glow of the lamp on the face
    spill = key * bg_w * 0.22
    img = blend(img, '#ffb676', 'screen', 1.0, mask_=spill)
    img = blend(img, '#ffc98a', 'screen', 1.0, mask_=key * person * 0.16)

    # --- cool moon rim along the edges of the silhouette facing the upper-left
    pm = blur(person_hard, 6)
    gy, gx = np.gradient(pm)
    mag = np.sqrt(gx * gx + gy * gy) + 1e-6
    lx, ly = -0.55, -0.83
    facing = np.clip((-gx * lx - gy * ly) / mag, 0, 1)
    rim = inner_edge(person_hard, width=10, softness=5) * facing
    img = blend(img, '#8fb8ff', 'screen', 1.0, mask_=rim * 0.6)

    # --- stars: denser where the real sky was, sprinkled across the dark upper background
    sky_like = smoothstep(0.02, 0.15, original[..., 2] - original[..., 0]) * smoothstep(0.45, 0.7, luminance(original))
    sky_like = blur(sky_like, 12)
    upper = 1 - linear(90, 0.30, 0.55)
    density = mask('background', feather=3) * (1 - mask('person', feather=6, grow=12)) * upper * (0.22 + 0.78 * sky_like)
    pts = _rejection_points(r, 170, np.clip(density * 1.4, 0, 1))
    stars = np.zeros((H, W), np.float32)
    for (px, py) in pts:
        rad = r.uniform(0.7, 2.2) ** 1.3
        cv2.circle(stars, (int(px * 16), int(py * 16)), max(4, int(rad * 16)), float(r.uniform(0.45, 1.0)), -1, cv2.LINE_AA, 4)
    stars = np.clip(blur(stars, 0.7) + blur(stars, 5) * 0.6, 0, 1)
    star_layer = stars[..., None] * color('#f2f5ff')
    bright = [pts[i] for i in r.choice(len(pts), size=min(8, len(pts)), replace=False)]
    star_layer = np.clip(star_layer + sparkle_layer(bright, [r.uniform(8, 15) for _ in bright], color_='#fff6e0', seed=3) * 0.85, 0, 1)
    img = blend(img, star_layer, 'screen', 1.0)

    img = glow(img, sigma=30, strength=0.3, threshold=0.55)
    img = vignette(img, strength=0.4)
    img = grain(img, amount=0.025, seed=30)
    return img
