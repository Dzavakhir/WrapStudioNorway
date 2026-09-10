"""Group g29 — Ijodiy (Creative): duotone, neon, cyberpunk, retro_poster, vaporwave."""
from effects.lib import *
from effects.registry import effect

PINK = '#ff2fa0'
CYAN = '#22d3ff'


# ----------------------------------------------------------------------------- private helpers

def _person(feather_=1.5):
    """Cleaned person mask: solid 1.0 core (the stored mask sits at ~0.988 inside), soft edge, optional feather."""
    p = smoothstep(0.03, 0.97, mask('person'))
    return feather(p, feather_) if feather_ else p


def _skin(feather_=6.0, grow=0):
    """Face-skin mask minus the hijab (the stored oval overlaps the fabric at the temple)."""
    m = mask('face_skin') * (1 - smoothstep(0.2, 0.6, mask('seg_clothes', 2)))
    if grow:
        k = np.ones((abs(grow) * 2 + 1,) * 2, np.uint8)
        m = cv2.dilate(m, k) if grow > 0 else cv2.erode(m, k)
    return feather(m, feather_) if feather_ else m


def _skin_protect(img, ref, amount=0.5, feather_=5):
    """Pull face-skin hue & saturation part of the way back to `ref` so a grade never turns the skin garish."""
    m = _skin(feather_, grow=-6)
    hsv = rgb2hsv(img)
    hsv0 = rgb2hsv(ref)
    t = m * amount
    dh = ((hsv[..., 0] - hsv0[..., 0] + 180.0) % 360.0) - 180.0
    hsv[..., 0] = (hsv0[..., 0] + dh * (1 - t)) % 360.0
    hsv[..., 1] = hsv[..., 1] * (1 - t) + hsv0[..., 1] * t
    return hsv2rgb(hsv)


def _remove_small(binary, min_px):
    """Drop connected components smaller than min_px from a binary (H,W) mask."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(binary.astype(np.uint8), connectivity=8)
    keep = np.zeros(n, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_px
    return keep[lab].astype(np.float32)


def _dilate(m, r):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    return cv2.dilate(np.asarray(m, np.float32), k)


def _x_field(c_left, c_right, x0=0.32, x1=0.68):
    """(H,W,3) colour field: c_left on the left fading to c_right on the right."""
    x, _ = coords()
    w = smoothstep(W * x0, W * x1, x)[..., None]
    return (1 - w) * color(c_left) + w * color(c_right)


def _facing(p, direction, sigma=8.0):
    """(H,W) 0..1: how much the local outline of mask p faces `direction` (unit vector, y down)."""
    mb = blur(p, sigma)
    gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
    mag = np.sqrt(gx * gx + gy * gy) + 1e-5
    nx, ny = -gx / mag, -gy / mag
    return smoothstep(-0.05, 0.6, nx * direction[0] + ny * direction[1])


def _dots(c, cell=10.0, angle=15.0):
    """Halftone dot mask (1 = ink) for an ink coverage c (H,W) in 0..1; screen rotated by `angle` degrees.
    Solid where coverage is (almost) complete, empty where it is (almost) zero, dots in between."""
    x, y = coords()
    a = math.radians(angle)
    u = x * math.cos(a) + y * math.sin(a)
    v = -x * math.sin(a) + y * math.cos(a)
    cu = np.round(u / cell) * cell
    cv_ = np.round(v / cell) * cell
    cx = cu * math.cos(a) - cv_ * math.sin(a)
    cy = cu * math.sin(a) + cv_ * math.cos(a)
    cb = cv2.blur(np.asarray(c, np.float32), (int(cell), int(cell)))
    samp = cv2.remap(cb, cx.astype(np.float32), cy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rad = cell * 0.6 * np.sqrt(np.clip(samp, 0, 1))
    dist = np.sqrt((u - cu) ** 2 + (v - cv_) ** 2)
    dot = (1 - smoothstep(rad - 0.7, rad + 0.7, dist)) * smoothstep(0.03, 0.10, samp)
    return np.clip(np.maximum(dot, smoothstep(0.85, 0.97, samp)), 0, 1).astype(np.float32)


def _vapor_sun(center, radius, top='#ffe38a', mid='#ff8fb0', bottom='#ff3fa8'):
    """Retro striped vaporwave sun -> (colour layer (H,W,3), alpha (H,W))."""
    x, y = coords()
    cx, cy = center
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    disc = 1 - smoothstep(radius - 2.5, radius + 2.5, d)
    t = np.clip((y - (cy - radius)) / (2.0 * radius), 0, 1)
    col = lerp(as_layer(top), as_layer(mid), smoothstep(0.0, 0.55, t))
    col = lerp(col, as_layer(bottom), smoothstep(0.55, 1.0, t))
    alpha = disc.copy()
    # horizontal cut-outs in the lower half, thicker towards the bottom
    for i in range(6):
        yc = cy + radius * (0.08 + 0.155 * i)
        h = 4 + 5 * i
        gap = smoothstep(yc - h - 1.5, yc - h + 1.5, y) * (1 - smoothstep(yc + h - 1.5, yc + h + 1.5, y))
        alpha *= 1 - gap
    return col, alpha.astype(np.float32)


def _vapor_grid(hy, vp_x=W * 0.5, cols=8, rows=10, spacing=175):
    """Neon perspective floor grid mask (H,W): verticals converging to (vp_x, hy) + perspective-spaced horizontals."""
    m = np.zeros((H, W), np.float32)
    for k in range(-cols, cols + 1):
        xb = vp_x + k * spacing
        cv2.line(m, (int(round(xb)), H + 30), (int(round(vp_x)), int(round(hy))), 1.0, 3, cv2.LINE_AA)
    for i in range(rows):
        yy = hy + (H - hy) / (1 + (i + 0.35) * 0.42)
        th = max(2, int(round(1.5 + 2.5 * (yy - hy) / (H - hy))))
        cv2.line(m, (0, int(round(yy))), (W, int(round(yy))), 1.0, th, cv2.LINE_AA)
    _, y = coords()
    m *= smoothstep(hy + 6, hy + 90, y)
    return np.clip(m, 0, 1)


# ----------------------------------------------------------------------------- 141 duotone

@effect('duotone')
def duotone(img):
    """Two-colour duotone: burgundy shadows -> rose mids -> cream highlights (the guide's signature palette)."""
    x = clarity(img, 0.2, 45)
    x = curve(x, [(0, 0), (0.15, 0.09), (0.4, 0.48), (0.6, 0.76), (0.8, 0.92), (1, 1)])   # face -> cream, hijab -> deep
    x = gradient_map(x, [(0.0, BURGUNDY_DEEP), (0.3, BURGUNDY), (0.6, ROSE), (1.0, CREAM)], 1.0)
    x = vignette(x, 0.2, 1.0, 0.75, BURGUNDY_DEEP)
    return grain(x, 0.03, 1.2, seed=29)


# ----------------------------------------------------------------------------- 142 neon

@effect('neon')
def neon(img):
    """Glowing pink/cyan neon tube outlines of the subject on a near-black background; face dimly visible."""
    p = _person(0)
    ph = (p > 0.5).astype(np.uint8)
    field = _x_field(PINK, CYAN)
    # dark base: dim desaturated subject, almost black background, tubes tint the subject pink / cyan
    dark = exposure(saturation(img, 0.45), -1.3)
    bgw = 1 - feather(p, 4)
    dark = dark * (1 - 0.8 * bgw)[..., None]
    dark = blend(dark, field, 'soft_light', 0.55, mask_=feather(p, 3))
    dark = clip(dark + 0.02 * color('#5a2a8a'))
    # line art: silhouette + facial / fabric detail edges (background edges excluded)
    sil = cv2.Canny(ph * 255, 50, 150).astype(np.float32) / 255.0
    g = cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2GRAY)
    g = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(g)
    g = cv2.GaussianBlur(g, (0, 0), 1.8)
    inner = cv2.erode(ph, np.ones((13, 13), np.uint8)).astype(np.float32)
    det_lo = cv2.Canny(g, 40, 110).astype(np.float32) / 255.0
    det_hi = cv2.Canny(g, 95, 210).astype(np.float32) / 255.0
    eye_zone = mask('eyes', grow=34)
    det = np.where(eye_zone > 0.5, det_hi, det_lo) * inner
    det *= 1 - mask('mouth', grow=2)
    det = _remove_small(det > 0.5, 100)
    lines = np.maximum(_dilate(sil, 3), _dilate(det, 1))
    # neon tube: hot near-white core + layered coloured glow
    core = blur(lines, 1.3)
    halo = blur(lines, 4) * 0.9 + blur(lines, 12) * 0.55 + blur(lines, 30) * 0.4 + blur(lines, 70) * 0.35
    tube = core[..., None] * lerp(field, as_layer('#ffffff'), 0.7) + np.clip(halo, 0, 1.6)[..., None] * field
    return blend(dark, np.clip(tube, 0, 1), 'screen', 1.0)


# ----------------------------------------------------------------------------- 143 cyberpunk

@effect('cyberpunk')
def cyberpunk(img):
    """Night-city grade: cyan shadows / magenta highlights, teal foliage, two-colour rim light, glow, faint scanlines."""
    p = _person(2)
    x = lerp(exposure(img, -0.9), exposure(img, -0.25), p)
    x = hsl_adjust(x, 100, width=50, sat=1.1, lum=-0.03, shift=72)
    x = lerp(x, saturation(x, 1.35), 1 - p)
    x = split_tone(x, shadows='#12d0ff', highlights='#ff2fa0', strength=0.5)
    field = _x_field('#ff2fa0', '#22d3ff', 0.2, 0.8)
    x = blend(x, field, 'soft_light', 0.55, mask_=1 - p * 0.5)
    x = s_curve(x, 0.25)
    x = _skin_protect(x, img, 0.6)
    x = lerp(x, light_leak(x, '#ff2fa0', 'left', 0.45, seed=3, size=0.5), 1 - p * 0.55)
    band = inner_edge(p, 14, 6)
    x = blend(x, '#ff5ac8', 'screen', 0.9, mask_=band * _facing(p, (-0.85, -0.5)))
    x = blend(x, '#5ef0ff', 'screen', 0.9, mask_=band * _facing(p, (0.85, -0.5)))
    x = glow(x, 35, 0.4, 0.55)
    x = chromatic_aberration(x, 3)
    x = scanlines(x, 6, 0.12)
    x = grain(x, 0.03, seed=29)
    return vignette(x, 0.25, 1.0, 0.7)


# ----------------------------------------------------------------------------- 144 retro_poster

@effect('retro_poster')
def retro_poster(img):
    """Screen-print poster: 4 flat inks (cream paper, orange, burgundy, near-black) with halftone transitions,
    a slightly misregistered orange screen and paper texture."""
    sm = bilateral(img, 9, 0.12, 12)
    sm = bilateral(sm, 9, 0.10, 12)
    p = _person(3)
    L = luminance(sm)
    L = L * p + blur(L, 5.0) * (1 - p)                     # bigger flat shapes in the foliage
    L = clip(L + 0.15 * (L - blur(L, 50)))
    L = levels(L, 0.02, 0.78)
    L = clip(L + 0.06 * _skin(8, grow=-2))                 # the face prints mostly cream
    L = blur(L, 1.2)
    m_orange = _dots(1 - smoothstep(0.44, 0.62, L), 8, 15)
    m_burg = _dots(1 - smoothstep(0.24, 0.40, L), 9, 45)
    m_dark = _dots(1 - smoothstep(0.08, 0.20, L), 9, 75)
    m_orange = translate(as_layer(m_orange), 3, 2)[..., 0]
    out = canvas('#F2E4C8')
    out = lerp(out, as_layer('#e0823f'), m_orange)
    out = lerp(out, as_layer(BURGUNDY), m_burg)
    out = lerp(out, as_layer('#2b1a1a'), m_dark)
    tex = paper(seed=29, strength=0.14)
    return clip(out * tex[..., None])


# ----------------------------------------------------------------------------- 145 vaporwave

@effect('vaporwave')
def vaporwave(img):
    """Vaporwave: pink-purple-cyan gradient grade, striped retro sun behind the subject, neon perspective grid
    over the lower 30 %, retro glow and chromatic fringing."""
    p = _person(2)
    mapped = gradient_map(img, [(0.0, '#1a0b3a'), (0.33, '#7a2a9a'), (0.66, '#ff6ec7'), (1.0, '#8ef5ff')], 1.0)
    x = lerp(img, mapped, 0.78)
    x = lerp(x, lerp(img, mapped, 0.4), _skin(6, grow=-4))
    x = vibrance(x, 0.15)
    sun_col, sun_a = _vapor_sun((W * 0.80, H * 0.19), 235)
    sun_glow = (1 - smoothstep(235, 235 * 1.7, np.sqrt((coords()[0] - W * 0.80) ** 2 + (coords()[1] - H * 0.19) ** 2)))
    x = blend(x, '#ff6ec7', 'screen', 0.45, mask_=sun_glow * (1 - p))
    x = lerp(x, sun_col, sun_a * (1 - p) * 0.95)
    hy = H * 0.70
    grid = _vapor_grid(hy)
    gl = blur(grid, 1.0) * 1.0 + blur(grid, 6) * 0.7 + blur(grid, 20) * 0.5
    grid_layer = blur(grid, 1.0)[..., None] * color('#ffd6f2') * 0.6 + np.clip(gl, 0, 1.4)[..., None] * color('#ff2fb0')
    x = blend(x, np.clip(grid_layer, 0, 1), 'screen', 1.0)
    _, yy = coords()
    horizon = np.exp(-((yy - hy) / 2.5) ** 2) + 0.55 * np.exp(-((yy - hy) / 18.0) ** 2)
    x = blend(x, np.clip(horizon, 0, 1)[..., None] * color('#7ff6ff'), 'screen', 0.9)
    x = glow(x, 40, 0.3, 0.55)
    return chromatic_aberration(x, 4)
