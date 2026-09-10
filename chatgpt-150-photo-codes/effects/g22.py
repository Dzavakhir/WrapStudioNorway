"""Group g22 — Ramkalar (Frames)
#106 vintage_frame   #107 passport   #108 torn_paper   #109 double_border   #110 postcard
"""
from effects.lib import *
from effects.registry import effect

SS = 3          # supersampling factor for the hand-drawn ornaments (drawn 3x, area-downsampled -> clean AA)
_SHIFT = 3      # cv2 fixed-point sub-pixel bits


# ----------------------------------------------------------------------------- vector drawing helpers

def _aa(w, h, draw_fn, ss=SS):
    """Anti-aliased alpha tile (h, w) in [0,1]. draw_fn(u8_array, scale) paints 255 at ss x resolution."""
    a = np.zeros((h * ss, w * ss), np.uint8)
    draw_fn(a, ss)
    return cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def _fx(v, s):
    return int(round(v * s * (1 << _SHIFT)))


def _dot(a, x, y, r, s, val=255):
    cv2.circle(a, (_fx(x, s), _fx(y, s)), max(1, _fx(r, s)), val, -1, cv2.LINE_AA, _SHIFT)


def _stroke(a, pts, widths, s):
    """Tapered calligraphic stroke: overlapping discs along a dense point list."""
    for (x, y), w in zip(pts, widths):
        cv2.circle(a, (_fx(x, s), _fx(y, s)), max(1, _fx(w / 2, s)), 255, -1, cv2.LINE_AA, _SHIFT)


def _poly(a, pts, s, val=255):
    p = np.array([[_fx(x, s), _fx(y, s)] for x, y in pts], np.int32)
    cv2.fillPoly(a, [p], val, cv2.LINE_AA, _SHIFT)


def _line(a, p, q, w, s, val=255):
    cv2.line(a, (_fx(p[0], s), _fx(p[1], s)), (_fx(q[0], s), _fx(q[1], s)), val, max(1, int(round(w * s))), cv2.LINE_AA, _SHIFT)


def _spiral(cx, cy, r0, r1, turns, end_deg, n=500):
    """Log spiral traversed outwards (r0 -> r1), ending at angle end_deg (screen coords, y down)."""
    t = np.linspace(0, 1, n)
    th = np.radians(end_deg) - (1 - t) * turns * 2 * np.pi
    r = r0 * (r1 / r0) ** t
    return np.stack([cx + r * np.cos(th), cy + r * np.sin(th)], 1).astype(np.float32)


def _bezier(p0, p1, p2, p3, n=300):
    t = np.linspace(0, 1, n)[:, None]
    P = [np.asarray(p, np.float32) for p in (p0, p1, p2, p3)]
    return ((1 - t) ** 3) * P[0] + 3 * ((1 - t) ** 2) * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


def _resample(pts, step=0.5):
    """Resample a polyline to ~step px spacing; returns (points, normalised arclength u in 0..1)."""
    pts = np.asarray(pts, np.float32)
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(2, int(s[-1] / step))
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, pts[:, 0]), np.interp(t, s, pts[:, 1])], 1), t / max(s[-1], 1e-6)


def _leaf(a, p, direction, length, width, s):
    """Small filled leaf (lens) starting at p, pointing along `direction`."""
    d = np.asarray(direction, np.float32); d = d / (np.linalg.norm(d) + 1e-6)
    nrm = np.array([-d[1], d[0]], np.float32)
    t = np.linspace(0, 1, 40)
    hw = width * np.sin(np.pi * t) ** 0.85
    c = p + d[None, :] * (t[:, None] * length)
    outline = np.concatenate([c + nrm * hw[:, None], (c - nrm * hw[:, None])[::-1]])
    _poly(a, outline, s)


def _blit_alpha(c, tile, x0, y0, col):
    """Paint colour `col` through alpha `tile` onto canvas `c` (in place) at (x0, y0)."""
    h, w = tile.shape
    reg = c[y0:y0 + h, x0:x0 + w]
    c[y0:y0 + h, x0:x0 + w] = lerp(reg, np.ones_like(reg) * color(col), tile)


def _rules(c, specs, col):
    """Axis-aligned rectangular rules on the full canvas. specs: [(inset, thickness), ...]."""
    col = color(col)
    for i, t in specs:
        c[i:i + t, i:W - i] = col; c[H - i - t:H - i, i:W - i] = col
        c[i:H - i, i:i + t] = col; c[i:H - i, W - i - t:W - i] = col


def _inner_shadow(pic, width=26, strength=0.28):
    h, w = pic.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    wgt = (1 - smoothstep(0, width, d)) ** 1.5
    return clip(pic * (1 - strength * wgt)[..., None])


def _local_radial(w, h, center=None, radius=0.95, softness=0.7):
    """radial() for an arbitrary tile size: 1 in the centre fading to 0 at `radius`."""
    cx, cy = center or (w / 2, h / 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
    return (1 - smoothstep(radius * (1 - softness), radius, d)).astype(np.float32)


def _rgba(rgb, alpha):
    a = np.clip(alpha, 0, 1)
    return np.dstack([np.clip(rgb, 0, 1), a])


def _rotate_rgba(rgb, alpha, deg, fill):
    """Rotate an RGB + alpha tile (expand=True). Transparent pixels are pre-filled with `fill` to avoid dark fringes."""
    fill = color(fill)
    rgb = np.where(alpha[..., None] > 0.02, rgb, fill)
    pil = Image.fromarray(np.dstack([to_u8(rgb), to_u8(alpha)[..., None]]), 'RGBA')
    if deg:
        pil = pil.rotate(deg, resample=Image.BICUBIC, expand=True, fillcolor=color255(fill) + (0,))
    return pil


def _composite(canvas_img, pil_rgba, center, shadow=(0.38, 26, (10, 16))):
    """Composite an RGBA PIL tile onto a float canvas with a soft drop shadow."""
    cx, cy = center
    x0, y0 = int(round(cx - pil_rgba.width / 2)), int(round(cy - pil_rgba.height / 2))
    out = to_pil(canvas_img).convert('RGBA')
    if shadow:
        op, sb, (dx, dy) = shadow
        sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
        a = pil_rgba.split()[3].point(lambda v: int(v * op))
        sh.paste(Image.new('RGBA', pil_rgba.size, (20, 10, 6, 255)), (x0 + dx, y0 + dy), a)
        sh = sh.filter(ImageFilter.GaussianBlur(sb))
        out = Image.alpha_composite(out, sh)
    layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    layer.paste(pil_rgba, (x0, y0), pil_rgba)
    return from_pil(Image.alpha_composite(out, layer))


def _crop_aspect(img, aspect, y_bias=0.5):
    """Centre-crop `img` to width/height = aspect. y_bias: where to keep the crop vertically (0 top .. 1 bottom)."""
    h, w = img.shape[:2]
    if w / h > aspect:
        cw = int(round(h * aspect)); x0 = (w - cw) // 2
        return img[:, x0:x0 + cw]
    ch = int(round(w / aspect)); y0 = int(round((h - ch) * y_bias))
    return img[y0:y0 + ch]


# ----------------------------------------------------------------------------- #106 vintage_frame ornaments

def _scroll_path():
    """Top-edge scroll of the corner piece, in tile coordinates (origin = inner corner of the thin rule)."""
    S = (96.0, 47.0)
    sp = _spiral(S[0], S[1], 2.4, 23.0, 2.0, -90)
    p0 = sp[-1]
    tail = _bezier(p0, (p0[0] + 55, p0[1] - 2), (172, 76), (262, 44))
    path = np.concatenate([sp, tail[1:]])
    pts, u = _resample(path, 0.5)
    peak = 0.38
    wd = np.where(u < peak, 1.2 + (5.2 - 1.2) * smoothstep(0, peak, u), 5.2 - (5.2 - 0.9) * smoothstep(peak, 1, u))
    # accents: trailing dots after the tail, a small leaf at the tail's dip
    d = np.array([262 - 172, 44 - 76], np.float32); d /= np.linalg.norm(d)
    dots = [((262 + d[0] * k, 44 + d[1] * k), r) for k, r in ((9, 2.3), (18, 1.7), (26, 1.2))]
    tb = _bezier(p0, (p0[0] + 55, p0[1] - 2), (172, 76), (262, 44), 200)
    i = 118
    tang = tb[i + 1] - tb[i - 1]; tang /= np.linalg.norm(tang)
    nrm = np.array([-tang[1], tang[0]], np.float32)
    if nrm[1] < 0:
        nrm = -nrm
    leaf = (tb[i] + nrm * 1.5, nrm * 0.75 + tang * 0.35)
    return pts, wd, dots, leaf


def _corner_tile(T=280):
    """Corner flourish for the top-left corner -> (T, T) alpha. Flip for the other corners."""
    pts, wd, dots, leaf = _scroll_path()

    def draw(a, s):
        for mirror in (False, True):
            P = pts[:, ::-1] if mirror else pts
            _stroke(a, P, wd, s)
            for (x, y), r in dots:
                _dot(a, y if mirror else x, x if mirror else y, r, s)
            lp, ld = leaf
            if mirror:
                _leaf(a, lp[::-1], ld[::-1], 20, 5.2, s)
            else:
                _leaf(a, lp, ld, 20, 5.2, s)
        # lozenge on the diagonal + a cream 'eye' in its centre
        C = np.array([40.0, 40.0]); d1 = np.array([1, 1]) / math.sqrt(2); d2 = np.array([1, -1]) / math.sqrt(2)
        _poly(a, [C + d1 * 19, C + d2 * 8, C - d1 * 19, C - d2 * 8], s)
        _dot(a, C[0], C[1], 2.6, s, 0)
        # small bridging dots between the lozenge and the two scrolls
        for x, y in ((64, 39), (39, 64)):
            _dot(a, x, y, 2.0, s)
    return _aa(T, T, draw)


def _midside_tile():
    """Small centre ornament for the middle of each side (horizontal orientation) -> (36, 96) alpha."""
    def draw(a, s):
        C = np.array([48.0, 18.0])
        _poly(a, [C + (15, 0), C + (0, 5.5), C - (15, 0), C - (0, 5.5)], s)
        _dot(a, C[0], C[1], 1.8, s, 0)
        for dx, r in ((24, 2.2), (-24, 2.2), (33, 1.3), (-33, 1.3)):
            _dot(a, C[0] + dx, C[1], r, s)
    return _aa(96, 36, draw)


@effect('vintage_frame')
def vintage_frame(img):
    P = 150                                   # photo inset
    # --- antique photo grade: light sepia, gentle fade, warm vignette, whisper of grain
    pic = sepia(img, 0.3)
    pic = fade(pic, 0.05, 0.03)
    pic = temperature(pic, 0.06)
    pic = vignette(pic, 0.32, radius=1.05, softness=0.8, color_='#2a1a10')
    pic = grain(pic, 0.03, seed=106)
    pic = resize(pic, W - 2 * P, H - 2 * P)
    pic = _inner_shadow(pic, 26, 0.26)
    # --- cream paper mat, faintly aged
    c = canvas('#F6EFE2', paper(seed=106, strength=0.13))
    c = vignette(c, 0.12, radius=1.2, softness=0.9, color_='#9a7a55')
    c[P:H - P, P:W - P] = pic
    # --- double rule (thick + thin) in burgundy, gold keyline hugging the photo
    _rules(c, [(42, 5), (56, 2)], BURGUNDY)
    _rules(c, [(144, 2)], GOLD)
    # --- corner flourishes + centre ornaments
    tile = _corner_tile()
    T = tile.shape[0]; o = 58
    for y0, x0, fy, fx in ((o, o, 0, 0), (o, W - o - T, 0, 1), (H - o - T, o, 1, 0), (H - o - T, W - o - T, 1, 1)):
        t = tile[::-1] if fy else tile
        t = t[:, ::-1] if fx else t
        _blit_alpha(c, t, x0, y0, BURGUNDY)
    ms = _midside_tile(); mh, mw = ms.shape
    cy = o + (P - o) // 2
    _blit_alpha(c, ms, W // 2 - mw // 2, cy - mh // 2, BURGUNDY)
    _blit_alpha(c, ms, W // 2 - mw // 2, H - cy - mh // 2, BURGUNDY)
    msv = np.ascontiguousarray(ms.T)
    _blit_alpha(c, msv, cy - mh // 2, H // 2 - mw // 2, BURGUNDY)
    _blit_alpha(c, msv, W - cy - mh // 2, H // 2 - mw // 2, BURGUNDY)
    return c


# ----------------------------------------------------------------------------- #107 passport (photo-booth sheet)

@effect('passport')
def passport(img):
    g = 44                                           # equal gaps and margins
    w, h = (W - 3 * g) // 2, (H - 3 * g) // 2        # 510 x 654
    pic = _crop_aspect(img, w / h)                   # trims ~15 px per side instead of distorting
    pic = s_curve(pic, 0.1)
    pic = vibrance(pic, 0.08)
    small = cv2.resize(pic, (w, h), interpolation=cv2.INTER_AREA)
    small = unsharp(small, 1.0, 0.3)
    c = canvas('#FFFFFF')
    xs = (g, 2 * g + w); ys = (g, 2 * g + h)
    for y in ys:
        for x in xs:
            c[y:y + h, x:x + w] = small

    def cuts(d):
        grey = rgba('#BDBDBD', 1.0)
        dash, gap = 14, 10
        # dashed cut lines through the centre of the gaps
        x = W // 2
        for y in range(0, H, dash + gap):
            d.line((x, y, x, min(H, y + dash)), fill=grey, width=1)
        y = H // 2
        for x in range(0, W, dash + gap):
            d.line((x, y, min(W, x + dash), y), fill=grey, width=1)
        # corner crop marks at the sheet edges, aligned with the photo edges
        L = 22
        for x in (g, W - g):
            d.line((x, 6, x, 6 + L), fill=grey, width=1); d.line((x, H - 7 - L, x, H - 7), fill=grey, width=1)
        for y in (g, H - g):
            d.line((6, y, 6 + L, y), fill=grey, width=1); d.line((W - 7 - L, y, W - 7, y), fill=grey, width=1)
    return draw_shapes(c, cuts)


# ----------------------------------------------------------------------------- #108 torn_paper

def _edge_profile(n, seed, amp, rough):
    """1-D torn-edge displacement: smooth wobble + mid detail + fine jaggedness."""
    r = rng(seed)
    coarse = cv2.resize((r.random(9).astype(np.float32) * 2 - 1)[None, :], (n, 1), interpolation=cv2.INTER_CUBIC)[0]
    mid = cv2.resize((r.random(48).astype(np.float32) * 2 - 1)[None, :], (n, 1), interpolation=cv2.INTER_CUBIC)[0]
    fine = cv2.GaussianBlur(r.standard_normal(n).astype(np.float32)[None, :], (0, 0), sigmaX=1.1)[0]
    return amp * coarse + amp * 0.35 * mid + rough * fine


@effect('torn_paper')
def torn_paper(img):
    tw, th = 1040, 1300                              # paper tile
    ins, amp = 36, 24
    pic = resize(img, tw, th)
    pic = fade(pic, 0.05, 0.02)
    pic = s_curve(pic, 0.05)
    pic = temperature(pic, 0.04)
    yy, xx = np.mgrid[0:th, 0:tw].astype(np.float32)
    top = ins + _edge_profile(tw, 1081, amp, 2.2)
    bot = th - ins + _edge_profile(tw, 1082, amp, 2.2)
    lef = ins + _edge_profile(th, 1083, amp, 2.2)
    rig = tw - ins + _edge_profile(th, 1084, amp, 2.2)
    sm = lambda v: smoothstep(-0.8, 0.8, v)
    P = sm(yy - top[None, :]) * sm(bot[None, :] - yy) * sm(xx - lef[:, None]) * sm(rig[:, None] - xx)
    Pb = (P > 0.5).astype(np.uint8)
    dist_in = cv2.distanceTransform(Pb, cv2.DIST_L2, 5)
    # white paper core between the torn outline and the (receded) image layer: 4..15 px, rough
    wf = 4.5 + 10.0 * noise(1085, 6.0, (th, tw)) + 2.5 * (noise(1086, 1.0, (th, tw)) - 0.5)
    I = smoothstep(wf - 0.8, wf + 0.8, dist_in)
    # thin darker line where the emulsion breaks (just outside the image layer)
    Ib = (I > 0.5).astype(np.uint8)
    dist_I = cv2.distanceTransform(1 - Ib, cv2.DIST_L2, 5)
    edge_line = (1 - smoothstep(0.3, 2.2, dist_I)) * (1 - I)
    rim = np.ones((th, tw, 3), np.float32) * color('#F4EFE6')
    rim *= (0.9 + 0.1 * noise(1087, 0.8, (th, tw)))[..., None]              # fibrous texture
    rim *= (1 - 0.42 * edge_line)[..., None]
    rgb = lerp(rim, pic, I)
    alpha = P.copy()
    # fibre wisps sticking out of the torn outline
    r = rng(1088)
    fib = np.zeros((th, tw), np.uint8)
    for k in range(260):
        side = r.integers(4)
        if side == 0:
            x = r.uniform(ins, tw - ins); y = top[int(x)]; d = (r.uniform(-0.4, 0.4), -1)
        elif side == 1:
            x = r.uniform(ins, tw - ins); y = bot[int(x)]; d = (r.uniform(-0.4, 0.4), 1)
        elif side == 2:
            y = r.uniform(ins, th - ins); x = lef[int(y)]; d = (-1, r.uniform(-0.4, 0.4))
        else:
            y = r.uniform(ins, th - ins); x = rig[int(y)]; d = (1, r.uniform(-0.4, 0.4))
        L = r.uniform(3, 13)
        cv2.line(fib, (int(x), int(y)), (int(x + d[0] * L), int(y + d[1] * L)), int(r.uniform(120, 220)), 1, cv2.LINE_AA)
    fibm = fib.astype(np.float32) / 255.0
    rgb = np.where((fibm > alpha)[..., None], color('#F4EFE6'), rgb)
    alpha = np.maximum(alpha, fibm)
    pil = _rotate_rgba(rgb, alpha, 2.0, '#F4EFE6')
    # --- beige paper backdrop
    c = canvas(BEIGE, paper(seed=108, strength=0.16))
    c = vignette(c, 0.16, radius=1.25, softness=0.9, color_='#7a6247')
    return _composite(c, pil, (W / 2, H / 2 - 4), shadow=(0.4, 24, (10, 16)))


# ----------------------------------------------------------------------------- #109 double_border

@effect('double_border')
def double_border(img):
    P = 88                                           # photo inset (cream mat width)
    pic = s_curve(img, 0.06)
    pic = vibrance(pic, 0.08)
    pic = resize(pic, W - 2 * P, H - 2 * P)
    pic = _inner_shadow(pic, 14, 0.14)
    c = canvas(CREAM, paper(seed=109, strength=0.05))
    c[P:H - P, P:W - P] = pic
    _rules(c, [(60, 14)], BURGUNDY)                  # inner burgundy frame line
    _rules(c, [(P - 2, 2)], '#FFFFFF')               # white bevel of the mat aperture
    return c


# ----------------------------------------------------------------------------- #110 postcard

def _stamp(img, w=168, h=204, pitch=12, hole=4.6):
    """Perforated postage stamp with a burgundy-toned mini portrait -> (rgb, alpha) at 1x, built at 3x."""
    s = SS
    Wt, Ht = w * s, h * s
    paper_c = color('#F3EDE0')
    tile = np.ones((Ht, Wt, 3), np.float32) * paper_c
    # picture window
    m = 14 * s; mb = 36 * s
    ww, wh = Wt - 2 * m, Ht - m - mb
    mini = _crop_aspect(img, ww / wh)
    mini = cv2.resize(mini, (ww, wh), interpolation=cv2.INTER_AREA)
    mini = duotone(s_curve(mini, 0.12), BURGUNDY_DEEP, '#F3E7D4')
    tile[m:m + wh, m:m + ww] = mini
    tile = draw_shapes(tile, lambda d: d.rectangle((m - 1, m - 1, m + ww, m + wh), outline=rgba(BURGUNDY_DEEP, 0.85), width=2 * s))
    tile = draw_shapes(tile, lambda d: d.rectangle((m - 4 * s, m - 4 * s, Wt - m + 4 * s, Ht - m + 4 * s), outline=rgba(BURGUNDY_DEEP, 0.55), width=s))
    tile = draw_text(tile, 'POCHTA', (Wt / 2, Ht - mb / 2 - 2 * s), font('lato-bold', 11 * s), BURGUNDY_DEEP, anchor='mm', tracking=2.5 * s, opacity=0.9)
    tile = draw_text(tile, '12', (m + 3 * s, Ht - mb / 2 - 2 * s), font('playfair-bold', 15 * s), BURGUNDY_DEEP, anchor='lm', opacity=0.9)
    tile = draw_text(tile, '12', (Wt - m - 3 * s, Ht - mb / 2 - 2 * s), font('playfair-bold', 15 * s), BURGUNDY_DEEP, anchor='rm', opacity=0.9)
    # perforation
    a = np.full((Ht, Wt), 255, np.uint8)
    for x in np.arange(pitch / 2, w, pitch):
        for y in (0, h):
            _dot(a, x, y, hole, s, 0)
    for y in np.arange(pitch / 2, h, pitch):
        for x in (0, w):
            _dot(a, x, y, hole, s, 0)
    alpha = a.astype(np.float32) / 255.0
    # premultiplied downsample
    prem = cv2.resize(tile * alpha[..., None], (w, h), interpolation=cv2.INTER_AREA)
    al = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_AREA)
    rgb = np.where(al[..., None] > 1e-3, prem / np.maximum(al, 1e-3)[..., None], paper_c)
    return clip(rgb), al


def _postmark(tw=470, th=210, R=76, cx=95, cy=105):
    """Circular postmark with ring text + wavy cancellation bars -> (th, tw) alpha at 1x (drawn at 3x)."""
    s = SS
    a = np.zeros((th * s, tw * s), np.uint8)
    cv2.circle(a, (_fx(cx, s), _fx(cy, s)), _fx(R, s), 255, max(1, int(round(2.6 * s))), cv2.LINE_AA, _SHIFT)
    cv2.circle(a, (_fx(cx, s), _fx(cy, s)), _fx(R - 16, s), 255, max(1, int(round(1.8 * s))), cv2.LINE_AA, _SHIFT)
    # wavy killer bars to the right of the circle
    xs = np.linspace(cx + R + 6, tw - 8, 220)
    for k in range(-2, 3):
        yb = cy + k * 17
        ys = yb + 4.5 * np.sin(xs / 11.0 + k * 0.9)
        pts = np.array([[_fx(x, s), _fx(y, s)] for x, y in zip(xs, ys)], np.int32)
        cv2.polylines(a, [pts], False, 255, max(1, int(round(3.0 * s))), cv2.LINE_AA, _SHIFT)
    # ring text (top arc reads clockwise, bottom arc counter-clockwise) + date in the centre
    pil = Image.fromarray(a)
    f = font('lato-bold', 14 * s)
    rr = (R - 8) * s
    for text, a0, flip in (('SALOM  ·  POCHTA', -90, False), ('2026', 90, True)):
        widths = [f.getlength(ch) for ch in text]
        trk = 2.2 * s
        total = sum(widths) + trk * (len(text) - 1)
        ang = a0 - math.degrees(total / 2 / rr) * (-1 if flip else 1)
        for ch, wch in zip(text, widths):
            step = math.degrees((wch / 2) / rr)
            ang += step * (-1 if flip else 1)
            L = Image.new('L', pil.size, 0)
            d = ImageDraw.Draw(L)
            d.text((cx * s, cy * s - rr), ch, font=f, fill=255, anchor='mm')
            if flip:
                L = L.rotate(180, center=(cx * s, cy * s - rr))
            L = L.rotate(-(ang + 90), resample=Image.BICUBIC, center=(cx * s, cy * s))
            pil = ImageChops.lighter(pil, L)
            ang += (step + math.degrees(trk / rr)) * (-1 if flip else 1)
    d = ImageDraw.Draw(pil)
    d.text((cx * s, cy * s - 9 * s), '10 · 09', font=font('lato-bold', 17 * s), fill=255, anchor='mm')
    d.text((cx * s, cy * s + 11 * s), 'SAAT 9', font=font('lato-bold', 12 * s), fill=255, anchor='mm')
    al = cv2.resize(np.array(pil), (tw, th), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    ink = 0.55 + 0.45 * noise(1101, 1.2, (th, tw))          # uneven ink coverage
    return al * ink


@effect('postcard')
def postcard(img):
    cw, ch = 1000, 1260                              # card size
    # --- card stock: cream paper, slightly yellowed towards the edges
    card = np.ones((ch, cw, 3), np.float32) * color('#F6F0E3')
    card *= paper(seed=110, strength=0.14)[:ch, :cw][..., None]
    card = clip(lerp(card, np.ones_like(card) * color('#D9C4A0'), 0.22 * (1 - _local_radial(cw, ch, radius=1.15, softness=0.9))))
    # --- the picture: white-border print, light sepia + fade
    bx0, by0, bx1, by1 = 36, 36, cw - 36, 1096         # white border rectangle
    card[by0:by1, bx0:bx1] = color('#FBF9F4')
    px0, py0 = bx0 + 30, by0 + 30
    pw, ph = (bx1 - bx0) - 60, (by1 - by0) - 60
    pic = _crop_aspect(img, pw / ph, y_bias=0.2)
    pic = sepia(pic, 0.25)
    pic = fade(pic, 0.08, 0.04)
    pic = temperature(pic, 0.05)
    pic = resize(pic, pw, ph)
    pic = clip(lerp(pic, np.zeros_like(pic) + color('#2a1a10'), 0.22 * (1 - _local_radial(pw, ph, radius=1.05, softness=0.8))))
    card[py0:py0 + ph, px0:px0 + pw] = pic
    # --- greeting
    card = draw_text(card, 'Salom!', (72, 1192), font('playfair-italic', 100), BURGUNDY, anchor='ls')
    card = draw_text(card, 'Sevgi bilan', (78, 1234), font('cormorant-italic', 38), INK, anchor='ls', opacity=0.7)
    card = draw_text(card, 'POST CARD', (cw - 72, 1225), font('lato-bold', 17), TAUPE, anchor='rs', tracking=5)
    card = draw_shapes(card, lambda d: d.line((cw - 72 - 132, 1198, cw - 72, 1198), fill=rgba(TAUPE, 0.9), width=1))
    # --- stamp (top-right, slightly askew) with a tiny shadow
    st_rgb, st_a = _stamp(img)
    st = _rotate_rgba(st_rgb, st_a, 4.0, '#F3EDE0')
    card = _composite(card, st, (838, 172), shadow=(0.28, 3, (2, 3)))
    # --- postmark over stamp + picture
    pm = _postmark()
    pmh, pmw = pm.shape
    x0, y0 = 655, 176
    region = card[y0:y0 + pmh, x0:x0 + pmw]
    card[y0:y0 + pmh, x0:x0 + pmw] = lerp(region, np.ones_like(region) * color('#26262b'), 0.72 * pm[:region.shape[0], :region.shape[1]])
    # --- lay the card on a warm desk
    alpha = rounded_mask(cw, ch, 10)
    pil = _rotate_rgba(card, alpha, -1.5, '#F6F0E3')
    bg = canvas('#BFAE95', paper(seed=111, strength=0.16))
    bg = vignette(bg, 0.32, radius=1.2, softness=0.9, color_='#5a4634')
    return _composite(bg, pil, (W / 2, H / 2 + 2), shadow=(0.42, 30, (12, 22)))
