"""Group g23 — Effektlar (Effects): glitch, vhs, double_exposure, reflection, prism."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _person(feather_=1.5, grow=0):
    """Cleaned person mask (the stored mask has a 0.035 floor / 0.996 ceiling): solid core, soft edge."""
    p = smoothstep(0.03, 0.97, mask('person', grow=grow))
    return feather(p, feather_) if feather_ else p


def _rgb_split(img, dx, dy=0):
    """Flat RGB channel split: R shifted (+dx, +dy), B shifted (-dx, -dy), G in place (wrap-around)."""
    r = np.roll(img[..., 0], (dy, dx), axis=(0, 1))
    b = np.roll(img[..., 2], (-dy, -dx), axis=(0, 1))
    return np.stack([r, img[..., 1], b], axis=-1)


def _cos_window(h, w, m):
    """Separable raised-cosine plateau window (h, w) with an m px soft margin."""
    def prof(n):
        t = np.arange(n, dtype=np.float32)
        a = np.clip(np.minimum(t, n - 1 - t) / max(m, 1), 0, 1)
        return 0.5 - 0.5 * np.cos(np.pi * a)
    return prof(h)[:, None] * prof(w)[None, :]


def _foliage_layer(img, seed=23, cols=6, rows=(150, 215, 215, 215, 215, 215, 215), margin=40):
    """Full-frame 'trees' layer built ONLY from the clean foliage of the background (no ghost of the person):
    the frame is covered by an irregular grid of foliage patches cut from the person-free, sky-free part of the
    photo, each mildly enlarged/flipped and cross-faded 2-way with its neighbours; outside the silhouette the
    real background is kept."""
    r = rng(seed)
    x, y = coords()
    pm = cv2.dilate((mask('person') > 0.5).astype(np.float32), np.ones((25, 25), np.uint8))
    sky = ((img[..., 2] > img[..., 0] + 0.08) & (luminance(img) > 0.55)).astype(np.float32)
    sky = cv2.dilate(sky, np.ones((15, 15), np.uint8))
    blocked = np.maximum(np.maximum(pm, sky), (y >= 585).astype(np.float32))       # fence & bystander below
    S = np.zeros((H + 1, W + 1), np.float64)
    S[1:, 1:] = np.cumsum(np.cumsum(blocked, 0), 1)

    def clean_positions(ch, cw):
        if ch > H or cw > W:
            return None
        tot = (S[ch:, cw:] - S[:-ch, cw:] - S[ch:, :-cw] + S[:-ch, :-cw])[::4, ::4]
        pos = np.argwhere(tot < 0.5) * 4
        return pos if len(pos) else None

    acc = np.zeros((H, W, 3), np.float32)
    wsum = np.zeros((H, W), np.float32)
    ys = np.concatenate([[0], np.cumsum(rows)]).astype(int)
    for j in range(len(rows)):
        # irregular column boundaries per row so seams never line up into a grid
        xs = np.linspace(0, W, cols + 1)
        xs[1:-1] += r.uniform(-45, 45, cols - 1)
        xs = xs.astype(int)
        jy = int(r.integers(-18, 19))
        for i in range(cols):
            X0, Y0 = xs[i] - margin, ys[j] - margin + jy
            X1, Y1 = xs[i + 1] + margin, ys[j + 1] + margin + jy
            nw, nh = X1 - X0, Y1 - Y0
            tries = [(float(r.uniform(1.15, 1.9)), float(r.uniform(1.15, 1.9))) for _ in range(20)]
            tries.sort(key=lambda t: t[0] * t[1])
            chosen = None
            for sx, sy in tries[int(r.integers(0, 4)):]:                     # not always the smallest scale
                cw, ch = int(math.ceil(nw / sx)), int(math.ceil(nh / sy))
                pos = clean_positions(ch, cw)
                if pos is not None:
                    py, px = pos[r.integers(len(pos))]
                    chosen = (int(px), int(py), cw, ch)
                    break
            if chosen is None:
                continue
            px, py, cw, ch = chosen
            patch = img[py:py + ch, px:px + cw]
            if r.random() < 0.5:
                patch = patch[:, ::-1]
            if r.random() < 0.3:
                patch = patch[::-1, :]
            patch = cv2.resize(np.ascontiguousarray(patch), (nw, nh), interpolation=cv2.INTER_CUBIC)
            win = _cos_window(nh, nw, margin)
            xa, ya = max(0, X0), max(0, Y0)
            xb, yb = min(W, X1), min(H, Y1)
            if xb <= xa or yb <= ya:
                continue
            pa = patch[ya - Y0:yb - Y0, xa - X0:xb - X0]
            wa = win[ya - Y0:yb - Y0, xa - X0:xb - X0]
            acc[ya:yb, xa:xb] += pa * wa[..., None]
            wsum[ya:yb, xa:xb] += wa
    layer = acc / np.maximum(wsum, 1e-3)[..., None]
    hole = wsum < 0.05
    if hole.any():
        layer = np.where(hole[..., None], blur(layer, 40), layer)
    layer = unsharp(clip(layer), 1.5, 0.3)
    keep_bg = feather(smoothstep(0.03, 0.97, 1 - mask('person', grow=10)), 6)
    return clip(lerp(layer, img, keep_bg))


def _text_layer(fn):
    """Render white text/shapes on black via fn(ImageDraw) -> (H,W,3) float layer."""
    pil = Image.new('RGB', (W, H), (0, 0, 0))
    fn(ImageDraw.Draw(pil))
    return from_pil(pil)


# ----------------------------------------------------------------------------- 111 glitch

@effect('glitch')
def glitch(img):
    """Digital glitch: flat RGB channel split, displaced horizontal slices (some inverted / single-channel /
    pixelated), thin scanline zones and small blocks of colour corruption. The eyes and mouth stay readable."""
    r = rng(2311)
    x, y = coords()
    out = saturation(contrast(img, 1.08), 1.1)
    face_soft = mask('face', feather=25, grow=20)
    face_hard = mask('face', grow=14)
    # 1. RGB split: strong everywhere, gentle over the face
    out = lerp(_rgb_split(out, 9, 1), _rgb_split(out, 3, 0), face_soft)

    # 2. displaced horizontal slices
    eye_zone = (455, 645)
    mouth_zone = (735, 835)

    def overlaps(y0, y1, zone):
        return not (y1 < zone[0] or y0 > zone[1])

    kinds = ['invert', 'mono_r', 'pixel', 'split', 'split'] + ['plain'] * 9
    r.shuffle(kinds)
    for kind in kinds:
        h = int(r.integers(10, 110))
        if kind == 'invert':                                  # keep the inversion off the face rows
            y0 = int(r.choice([r.integers(0, 260), r.integers(1010, H - h)]))
        else:
            y0 = int(r.integers(0, H - h))
        y1 = y0 + h
        sensitive = overlaps(y0, y1, eye_zone) or overlaps(y0, y1, mouth_zone)
        mag = int(r.integers(14, 27)) if sensitive else int(r.integers(20, 81))
        shift = mag * int(r.choice([-1, 1]))
        band = np.roll(out[y0:y1], shift, axis=1)
        if kind == 'invert':
            band = 1 - band
        elif kind == 'mono_r':
            band = np.stack([band[..., 0] * 1.05, band[..., 1] * 0.35, band[..., 2] * 0.45], -1)
        elif kind == 'pixel' and not sensitive:
            small = cv2.resize(band, (max(1, band.shape[1] // 10), max(1, band.shape[0] // 10)), interpolation=cv2.INTER_AREA)
            band = cv2.resize(small, (band.shape[1], band.shape[0]), interpolation=cv2.INTER_NEAREST)
        elif kind == 'split':
            band = _rgb_split(band, 8 if sensitive else 26)
        if kind == 'plain' and r.random() < 0.4:
            band = clip(band + r.uniform(-0.06, 0.08))
        out[y0:y1] = clip(band)

    # 3. thin scanline zones
    for _ in range(3):
        h = int(r.integers(50, 150)); y0 = int(r.integers(0, H - h))
        m = ((np.arange(y0, y0 + h) % 4) < 2).astype(np.float32)[:, None, None]
        out[y0:y0 + h] = clip(out[y0:y0 + h] * (1 - 0.32 * m) + 0.03)

    # 4. small blocks of corruption: solid colour chips + displaced pixel blocks
    palette = ['#00e8ff', '#ff2ad4', '#ffffff', '#0a0a0a', '#c8ff1e', '#2d5bff']
    placed = 0
    while placed < 70:
        w = int(r.integers(6, 72)); h = int(r.integers(3, 17))
        x0 = int(r.integers(0, W - w)); y0 = int(r.integers(0, H - h))
        if face_hard[y0 + h // 2, x0 + w // 2] > 0.2:
            continue
        col = color(palette[r.integers(len(palette))])
        a = float(r.uniform(0.65, 1.0))
        out[y0:y0 + h, x0:x0 + w] = out[y0:y0 + h, x0:x0 + w] * (1 - a) + col * a
        placed += 1
    placed = 0
    while placed < 14:
        w = int(r.integers(40, 220)); h = int(r.integers(8, 42))
        x0 = int(r.integers(0, W - w)); y0 = int(r.integers(0, H - h))
        if face_hard[y0 + h // 2, x0 + w // 2] > 0.2:
            continue
        sx = int(np.clip(x0 + r.integers(-160, 161), 0, W - w)); sy = int(np.clip(y0 + r.integers(-160, 161), 0, H - h))
        src = out[sy:sy + h, sx:sx + w]
        perm = [[2, 1, 0], [0, 2, 1], [1, 0, 2]][int(r.integers(3))]
        out[y0:y0 + h, x0:x0 + w] = src[..., perm]
        placed += 1

    # 5. a few thin bright lines
    for _ in range(9):
        y0 = int(r.integers(0, H - 2)); x0 = int(r.integers(0, W)); L = int(r.integers(120, 700))
        col = color(['#ffffff', '#00e8ff', '#ff2ad4'][r.integers(3)])
        t = int(r.integers(1, 3))
        out[y0:y0 + t, x0:min(W, x0 + L)] = lerp(out[y0:y0 + t, x0:min(W, x0 + L)], col, 0.7)
    return grain(out, 0.02, seed=5)


# ----------------------------------------------------------------------------- 112 vhs

@effect('vhs')
def vhs(img):
    """VHS tape: lifted blacks, chroma bleed + delay, soft luma, scanlines, tape noise, line wobble,
    a tracking-error band near the bottom, dropout streaks and a glowing 'PLAY' / timecode OSD."""
    r = rng(2312)
    x, y = coords()
    out = fade(img, 0.10, 0.05)
    out = tint(temperature(out, 0.10), 0.07)
    # colour bleed: luma stays fairly sharp, chroma smeared horizontally and delayed 6 px
    ycc = cv2.cvtColor(np.ascontiguousarray(out), cv2.COLOR_RGB2YCrCb)
    Y = cv2.GaussianBlur(ycc[..., 0], (0, 0), sigmaX=1.4, sigmaY=0.4)
    Cr = cv2.GaussianBlur(ycc[..., 1], (0, 0), sigmaX=7.0, sigmaY=1.5)
    Cb = cv2.GaussianBlur(ycc[..., 2], (0, 0), sigmaX=7.0, sigmaY=1.5)
    M = np.array([[1, 0, 6], [0, 1, 0]], np.float32)
    Cr = cv2.warpAffine(Cr, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    Cb = cv2.warpAffine(Cb, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    out = cv2.cvtColor(np.stack([Y, Cr, Cb], -1), cv2.COLOR_YCrCb2RGB)
    out = saturation(clip(out), 0.9)

    # line wobble + tracking band + head-switching noise (per-row horizontal displacement)
    yy = np.arange(H, dtype=np.float32)
    dx_row = 2.2 * np.sin(2 * np.pi * yy / 113 + 0.7) + 1.3 * np.sin(2 * np.pi * yy / 29)
    band = smoothstep(1165, 1185, yy) * (1 - smoothstep(1250, 1272, yy))
    jit = cv2.GaussianBlur(r.uniform(-1, 1, (H, 1)).astype(np.float32), (0, 0), sigmaX=0.1, sigmaY=1.2)[:, 0]
    dx_row += band * 30 * jit
    head = smoothstep(1400, 1412, yy)
    dx_row += head * 55 * jit
    map_x = (x + dx_row[:, None]).astype(np.float32)
    out = cv2.remap(out, map_x, y.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # luminance streaks inside the tracking band + bottom tear
    streak = cv2.GaussianBlur(r.uniform(-1, 1, (H, 1)).astype(np.float32), (0, 0), sigmaX=0.1, sigmaY=0.8)[:, 0]
    out = clip(out + (band * 0.22 * streak + head * 0.3 * streak)[:, None, None])
    out = lerp(out, gray(out), (band * 0.6 + head * 0.8)[:, None])

    # scanlines (soft cosine profile, period 6) and colour tape noise
    sl = 0.5 - 0.5 * np.cos(2 * np.pi * y / 6.0)
    out = clip(out * (1 - 0.22 * sl[..., None]))
    out = grain(out, 0.075, size=1.4, mono=False, seed=12)
    # dropouts: short bright horizontal dashes
    for _ in range(38):
        y0 = int(r.integers(0, H - 2)); x0 = int(r.integers(0, W)); L = int(r.integers(15, 170))
        t = int(r.integers(1, 3)); a = float(r.uniform(0.35, 0.85))
        out[y0:y0 + t, x0:min(W, x0 + L)] = lerp(out[y0:y0 + t, x0:min(W, x0 + L)], color('#ffffff'), a)
    out = vignette(out, 0.32, softness=0.75)

    # OSD: "▶ PLAY" top-left, "SP 0:12:47" bottom-left, white with glow and a hint of chroma fringe
    f = font('lato-bold', 54)

    def osd(d):
        d.polygon([(72, 66), (72, 118), (120, 92)], fill=(255, 255, 255))
        d.text((146, 92), 'PLAY', font=f, fill=(255, 255, 255), anchor='lm')
        d.text((72, H - 92), 'SP  0:12:47', font=f, fill=(255, 255, 255), anchor='lm')
    txt = _text_layer(osd)
    txt = _rgb_split(txt, 2)
    out = blend(out, blur(txt, 6), 'screen', 0.7)
    out = blend(out, txt, 'screen', 0.95)
    return out


# ----------------------------------------------------------------------------- 113 double_exposure

@effect('double_exposure')
def double_exposure(img):
    """Double exposure: a high-key, muted portrait whose silhouette is filled with the park's foliage (built from
    the photo's own background), over a light cream field; the trees drift out of the head-top, the lower
    body dissolves into the light. The face keeps its features (foliage weight is reduced there)."""
    x, y = coords()
    p = _person(2.0)
    face = mask('face', feather=14)
    trees = _foliage_layer(img)
    trees = saturation(trees, 0.8)
    trees = hsl_adjust(trees, 90, width=60, sat=0.85, shift=8)           # yellow-greens -> calmer greens

    # high-key muted portrait as the base of the silhouette
    person_base = saturation(img, 0.5)
    person_base = levels(person_base, 0.0, 0.92, 1.35)
    person_base = lerp(person_base, saturation(img, 0.7), face * 0.5)   # keep some life in the skin
    w_in = 0.78 * (1 - face) + 0.34 * face
    inside = blend(person_base, trees, 'screen', w_in)
    inside = blend(inside, trees, 'multiply', 0.12 * (1 - face))       # a touch of tree shadow detail in the cloth

    # light background with the trees escaping upward out of the silhouette
    bgcol = as_layer('#f6f2ec') * (1 - 0.06 * linear(90)[..., None])
    halo = feather(np.clip(cv2.dilate(p, np.ones((181, 181), np.uint8)) - p, 0, 1), 45)
    halo = halo * (1 - smoothstep(700, 1000, y)) * 0.55
    trees_light = levels(trees, 0.0, 1.0, 1.0, 0.25, 1.0)
    outside = blend(bgcol, trees_light, 'multiply', halo)
    out = lerp(outside, inside, p)

    # dissolve the lower body into the light field
    dissolve = smoothstep(1060, 1440, y) * 0.9
    out = lerp(out, bgcol, dissolve)
    out = fade(out, 0.04, 0.02)
    out = temperature(out, 0.04)
    return grain(out, 0.018, seed=3)


# ----------------------------------------------------------------------------- 114 reflection

@effect('reflection')
def reflection(img):
    """Water reflection: the portrait keeps its full width; below the waterline the image is mirrored with
    growing sinusoidal ripples, softened, darkened and cooled, fading into deep blue water at the bottom."""
    r = rng(2314)
    yw = 1096                                         # waterline (below the chin and neck)
    depth = H - yw
    out = img.copy()
    xx, ry = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(depth, dtype=np.float32))
    t = ry / (depth - 1)
    # ripples: two wave trains whose phase drifts along x so crests are not perfectly straight
    amp = 2.5 + 20.0 * smoothstep(0.0, 1.0, t)
    ph1 = 1.3 * np.sin(2 * np.pi * xx / 300 + 0.4) + 0.5 * np.sin(2 * np.pi * xx / 77)
    ph2 = 0.9 * np.sin(2 * np.pi * xx / 130 + 1.1)
    wave = np.sin(2 * np.pi * ry / 34 + ph1) + 0.55 * np.sin(2 * np.pi * ry / 15.5 + ph2)
    dx = amp * wave
    dy = 0.35 * amp * np.cos(2 * np.pi * ry / 34 + ph1)
    src_y = (yw - 1) - ry * 1.12 + dy                  # mirrored, slightly foreshortened
    refl = cv2.remap(img, (xx + dx).astype(np.float32), np.clip(src_y, 0, H - 1).astype(np.float32),
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # depth-dependent softening
    b1 = cv2.GaussianBlur(refl, (0, 0), sigmaX=1.5, sigmaY=3.0)
    b2 = cv2.GaussianBlur(refl, (0, 0), sigmaX=3.0, sigmaY=7.0)
    refl = lerp(lerp(refl, b1, smoothstep(0.0, 0.5, t)), b2, smoothstep(0.4, 1.0, t))
    # wave shading (crests catch light, troughs darken)
    slope = np.gradient(dx, axis=0) / (np.abs(np.gradient(dx, axis=0)).max() + 1e-6)
    refl = clip(refl * (1 + 0.10 * slope[..., None]))
    # darken, cool, and fade into deep water
    refl = refl * np.array([0.82, 0.86, 0.96], np.float32)
    refl = clip(lerp(refl, color('#12263a'), 0.16 + 0.62 * smoothstep(0.15, 1.0, t)))
    # specular sparkle: short bright dashes drifting on the surface
    for _ in range(26):
        yy0 = int(r.integers(20, depth - 3)); x0 = int(r.integers(0, W)); L = int(r.integers(15, 110))
        a = float(r.uniform(0.12, 0.42)) * (0.4 + 0.6 * (yy0 / depth))
        refl[yy0:yy0 + 2, x0:min(W, x0 + L)] = lerp(refl[yy0:yy0 + 2, x0:min(W, x0 + L)], color('#e8f1ff'), a)
    refl = cv2.GaussianBlur(refl, (0, 0), 0.6)
    out[yw:] = clip(refl)
    # thin horizon line with a soft glow
    line = np.zeros((H, W), np.float32)
    line[yw - 1:yw + 1] = 1.0
    out = blend(out, feather(line, 3.0) * 1.2, 'screen', 0.35)
    out = clip(lerp(out, color('#dfe8f0'), feather(line, 0.8) * 0.55))
    return out


# ----------------------------------------------------------------------------- 115 prism

@effect('prism')
def prism(img):
    """Prism light: two rainbow streaks (plus thin refracted lines) crossing the frame at 35 degrees with a
    luminous glow, slight glassy displacement inside the main streak and subtle chromatic edges."""
    x, y = coords()
    a = math.radians(35)
    nx, ny = -math.sin(a), math.cos(a)                # normal to the streak direction
    cx, cy = 820.0, 380.0
    d0 = (x - cx) * nx + (y - cy) * ny                # signed distance from the main streak axis

    def streak(offset, width, gain, hue0=0.0, hue1=285.0, core=0.0):
        t = (d0 - offset) / width + 0.5
        inside = ((t > 0) & (t < 1)).astype(np.float32)
        w = np.clip(np.sin(np.pi * np.clip(t, 0, 1)), 0, 1) ** 0.75 * inside
        hsv = np.stack([(hue0 + (hue1 - hue0) * np.clip(t, 0, 1)) % 360, np.ones_like(t), np.ones_like(t)], -1).astype(np.float32)
        rgb = cv2.cvtColor(np.ascontiguousarray(hsv), cv2.COLOR_HSV2RGB)
        layer = rgb * (w * gain)[..., None]
        if core:
            layer += (np.exp(-((t - 0.5) / 0.16) ** 2) * inside * core)[..., None]
        return layer

    L = streak(0, 380, 1.0, core=0.35) + streak(911, 200, 0.85, core=0.2)
    L += streak(-330, 26, 0.75) + streak(690, 22, 0.7) + streak(1130, 16, 0.5)
    L = np.clip(L, 0, 1)
    face = mask('face', feather=30)
    opac = 0.65 * (1 - 0.45 * face)

    # glassy refraction inside the main streak: the picture shifts a little along the streak normal
    w_main = np.clip(np.sin(np.pi * np.clip(d0 / 380 + 0.5, 0, 1)), 0, 1) * ((np.abs(d0) < 190).astype(np.float32))
    disp = blur(w_main, 12) * (12.0 - 8.0 * face)
    out = exposure(img, 0.08)
    chans = []
    for c, extra in enumerate((3.0, 0.0, -3.0)):
        mx = (x + (disp + extra * blur(w_main, 12)) * nx).astype(np.float32)
        my = (y + (disp + extra * blur(w_main, 12)) * ny).astype(np.float32)
        chans.append(cv2.remap(out[..., c], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    out = np.stack(chans, -1)

    out = blend(out, blur(L, 10), 'screen', opac)
    out = blend(out, blur(L, 55), 'screen', 0.4)
    out = blend(out, blur(L, 160), 'screen', 0.2)
    out = chromatic_aberration(out, 6)
    out = glow(out, 40, 0.2, 0.6)
    out = clip(out * np.array([1.02, 1.0, 1.03], np.float32))
    return out
