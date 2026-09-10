"""Group g27 — Tekstura & nur o'yini (Texture & Light Play).

Codes: dust_scratches, paper_texture, bokeh_lights, sparkle, glitter.
All overlays are built as photographic layers: varied sizes, soft edges, depth-aware
placement (fewer/none over the face), warm glow that binds them to the photo.
"""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _win(cx, cy, R):
    """Clamped integer window (x0, x1, y0, y1) of half-size R around (cx, cy)."""
    x0, x1 = int(max(0, math.floor(cx - R))), int(min(W, math.ceil(cx + R) + 1))
    y0, y1 = int(max(0, math.floor(cy - R))), int(min(H, math.ceil(cy + R) + 1))
    return x0, x1, y0, y1


def _twinkle(layer, cx, cy, size, rotation=0.0, rays=4, intensity=1.0, minor=0.5, core=0.13, halo=0.3, width=None):
    """Sparkle star with thin tapered rays (main rays `size` px, minor rays in between at `minor` * size),
    a bright soft core and a faint halo. Added (max) into the (H,W) layer using a local window only."""
    R = int(size) + 4
    x0, x1, y0, y1 = _win(cx, cy, R)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    d = np.sqrt(dx * dx + dy * dy)
    w0 = width if width is not None else max(1.0, size * 0.05)
    s = np.zeros_like(d)
    rot = math.radians(rotation)
    for k in range(rays * 2):
        Lk = size if k % 2 == 0 else size * minor
        if Lk <= 1:
            continue
        a = rot + k * math.pi / rays
        ux, uy = math.cos(a), math.sin(a)
        along = dx * ux + dy * uy
        perp = np.abs(dy * ux - dx * uy)
        t = np.clip(along / Lk, 0, 1)
        w = w0 * (1 - 0.75 * t) + 0.45
        ray = np.exp(-(perp / w) ** 2) * (1 - t) ** 1.6 * (along > 0)
        s = np.maximum(s, ray)
    s = s + np.exp(-(d / (size * core)) ** 2) + halo * np.exp(-(d / (size * 0.4)) ** 2)
    layer[y0:y1, x0:x1] = np.maximum(layer[y0:y1, x0:x1], np.clip(s, 0, 1) * intensity)


def _disc(layer, cx, cy, rad, col, alpha, soft=0.3, rim=0.22):
    """Defocused-light bokeh disc (soft edge, slightly brighter rim) accumulated into an (H,W,3) layer."""
    R = rad * (1 + soft) + 3
    x0, x1, y0, y1 = _win(cx, cy, R)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad
    edge = 1 - smoothstep(1 - soft, 1 + soft * 0.4, d)
    body = (1 - rim) + rim * smoothstep(0.25, 0.92, d)
    layer[y0:y1, x0:x1] += (edge * body)[..., None] * col * alpha


def _film_scratches(r, count, x_ranges, intensity, thickness, length=(600, 1700)):
    """Near-vertical film-transport scratches with a slight wobble -> (H,W) mask."""
    m = np.zeros((H, W), np.float32)
    S = 16
    for _ in range(count):
        xr = x_ranges[r.integers(len(x_ranges))]
        x = r.uniform(*xr)
        Lx = r.uniform(*length)
        y0 = r.uniform(-120, H - Lx * 0.45)
        slope = math.tan(math.radians(r.uniform(-2.5, 2.5)))
        pts = []
        drift = 0.0
        for i in range(int(Lx / 20) + 1):
            t = i * 20.0
            drift += r.normal(0, 0.35)
            pts.append((int((x + t * slope + drift) * S), int((y0 + t) * S)))
        cv2.polylines(m, [np.array(pts, np.int32)], False, float(r.uniform(*intensity)),
                      int(r.integers(thickness[0], thickness[1] + 1)), cv2.LINE_AA, shift=4)
    return m


def _hairs(r, count, avoid, length=(90, 230)):
    """Small curly hair/fibre strands (as land on film in a scanner), kept off the `avoid` mask -> (H,W) mask."""
    m = np.zeros((H, W), np.float32)
    S = 16
    n = 0
    tries = 0
    while n < count and tries < 200:
        tries += 1
        x, y = r.uniform(0.06, 0.94) * W, r.uniform(0.06, 0.94) * H
        if avoid[int(y), int(x)] > 0.3:
            continue
        ang = r.uniform(0, 2 * math.pi)
        curv = r.uniform(0.02, 0.09) * (1 if r.random() < 0.5 else -1)
        pts = []
        for _i in range(int(r.uniform(*length) / 4)):
            pts.append((int(x * S), int(y * S)))
            ang += curv + r.normal(0, 0.05)
            x += 4 * math.cos(ang)
            y += 4 * math.sin(ang)
        cv2.polylines(m, [np.array(pts, np.int32)], False, float(r.uniform(0.65, 0.85)), int(r.integers(1, 3)), cv2.LINE_AA, shift=4)
        n += 1
    return feather(m, 0.6)


def _strands(count, seed, length=(14, 55), value=(0.06, 0.14)):
    """Sparse, faint, slightly curved paper fibres -> (H,W) mask."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    S = 16
    for _ in range(count):
        x, y = r.uniform(0, W), r.uniform(0, H)
        a = r.uniform(0, math.pi)
        Lx = r.uniform(*length)
        curv = r.uniform(-0.35, 0.35)
        pts = []
        for t in (0.0, 0.33, 0.66, 1.0):
            aa = a + curv * (t - 0.5)
            pts.append((int((x + Lx * t * math.cos(aa)) * S), int((y + Lx * t * math.sin(aa)) * S)))
        cv2.polylines(m, [np.array(pts, np.int32)], False, float(r.uniform(*value)), 1, cv2.LINE_AA, shift=4)
    return feather(m, 0.5)


def _bright_points(lb, allowed, count, min_dist, r, lo=0.62, hi=0.94):
    """Random well-spaced points on bright (but not blown) spots of the scene -> [(x, y, value), ...]."""
    cand = np.argwhere((lb > lo) & (lb < hi) & (allowed > 0.5))
    pts = []
    if len(cand) == 0:
        return pts
    for i in r.permutation(len(cand)):
        y, x = cand[i]
        if all((x - px) ** 2 + (y - py) ** 2 >= min_dist ** 2 for px, py, _ in pts):
            pts.append((int(x), int(y), float(lb[y, x])))
            if len(pts) >= count:
                break
    return pts


# ----------------------------------------------------------------------------- #131 dust & scratches

@effect('dust_scratches')
def dust_scratches(img):
    """Old film scan: faded warm base, uneven age mottling, sparse near-vertical light scratches (the strong
    ones off the face), a few small hairs, dust of all sizes, some dark specks, grain and a soft vignette."""
    r = rng(131)
    out = fade(img, 0.07, 0.03)
    out = saturation(out, 0.88)
    out = temperature(out, 0.07)
    out = split_tone(out, shadows='#2f3140', highlights='#f3e7cf', strength=0.15)
    mott = fbm(4, seed=131, scale=0.6)
    out = clip(out * (1 + 0.08 * (mott - 0.5))[..., None])

    face_soft = mask('face', feather=25)
    keep = 1 - 0.6 * face_soft                                      # the face stays comparatively clean
    x0, y0, x1, y1 = face_box()
    sides = [(30, x0 - 40), (x1 + 40, W - 30)]
    strong = _film_scratches(r, 4, sides, (0.7, 0.95), (2, 3), length=(1200, 1900))
    faint = _film_scratches(r, 13, [(0, W)], (0.22, 0.5), (1, 2), length=(400, 1500))
    along = noise(seed=139)
    along = cv2.GaussianBlur(along, (0, 0), sigmaX=30, sigmaY=5)
    along = (along - along.min()) / (along.max() - along.min() + 1e-6)
    mod = 0.45 + 0.55 * along                                       # scratches fade in and out along their length
    scr = np.clip(strong + faint * keep, 0, 1) * mod
    hairs = _hairs(r, 3, mask('face', feather=10, grow=40))
    d1 = dust(1100, seed=134, size=(1, 3)) * 0.7
    d2 = feather(dust(170, seed=135, size=(3, 6)), 0.6) * 0.6
    d3 = feather(dust(28, seed=136, size=(6, 12)), 1.5) * 0.35
    light = np.clip(scr + hairs + (d1 + d2 + d3) * keep, 0, 1)
    out = blend(out, light[..., None] * color('#fff3e2'), 'screen')
    dark = np.clip(dust(300, seed=137, size=(1, 3)) * 0.45 + feather(dust(20, seed=140, size=(3, 6)), 0.8) * 0.3, 0, 1) * keep
    out = clip(out * (1 - dark)[..., None])

    out = grain(out, 0.045, size=1.2, seed=138)
    out = vignette(out, 0.2, softness=0.75)
    return out


# ----------------------------------------------------------------------------- #132 paper texture

@effect('paper_texture')
def paper_texture(img):
    """Printed on fibrous art paper: cream paper white, matte ink, fine lit paper tooth, a woven field of
    fibres plus a few visible strands, small flecks, mottled sheet and lighter paper edges."""
    out = fade(img, 0.08, 0.05)
    out = contrast(out, 0.94)
    out = saturation(out, 0.9)
    out = clip(out * color(CREAM))                          # whites become paper white
    out = lerp(out, blur(out, 1.2), 0.3)                    # ink spreads a little into the fibres
    skin = mask('face_skin', feather=15)
    tex_w = (1 - 0.4 * skin)[..., None]                     # texture a little lighter on the skin

    # paper tooth: fine relief (2-10 px features) lit from the top-left
    hm = 0.6 * noise(seed=132, sigma=1.3) + 0.4 * noise(seed=133, sigma=3.5)
    gx = cv2.Sobel(hm, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(hm, cv2.CV_32F, 0, 1, ksize=3)
    a = math.radians(-135)
    sh = gx * math.cos(a) + gy * math.sin(a)
    sh = np.clip(sh / (sh.std() * 2.2 + 1e-6), -1, 1)
    relief = np.clip(0.5 + 0.5 * sh, 0, 1)
    out = blend(out, relief, 'overlay', 0.26 * tex_w)

    # woven fibre field (two directions) + mottled sheet
    fv = cv2.GaussianBlur(noise(seed=134), (0, 0), sigmaX=0.7, sigmaY=7.0)
    fh = cv2.GaussianBlur(noise(seed=135), (0, 0), sigmaX=7.0, sigmaY=0.7)
    fib = (fv - fv.mean()) / (fv.std() + 1e-6) + (fh - fh.mean()) / (fh.std() + 1e-6)
    out = clip(out * (1 + 0.035 * fib)[..., None] * paper(seed=27, strength=0.2, fibers=False)[..., None])
    # a few visible individual fibres and flecks (handmade-paper look)
    light = _strands(900, seed=1321, value=(0.08, 0.2))
    darkf = _strands(650, seed=1322, value=(0.07, 0.16))
    out = blend(out, light[..., None] * color('#fffaf0'), 'screen', tex_w)
    out = clip(out * (1 - darkf * tex_w[..., 0])[..., None])
    flecks = dust(260, seed=1323, size=(1, 2)) * 0.2 * (1 - 0.7 * skin)
    out = clip(out * (1 - flecks)[..., None])

    mott = fbm(3, seed=1324, scale=0.6)
    out = clip(out * (1 + 0.05 * (mott - 0.5))[..., None])
    out = vignette(out, 0.26, radius=0.95, softness=0.7, color_=CREAM)
    return out


# ----------------------------------------------------------------------------- #133 bokeh lights

@effect('bokeh_lights')
def bokeh_lights(img):
    """Warm festive grade with floating golden bokeh discs over the whole frame (sizes, softness and
    brightness varied for depth), kept off the eyes and mouth, bound with a soft glow."""
    r = rng(133)
    out = temperature(img, 0.12)
    out = hsl_adjust(out, 100, width=50, sat=0.85, shift=-18)          # greens drift golden
    out = split_tone(out, shadows='#4a3220', highlights='#ffd27a', strength=0.25)
    bgm = mask('background', feather=6)
    dim = curve(exposure(out, -0.3), [(0, 0), (0.7, 0.6), (1, 0.85)])   # background steps back, sky calms
    out = lerp(out, dim, bgm)
    out = vignette(out, 0.22, softness=0.75)

    face_zone = mask('face', feather=20, grow=30)
    protect = np.clip(mask('eyes', grow=55, feather=15) + mask('lips', grow=50, feather=15), 0, 1)
    pal = [color(c) for c in ('#ffcf6a', '#ffcf6a', '#ffb347', '#ffc9a0', '#fff1d2', '#ffe3a3')]
    layer = np.zeros((H, W, 3), np.float32)
    cols, rows = 6, 7
    for j in range(rows):
        for i in range(cols):
            n = 2 if r.random() < 0.45 else 1
            for _ in range(n):
                cx, cy = (i + r.random()) * W / cols, (j + r.random()) * H / rows
                if protect[int(cy), int(cx)] > 0.3:
                    continue
                fz = face_zone[int(cy), int(cx)]
                if fz > 0.5 and r.random() > 0.15:
                    continue
                rad = 22 + 93 * r.random() ** 1.4
                if fz > 0.5:
                    rad = min(rad, 36)
                big = (rad - 22) / 93                                    # 0 small .. 1 large
                alpha = r.uniform(0.55, 0.9) * (1 - 0.58 * big)           # big = nearer the lens = fainter
                soft = 0.18 + 0.32 * big + r.uniform(0, 0.08)            # ... and softer
                _disc(layer, cx, cy, rad, pal[r.integers(len(pal))], alpha, soft=soft, rim=r.uniform(0.15, 0.3))
    for _ in range(22):                                                  # distant tiny lights in the background
        cx, cy = r.uniform(0, W), r.uniform(0, H)
        if bgm[int(cy), int(cx)] < 0.5 or protect[int(cy), int(cx)] > 0.3:
            continue
        _disc(layer, cx, cy, r.uniform(7, 16), pal[r.integers(len(pal))], r.uniform(0.5, 0.85), soft=0.2, rim=0.1)
    layer = np.clip(layer, 0, 1)
    layer = np.clip(layer + blur(layer, 28) * 0.45, 0, 1)
    out = blend(out, layer, 'screen', 0.85)
    out = glow(out, sigma=40, strength=0.15, threshold=0.7)
    return out


# ----------------------------------------------------------------------------- #134 sparkle

@effect('sparkle')
def sparkle(img):
    """Twinkling stars on the eye catchlights and the smile, a dozen on the bright points of the scene,
    plus tiny glints; screen-blended with a soft glow."""
    r = rng(134)
    m = meta()
    tilt = math.degrees(math.atan2(m['eye_r'][1] - m['eye_l'][1], m['eye_r'][0] - m['eye_l'][0]))
    lb = blur(luminance(img), 1.2)
    layer = np.zeros((H, W), np.float32)

    # eyes: the actual specular catchlight inside each iris
    for name, (gx, gy) in (('iris_l', (404, 586)), ('iris_r', (599, 486))):
        im = mask(name, grow=2)
        x0, x1, y0, y1 = _win(gx, gy, 14)
        sub = lb[y0:y1, x0:x1] * im[y0:y1, x0:x1]
        yy, xx = divmod(int(np.argmax(sub)), x1 - x0)
        _twinkle(layer, x0 + xx, y0 + yy, 46, rotation=tilt, intensity=1.0, minor=0.55, core=0.1, halo=0.32, width=1.7)
    # smile: two front-teeth highlights
    for px, py, s in ((622, 765, 32), (556, 798, 25)):
        _twinkle(layer, px, py, s, rotation=tilt, intensity=0.95, minor=0.5, core=0.12, halo=0.25, width=1.3)

    # scene: bright leaf / sky-gap points, well spaced, sizes 20-70 (bigger on brighter points)
    allowed = 1 - mask('person', grow=14, feather=6)
    allowed[:50] = 0; allowed[-50:] = 0; allowed[:, :50] = 0; allowed[:, -50:] = 0      # keep stars off the frame edge
    pts = _bright_points(blur(lb, 2), allowed, 12, 150, r, lo=0.6, hi=0.95)
    for px, py, v in pts:
        size = r.uniform(28, 80) * (0.8 + 0.4 * smoothstep(0.6, 0.95, v))
        _twinkle(layer, px, py, min(size, 82), rotation=r.uniform(-20, 20), intensity=r.uniform(0.85, 1.0),
                 minor=r.uniform(0.4, 0.6), core=0.12, halo=0.32, width=r.uniform(1.4, 2.2))
    glints = _bright_points(blur(lb, 2), allowed, 26, 60, rng(1341), lo=0.5, hi=0.97)
    for px, py, v in glints:
        _twinkle(layer, px, py, r.uniform(5, 11), rotation=r.uniform(0, 90), intensity=r.uniform(0.5, 0.9),
                 minor=0.3, core=0.16, halo=0.2, width=0.8)

    col = layer[..., None] * color('#fff7e6')
    col = np.clip(col + blur(col, 7) * 0.6, 0, 1)
    out = blend(img, col, 'screen', 0.9)
    out = glow(out, sigma=30, strength=0.12, threshold=0.75)
    out = brightness(out, 0.02)
    return out


# ----------------------------------------------------------------------------- #135 glitter

@effect('glitter')
def glitter(img):
    """Fine glitter shimmer: thousands of soft 1-6 px specks (white / champagne / gold / pink) densest on
    clothing and background, a few mini sparkles, over a warm satin sheen."""
    r = rng(135)
    out = temperature(img, 0.08)
    t = linear(angle=35)
    band = np.exp(-((t - 0.48) / 0.28) ** 2).astype(np.float32)
    out = blend(out, band[..., None] * color('#ffd9a0'), 'soft_light', 0.5)
    out = glow(out, sigma=35, strength=0.15, threshold=0.65)

    w = np.ones((H, W), np.float32)
    w -= 0.85 * mask('face_skin', feather=8)
    w -= mask('eyes', grow=6, feather=4) + mask('lips', grow=4, feather=4) + mask('mouth', feather=3) + mask('brows', feather=3)
    w = np.clip(w, 0, 1)
    pal = [color(c) for c in ('#ffffff', '#fff3d0', '#ffd98a', '#ffe6b0', '#ffc9d6', '#ffffff')]

    def sample(n):
        xs, ys = r.uniform(0, W, n * 2), r.uniform(0, H, n * 2)
        ok = r.random(n * 2) < w[ys.astype(int), xs.astype(int)]
        return xs[ok][:n], ys[ok][:n]

    def specks(n, rad, inten, sigma=0.0):
        lay = np.zeros((H, W, 3), np.float32)
        for x, y in zip(*sample(n)):
            c = pal[r.integers(len(pal))] * r.uniform(*inten)
            cv2.circle(lay, (int(x * 16), int(y * 16)), int(r.uniform(*rad) * 16), c.tolist(), -1, cv2.LINE_AA, 4)
        return blur(lay, sigma) if sigma else lay

    layer = specks(5200, (0.6, 1.2), (0.35, 1.0), 0.4)
    layer += specks(1300, (1.2, 2.2), (0.5, 1.0))
    big = specks(220, (2.0, 3.2), (0.7, 1.0))
    layer += big + blur(big, 3) * 0.8
    sp = np.zeros((H, W), np.float32)
    for x, y in zip(*sample(48)):
        _twinkle(sp, x, y, r.uniform(7, 22), rotation=r.uniform(0, 90), intensity=r.uniform(0.6, 1.0),
                 minor=0.35, core=0.14, halo=0.25, width=0.9)
    layer += sp[..., None] * color('#fff4d8')
    layer = np.clip(layer, 0, 1)
    layer = np.clip(layer + blur(layer, 2.5) * 0.5, 0, 1)
    out = blend(out, layer, 'screen', 0.85)
    return brightness(out, 0.01)
