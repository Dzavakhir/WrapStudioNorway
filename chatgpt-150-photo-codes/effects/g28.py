"""Group g28 — Tekstura & nur o'yini (Texture & light play):
light_rays, blinds_shadow, leaf_shadow, lace_shadow, haze.

The four "shadow / beam" codes share one physically-motivated relighting model (_relight): the photo is
split into an ambient (shade) version — darker, a touch cooler and flatter — and a direct-sun version —
warmer, brighter with a soft highlight knee — and a (H,W) light pattern mixes the two. A blurred copy of
the lit areas is then screened back at low opacity (light scattered in the air / bounced off the lit patches),
which makes the gaps read as real warm light rather than a pasted overlay.
"""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- shared helpers

def _person(feather_=2.0):
    """Solid-core person mask (the stored one sits at ~0.988 with a faint ring), lightly feathered."""
    p = smoothstep(0.03, 0.97, mask('person'))
    return feather(p, feather_) if feather_ else p


def _face_blob(grow=30, feather_=40.0):
    """Soft blob over the face — used to keep light patterns a little gentler on the skin (flattering)."""
    return mask('face', feather=feather_, grow=grow)


def _soft_gain(img, gain, knee=0.72):
    """Multiply by gain (scalar or (H,W,1)) with a smooth highlight roll-off so nothing clips to flat white."""
    y = img * gain
    over = knee + (1 - knee) * (1 - np.exp(-(y - knee) / (1 - knee)))
    return np.where(y > knee, over, y).astype(np.float32)


def _relight(img, lit, shade=0.6, gain=1.15, shade_tint=(0.97, 1.0, 1.05), sun_tint=(1.06, 1.0, 0.9),
             shade_lift=0.02, shade_desat=0.1, scatter=0.12, scatter_sigma=35, scatter_color='#ffdcae'):
    """Relight the photo with a (H,W) pattern: 1 = direct sun, 0 = shade.
    shade: ambient level (scalar or (H,W,1)); gain: direct-sun multiplier; tints are RGB gains."""
    lit = np.clip(np.asarray(lit, np.float32), 0, 1)
    lit3 = lit[..., None]
    amb = img * (shade * np.array(shade_tint, np.float32)) + shade_lift
    if shade_desat:
        amb = lerp(gray(amb), amb, 1 - shade_desat)
    sun = _soft_gain(img * np.array(sun_tint, np.float32), gain)
    out = clip(lerp(amb, sun, lit3))
    if scatter:
        g = blur(lit * np.clip(luminance(sun), 0, 1), scatter_sigma)
        out = blend(out, g[..., None] * color(scatter_color), 'screen', scatter)
    return out


# ----------------------------------------------------------------------------- 136 light_rays

@effect('light_rays')
def light_rays(img):
    """Soft diagonal shafts of sunlight from beyond the top-left corner: three wide beams (plus a faint fourth)
    that diverge slightly, are streaky along their length and fade with distance. Everything outside the beams
    sits in slightly dimmer ambient light, the beams light the surfaces they cross and glow in the air."""
    x, y = coords()
    sx, sy = -760.0, -420.0                                   # light source, off-frame top-left
    dx, dy = x - sx, y - sy
    ang = np.degrees(np.arctan2(dy, dx))
    dist = np.sqrt(dx * dx + dy * dy)
    fx, fy = face_center()
    a_face = math.degrees(math.atan2(fy - sy, fx - sx))       # the main beam falls across the face
    beam = np.zeros((H, W), np.float32)
    for da, wdeg, s in ((-16.0, 4.2, 0.8), (0.0, 5.2, 1.0), (15.5, 3.6, 0.7), (28.0, 2.4, 0.4)):
        d = ang - (a_face + da)
        beam += s * np.exp(-(d / wdeg) ** 2)
    tex = fbm(4, seed=28, scale=1.3)                          # streaks along the beams
    tex = motion_blur(tex, length=240, angle=-a_face)
    tex = (tex - tex.min()) / (tex.max() - tex.min() + 1e-6)
    beam *= 0.72 + 0.28 * tex
    beam *= 1 - 0.55 * smoothstep(600, 2700, dist)            # fades away from the source
    beam = np.clip(beam, 0, 1).astype(np.float32)
    fb = _face_blob(grow=20, feather_=40)
    b3 = beam[..., None]
    # 1) ambient outside the beams, warm light on the surfaces inside them
    amb = lerp(gray(img), img, 0.92) * np.array([0.78, 0.79, 0.84], np.float32) + 0.015
    sun = _soft_gain(img * np.array([1.07, 1.0, 0.86], np.float32), 1.22)
    out = clip(lerp(amb, sun, np.clip(beam * 1.25, 0, 1)))
    # 2) the shafts visible in the air (a little gentler over the face)
    out = blend(out, (beam * (1 - 0.35 * fb))[..., None] * color('#fff0d0'), 'screen', 0.6)
    # 3) the source itself glowing in the top-left corner
    src = radial(center=(-140, -80), radius=1.7, softness=0.92)
    out = blend(out, src[..., None] * color('#ffe6b8'), 'screen', 0.5)
    # 4) dust motes drifting inside the beams
    motes = bokeh_layer(count=80, seed=5, radius=(2.5, 8.0), color_='#fff3d8',
                        area=(beam > 0.35).astype(np.float32), softness=0.6, alpha=(0.3, 0.7))
    out = blend(out, motes * b3, 'screen', 0.85)
    # 5) atmosphere
    out = fade(out, 0.03, 0.0)
    out = temperature(out, 0.08)
    out = glow(out, sigma=45, strength=0.2, threshold=0.6)
    return out


# ----------------------------------------------------------------------------- 137 blinds_shadow

@effect('blinds_shadow')
def blinds_shadow(img):
    """Venetian-blind stripes across subject and background. The phase is locked so a lit slat crosses both
    eyes and the mouth; the background (further from the slats) gets softer, weaker stripes with a slight
    downward parallax shift; the shade is cool-neutral, the lit slats warm — classic noir."""
    m = meta()
    angle, period, duty = -8.0, 130.0, 0.52
    a = math.radians(angle)
    ex, ey = m['eye_r']
    t_eye = ex * math.sin(a) + ey * math.cos(a)
    offset = (period * duty / 2 - t_eye) % period
    near = stripes(angle, period, duty, softness=9, offset=offset)
    far = stripes(angle, period, duty, softness=30, offset=offset - 30)
    p = _person(2.5)
    lit = near * p + far * (1 - p)
    shade = (0.54 * p + 0.68 * (1 - p))[..., None]
    out = _relight(img, lit, shade=shade, gain=1.16, shade_tint=(0.96, 0.99, 1.05), sun_tint=(1.08, 1.0, 0.85),
                   shade_lift=0.015, shade_desat=0.08, scatter=0.1, scatter_sigma=30)
    out = contrast(out, 1.05)
    out = vignette(out, 0.25, radius=1.0, softness=0.75)
    return out


# ----------------------------------------------------------------------------- 138 leaf_shadow

def _leaf_poly(cx, cy, L, w, ang, qa=0.85, qb=1.15, n=22):
    """Leaf outline (pointed ends, slightly asymmetric) centred at (cx,cy), half-length L, half-width w."""
    t = np.linspace(-1, 1, n)
    base_ = np.clip(1 - t * t, 0, 1)
    top = w * base_ ** qa
    bot = -w * base_ ** qb
    xs = np.concatenate([t, t[::-1]]) * L
    ys = np.concatenate([top, bot[::-1]])
    c, s = math.cos(ang), math.sin(ang)
    px = cx + xs * c - ys * s
    py = cy + xs * s + ys * c
    return np.stack([px, py], 1).astype(np.int32)


def _foliage_mask(seed, twigs, leaves_per_twig, size, keep_fn=None, scale=1.0):
    """Shadow of leafy twigs -> (H,W) mask (1 = shadow). Leaves sit on random-walk twigs like real branches;
    keep_fn(x, y) -> probability of keeping a leaf / twig segment there (used to open a sun patch)."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(twigs):
        pts = [(r.uniform(-120, W + 120), r.uniform(-120, H + 120))]
        ang = r.uniform(0, 2 * math.pi)
        for _ in range(int(r.integers(3, 6))):
            ang += r.uniform(-0.55, 0.55)
            L = r.uniform(70, 130) * scale
            pts.append((pts[-1][0] + L * math.cos(ang), pts[-1][1] + L * math.sin(ang)))
        for k in range(len(pts) - 1):
            mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
            if keep_fn is not None and keep_fn(mx, my) < 0.5:
                continue
            cv2.line(m, (int(pts[k][0]), int(pts[k][1])), (int(pts[k + 1][0]), int(pts[k + 1][1])), 1.0,
                     int(max(2, round(4 * scale))), cv2.LINE_AA)
        for _ in range(leaves_per_twig):
            seg = int(r.integers(0, len(pts) - 1))
            u = r.uniform(0, 1)
            bx = pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * u
            by = pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * u
            seg_ang = math.atan2(pts[seg + 1][1] - pts[seg][1], pts[seg + 1][0] - pts[seg][0])
            side = 1 if r.random() < 0.5 else -1
            la = seg_ang + side * r.uniform(0.5, 1.25)
            Lf = r.uniform(*size) * scale
            wf = Lf * r.uniform(0.32, 0.5)
            cx = bx + math.cos(la) * Lf * 1.15
            cy = by + math.sin(la) * Lf * 1.15
            if keep_fn is not None and r.random() > keep_fn(cx, cy):
                continue
            cv2.line(m, (int(bx), int(by)), (int(cx - math.cos(la) * Lf * 0.9), int(cy - math.sin(la) * Lf * 0.9)), 1.0, 2, cv2.LINE_AA)
            cv2.fillPoly(m, [_leaf_poly(cx, cy, Lf, wf, la + r.uniform(-0.15, 0.15))], 1.0, cv2.LINE_AA)
    return np.clip(m, 0, 1)


def _leaf_lit():
    """Direct-sun mask for leaf_shadow: two canopy layers (near = crisper, far = softer) with the canopy
    opened over the face so a sun patch lands on it. Returns (lit, face_blob)."""
    fx, fy = face_center()

    def keep(cx, cy):
        d = math.hypot(cx - fx, (cy - fy) * 1.15)
        return smoothstep(210, 430, d) ** 1.2

    near = _foliage_mask(seed=281, twigs=24, leaves_per_twig=14, size=(40, 70), keep_fn=keep)
    far = _foliage_mask(seed=282, twigs=14, leaves_per_twig=13, size=(46, 80), keep_fn=keep, scale=1.15)
    near = blur(near, 5.0)
    far = blur(far, 14.0)
    shadow = 1 - (1 - near * 0.97) * (1 - far * 0.85)
    return 1 - shadow


@effect('leaf_shadow')
def leaf_shadow(img):
    """Dappled sunlight through leaves: leaf-shaped shadows everywhere except a sun patch on the face,
    warm bright sun in the gaps, cooler flat light in the shade, a little warm scatter around the patches."""
    lit = _leaf_lit()
    shade = (0.5 + 0.14 * _face_blob())[..., None]
    out = _relight(img, lit, shade=shade, gain=1.2, shade_tint=(0.97, 0.99, 1.04), sun_tint=(1.1, 1.0, 0.82),
                   shade_lift=0.02, shade_desat=0.05, scatter=0.18, scatter_sigma=30)
    out = temperature(out, 0.08)
    out = vibrance(out, 0.12)
    return out


# ----------------------------------------------------------------------------- 139 lace_shadow

def _lace_mask(period=140, rot=-12.0, hem=430, net_strength=0.45):
    """Procedural lace-curtain shadow -> (H,W) mask (1 = thread shadow).
    Rows of six-petal roses joined by wavy vines with leaf pairs, small quatrefoils at the tile corners, picot
    dots, all on a fine tulle net; optionally a scalloped hem below which the light is unobstructed."""
    P = period
    cw, ch = int(W * 1.6), int(H * 1.5)
    m = np.zeros((ch, cw), np.float32)
    nx, ny = cw // P + 2, ch // P + 2
    for j in range(ny):
        for i in range(nx):
            ox, oy = i * P, j * P
            cx, cy = ox + P / 2, oy + P / 2
            ci = (int(cx), int(cy))
            rot0 = math.pi / 6 if (i + j) % 2 else 0.0
            # vine through the row with leaf pairs at its crests
            xs = np.arange(ox, ox + P + 1, 3, dtype=np.float32)
            ys = cy + P * 0.30 * np.sin(2 * math.pi * (xs - ox) / P)
            cv2.polylines(m, [np.stack([xs, ys], 1).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA)
            for u, sgn in ((0.25, 1), (0.75, -1)):
                lx, ly = ox + P * u, cy + sgn * P * 0.30
                for da in (-0.9, 0.9):
                    a = da + (0.0 if sgn > 0 else math.pi)
                    px, py = lx + math.cos(a) * P * 0.085, ly + math.sin(a) * P * 0.085
                    cv2.ellipse(m, (int(px), int(py)), (int(P * 0.085), int(P * 0.036)), math.degrees(a), 0, 360, 1.0, -1, cv2.LINE_AA)
            # rose: six filled petals with a lighter vein, a heart, a ring of picot dots
            for k in range(6):
                a = k * math.pi / 3 + rot0
                px, py = cx + math.cos(a) * P * 0.17, cy + math.sin(a) * P * 0.17
                cv2.ellipse(m, (int(px), int(py)), (int(P * 0.12), int(P * 0.062)), math.degrees(a), 0, 360, 1.0, -1, cv2.LINE_AA)
            for k in range(6):
                a = k * math.pi / 3 + rot0
                x1, y1 = cx + math.cos(a) * P * 0.08, cy + math.sin(a) * P * 0.08
                x2, y2 = cx + math.cos(a) * P * 0.27, cy + math.sin(a) * P * 0.27
                cv2.line(m, (int(x1), int(y1)), (int(x2), int(y2)), 0.3, 2, cv2.LINE_AA)
            cv2.circle(m, ci, int(P * 0.05), 1.0, -1, cv2.LINE_AA)
            for k in range(14):
                a = k * 2 * math.pi / 14 + rot0
                cv2.circle(m, (int(cx + math.cos(a) * P * 0.36), int(cy + math.sin(a) * P * 0.36)), 2, 1.0, -1, cv2.LINE_AA)
            # small quatrefoil at the tile corner
            for k in range(4):
                a = k * math.pi / 2 + math.pi / 4
                px, py = ox + math.cos(a) * P * 0.07, oy + math.sin(a) * P * 0.07
                cv2.ellipse(m, (int(px), int(py)), (int(P * 0.065), int(P * 0.034)), math.degrees(a), 0, 360, 1.0, -1, cv2.LINE_AA)
            cv2.circle(m, (int(ox), int(oy)), int(P * 0.025), 1.0, -1, cv2.LINE_AA)
    # fine tulle net (diamond mesh)
    yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)

    def lines(a_deg, per, th):
        a = math.radians(a_deg)
        t = (xx * math.cos(a) + yy * math.sin(a)) % per
        return 1 - smoothstep(th * 0.5, th * 0.5 + 1.2, np.abs(t - per / 2))

    net = np.maximum(lines(60, 12, 1.3), lines(-60, 12, 1.3))
    m = np.maximum(m, net * net_strength)
    # scalloped hem: lace above y_h (+ half-circle scallops), free light below
    if hem is not None:
        y_h = int(ch / 2 + hem)
        y_h -= (y_h % P) - P                      # snap to a tile boundary so the last row of roses is complete
        region = np.zeros_like(m)
        region[:y_h] = 1.0
        outline = np.zeros_like(m)
        rad = int(P * 0.25)
        for k in range(-1, cw // (P // 2) + 2):
            cxs = int(k * P / 2 + P / 4)
            cv2.circle(region, (cxs, y_h), rad, 1.0, -1, cv2.LINE_AA)
            cv2.circle(outline, (cxs, y_h), rad, 1.0, 4, cv2.LINE_AA)
        outline[:y_h - 2] = 0
        cv2.line(outline, (0, y_h), (cw, y_h), 1.0, 3, cv2.LINE_AA)
        m = np.maximum(m * region, outline)
    # rotate the big canvas onto the frame
    M = cv2.getRotationMatrix2D((cw / 2, ch / 2), rot, 1.0)
    M[0, 2] += W / 2 - cw / 2
    M[1, 2] += H / 2 - ch / 2
    return cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


@effect('lace_shadow')
def lace_shadow(img):
    """A lace-curtain shadow across the photo: delicate floral thread shadows, warm window light in the holes,
    a scalloped hem across the lower part of the frame, a little lighter on the face."""
    lace = _lace_mask(period=140, rot=-12.0, hem=430)
    lace = blur(lace, 3.5)
    depth = 1 - 0.22 * _face_blob()
    lit = 1 - np.clip(lace * depth, 0, 1)
    out = _relight(img, lit, shade=0.5, gain=1.15, shade_tint=(0.98, 0.98, 1.0), sun_tint=(1.07, 1.0, 0.88),
                   shade_lift=0.015, shade_desat=0.05, scatter=0.12, scatter_sigma=25, scatter_color='#ffe0c0')
    win = linear(35)                                          # soft window light from the upper left
    out = blend(out, (1 - win)[..., None] * color('#ffe2c0'), 'soft_light', 0.5)
    out = temperature(out, 0.06)
    return out


# ----------------------------------------------------------------------------- 140 haze

@effect('haze')
def haze(img):
    """Warm sun haze: airlight that is stronger towards the sun (top-left) and on the far background,
    lifted blacks and reduced contrast, a ghost-free sun glow and a soft bloom — dreamy summer air."""
    p = _person(3.0)
    x, y = coords()
    sun = (70.0, 40.0)
    d = np.sqrt((x - sun[0]) ** 2 + (y - sun[1]) ** 2) / math.hypot(W, H)
    amount = 0.13 + 0.22 * (1 - smoothstep(0.0, 0.95, d)) ** 1.4
    amount = amount * (0.6 + 0.4 * (1 - p))                  # less air in front of the (closer) subject
    out = lerp(img, as_layer('#ffd9a8'), amount)
    out = blend(out, (1 - smoothstep(0.0, 0.8, d))[..., None] * color('#ffe6bf'), 'screen', 0.28)
    out = fade(out, 0.05, 0.02)
    out = contrast(out, 0.9)
    out = temperature(out, 0.18)
    out = saturation(out, 0.95)
    out = lens_flare(out, pos=sun, strength=0.3, color_='#fff1c8', ghosts=False, streak=False)
    out = glow(out, sigma=50, strength=0.28, threshold=0.55)
    out = orton(out, sigma=25, strength=0.12)
    return out
