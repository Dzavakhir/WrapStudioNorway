"""Group g20 — Badiiy (Artistic): comic, halftone, pointillism, impressionist, ink."""
from effects.lib import *
from effects.registry import effect

_INK_BLACK = '#1a1214'


# ----------------------------------------------------------------------------- shared helpers

def _flatten(img, sp=9, sr=24, scale=0.5):
    """Mean-shift colour flattening (cartoon fills), computed at reduced scale for speed."""
    w, h = int(W * scale), int(H * scale)
    small = cv2.resize(to_u8(img), (w, h), interpolation=cv2.INTER_AREA)
    ms = cv2.pyrMeanShiftFiltering(small, sp, sr)
    return from_u8(cv2.resize(ms, (W, H), interpolation=cv2.INTER_CUBIC))


def _quantize(x, n, soft=0.3):
    """Posterise a 0..1 channel into n bands with slightly softened band edges (no jaggies)."""
    t = np.clip(x, 0, 1) * (n - 1)
    lo = np.floor(t)
    f = t - lo
    f = smoothstep(0.5 - soft, 0.5 + soft, f)
    return np.clip((lo + f) / (n - 1), 0, 1).astype(np.float32)


def _jittered_grid(r, spacing, area=None, jitter=0.5):
    """Hex-offset jittered grid of points (N,2). `area` (H,W) probability mask keeps points stochastically."""
    xs = np.arange(spacing / 2, W, spacing, dtype=np.float32)
    ys = np.arange(spacing / 2, H, spacing, dtype=np.float32)
    gx, gy = np.meshgrid(xs, ys)
    gx = gx + (np.arange(len(ys))[:, None] % 2) * (spacing / 2)
    pts = np.stack([gx.ravel(), gy.ravel()], 1)
    pts = pts + r.uniform(-jitter, jitter, pts.shape).astype(np.float32) * spacing
    pts[:, 0] = np.clip(pts[:, 0], 0, W - 1)
    pts[:, 1] = np.clip(pts[:, 1], 0, H - 1)
    if area is not None:
        keep = r.random(len(pts)) < area[pts[:, 1].astype(int), pts[:, 0].astype(int)]
        pts = pts[keep]
    return pts


def _random_points(r, n, area=None):
    pts = np.stack([r.uniform(0, W - 1, n), r.uniform(0, H - 1, n)], 1).astype(np.float32)
    if area is not None:
        keep = r.random(n) < area[pts[:, 1].astype(int), pts[:, 0].astype(int)]
        pts = pts[keep]
    return pts


def _sample_hsv(hsv, pts):
    return hsv[pts[:, 1].astype(int), pts[:, 0].astype(int)].copy()


def _jitter_hsv(r, h, hue_sd, sat_sd, val_sd):
    n = len(h)
    h = h.copy()
    h[:, 0] = (h[:, 0] + r.normal(0, hue_sd, n)) % 360
    h[:, 1] = np.clip(h[:, 1] * (1 + r.normal(0, sat_sd, n)), 0, 1)
    h[:, 2] = np.clip(h[:, 2] + r.normal(0, val_sd, n), 0, 1)
    return h


def _hsv_rows_to_u8(h):
    rgb = cv2.cvtColor(np.ascontiguousarray(h.reshape(-1, 1, 3), dtype=np.float32), cv2.COLOR_HSV2RGB).reshape(-1, 3)
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)


def _feature_mask(feather_=2, grow=4):
    return np.clip(mask('eyes', feather_, grow + 2) + mask('brows', feather_, grow) + mask('lips', feather_, grow)
                   + mask('mouth', feather_, max(grow - 2, 0)), 0, 1)


def _canny(img, sigma, low, high, dilate=1):
    g = cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (0, 0), sigma), low, high).astype(np.float32) / 255.0
    if dilate:
        e = cv2.dilate(e, np.ones((2 * dilate + 1,) * 2, np.uint8))
    return e


# ----------------------------------------------------------------------------- 096 comic

@effect('comic')
def comic(img):
    """Comic-book illustration: black ink outlines, halftone dot shading, saturated flat colours."""
    flat = _flatten(img, 8, 22, 0.5)
    flat = bilateral(flat, 9, 0.10, 7)
    flat = curve(flat, [(0, 0.06), (0.25, 0.30), (0.6, 0.66), (1, 1)])

    skin = np.clip(mask('face_skin', 6) + mask('seg_body_skin', 6), 0, 1)
    feat = _feature_mask(3, 8)
    person = mask('person')
    l0 = blur(luminance(flat), 2)

    # --- flat cel colours: quantised value outside the skin, clean 2-tone shading on the skin
    hsv = rgb2hsv(flat)
    v = hsv[..., 2]
    v_cel = _quantize(blur(v, 2.0), 5, soft=0.35)
    shadow = smoothstep(0.66, 0.42, blur(l0, 4))                     # soft cel shadow on the face
    v_skin = np.clip(v * (1 - 0.15 * shadow) + 0.02, 0, 1)
    hsv[..., 2] = v_cel * (1 - skin) + v_skin * skin
    hsv[..., 1] = np.clip(hsv[..., 1] * (1.5 - 0.2 * skin), 0, 1)
    cel = hsv2rgb(hsv)
    # warm (not grey) shadow on the skin
    warm = np.array([1.0, 0.93, 0.86], np.float32)
    cel = clip(cel * lerp(np.ones(3, np.float32), warm, (shadow * skin * 0.8)[..., None]))

    # --- halftone dot shading in the shadows (kept off the eyes and mouth, lighter on skin)
    shade_w = smoothstep(0.58, 0.20, l0) * (1 - feat) * (1 - 0.45 * skin)
    ht = halftone(as_layer(0.45 + 0.55 * l0), cell=14, angle=45)[..., 0]     # 1 = no dot
    dots = 1 - (1 - ht) * shade_w
    out = clip(cel * lerp(1.0, dots, 0.6)[..., None])

    # --- ink outlines
    lines_gen = _canny(flat, 1.6, 40, 120, 1)                        # general 3 px lines
    lines_face = _canny(flat, 2.2, 70, 190, 1)                       # only strong lines inside the skin
    lines_bg = _canny(blur(flat, 2.0), 2.5, 55, 150, 1)              # calm blob outlines in the foliage
    interior = np.clip(skin - feat, 0, 1)
    fine = 1 - xdog(flat, sigma=1.2, k=1.6, p=14, eps=0.02, phi=8)   # crisp detail for eyes / lips / folds
    ink_m = lines_gen * (1 - interior) * person + lines_face * interior + lines_bg * (1 - person) * 0.9
    ink_m = np.maximum(ink_m, fine * 0.7 * np.maximum(feat, (1 - skin) * person))
    ink_m = np.maximum(ink_m, edge_band(person, width=3, softness=0.8))
    ink_m = feather(np.clip(ink_m, 0, 1), 0.5)
    out = clip(out * (1 - 0.94 * ink_m)[..., None])

    out = clip(out * paper(seed=5, strength=0.06, fibers=False)[..., None])
    return out


# ----------------------------------------------------------------------------- 097 halftone

@effect('halftone')
def halftone_print(img):
    """Newspaper halftone: burgundy ink dots of varying size on cream paper."""
    g = bw(img, 0.3, 0.59, 0.11)
    g = clarity(g, 0.4, 40)
    g = unsharp(g, 8.0, 0.9)                                       # keep eyes / brows / lips readable through the screen
    # lift the blacks so even the navy hijab keeps a visible dot structure, cap whites so lights still carry dots
    g = curve(g, [(0, 0.2), (0.25, 0.42), (0.55, 0.64), (0.85, 0.86), (1, 0.94)])
    ht = halftone(g, cell=15, angle=25)[..., 0]                    # 1 = paper, 0 = ink
    ht = np.clip(blur(ht, 0.6), 0, 1)                              # slight dot gain / ink softness
    density = (1 - ht) * (0.93 + 0.07 * fbm(4, seed=21, scale=2.0))
    paper_c = canvas(CREAM, paper(seed=3, strength=0.12))
    return clip(lerp(paper_c, as_layer(BURGUNDY_DEEP), density))


# ----------------------------------------------------------------------------- 098 pointillism

@effect('pointillism')
def pointillism(img):
    """Pointillism: tens of thousands of small coloured dots on a cream canvas."""
    r = rng(2098)
    src = blur(img, 2.5)
    src = curve(src, [(0, 0.14), (0.5, 0.56), (1, 1)])
    src = saturation(src, 1.3)
    src = vibrance(src, 0.25)
    hsv = rgb2hsv(src)

    face = mask('face', feather=12, grow=30)
    feat = _feature_mask(2, 4)
    # toned ground: cream canvas lightly stained with the local colour, so the gaps between dots read
    # as painted ground rather than white noise
    ground = lerp(canvas('#F4ECDC'), blur(src, 8), 0.45)
    cv = np.ascontiguousarray(to_u8(ground))

    def draw(pts, rad, hue_sd, sat_sd, val_sd, accent_p, accent_deg):
        n = len(pts)
        if n == 0:
            return
        h = _jitter_hsv(r, _sample_hsv(hsv, pts), hue_sd, sat_sd, val_sd)
        acc = r.random(n) < accent_p
        k = int(acc.sum())
        if k:
            h[acc, 0] = (h[acc, 0] + r.choice([-1.0, 1.0], k) * accent_deg) % 360
            h[acc, 1] = np.clip(h[acc, 1] * 1.15 + 0.05, 0, 1)
        # optical-mixing shimmer: some dots in dark passages are lighter (violet / blue lights in the navy)
        lift = (h[:, 2] < 0.38) & (r.random(n) < 0.22)
        h[lift, 2] = np.clip(h[lift, 2] + r.uniform(0.10, 0.20, int(lift.sum())), 0, 1)
        cols = _hsv_rows_to_u8(h)
        radii = r.uniform(rad[0], rad[1], n)
        for i in r.permutation(n):
            c = (int(cols[i, 0]), int(cols[i, 1]), int(cols[i, 2]))
            cv2.circle(cv, (int(pts[i, 0] * 4), int(pts[i, 1] * 4)), int(radii[i] * 4), c, -1, cv2.LINE_AA, 2)

    # 1. base coverage everywhere: bigger dots, ground peeking through
    draw(_jittered_grid(r, 12.0), (6.5, 9.5), 7, 0.12, 0.04, 0.14, 45)
    # 2. random medium dots, mostly outside the face
    draw(_random_points(r, 9000, 1 - 0.7 * face), (5.0, 7.5), 7, 0.12, 0.04, 0.14, 45)
    # 3. face: dense small dots for detail
    draw(_jittered_grid(r, 7.5, area=face), (4.2, 5.8), 4, 0.07, 0.03, 0.05, 25)
    draw(_random_points(r, 14000, face), (3.6, 5.0), 4, 0.07, 0.03, 0.05, 25)
    # 4. eyes / brows / lips: tiny dots so the features stay crisp
    draw(_jittered_grid(r, 3.8, area=feat), (2.4, 3.2), 3, 0.05, 0.02, 0.0, 0)

    out = from_u8(cv)
    out = clip(out * paper(seed=8, strength=0.08, fibers=False)[..., None])
    return out


# ----------------------------------------------------------------------------- 099 impressionist

@effect('impressionist')
def impressionist(img):
    """Impressionist painting: soft directional brush dabs, luminous colours, canvas texture."""
    r = rng(2099)
    pre = curve(img, [(0, 0.12), (0.3, 0.38), (0.7, 0.77), (1, 0.98)])
    pre = vibrance(pre, 0.4)
    pre = saturation(pre, 1.15)
    pre = split_tone(pre, shadows='#4a4f9a', highlights='#ffe0a8', strength=0.35)
    pre = brightness(pre, 0.05)
    src = blur(pre, 3.5)
    hsv = rgb2hsv(src)

    # stroke orientation follows the isophotes (perpendicular to the luminance gradient)
    lum = blur(luminance(img), 4)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=5)
    mag = np.sqrt(gx * gx + gy * gy)
    ang = np.arctan2(gy, gx) + np.pi / 2
    mag_n = mag / (np.percentile(mag, 95) + 1e-6)
    conf = smoothstep(0.06, 0.35, mag_n)

    face = mask('face', feather=10, grow=24)
    feat = _feature_mask(2, 4)
    detail = np.clip(np.maximum(face, smoothstep(0.2, 0.6, mag_n)), 0, 1)

    cv = np.ascontiguousarray(to_u8(blur(pre, 6)))
    hmap = np.zeros((H, W), np.float32)

    def strokes(pts, length, width, hue_sd, sat_sd, val_sd, ang_jit, default_ang):
        n = len(pts)
        if n == 0:
            return
        ix, iy = pts[:, 0].astype(int), pts[:, 1].astype(int)
        h = _jitter_hsv(r, hsv[iy, ix].copy(), hue_sd, sat_sd, val_sd)
        cols = _hsv_rows_to_u8(h)
        a_iso = ang[iy, ix]
        a_def = default_ang + r.normal(0, 0.35, n)
        use_iso = r.random(n) < conf[iy, ix]
        a = np.where(use_iso, a_iso, a_def) + r.normal(0, ang_jit, n)
        L = r.uniform(length[0], length[1], n)
        Wd = r.uniform(width[0], width[1], n)
        dx = np.cos(a) * L / 2
        dy = np.sin(a) * L / 2
        hv = r.uniform(0.5, 1.0, n)
        for i in r.permutation(n):
            p0 = (int((pts[i, 0] - dx[i]) * 4), int((pts[i, 1] - dy[i]) * 4))
            p1 = (int((pts[i, 0] + dx[i]) * 4), int((pts[i, 1] + dy[i]) * 4))
            c = (int(cols[i, 0]), int(cols[i, 1]), int(cols[i, 2]))
            t = int(round(Wd[i]))
            cv2.line(cv, p0, p1, c, t, cv2.LINE_AA, 2)
            cv2.line(hmap, p0, p1, float(hv[i]), t, cv2.LINE_8, 2)

    d_ang = math.radians(-35)
    person = mask('person', feather=16)
    # 1. big loose dabs in the background (foliage / sky), large dabs on the figure
    strokes(_jittered_grid(r, 24, area=1 - person), (56, 84), (20, 28), 10, 0.12, 0.09, 0.2, d_ang)
    strokes(_jittered_grid(r, 18, area=person), (40, 58), (14, 20), 6, 0.08, 0.06, 0.14, d_ang)
    # 2. medium dabs, dense on the figure and sparse in the background
    strokes(_jittered_grid(r, 11, area=0.35 + 0.65 * person), (26, 38), (9, 12), 6, 0.08, 0.06, 0.14, d_ang)
    # 3. fine dabs in the face and along edges
    strokes(_jittered_grid(r, 6.5, area=detail), (14, 22), (5, 6), 4, 0.06, 0.04, 0.10, d_ang)
    # 4. very fine dabs on the features
    strokes(_jittered_grid(r, 3.5, area=feat), (7, 11), (2, 3), 2, 0.04, 0.02, 0.08, d_ang)

    paint = blur(from_u8(cv), 0.8)
    # soft skin: the fine dabs melt together on the face, the features stay crisp
    skin_soft = np.clip(mask('face_skin', 8) - feat, 0, 1)
    paint = lerp(paint, blur(paint, 1.8), skin_soft * 0.65)

    # impasto relief from the stroke height map
    hb = blur(hmap, 2.0)
    sx = cv2.Sobel(hb, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(hb, cv2.CV_32F, 0, 1, ksize=3)
    rel = -(sx * 0.6 + sy * 0.8)
    rel = rel / (np.percentile(np.abs(rel), 98) + 1e-6)
    relief = np.clip(0.5 + 0.5 * rel, 0, 1)
    paint = blend(paint, relief, 'overlay', 0.35)

    # canvas weave
    x, y = coords()
    weave = 1 + 0.03 * (np.sin(2 * np.pi * x / 4.0) * np.sin(2 * np.pi * y / 4.0)) + 0.03 * (fbm(5, seed=31, scale=2.0) - 0.5)
    return clip(paint * weave[..., None])


# ----------------------------------------------------------------------------- 100 ink

@effect('ink')
def ink(img):
    """Minimal black ink line drawing on cream paper with a light wash."""
    pre = bilateral(img, 9, 0.08, 7)
    pre = bilateral(pre, 9, 0.06, 5)
    person_hard = mask('person')
    person = mask('person', feather=2)
    face_skin = mask('face_skin', feather=5)
    feat = _feature_mask(2, 6)
    interior = np.clip(face_skin - feat, 0, 1)

    # crisp black lines on the subject; inside the cheeks only the strong lines survive
    ln = smoothstep(0.15, 0.7, 1 - xdog(pre, sigma=1.3, k=1.6, p=18, eps=0.012, phi=14))
    ln_strong = smoothstep(0.45, 0.9, 1 - xdog(pre, sigma=1.6, k=1.6, p=14, eps=0.02, phi=10))
    ln_person = ln * (1 - interior) + ln_strong * interior * 0.85
    sil = edge_band(person_hard, width=2, softness=0.7)
    # background: only the strongest contours, faint, so the paper stays open and minimal
    ln_bg = smoothstep(0.5, 0.95, 1 - xdog(blur(pre, 3.5), sigma=3.0, k=1.6, p=9, eps=0.02, phi=5))
    density = ln_person * person + np.maximum(sil, ln_bg * 0.35 * (1 - person))
    # pen weight: the strongest contours get a slightly heavier nib
    heavy = cv2.dilate(smoothstep(0.6, 1.0, ln_person * person), np.ones((3, 3), np.uint8)) * 0.9
    density = feather(np.clip(np.maximum(density, heavy), 0, 1), 0.35)

    # one flat tone of diluted ink on the dark cloth, a whisper of it on the shadow side of the face
    tone_ = blur(luminance(pre), 6)
    w = smoothstep(0.55, 0.25, tone_)
    wash = w * person * (0.12 * (1 - face_skin) + 0.05 * face_skin)

    alpha = np.clip(density + wash * (1 - density), 0, 1)
    paper_c = canvas(CREAM, paper(seed=9, strength=0.08))
    out = lerp(paper_c, as_layer(_INK_BLACK), alpha)

    # a few small ink splatters in the lower-right corner
    r = rng(100)
    spl = np.zeros((H, W), np.float32)
    for _ in range(9):
        cx, cy = r.uniform(W * 0.78, W * 0.97), r.uniform(H * 0.86, H * 0.97)
        cv2.circle(spl, (int(cx), int(cy)), int(r.uniform(3, 8)), float(r.uniform(0.6, 0.95)), -1, cv2.LINE_AA)
        for _ in range(3):
            cv2.circle(spl, (int(cx + r.uniform(-14, 14)), int(cy + r.uniform(-14, 14))), int(r.uniform(1, 2)), float(r.uniform(0.4, 0.8)), -1, cv2.LINE_AA)
    out = lerp(out, as_layer(_INK_BLACK), spl)
    return clip(out)
