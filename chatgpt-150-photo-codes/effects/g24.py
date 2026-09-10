"""Group g24 — Effektlar (Effects): chromatic aberration, 8-bit pixel art, radial motion blur,
sun lens flare, film burn."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- shared helpers

def _remap(ch, mx, my):
    """Bicubic remap of a single (H,W) channel with reflected borders."""
    return cv2.remap(np.ascontiguousarray(ch, dtype=np.float32), mx.astype(np.float32), my.astype(np.float32),
                     cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def _mix2d(a, b, t):
    """lerp for (H,W) arrays with an (H,W) weight (lib.lerp expects 3-channel images)."""
    return a * (1 - t) + b * t


def _zoom_blur(img, center, strength, steps):
    """Radial (zoom) blur: average of progressively magnified copies about `center`."""
    cx, cy = center
    acc = np.zeros_like(img)
    for i in range(steps):
        s = 1 + strength * i / (steps - 1)
        M = cv2.getRotationMatrix2D((cx, cy), 0, s)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / steps


def _extend_background(img, bg):
    """Background plate: the subject area is filled with plausible nearby background colour
    (multi-scale normalised blur), so blurring the plate never smears the subject's colours."""
    src = img * bg[..., None]
    plate = src.copy()
    filled = bg.copy()
    for s in (10, 30, 80, 200):
        num = blur(src, s)
        den = blur(bg, s)
        cand = num / np.maximum(den, 1e-4)[..., None]
        valid = np.clip((den - 0.02) / 0.08, 0, 1)
        take = valid * (1 - filled)
        plate = plate + cand * take[..., None]
        filled = filled + take
    mean = src.sum((0, 1)) / max(bg.sum(), 1.0)
    plate = plate + mean * (1 - filled)[..., None]
    return clip(plate)


def _poly_mask(cx, cy, radius, sides, rot, soft=2.5):
    """Soft regular polygon -> (H,W) mask."""
    im = Image.new('L', (W, H), 0)
    pts = [(cx + radius * math.cos(math.radians(rot + 360.0 * i / sides)),
            cy + radius * math.sin(math.radians(rot + 360.0 * i / sides))) for i in range(sides)]
    ImageDraw.Draw(im).polygon(pts, fill=255)
    m = np.array(im).astype(np.float32) / 255.0
    return blur(m, soft) if soft else m


def _kmeans_palette(px, wt, k, seed=24, iters=30):
    """Weighted k-means (k-means++ init, fixed seed) -> (k,3) palette + channel weights used."""
    r = rng(seed)
    cw = np.array([0.55, 0.75, 0.35], np.float32)
    p0 = wt / wt.sum()
    centers = [px[r.choice(len(px), p=p0)]]
    for _ in range(1, k):
        d2 = np.min(np.stack([(((px - c) ** 2) * cw).sum(1) for c in centers]), axis=0)
        p = d2 * wt
        p = p / p.sum()
        centers.append(px[r.choice(len(px), p=p)])
    pal = np.array(centers, np.float32)
    for _ in range(iters):
        dist = (((px[:, None, :] - pal[None]) ** 2) * cw).sum(-1)
        idx = dist.argmin(1)
        for j in range(k):
            sel = idx == j
            if sel.any():
                w = wt[sel][:, None]
                pal[j] = (px[sel] * w).sum(0) / w.sum()
    return pal, cw


# ----------------------------------------------------------------------------- #116 chromatic

@effect('chromatic')
def chromatic(img):
    """Strong lateral chromatic aberration: red/blue fringes that grow quadratically toward the frame edges;
    the centre (face) stays sharp, plus a slight vignette."""
    x, y = coords()
    cx, cy = W / 2, H / 2
    dx, dy = x - cx, y - cy
    r = np.sqrt(dx * dx + dy * dy)
    R = math.hypot(cx, cy)
    t = r / R
    disp = 36.0 * t ** 2.0                      # px: 0 at centre, 36 px at the corners
    ux, uy = dx / np.maximum(r, 1e-6), dy / np.maximum(r, 1e-6)
    sx, sy = ux * disp, uy * disp
    red = _remap(img[..., 0], x - sx, y - sy)   # red magnified  -> fringe on the outer side of edges
    blue = _remap(img[..., 2], x + sx, y + sy)  # blue minified  -> fringe on the inner side
    green = img[..., 1]
    # real CA is smeared, not a crisp copy: soften the displaced channels toward the edges
    w = np.clip(t, 0, 1) ** 1.6
    red = _mix2d(red, blur(red, 1.6), w)
    blue = _mix2d(blue, blur(blue, 1.6), w)
    out = np.stack([red, green, blue], axis=-1)
    return vignette(out, 0.22, radius=1.0, softness=0.75)


# ----------------------------------------------------------------------------- #117 pixel_art

@effect('pixel_art')
def pixel_art(img):
    """8-bit pixel art: 16 px blocks (72 x 90 grid) and a 16-colour palette learnt from the photo — a dedicated
    6-tone skin/feature ramp for the face plus 10 colours for the rest — 4-bit colour snapping and a light
    ordered dither for the retro look."""
    block = 16
    sw, sh = W // block, H // block
    src = saturation(s_curve(img, 0.10), 1.25)
    small = cv2.resize(src, (sw, sh), interpolation=cv2.INTER_AREA)
    face_w = cv2.resize(mask('face', feather=6), (sw, sh), interpolation=cv2.INTER_AREA).reshape(-1)
    px = small.reshape(-1, 3).astype(np.float32)
    in_face = face_w > 0.5
    pal_face, cw = _kmeans_palette(px[in_face], np.ones(in_face.sum(), np.float32), 6, seed=24)
    pal_rest, _ = _kmeans_palette(px[~in_face], np.ones((~in_face).sum(), np.float32), 10, seed=25)
    pal = np.round(np.clip(np.concatenate([pal_face, pal_rest]), 0, 1) * 15) / 15.0   # 4 bits per channel
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0 - 0.5
    tile = np.tile(bayer, (sh // 4 + 1, sw // 4 + 1))[:sh, :sw]
    dith = np.clip(small + tile[..., None] * 0.035, 0, 1).reshape(-1, 3)
    dist = (((dith[:, None, :] - pal[None]) ** 2) * cw).sum(-1)
    # inside the face, non-skin colours are penalised so shadows never turn olive/grey
    penalty = np.zeros(len(pal), np.float32)
    penalty[len(pal_face):] = 0.12
    dist = dist + face_w[:, None] * penalty[None]
    q = pal[dist.argmin(1)].reshape(sh, sw, 3).astype(np.float32)
    big = cv2.resize(q, (W, H), interpolation=cv2.INTER_NEAREST)
    # faint pixel grid
    x, y = coords()
    grid = ((x.astype(np.int32) % block == 0) | (y.astype(np.int32) % block == 0)).astype(np.float32)
    return clip(big * (1 - 0.08 * grid[..., None]))


# ----------------------------------------------------------------------------- #118 motion_blur

@effect('motion_blur')
def motion_blur(img):
    """Radial zoom blur streaking outward from the face; the subject is composited back sharp from a
    subject-free background plate (no colour smearing/halo), plus contrast and vibrance for energy."""
    fc = face_center()
    p = mask('person')
    plate = _extend_background(img, 1 - p)
    zb = _zoom_blur(plate, fc, 0.17, 36)
    zb = _zoom_blur(zb, fc, 0.04, 8)         # second pass removes stepping in long streaks
    pm = mask('person', feather=4)
    out = lerp(zb, img, pm)
    out = s_curve(out, 0.12)
    out = vibrance(out, 0.15)
    out = apply_mask(out, unsharp(out, 1.5, 0.35), mask('face', feather=20))
    return vignette(out, 0.2, radius=1.0, softness=0.7, center=fc)


# ----------------------------------------------------------------------------- #119 lens_flare

@effect('lens_flare')
def lens_flare(img):
    """Sun in the top-right corner: white-hot core, warm glow and veiling haze, 16-point starburst rays,
    an anamorphic streak, a chain of polygon ghosts along the optical axis, warm rim light on the subject."""
    sx, sy = W * 0.90, H * 0.09
    cx, cy = W / 2, H / 2
    x, y = coords()
    d = np.sqrt((x - sx) ** 2 + (y - sy) ** 2)
    warm, amber = color('#fff1cf'), color('#ffc98a')
    layer = np.zeros((H, W, 3), np.float32)
    layer += (np.exp(-(d / 40) ** 2) * 1.5)[..., None]                           # white-hot core
    layer += (np.exp(-(d / 130) ** 2) * 0.9)[..., None] * warm                   # tight glow
    layer += (np.exp(-(d / 420) ** 2) * 0.5)[..., None] * amber                  # wide warm glow
    layer += (np.exp(-(d / 1300) ** 2) * 0.24)[..., None] * color('#ffdcb4')     # veiling haze over the frame
    # starburst rays (aperture diffraction)
    ang = np.arctan2(y - sy, x - sx)
    r = rng(24)
    rays_m = np.zeros((H, W), np.float32)
    for i in range(16):
        a0 = 2 * math.pi * i / 16 + r.uniform(-0.08, 0.08)
        wdt = r.uniform(0.010, 0.022)
        L = r.uniform(380, 1050)
        da = np.abs(((ang - a0 + math.pi) % (2 * math.pi)) - math.pi)
        rays_m += np.exp(-(da / wdt) ** 2) * np.exp(-(d / L) ** 1.1) * r.uniform(0.5, 1.0)
    rays_m *= smoothstep(20, 90, d)
    face_soft = mask('face', feather=40)
    rays_m *= 1 - 0.4 * face_soft
    layer += np.clip(rays_m, 0, 1)[..., None] * warm * 0.8
    # anamorphic horizontal streak (cool)
    s1 = np.exp(-((y - sy) / 10.0) ** 2) * np.exp(-(np.abs(x - sx) / (W * 0.6)) ** 1.3)
    s2 = np.exp(-((y - sy) / 40.0) ** 2) * np.exp(-(np.abs(x - sx) / (W * 0.35)) ** 1.5)
    layer += (s1 * 0.75 + s2 * 0.25)[..., None] * color('#a9c8ff')
    # faint iris ring around the sun
    ring = np.exp(-((d - 300) / 7.0) ** 2) * 0.09
    layer += ring[..., None] * color('#ffb8a0')
    # polygon ghosts along the sun -> image-centre axis (t = 1 is the centre)
    vx, vy = cx - sx, cy - sy
    ghosts = [(0.18, 22, 6, 0.45, '#ffd9a8', False), (0.30, 58, 6, 0.28, '#ffb27a', True),
              (0.42, 120, 7, 0.16, '#8fe3c8', True), (0.55, 16, 6, 0.55, '#fff4d6', False),
              (0.72, 40, 6, 0.18, '#ffc0d0', True), (0.95, 88, 6, 0.10, '#a8c8ff', True),
              (1.22, 30, 6, 0.22, '#d8ffe0', False), (1.50, 150, 7, 0.18, '#ffb890', True),
              (1.70, 60, 6, 0.26, '#ffe0b0', False), (1.92, 200, 6, 0.12, '#c0d0ff', True)]
    for t, rad, sides, alpha, col, hollow in ghosts:
        gx, gy = sx + vx * t, sy + vy * t
        rot = r.uniform(0, 60)
        m1 = _poly_mask(gx, gy, rad, sides, rot)
        m2 = _poly_mask(gx, gy, rad * 0.86, sides, rot)
        rim = np.clip(m1 - m2, 0, 1)
        g = m1 * (0.35 if hollow else 0.7) + rim * 0.9
        g = g * (1 - 0.65 * face_soft)
        layer += g[..., None] * color(col) * alpha
    out = blend(img, np.clip(layer, 0, 1), 'screen', 1.0)
    # backlight: warm rim along the subject's silhouette on the sun side
    edge = inner_edge(mask('person'), 16, 7)
    dirw = linear(-45, 0.4, 0.95)
    out = blend(out, '#ffd7a0', 'screen', 1.0, mask_=np.clip(edge * dirw * 1.3, 0, 1))
    out = temperature(out, 0.15)
    return out


# ----------------------------------------------------------------------------- #120 film_burn

@effect('film_burn')
def film_burn(img):
    """Burnt film: fbm-warped burn fronts creeping in from the top-right and bottom-left corners (plus a small
    one bottom-right) — scorched dark-red rim -> red -> orange -> yellow -> white-hot core, with white hot
    spots, a warm faded overall tone and grain."""
    x, y = coords()
    n1 = fbm(6, seed=241, scale=1.2)
    n2 = fbm(5, seed=242, scale=3.5)
    warp = (n1 - 0.5) * 0.55 + (n2 - 0.5) * 0.22

    def corner(cx, cy, rx, ry, lo, hi, gain=1.0):
        dd = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) + warp
        return (1 - smoothstep(lo, hi, dd)) * gain

    b = np.maximum(corner(W, 0, W * 0.46, H * 0.38, 0.15, 1.0),
                   corner(0, H, W * 0.47, H * 0.36, 0.15, 1.0))
    b = np.maximum(b, corner(W, H, W * 0.30, H * 0.20, 0.20, 1.0, 0.85))
    b = np.clip(b, 0, 1) * (1 - 0.9 * mask('face', feather=25, grow=20))
    # scorched dark ring at the burn front
    ring = blur(smoothstep(0.03, 0.14, b) * (1 - smoothstep(0.18, 0.34, b)), 5)
    out = blend(img, '#5a1208', 'multiply', 0.45, mask_=ring)
    # light: dark red -> red -> orange -> yellow -> white by burn depth
    stops = [(0.10, '#5a0e05'), (0.26, '#c8200a'), (0.46, '#ff6a00'), (0.68, '#ffc63a'), (0.88, '#fffbe8'), (1.0, '#ffffff')]
    pos = [s[0] for s in stops]
    cols = np.array([color(s[1]) for s in stops], np.float32)
    lc = np.stack([np.interp(b, pos, cols[:, c]) for c in range(3)], -1).astype(np.float32)
    a = smoothstep(0.12, 0.62, b)[..., None]
    out = blend(out, blur(lc * a, 6), 'screen', 1.0)
    core = blur(smoothstep(0.62, 0.95, b), 8)
    out = clip(out + core[..., None] * color('#fff6dc') * 0.9)
    # white-hot spots inside the burnt zones with a soft orange fringe
    hs = smoothstep(0.80, 0.92, fbm(4, seed=243, scale=5.0)) * smoothstep(0.25, 0.55, b)
    hs = blur(hs, 3.0)
    out = blend(out, np.clip(blur(hs, 16) * 1.5, 0, 1)[..., None] * color('#ffb040'), 'screen', 1.0)
    out = clip(out + hs[..., None] * 1.0)
    # overall: warm, faded, grainy
    out = temperature(out, 0.12)
    out = split_tone(out, '#3a1a10', '#ffb070', strength=0.22)
    out = fade(out, 0.07, 0.02)
    return grain(out, 0.05, size=1.3, seed=24)
