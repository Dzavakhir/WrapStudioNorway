"""Group g19 - Badiiy (Artistic): oil_painting, watercolor, pencil_sketch, charcoal, pop_art."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _mix(a, b, t):
    """lerp for 2-D arrays (lib.lerp expands 2-D masks to 3 channels)."""
    return a * (1 - t) + b * t


def _normalize(a, lo=1.0, hi=99.0):
    p0, p1 = np.percentile(a, lo), np.percentile(a, hi)
    return np.clip((a - p0) / (p1 - p0 + 1e-6), 0, 1).astype(np.float32)


def _coarse_noise(seed, div):
    """White noise generated at 1/div resolution and upsampled (blobs ~div px wide)."""
    n = noise(seed, 0.0, (H // div + 1, W // div + 1))
    return cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)


def _flow(l, sigma_grad=1.5, sigma_tensor=6.0):
    """Edge-tangent flow field from the structure tensor of a luminance image -> (tx, ty) unit vectors."""
    g = blur(l, sigma_grad)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    jxx = blur(gx * gx, sigma_tensor); jyy = blur(gy * gy, sigma_tensor); jxy = blur(gx * gy, sigma_tensor)
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy)          # gradient orientation
    tx = (-np.sin(theta)).astype(np.float32)               # tangent = perpendicular to the gradient
    ty = (np.cos(theta)).astype(np.float32)
    return tx, ty


def _lic(img, tx, ty, length=12, step=1.0, falloff=0.0):
    """Line-integral-convolution style smoothing along a flow field (straight-line kernel)."""
    x, y = coords()
    acc = np.zeros_like(img); wsum = 0.0
    for k in range(-length, length + 1):
        w = 1.0 - falloff * abs(k) / (length + 1e-6)
        mx = (x + tx * (k * step)).astype(np.float32); my = (y + ty * (k * step)).astype(np.float32)
        acc += w * cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        wsum += w
    return acc / wsum


def _hatch(angle, seed, length=34, density=0.97, jitter=4.0, crisp=(0.12, 0.6)):
    """Directional pencil strokes -> (H,W) in [0,1] (1 = stroke)."""
    r = rng(seed)
    out = np.zeros((H, W), np.float32)
    for i, da in enumerate((-jitter, 0.0, jitter)):
        n = noise(seed * 7 + i)
        pts = (n > density).astype(np.float32)
        s = motion_blur(pts, length, angle + da + float(r.uniform(-1.5, 1.5)))
        out = np.maximum(out, s)
    out = _normalize(blur(out, 0.5), 0, 99.7)
    return smoothstep(crisp[0], crisp[1], out)


def _warp(img, dx, dy):
    x, y = coords()
    return cv2.remap(img, (x + dx).astype(np.float32), (y + dy).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def _canvas_weave(period=6.0, strength=0.14, seed=3):
    """Linen canvas weave multiplier (H,W) centred on 1.0."""
    a = stripes(0.0, period, 0.5, softness=1.8)
    b = stripes(90.0, period, 0.5, softness=1.8)
    weave = (a * 0.5 + b * 0.5)
    weave = weave * (0.8 + 0.4 * fbm(5, seed, 2.0))          # irregular thread thickness
    fine = noise(seed + 2, 0.7)
    tex = (weave - weave.mean()) * 2.0 + (fine - 0.5) * 0.5
    return (1 + strength * tex).astype(np.float32)


def _rough_rect(margin=46, rough=(30, 16), seed=24):
    """Ragged rectangular wash area -> (H,W) mask (1 = painted)."""
    x, y = coords()
    d = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y))
    r = (fbm(3, seed, 0.7) - 0.5) * 2 * rough[0] + (fbm(5, seed + 1, 2.5) - 0.5) * 2 * rough[1]
    return smoothstep(margin - 6, margin + 6, d + r).astype(np.float32)


def _splashes(area, count=26, seed=25, margin=46):
    """A few soft paint splashes just outside the wash boundary -> (H,W) alpha."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    x, y = coords()
    d = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y))
    n = 0; tries = 0
    while n < count and tries < count * 40:
        tries += 1
        px, py = int(r.uniform(0, W)), int(r.uniform(0, H))
        if area[py, px] > 0.3 or d[py, px] > margin * 1.6:
            continue
        rad = float(r.uniform(2.5, 11.0))
        cv2.circle(m, (px, py), int(rad), float(r.uniform(0.45, 0.9)), -1, cv2.LINE_AA)
        n += 1
    return blur(m, 1.0)


# ----------------------------------------------------------------------------- 091 oil painting

@effect('oil_painting')
def oil_painting(img):
    face = mask('face', feather=12)
    features = np.clip(mask('eyes', feather=6, grow=10) + mask('lips', feather=6, grow=6) + mask('brows', feather=6, grow=6), 0, 1)

    # 1. rich colour first (paint is mixed richer than a photo)
    rich = saturation(img, 1.3)
    rich = s_curve(rich, 0.16)
    rich = levels(rich, 0.03, 1.0)
    rich = split_tone(rich, shadows='#4a2a20', highlights='#ffe0b0', strength=0.25)

    # 2. blotchy oil base: broad knife work on the background, finer on the face
    face_base = lerp(cv_oil(rich, 7, 1), bilateral(rich, 9, 0.12, 10), 0.5)          # blended skin passages
    oil = lerp(cv_oil(rich, 15, 1), face_base, face)

    # 3. brush strokes: smear the paint along the edge-tangent flow
    tx, ty = _flow(luminance(rich), 1.5, 5.0)
    strokes = _lic(oil, tx, ty, length=18, step=1.3, falloff=0.3)
    strokes = lerp(strokes, _lic(oil, tx, ty, length=6, step=1.0), face * 0.85)     # shorter strokes on the face

    # bristle textures (fine hairs + broader ridges) dragged along the same flow
    b_fine = _lic(noise(19), tx, ty, length=16, step=1.2)
    b_fine = b_fine - blur(b_fine, 3.0); b_fine = b_fine / (b_fine.std() + 1e-6)
    b_med = _lic(_coarse_noise(20, 3), tx, ty, length=16, step=1.5)
    b_med = b_med - blur(b_med, 8.0); b_med = b_med / (b_med.std() + 1e-6)
    strokes = clip(strokes * (1 + (0.02 * b_fine + 0.035 * b_med) * (1 - 0.6 * face))[..., None])   # per-stroke tonal variation

    # 4. bring back crisp detail in eyes / lips / brows (painters paint these finely)
    detail = bilateral(rich, 9, 0.08, 8)
    strokes = lerp(strokes, detail, features * 0.5)

    # 5. impasto relief: light from top-left catches the ridges of the stroke texture
    def _relief(t):
        r = cv2.Sobel(t, cv2.CV_32F, 1, 0, ksize=3) + cv2.Sobel(t, cv2.CV_32F, 0, 1, ksize=3)
        return r / (r.std() + 1e-6)
    thick = 0.35 + 0.65 * smoothstep(0.25, 0.85, luminance(strokes))                 # thicker paint in the lights
    relief = (0.025 * _relief(b_fine) + 0.06 * _relief(b_med)) * thick * (1 - 0.65 * face)
    out = clip(strokes + relief[..., None])

    # 6. canvas weave under the paint (shows in the thinner passages), then a warm varnish vignette
    weave = _canvas_weave(6.0, 0.16)
    out = clip(out * (1 + (weave - 1) * (1 - 0.5 * thick))[..., None])
    out = blend(out, '#3a2418', 'multiply', 0.28, 1 - radial(None, 1.05, 0.7))
    return out


# ----------------------------------------------------------------------------- 092 watercolour

@effect('watercolor')
def watercolor(img):
    paper_col = color('#faf6ee')
    ptex = paper(2, 0.30)
    face = mask('face', feather=20)
    skin = mask('face_skin', feather=6, grow=-6)
    features = np.clip(mask('eyes', feather=4, grow=6) + mask('lips', feather=4, grow=3) + mask('brows', feather=4, grow=4), 0, 1)
    skin_flat = np.clip(skin - features, 0, 1)

    # 1. simplified, lively washes
    sty = cv_stylization(img, 80, 0.5)
    sty = lerp(sty, bilateral(img, 9, 0.12, 10), 0.25)
    sty = saturation(sty, 1.25)
    sty = hsl_adjust(sty, 240, 40, sat=1.15, lum=0.06)               # navy -> soft indigo/ultramarine wash
    sty = hsl_adjust(sty, 100, 45, sat=1.15, lum=0.04)               # sap-green foliage

    # 2. colour bleed: washes drift out of the pencil lines (much less on the face)
    amp = (1 - 0.8 * face)
    dx = (fbm(4, 21, 1.4) - 0.5) * 26 * amp
    dy = (fbm(4, 22, 1.4) - 0.5) * 26 * amp
    wash = blur(_warp(sty, dx, dy), 1.6)
    wash = lerp(wash, blur(wash, 10), 0.4 * (1 - 0.6 * face))       # wet-in-wet softness
    wash = lerp(wash, blur(posterize(wash, 7), 2.5), 0.4 * (1 - 0.3 * face))   # layered washes

    # 3. translucent pigment: paper shows through, highlights are bare paper
    pig = levels(wash, 0.0, 0.93)
    density = 0.76 + 0.12 * (1 - luminance(pig))[..., None]
    out = paper_col * (1 - (1 - pig) * density)

    # 4. wet-edge darkening where pigment pools at the borders of a wash
    lw = blur(luminance(wash), 1.2)
    e = np.sqrt(cv2.Sobel(lw, cv2.CV_32F, 1, 0) ** 2 + cv2.Sobel(lw, cv2.CV_32F, 0, 1) ** 2)
    e = blur(_normalize(e, 0, 98.5), 1.5)
    out = blend(out, pig * 0.9, 'multiply', 0.55 * e)
    out = blend(out, pig, 'multiply', 0.30 * blur(e, 5.0))

    # 5. granulation + paper
    gran = (fbm(6, 23, 3.0) - 0.5) * 0.40 * (1 - luminance(out))
    out = clip(out * (1 - gran)[..., None])
    out = clip(out * ptex[..., None])

    # 6. light pencil outlines (soft grey, drawn before painting; almost none across the skin)
    smooth = blur(bilateral(img, 9, 0.1, 8), 1.6)
    lines = xdog(smooth, sigma=2.0, k=1.6, p=14.0, eps=0.02, phi=5.0)
    bg = 1 - mask('person', feather=6)
    pencil_strength = 0.52 - 0.38 * skin_flat - 0.12 * bg
    out = clip(out * (1 - (1 - lines) * pencil_strength)[..., None])

    # 7. ragged rectangular wash on white paper, pooled pigment along its boundary, a few splashes
    area = _rough_rect(46, (30, 16), 24)
    rim = np.clip(blur(area, 1.5) - blur(area, 6.0), 0, 1)
    out = blend(out, pig * 0.85, 'multiply', 0.7 * rim)
    bare = paper_col * ptex[..., None]
    out = lerp(bare, out, area)
    spl = _splashes(area, 26, 25, 46)
    out = lerp(out, paper_col * (1 - (1 - blur(wash, 25)) * 0.75), spl)
    out = curve(out, [(0, 0.10), (0.5, 0.55), (1, 1.0)])
    return clip(out)


# ----------------------------------------------------------------------------- 093 pencil sketch

@effect('pencil_sketch')
def pencil_sketch(img):
    paper_col = color('#f5f0e6')
    skin = mask('face_skin', feather=8)
    features = np.clip(mask('eyes', feather=4, grow=4) + mask('brows', feather=4, grow=3) + mask('lips', feather=4, grow=3), 0, 1)
    smooth = bilateral(img, 9, 0.1, 8)

    # tonal map: how much graphite goes down (kept light and delicate)
    tone_ = levels(luminance(smooth), 0.04, 0.96, 1.2)
    dark = clip(1 - tone_) ** 1.7

    # OpenCV pencil: soft smudged shading (nice on the skin)
    g, _ = cv_pencil(img, 70, 0.08, 0.06)
    cvd = clip(1 - g[..., 0])

    # hatching: distinct strokes in one direction, cross-hatch only in the darker passages
    h1 = _hatch(38.0, 31, length=40, density=0.975, crisp=(0.1, 0.55))
    h2 = _hatch(-52.0, 32, length=34, density=0.978, crisp=(0.1, 0.55))
    d_shade = dark * (0.30 + 1.1 * h1)
    d_cross = smoothstep(0.45, 0.9, dark) * (0.2 + 1.0 * h2) * 0.7
    hatched = 1 - (1 - np.clip(d_shade, 0, 1)) * (1 - np.clip(d_cross, 0, 1))
    blended = dark * 0.75 * (0.85 + 0.3 * h1)                                # smooth, lightly stroked skin
    shade = _mix(hatched, blended, skin * 0.9)
    shade = np.maximum(shade, cvd * 0.5)

    # fine lines
    lines = xdog(smooth, sigma=1.0, k=1.6, p=18.0, eps=0.015, phi=12.0)
    d_line = (1 - lines) * 0.9
    d_line = np.maximum(d_line, (1 - xdog(img, sigma=0.7, k=1.6, p=22.0, eps=0.02, phi=14.0)) * 0.6 * features)

    deposit = 1 - (1 - np.clip(shade, 0, 1)) * (1 - np.clip(d_line, 0, 1))
    deposit = np.minimum(deposit, 0.88)
    deposit = deposit * (0.70 + 0.30 * radial(None, 1.15, 0.55))              # drawing fades out towards the edges
    deposit = deposit * (1 + 0.12 * (noise(33, 0.8) - 0.5))                  # graphite grain

    graphite = np.array([0.18, 0.18, 0.20], np.float32)
    out = paper_col * (1 - deposit[..., None]) + graphite * deposit[..., None]
    out = clip(out * paper(5, 0.15)[..., None])
    return out


# ----------------------------------------------------------------------------- 094 charcoal

@effect('charcoal')
def charcoal(img):
    paper_col = color('#e4ded3')
    skin = mask('face_skin', feather=10)
    face = mask('face', feather=14)
    person = mask('person', feather=10)

    # tonal base: bold and dark
    l = luminance(bilateral(img, 9, 0.1, 8))
    l = s_curve(np.repeat(l[..., None], 3, 2), 0.30)[..., 0]
    l = levels(l, 0.04, 0.96, 0.85)
    dark = np.clip((1 - l) * 1.15 - 0.03, 0, 1)
    dark = np.clip((dark - 0.06) / 0.94, 0, 1)                              # lights stay clean paper
    dark = _mix(dark, dark ** 1.6, skin * 0.9)                               # keep the skin luminous

    # marks: broad diagonal side-of-stick strokes on the background, form-following strokes on the figure
    tx, ty = _flow(luminance(img), 2.0, 8.0)
    streak = _lic(_coarse_noise(41, 3), tx, ty, length=14, step=1.5)
    streak = smoothstep(0.3, 0.8, _normalize(streak - blur(streak, 8.0), 1, 99))
    diag = motion_blur(_coarse_noise(42, 5), 70, -35.0)
    diag = smoothstep(0.3, 0.75, _normalize(diag - blur(diag, 12.0), 1, 99))
    marks_bg = 0.5 + 0.7 * diag + 0.15 * streak
    marks_person = 0.6 + 0.55 * streak + 0.15 * diag
    marks_face = 0.8 + 0.3 * streak
    marks = _mix(_mix(marks_bg, marks_person, person), marks_face, face)
    stroked = np.clip(dark * marks, 0, 1)

    # smudged (finger-blended) darks
    smudge = blur(dark, 7.0)
    stroked = np.maximum(stroked, smudge * 0.85 * smoothstep(0.3, 0.9, smudge) * (1 - 0.3 * face))

    # paper tooth: bright specks of paper show through the dark passages
    tooth = smoothstep(0.55, 0.95, _coarse_noise(43, 2)) * (1 - 0.5 * face)   # cleaner skin
    stroked = stroked * (1 - 0.35 * tooth * smoothstep(0.3, 0.9, stroked))

    # bold lines (hand-drawn: jittered edges)
    jit = _warp(img, (noise(44, 2.0) - 0.5) * 3.0, (noise(45, 2.0) - 0.5) * 3.0)
    lines = xdog(jit, sigma=1.5, k=1.6, p=16.0, eps=0.02, phi=20.0)
    lines_soft = xdog(jit, sigma=2.4, k=1.6, p=12.0, eps=0.03, phi=8.0)
    d_line = np.clip((1 - lines) * 0.95 + (1 - lines_soft) * 0.5 * (1 - 0.5 * skin), 0, 1)
    d_line = d_line * (1 - 0.45 * skin)                                     # lighter lines across the skin

    deposit = np.clip(1 - (1 - stroked) * (1 - d_line), 0, 1)
    # rough, unfinished drawing edge
    edge = radial(None, 1.2, 0.4) + (fbm(5, 46, 1.6) - 0.5) * 0.35 + (diag - 0.5) * 0.3
    deposit = deposit * smoothstep(0.15, 0.7, edge)

    black = np.array([0.07, 0.065, 0.06], np.float32)
    out = paper_col * (1 - deposit[..., None]) + black * deposit[..., None]
    out = clip(out * paper(9, 0.25)[..., None])
    out = grain(out, 0.07, 2.0, seed=47)
    # a touch of white chalk on the brightest skin
    chalk = smoothstep(0.78, 0.95, l) * skin
    out = blend(out, '#f7f3ea', 'screen', 0.35, chalk)
    return clip(out)


# ----------------------------------------------------------------------------- 095 pop art

def _pop_panel(ink_lum, regions, pal):
    """One Warhol-style silkscreen panel: flat colour blocks per region + 4-level posterized ink."""
    ink_col = as_layer(pal['ink'])
    flat = as_layer(pal['bg']); shade = lerp(flat, ink_col, 0.45); hi = lerp(flat, as_layer('#ffffff'), 0.35)
    for key, m in regions.items():
        c = as_layer(pal[key])
        flat = lerp(flat, c, m)
        s = as_layer(pal['skin_shade']) if key == 'skin' else lerp(c, ink_col, 0.45)
        shade = lerp(shade, s, m)
        hi = lerp(hi, lerp(c, as_layer('#ffffff'), 0.2 if key == 'skin' else 0.3), m)
    out = lerp(flat, hi, smoothstep(0.82, 0.9, ink_lum))
    out = lerp(out, shade, smoothstep(0.52, 0.45, ink_lum) * 0.9)
    out = lerp(out, ink_col, smoothstep(0.30, 0.24, ink_lum))
    return out


@effect('pop_art')
def pop_art(img):
    # region masks (hard-edged silkscreen blocks, 1 px anti-aliased)
    person = mask('person', feather=1.0)
    clothes = mask('seg_clothes', feather=1.0)
    hsv = rgb2hsv(img)
    redness = smoothstep(25.0, 12.0, np.abs(((hsv[..., 0] + 180.0) % 360.0) - 180.0)) * smoothstep(0.25, 0.5, hsv[..., 1])
    sleeve = np.clip(clothes * smoothstep(0.35, 0.6, blur(redness, 3.0)), 0, 1)
    sleeve = smoothstep(0.3, 0.7, blur(sleeve, 2.0))
    lips = mask('lips', feather=1.0)
    teeth = mask('mouth', feather=0.8)
    skin = np.clip(mask('face', feather=1.0) - lips - teeth, 0, 1)
    hijab = np.clip(person - sleeve - skin - lips - teeth, 0, 1)
    bg = 1 - person
    regions = dict(hijab=hijab, sleeve=sleeve, skin=skin, lips=lips, teeth=teeth)

    # ink layer: each block gets its own tonal stretch so the flat colour survives and only real shadows go to ink
    l = luminance(bilateral(img, 9, 0.08, 6))
    l = blur(l, 0.8)
    ink_lum = (bg * levels(l, 0.10, 0.72) + hijab * levels(l, 0.03, 0.30) + sleeve * levels(l, 0.05, 0.30)
               + skin * levels(l, 0.15, 0.80) + lips * levels(l, 0.10, 0.65) + teeth * 1.0)
    ink_lum = translate(np.repeat(ink_lum[..., None], 3, 2), 5, 4)[..., 0]     # misregistered like a real screen print

    pals = [
        dict(bg='#FFE200', hijab='#FF2E7A', sleeve='#00C2FF', skin='#FFD9B3', skin_shade='#F0A070', lips='#E0004A', teeth='#FFF8F0', ink='#1A0A2A'),
        dict(bg='#00C2FF', hijab='#FF7A00', sleeve='#FFE200', skin='#FFE6C8', skin_shade='#F5B08A', lips='#FF2E7A', teeth='#FFF8F0', ink='#0A1A3A'),
        dict(bg='#FF3B3B', hijab='#2A0A5A', sleeve='#FFE200', skin='#FFDDC0', skin_shade='#E8A890', lips='#FF2E7A', teeth='#FFF8F0', ink='#2A0A0A'),
        dict(bg='#00E07A', hijab='#6B1F2E', sleeve='#FF7A00', skin='#FFD0C8', skin_shade='#E89AA0', lips='#FF2E7A', teeth='#FFF8F0', ink='#0A2A2A'),
    ]
    g = 10
    pw, ph = (W - 3 * g) // 2, (H - 3 * g) // 2
    out = np.zeros((H, W, 3), np.float32) + 0.04
    for i, pal in enumerate(pals):
        panel = _pop_panel(ink_lum, regions, pal)
        small = cv2.resize(panel, (pw, ph), interpolation=cv2.INTER_AREA)
        x0 = g + (i % 2) * (pw + g); y0 = g + (i // 2) * (ph + g)
        out[y0:y0 + ph, x0:x0 + pw] = small
    return out
