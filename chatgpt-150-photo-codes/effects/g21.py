"""g21 - Ramkalar (Frames): polaroid_frame, film_strip, white_border, rounded_card, magazine.

All five are graphic-design codes: the photo is composited onto a same-size canvas with
frames, typography (Playfair / Cormorant / Lato via font()) and soft shadows.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _rot(dx, dy, deg):
    """Rotate an offset (image coords, y down) counter-clockwise as seen on screen (PIL convention)."""
    a = math.radians(deg)
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


def _shape_mask(fn, scale=2):
    """Anti-aliased (H, W) float mask. fn(draw, s) draws in coordinates multiplied by s."""
    im = Image.new('L', (W * scale, H * scale), 0)
    fn(ImageDraw.Draw(im), scale)
    if scale != 1:
        im = im.resize((W, H), Image.LANCZOS)
    return np.array(im).astype(np.float32) / 255.0


def _heart_points(cx, cy, size, deg=0.0, n=120):
    """Outline points of a heart (classic parametric curve), `size` = height in px, rotated by deg."""
    pts = []
    s = size / 29.0
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        dx, dy = _rot(s * x, -s * (y - 2.0), deg)
        pts.append((cx + dx, cy + dy))
    return pts


def _soft_shadow(canvas_img, alpha_pil, xy, opacity, blur_px):
    """Composite a blurred black shadow with the given alpha (PIL 'L') at xy onto a float canvas."""
    out = to_pil(canvas_img).convert('RGBA')
    sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
    a = alpha_pil.point(lambda v: int(v * opacity))
    sh.paste(Image.new('RGBA', alpha_pil.size, (0, 0, 0, 255)), xy, a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur_px))
    return from_pil(Image.alpha_composite(out, sh))


def _fit_font(name, text, target_w, tracking=0.0, start=150):
    """Font of `name` sized so that `text` (with tracking) is `target_w` px wide."""
    f = font(name, start)
    w = text_width(text, f, tracking)
    size = max(20, int(round(start * target_w / max(w, 1))))
    return font(name, size), size


# ----------------------------------------------------------------------------- 101 polaroid frame

@effect('polaroid_frame')
def polaroid_frame(img):
    # instant-film look on the photo: warm, gently faded, a touch of grain
    photo = temperature(img, 0.14)
    photo = fade(photo, 0.05, 0.03)
    photo = s_curve(photo, 0.05)
    photo = split_tone(photo, shadows='#3d3a46', highlights='#ffe0b0', strength=0.18)
    photo = grain(photo, 0.02, seed=21)
    # slight recess (inner shadow) around the photo window
    x, y = coords()
    edge = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y)) / 10.0
    photo = photo * (0.78 + 0.22 * smoothstep(0, 1, edge))[..., None]

    # beige table: paper texture + window light from the top-left
    table = canvas(BEIGE, paper(seed=3, strength=0.16))
    table = blend(table, '#ffffff', 'soft_light', 0.4, radial(center=(280, 220), radius=1.5, softness=0.95))
    table = vignette(table, 0.22, radius=1.05, softness=0.8, color_='#5a4638')

    size, brd, bb, ang = (760, 950), 44, 200, 4.0
    card_w, card_h = size[0] + 2 * brd, size[1] + brd + bb
    ccx, ccy = W / 2 + 6, H / 2 - 14

    # contact shadow (tight) under the tilted card, then the soft main shadow via paste()
    corners = [(-card_w / 2, -card_h / 2), (card_w / 2, -card_h / 2), (card_w / 2, card_h / 2), (-card_w / 2, card_h / 2)]
    poly = [(ccx + _rot(dx, dy, ang)[0], ccy + _rot(dx, dy, ang)[1]) for dx, dy in corners]
    alpha = Image.new('L', (W, H), 0)
    ImageDraw.Draw(alpha).polygon([(px + 2, py + 5) for px, py in poly], fill=255)
    table = _soft_shadow(table, alpha, (0, 0), 0.22, 7)
    out = paste(table, photo, size, center=(ccx, ccy), rotate_=ang, border=brd, border_color='#FBF8F1',
                border_bottom=bb, shadow=(0.34, 30, (14, 26)))

    # handwritten caption on the bottom border, following the tilt: "yozgi kunlar" + outline heart
    f = font('cormorant-italic', 64)
    text = 'yozgi kunlar'
    ink = '#3a2a2a'
    tw = text_width(text, f)
    hs, gap = 34, 20
    total = tw + gap + hs * 1.1
    dy_border = (brd + size[1] + card_h / 2) / 2 - card_h / 2 - 4   # centre of the bottom border, relative to card centre
    dx0 = -total / 2
    tx, ty = _rot(dx0, dy_border, ang)
    out = draw_text(out, text, (ccx + tx, ccy + ty), f, ink, anchor='lm', rotate_=ang, opacity=0.92)
    hx, hy = _rot(dx0 + tw + gap + hs * 0.55, dy_border + 2, ang)
    pts = _heart_points(ccx + hx, ccy + hy, hs, ang)
    m = _shape_mask(lambda d, s: d.line([(px * s, py * s) for px, py in pts + pts[:2]], fill=255, width=3 * s, joint='curve'))
    out = blend(out, ink, 'normal', 0.9, m)
    return out


# ----------------------------------------------------------------------------- 102 film strip

@effect('film_strip')
def film_strip(img):
    # film base: near black with a faint gloss
    strip = canvas('#0F0F10')
    strip = blend(strip, '#ffffff', 'screen', 0.06, radial(center=(200, 200), radius=1.6, softness=1.0))

    # graded photo (slightly warm, a little punch, fine grain)
    photo = temperature(img, 0.1)
    photo = s_curve(photo, 0.08)
    photo = vibrance(photo, 0.1)
    photo = grain(photo, 0.025, seed=22)

    fx, fw = 130, 892                    # frame x / width (4:5 -> 1115 tall)
    fh = int(round(fw * H / W))
    fy = (H - fh) // 2
    gap = 34
    main = resize(photo, fw, fh)
    strip[fy:fy + fh, fx:fx + fw] = main

    # neighbouring frames (partially visible above & below): a slightly different take, a touch darker
    other = resize(zoom(photo, 1.08, center=(620, 680)), fw, fh) * 0.82
    top_h = fy - gap
    strip[0:top_h, fx:fx + fw] = other[fh - top_h:fh]
    bot_y = fy + fh + gap
    strip[bot_y:H, fx:fx + fw] = other[0:H - bot_y]

    # sprocket holes: two columns of rounded rectangles, light-table cream showing through
    hw, hh, pitch, n = 44, 60, 100, 14
    y0 = (H - ((n - 1) * pitch + hh)) / 2
    def holes(d, s):
        for k in range(n):
            cy = y0 + hh / 2 + k * pitch
            for cx in (62, W - 62):
                d.rounded_rectangle(((cx - hw / 2) * s, (cy - hh / 2) * s, (cx + hw / 2) * s, (cy + hh / 2) * s), radius=9 * s, fill=255)
    hm = _shape_mask(holes)
    strip = blend(strip, '#EDE6D6', 'normal', 1.0, hm)
    strip = blend(strip, '#ffffff', 'screen', 0.35, feather(hm, 3) * (1 - hm))   # light bleeding around the holes

    # edge print: film name / ISO on the left lane, frame numbers on the right lane (running along the strip)
    amber = '#F2A83E'
    f_edge = font('lato-bold', 24)
    f_num = font('lato-bold', 28)
    lx, rx = 107, W - 107
    for yy in (330, 1130):
        strip = draw_text(strip, 'ISO 400  ·  35 MM  ·  COLOUR', (lx, yy), f_edge, amber, anchor='mm', tracking=3, rotate_=90, opacity=0.92)
    strip = draw_text(strip, '24', (rx, 300), f_num, amber, anchor='mm', tracking=2, rotate_=90, opacity=0.92)
    strip = draw_text(strip, '24A', (rx, 1180), f_num, amber, anchor='mm', tracking=2, rotate_=90, opacity=0.92)
    strip = draw_text(strip, '23A', (rx, 70), f_num, amber, anchor='mm', tracking=2, rotate_=90, opacity=0.92)
    strip = draw_text(strip, '25', (rx, 1372), f_num, amber, anchor='mm', tracking=2, rotate_=90, opacity=0.92)

    # DX-style barcode ticks on the left lane + small frame-marker triangles on the right lane
    r = rng(22)
    def marks(d, s):
        yy = 600
        while yy < 860:
            t = int(r.integers(2, 7))
            d.rectangle((94 * s, yy * s, 120 * s, (yy + t) * s), fill=255)
            yy += t + int(r.integers(3, 8))
        for ty in (1245, 365):
            d.polygon([(rx * s, (ty - 9) * s), ((rx - 8) * s, (ty + 6) * s), ((rx + 8) * s, (ty + 6) * s)], fill=255)
    strip = blend(strip, amber, 'normal', 0.92, _shape_mask(marks))
    return strip


# ----------------------------------------------------------------------------- 103 white border

@effect('white_border')
def white_border(img):
    photo = s_curve(img, 0.08)
    photo = vibrance(photo, 0.08)
    side = 70
    pw = W - 2 * side
    ph = int(round(pw * H / W))          # keep the 4:5 aspect exactly
    px, py = side, (H - ph) // 2
    out = canvas('#FFFFFF')
    out[py:py + ph, px:px + pw] = resize(photo, pw, ph)
    g, kw = 18, 3                         # keyline gap from the photo and its width
    def keyline(d):
        d.rectangle((px - g, py - g, px + pw - 1 + g, py + ph - 1 + g), outline=rgba(BURGUNDY, 1.0), width=kw)
    return draw_shapes(out, keyline)


# ----------------------------------------------------------------------------- 104 rounded card

@effect('rounded_card')
def rounded_card(img):
    photo = s_curve(img, 0.06)
    photo = vibrance(photo, 0.08)
    bg = canvas(CREAM)
    bg = blend(bg, '#ffffff', 'soft_light', 0.45, radial(radius=1.25, softness=1.0))
    size, rad = (960, 1200), 60
    x0, y0 = (W - size[0]) // 2, (H - size[1]) // 2 - 6
    # tight contact shadow + soft ambient shadow (layered, app-style)
    alpha = Image.fromarray((rounded_mask(size[0], size[1], rad) * 255).astype(np.uint8))
    bg = _soft_shadow(bg, alpha, (x0, y0 + 6), 0.14, 10)
    return paste(bg, photo, size, center=(W / 2, H / 2 - 6), radius=rad, shadow=(0.30, 42, (0, 26)))


# ----------------------------------------------------------------------------- 105 magazine cover

@effect('magazine')
def magazine(img):
    g = s_curve(img, 0.1)
    g = temperature(g, 0.05)
    g = vibrance(g, 0.1)
    t = linear(90)                                            # 0 top -> 1 bottom
    person = mask('person', feather=1.5)
    # editorial gradients: plum-dark top (background only) so the cream masthead reads, ink bottom for cover lines
    top_w = (1 - smoothstep(0.02, 0.26, t)) * (1 - person)
    g = blend(g, INK, 'multiply', 0.62 * top_w)
    bot_w = smoothstep(0.60, 1.0, t)
    g = blend(g, INK, 'multiply', 0.55 * bot_w)

    # masthead, partly behind the head
    title = 'ÉLÉGANCE'
    f_mast, _ = _fit_font('playfair-bold', title, W - 2 * 84, tracking=12)
    with_title = draw_text(g, title, (W / 2, 172), f_mast, CREAM, anchor='ms', tracking=12, shadow=(0, 6, 16, INK, 0.45))
    out = apply_mask(with_title, g, person)

    cream, gold = CREAM, GOLD
    m = 80
    # issue line (top-left) and burgundy accent bar (top-right)
    out = draw_text(out, 'SENTABR 2026  ·  № 09', (m, 198), font('lato-bold', 24), cream, anchor='la', tracking=4)
    f_bar = font('lato-bold', 22)
    label = 'MAXSUS SON'
    bw = text_width(label, f_bar, 5) + 44
    out = draw_shapes(out, lambda d: d.rectangle((W - m - bw, 190, W - m, 232), fill=rgba(BURGUNDY, 1.0)))
    out = draw_text(out, label, (W - m - bw / 2, 211), f_bar, cream, anchor='mm', tracking=5)

    # bottom-left cover lines
    out = draw_text(out, 'YANGI MAVSUM', (m, 1032), font('lato-bold', 28), gold, anchor='ls', tracking=7)
    f_head = font('playfair-italic', 78)
    out = draw_text(out, 'Nafis kuz', (m - 4, 1118), f_head, cream, anchor='ls', shadow=(0, 4, 12, INK, 0.35))
    out = draw_text(out, 'ohanglari', (m - 4, 1204), f_head, cream, anchor='ls', shadow=(0, 4, 12, INK, 0.35))
    out = draw_shapes(out, lambda d: d.rectangle((m, 1236, m + 70, 1238), fill=rgba(gold, 1.0)))
    out = draw_text(out, '50 ta ilhom g’oyasi va uslub sirlari', (m, 1284), font('lato', 28), cream, anchor='ls', tracking=1)

    # right column above the barcode
    rxm = W - m
    out = draw_text(out, 'PORTRET', (rxm, 1006), font('lato-bold', 26), gold, anchor='rs', tracking=7)
    f_sub = font('playfair-italic', 48)
    out = draw_text(out, 'Tabiiy go’zallik', (rxm, 1064), f_sub, cream, anchor='rs', shadow=(0, 3, 10, INK, 0.35))
    out = draw_text(out, 'haqida suhbat', (rxm, 1122), f_sub, cream, anchor='rs', shadow=(0, 3, 10, INK, 0.35))

    # barcode: white box, thin bars, digits
    bx1, by1 = W - m, H - m
    bx0, by0 = bx1 - 206, by1 - 112
    r = rng(105)
    def barcode(d):
        d.rectangle((bx0, by0, bx1, by1), fill=(255, 255, 255, 255))
        x = bx0 + 14
        while x < bx1 - 16:
            wdt = int(r.integers(2, 6))
            d.rectangle((x, by0 + 12, x + wdt - 1, by1 - 34), fill=(20, 12, 14, 255))
            x += wdt + int(r.integers(2, 5))
    out = draw_shapes(out, barcode)
    out = draw_text(out, '9  771234  567021', ((bx0 + bx1) / 2, by1 - 18), font('lato', 18), INK, anchor='mm', tracking=2)
    return out
