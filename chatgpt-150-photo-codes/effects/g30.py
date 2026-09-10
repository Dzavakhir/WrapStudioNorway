"""Group g30 — Ijodiy (Creative): thermal, negative, solarize, risograph, stamp."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _person(feather_=3.0):
    """Solid person mask (the stored one sits at ~0.99 with a faint ring), softly feathered."""
    p = smoothstep(0.03, 0.97, mask('person'))
    return feather(p, feather_) if feather_ else p


def _skin(feather_=6.0, grow=0):
    """Face skin minus the hijab (the stored oval overlaps the fabric at the temples)."""
    m = mask('face_skin') * (1 - smoothstep(0.2, 0.6, mask('seg_clothes', 2)))
    if grow:
        k = np.ones((abs(grow) * 2 + 1,) * 2, np.uint8)
        m = cv2.dilate(m, k) if grow > 0 else cv2.erode(m, k)
    return feather(m, feather_) if feather_ else m


def _shift(a, dx, dy):
    """Integer pixel shift of an (h,w) / (h,w,3) array, zero-filled (misregistration)."""
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    xs0, xs1 = max(0, dx), min(w, w + dx)
    ys0, ys1 = max(0, dy), min(h, h + dy)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def _draw_ss(img, fn, ss=3):
    """Anti-aliased vector drawing: fn(draw, s) draws onto an RGBA layer at `ss`x resolution
    (multiply every coordinate by s), which is then downsampled and composited over img."""
    base_pil = to_pil(img).convert('RGBA')
    w, h = base_pil.size
    layer = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer), ss)
    layer = layer.resize((w, h), Image.LANCZOS)
    return from_pil(Image.alpha_composite(base_pil, layer))


def _ramp(t, stops):
    """(h,w) scalar field in 0..1 -> (h,w,3) colours through gradient stops."""
    pos = [s[0] for s in stops]
    cols = np.array([color(s[1]) for s in stops], np.float32)
    t = np.clip(t, 0, 1)
    return np.stack([np.interp(t, pos, cols[:, c]) for c in range(3)], axis=-1).astype(np.float32)


# ----------------------------------------------------------------------------- 146 thermal

_THERMAL_STOPS = [(0.00, '#03041a'), (0.10, '#0f0c68'), (0.22, '#3a0c9e'), (0.34, '#7c0fa4'), (0.46, '#ba1a84'),
                  (0.58, '#ea323a'), (0.70, '#ff6c12'), (0.82, '#ffc51a'), (0.92, '#fff1a2'), (1.00, '#ffffff')]


@effect('thermal')
def thermal(img):
    """Synthetic heat map: cold blue/purple background, red/magenta clothing, yellow-white face,
    with luminance detail modulating the temperature so the features stay readable; plus a
    small camera UI (spot readout, colour scale)."""
    l = blur(luminance(img), 1.5)
    p = _person(3.0)
    skin = np.minimum(_skin(6.0), p)
    cloth = np.clip(p - skin, 0, 1)
    bg = np.clip(1 - p, 0, 1)

    def rmean(m):
        return float((l * m).sum() / max(m.sum(), 1.0))

    lb = blur(l, 4.0)
    t = (bg * (0.17 - 0.22 * (lb - rmean(bg)) + 0.08 * linear(90))          # sky coldest, ground a bit warmer
         + cloth * (0.50 + 0.95 * (l - rmean(cloth)))                         # fabric: warm red/magenta, folds visible
         + skin * (0.87 + 0.85 * (l - rmean(skin))))                          # skin: yellow-white, features cooler
    nose = meta()['nose']
    t -= 0.10 * radial(nose, 0.075, 0.8) * skin                               # nose tip is cooler
    t -= 0.10 * mask('mouth', 3)
    t = blur(t, 2.2)
    t += 0.03 * (noise(3011, 1.0) - 0.5)                                      # sensor noise
    out = _ramp(t, _THERMAL_STOPS)

    # --- camera UI: colour scale on the right, spot reticle + readout, label
    bx0, bx1, by0, by1 = W - 70, W - 40, 250, H - 250
    ramp = np.linspace(1, 0, by1 - by0, dtype=np.float32)[:, None].repeat(bx1 - bx0, 1)
    out[by0:by1, bx0:bx1] = _ramp(ramp, _THERMAL_STOPS)
    cx, cy = 598, 646

    def ui(d, s):
        white = (255, 255, 255, 215)
        d.rectangle((bx0 * s, by0 * s, bx1 * s, by1 * s), outline=white, width=2 * s)
        for i in range(7):                                                    # ticks
            yy = (by0 + (by1 - by0) * i / 6) * s
            d.line((bx1 * s, yy, (bx1 + 8) * s, yy), fill=white, width=2 * s)
        g, L = 7 * s, 26 * s
        for (x0, y0, x1, y1) in ((cx * s - L, cy * s, cx * s - g, cy * s), (cx * s + g, cy * s, cx * s + L, cy * s),
                                 (cx * s, cy * s - L, cx * s, cy * s - g), (cx * s, cy * s + g, cx * s, cy * s + L)):
            d.line((x0, y0, x1, y1), fill=white, width=2 * s)
        r = 15 * s
        d.ellipse((cx * s - r, cy * s - r, cx * s + r, cy * s + r), outline=white, width=2 * s)
    out = _draw_ss(out, ui)
    sh = (0, 0, 6, '#000000', 0.55)
    out = draw_text(out, '38°', (bx0 + 15, by0 - 26), font('lato-bold', 30), '#ffffff', anchor='mm', shadow=sh)
    out = draw_text(out, '20°', (bx0 + 15, by1 + 26), font('lato-bold', 30), '#ffffff', anchor='mm', shadow=sh)
    out = draw_text(out, '36.6°C', (cx + 40, cy - 30), font('lato-bold', 48), '#ffffff', anchor='ls', shadow=sh)
    out = draw_text(out, 'THERMAL', (46, 48), font('lato-bold', 28), '#ffffff', anchor='la', tracking=8, opacity=0.9, shadow=sh)
    return out


# ----------------------------------------------------------------------------- 147 negative

@effect('negative')
def negative(img):
    """Inverted colours under an orange C-41 film base, presented as a frame on a 35 mm strip:
    orange rebate, sprocket holes, edge markings and slivers of the neighbouring frames."""
    neg = 1 - img
    neg = fade(neg, 0.10, 0.06)
    neg = blend(neg, '#ff9a3c', 'multiply', 0.55)                       # orange mask
    neg = color_balance(neg, shadows=(0.12, 0.05, -0.02), midtones=(0.04, 0.01, -0.02))
    neg = contrast(neg, 0.95)
    neg = grain(neg, 0.035, 1.3, seed=3002)

    rebate = 120
    fw = W - 2 * rebate
    fh = int(round(fw * 1.25))
    gap = 22
    sl = (H - fh - 2 * gap) // 2                                        # sliver of the neighbouring frames
    y0 = sl + gap
    base_col = color('#b45c1a')
    strip = np.ones((H, W, 3), np.float32) * base_col
    strip *= (0.90 + 0.20 * fbm(4, 3003, 0.6))[..., None]              # uneven base density
    small = resize(neg, fw, fh)
    strip[y0:y0 + fh, rebate:rebate + fw] = small
    strip[:sl, rebate:rebate + fw] = small[fh - sl:]                    # previous frame (its bottom)
    strip[H - sl:, rebate:rebate + fw] = small[:sl]                     # next frame (its top)

    # sprocket holes (light-table white), one column per side
    hw, hh, pitch = 44, 64, 110
    ys = np.arange(y0 + 12, H + pitch, pitch)
    ys = np.concatenate([ys[::-1][1:][::-1], ys])  # keep simple: forward
    ys = np.arange((y0 + 12) % pitch - pitch, H + pitch, pitch)
    rects = []
    for yc in ys:
        for xc in (24 + hw / 2, W - 24 - hw / 2):
            rects.append((xc - hw / 2, yc - hh / 2, xc + hw / 2, yc + hh / 2))
    ss = 4
    m = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    for (x0, ya, x1, yb) in rects:
        d.rounded_rectangle((x0 * ss, ya * ss, x1 * ss, yb * ss), radius=9 * ss, fill=255)
    holes = np.array(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    rim = np.clip(feather(holes, 2.0) - holes, 0, 1)
    strip = lerp(strip, as_layer('#f6f0e6'), holes)
    strip = strip * (1 - 0.35 * rim)[..., None]

    # edge markings
    f = font('lato-bold', 26)
    col = '#f7d98a'
    strip = draw_text(strip, 'CN 400   ·   24', (rebate - 26, y0 + fh - 8), f, col, anchor='lm', tracking=3, opacity=0.9, rotate_=90)
    strip = draw_text(strip, '24A', (rebate - 26, y0 + 260), f, col, anchor='lm', tracking=3, opacity=0.9, rotate_=90)
    strip = draw_text(strip, '150 PHOTO CODES   ·   2026', (W - rebate + 26, y0 + 8), f, col, anchor='lm', tracking=3, opacity=0.9, rotate_=-90)
    strip = draw_text(strip, '25', (W - rebate + 26, y0 + fh - 120), f, col, anchor='lm', tracking=3, opacity=0.9, rotate_=-90)
    return vignette(strip, 0.18, 1.1, 0.8)


# ----------------------------------------------------------------------------- 148 solarize

@effect('solarize')
def solarize(img):
    """Sabattier: a tone curve that rises then reverses above the threshold (highlights partially inverted),
    bright Mackie lines along the threshold contours, cool silver split-tone for a metallic sheen."""
    l = luminance(img)
    t = 0.56
    pts = [(0.0, 0.03), (0.15, 0.17), (0.35, 0.42), (t, 0.66), (0.68, 0.40), (0.82, 0.22), (1.0, 0.16)]
    l2 = curve(as_layer(l), pts)[..., 0]
    lb = blur(l, 1.6)
    gx = cv2.Sobel(lb, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lb, cv2.CV_32F, 0, 1, ksize=3)
    g = np.sqrt(gx * gx + gy * gy)
    band = np.exp(-((lb - t) / 0.045) ** 2)
    line = band * smoothstep(0.01, 0.06, g)
    line = np.clip(line + blur(line, 1.0) * 0.5, 0, 1)
    l3 = np.clip(l2 + 0.32 * line, 0, 1)

    src = saturation(img, 0.45)
    out = blend(src, as_layer(l3), 'luminosity')
    out = split_tone(out, shadows='#1b2a3f', highlights='#dfe7ee', strength=0.4)
    out = s_curve(out, 0.12)
    out = clarity(out, 0.35, 30)
    out = grain(out, 0.03, 1.0, seed=3004)
    return vignette(out, 0.22, 1.0, 0.75)


# ----------------------------------------------------------------------------- 149 risograph

_BURG_INK = '#7a1d38'
_NAVY_INK = '#1e3a6e'


@effect('risograph')
def risograph(img):
    """Two ink plates (burgundy = warm/key, navy = cool) separated from tone & warmth, each with its own
    stochastic grain and roller streaks, multiplied over cream paper with the navy plate misregistered."""
    src = bilateral(img, 7, 0.08, 8)
    l = luminance(src)
    warm = smoothstep(-0.06, 0.28, src[..., 0] - src[..., 2])
    dark = smoothstep(0.06, 0.96, 1 - l)
    c_b = dark * (0.30 + 0.70 * warm)
    c_n = (dark ** 0.9) * (0.12 + 0.88 * (1 - warm))

    m = 44
    pw, ph = W - 2 * m, H - 2 * m

    def plate(c, seed, dx, dy):
        c = cv2.resize(c, (pw, ph), interpolation=cv2.INTER_AREA)
        c = _shift(c, dx, dy)
        n = rng(seed).random((ph // 2 + 1, pw // 2 + 1)).astype(np.float32)
        n = cv2.resize(n, (pw, ph), interpolation=cv2.INTER_LINEAR)
        gain = 0.5 + 1.2 * np.sqrt(np.clip(c * (1 - c), 0, 1))
        c = np.clip(c + 0.30 * (n - 0.5) * gain, 0, 1)
        streak = 1 + 0.10 * (fbm(3, seed + 5, 0.4, (ph, pw)) - 0.5)
        return np.clip(blur(c * streak, 0.6), 0, 1)

    burg = plate(c_b, 3005, -2, 1)
    navy = plate(c_n, 3006, 7, 5)
    ones = np.ones((ph, pw, 3), np.float32)
    ink = lerp(ones, ones * color(_BURG_INK), burg) * lerp(ones, ones * color(_NAVY_INK), navy)
    out = canvas('#F4ECDD', paper(seed=3007, strength=0.10))
    out[m:H - m, m:W - m] *= ink
    return clip(out)


# ----------------------------------------------------------------------------- 150 stamp

def _engrave(pic, period=7.0):
    """Intaglio line screen: parallel lines (bending with the tonal forms) whose width follows darkness,
    plus a cross-hatch in the darks -> ink coverage (h,w) in [0,1]."""
    h, w = pic.shape[:2]
    l = blur(luminance(pic), 0.8)
    tone = np.clip((1 - l - 0.06) * 1.12, 0, 1)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = blur(l, 9.0) * period * 1.6

    def screen(angle, half):
        a = math.radians(angle)
        u = x * math.cos(a) + y * math.sin(a) + warp
        tt = np.abs((u % period) - period / 2)
        return smoothstep(half + 0.7, half - 0.7, tt)

    ink1 = screen(22.0, tone * period / 2 * 1.05)
    tone2 = smoothstep(0.50, 0.95, tone)
    ink2 = screen(-40.0, tone2 * period / 2 * 0.9)
    return np.clip(1 - (1 - ink1) * (1 - ink2), 0, 1)


def _perforated_alpha(w, h, pitch=26.0, radius=8.6):
    nx, ny = max(1, round(w / pitch)), max(1, round(h / pitch))
    px, py = w / nx, h / ny
    y, x = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx = np.round(x / px) * px
    cy = np.round(y / py) * py
    d = np.minimum(np.minimum(np.hypot(x - cx, y), np.hypot(x - cx, y - h)),
                   np.minimum(np.hypot(x, y - cy), np.hypot(x - w, y - cy)))
    return smoothstep(radius - 0.75, radius + 0.75, d).astype(np.float32)


@effect('stamp')
def stamp(img):
    """Perforated postage stamp on a warm envelope: engraved burgundy-ink portrait, country name,
    denomination and a light circular postmark."""
    # --- tonal prep: light vignetted background, lifted fabric shadows so the folds engrave
    l = luminance(img)
    p = _person(2.0)
    lp = 0.06 + 0.94 * np.clip(l, 0, 1) ** 0.72
    lp = np.clip(lp + 0.5 * (lp - blur(lp, 18)), 0, 1)                   # local contrast for the engraver
    bg_val = 0.74 + 0.20 * radial(face_center(), 0.85, 0.9) + 0.10 * (l - blur(l, 14))
    tonal = lerp(as_layer(np.clip(bg_val, 0, 1)), as_layer(lp), p)

    sw, sh = 880, 1150
    px0, py0, px1, py1 = 72, 150, 808, 990
    pw, ph = px1 - px0, py1 - py0
    crop_h = int(round(W * ph / pw))
    cy0 = 12
    pic = cv2.resize(tonal[cy0:cy0 + crop_h], (pw, ph), interpolation=cv2.INTER_AREA)
    ink = _engrave(pic)

    paper_col = color('#F8F3EA')
    ink_col = color('#6B1F2E')
    tex = paper(seed=3008, strength=0.06)[:sh, :sw]
    st = np.ones((sh, sw, 3), np.float32) * paper_col * tex[..., None]
    picture = paper_col * lerp(np.ones((ph, pw, 3), np.float32), np.ones((ph, pw, 3), np.float32) * ink_col, ink * 0.96)
    st[py0:py1, px0:px1] = picture

    def rules(d, s):
        c = rgba('#6B1F2E', 1.0)
        d.rectangle((44 * s, 44 * s, (sw - 44) * s, (sh - 44) * s), outline=c, width=3 * s)
        d.rectangle((52 * s, 52 * s, (sw - 52) * s, (sh - 52) * s), outline=c, width=1 * s)
        d.rectangle(((px0 - 6) * s, (py0 - 6) * s, (px1 + 6) * s, (py1 + 6) * s), outline=c, width=2 * s)
    st = _draw_ss(st, rules)
    st = draw_text(st, 'O‘ZBEKISTON', (sw / 2, 100), font('lato-bold', 52), '#6B1F2E', anchor='mm', tracking=10)
    st = draw_text(st, '150', (px0, sh - 60), font('playfair-bold', 96), '#6B1F2E', anchor='ls')
    st = draw_text(st, 'POST  ·  2026', (px1, sh - 66), font('lato-bold', 34), '#6B1F2E', anchor='rs', tracking=5)

    alpha = _perforated_alpha(sw, sh)
    rgba_st = np.dstack([to_u8(st), (alpha * 255 + 0.5).astype(np.uint8)])
    pil = Image.fromarray(rgba_st, 'RGBA').rotate(-3.0, resample=Image.BICUBIC, expand=True)

    # --- envelope background + shadow + composite
    bgc = canvas('#C9B9A3', paper(seed=3009, strength=0.14))
    bgc = vignette(bgc, 0.28, 1.05, 0.8)
    out = to_pil(bgc).convert('RGBA')
    x0, y0 = int(W / 2 - pil.width / 2), int(H / 2 - pil.height / 2)
    shadow = Image.new('RGBA', out.size, (0, 0, 0, 0))
    shadow.paste(Image.new('RGBA', pil.size, (40, 20, 20, 110)), (x0 + 10, y0 + 16), pil.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    out = Image.alpha_composite(out, shadow)
    layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    layer.paste(pil, (x0, y0), pil)
    out = from_pil(Image.alpha_composite(out, layer))

    # --- light circular postmark over the bottom-right corner
    pcx, pcy, pr = 905, 1225, 112
    inkc = '#3a2f36'

    def postmark(d, s):
        c = rgba(inkc, 0.55)
        d.ellipse(((pcx - pr) * s, (pcy - pr) * s, (pcx + pr) * s, (pcy + pr) * s), outline=c, width=4 * s)
        r2 = pr - 14
        d.ellipse(((pcx - r2) * s, (pcy - r2) * s, (pcx + r2) * s, (pcy + r2) * s), outline=c, width=2 * s)
        for k in range(4):
            yy = pcy - 36 + k * 24
            pts = [((pcx + pr + 6 + i * 6) * s, (yy + 5 * math.sin(i * 0.55)) * s) for i in range(0, 60)]
            d.line(pts, fill=c, width=3 * s)
    out = _draw_ss(out, postmark)
    out = draw_text(out, 'TOSHKENT', (pcx, pcy - 46), font('lato-bold', 24), inkc, anchor='mm', tracking=4, opacity=0.6)
    out = draw_text(out, '10 · 09 · 2026', (pcx, pcy), font('lato-bold', 26), inkc, anchor='mm', tracking=2, opacity=0.6)
    out = draw_text(out, 'POCHTA', (pcx, pcy + 46), font('lato-bold', 24), inkc, anchor='mm', tracking=4, opacity=0.6)
    return out
