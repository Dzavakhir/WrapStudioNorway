"""g03 — Plyonka & Vintage (Film & Vintage)

#011 kodak_gold   #012 fuji_film   #013 polaroid   #014 film_grain   #015 vintage_90s
"""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- #011 Kodak Gold 200

@effect('kodak_gold')
def kodak_gold(img):
    src = img
    # 1. Kodak Gold tone: warm, sunny mids, gently lifted (slightly cool) shadows, yellow-capped highlights
    img = curve(img, [(0, .02), (.5, .57), (1, 1)], 'r')
    img = curve(img, [(0, .02), (.5, .54), (1, .98)], 'g')
    img = curve(img, [(0, .06), (.5, .47), (1, .9)], 'b')
    # 2. Park greens go golden-olive, yellows glow; reds stay rich but soft
    img = hsl_adjust(img, 90, width=50, sat=0.95, shift=-22)
    img = hsl_adjust(img, 55, width=25, sat=1.1, lum=0.02)
    img = hsl_adjust(img, 0, width=22, sat=1.08)
    img = vibrance(img, 0.18)
    # 3. Golden highlights, lifted shadows
    img = split_tone(img, shadows='#3a3346', highlights='#ffd27a', strength=0.35)
    img = fade(img, 0.05, 0.0)
    # 4. Warm bloom, fine grain, warm vignette
    img = glow(img, sigma=35, strength=0.18, threshold=0.65)
    # keep skin natural: pull the face 15% back towards the original colour
    img = clip(lerp(img, src, 0.15 * mask('face_skin', 6)))
    img = grain(img, 0.05, size=1.2, seed=11)
    img = vignette(img, strength=0.18, color_='#2b1a08')
    return img


# ----------------------------------------------------------------------------- #012 Fujifilm colour negative

@effect('fuji_film')
def fuji_film(img):
    # 1. Yellow-green park foliage -> pale, cool minty green (two passes so the yellows come along)
    img = hsl_adjust(img, 78, width=46, sat=0.88, lum=0.08, shift=30)
    img = hsl_adjust(img, 125, width=45, sat=0.8, lum=0.06, shift=14)
    # 2. Fuji blue lift
    img = curve(img, [(0, .05), (.5, .52), (1, .97)], 'b')
    pre = img
    # 3. Cyan highlights, muted magenta shadows
    img = split_tone(img, shadows='#3a2d48', highlights='#cfeee0', strength=0.34)
    img = color_balance(img, shadows=(0.02, -0.01, 0.03), highlights=(-0.03, 0.01, 0.02))
    # the navy hijab and red sleeve keep their own colour (only a light cast)
    img = clip(lerp(img, pre, 0.55 * mask('seg_clothes', 6)))
    # 4. Soft, slightly muted, faded, gentle grain
    img = saturation(img, 0.9)
    img = fade(img, 0.06, 0.03)
    img = skin_smooth(img, strength=0.35)
    img = grain(img, 0.05, size=1.3, seed=12)
    return img


# ----------------------------------------------------------------------------- #013 Polaroid

@effect('polaroid')
def polaroid(img):
    # --- the instant-film image: washed out, low contrast, cyan highlights / yellow shadows
    pic = fade(img, 0.15, 0.05)
    pic = gamma(pic, 1.12)
    pic = contrast(pic, 0.86)
    pic = saturation(pic, 0.76)
    pic = temperature(pic, 0.1)
    pic = color_balance(pic, shadows=(0.04, 0.035, -0.035), midtones=(0.02, 0.02, -0.01), highlights=(-0.06, 0.0, 0.05))
    pic = soft_focus(pic, sigma=2.2, mix=0.35)
    pic = glow(pic, sigma=30, strength=0.2, threshold=0.7)
    dev = 1 + 0.06 * (fbm(4, 13, 0.6) - 0.5)                 # faint uneven chemical development
    pic = clip(pic * dev[..., None])
    pic = vignette(pic, strength=0.22, radius=1.0, softness=0.8, color_='#1a1410')
    pic = grain(pic, 0.05, size=1.3, seed=13)
    # --- the print on a beige paper backdrop
    bg = canvas('#DFD2BE', paper(seed=3, strength=0.16))
    bg = vignette(bg, strength=0.2, radius=1.1, softness=0.9, color_='#5a4634')
    w, h, bd, bb, ang, cy0 = 780, 975, 46, 190, -3.0, H / 2 - 10
    out = paste(bg, pic, (w, h), center=(W / 2, cy0), rotate_=ang, border=bd, border_color='#FAF8F3',
                border_bottom=bb, shadow=(0.4, 30, (12, 22)), radius=6)
    # caption on the bottom border (rotated with the card)
    off = (h + bd + bb) / 2 - bb / 2 + 6
    a = math.radians(ang)
    cx, cy = W / 2 + off * math.sin(a), cy0 + off * math.cos(a)
    out = draw_text(out, 'yoz ’26', (cx, cy), font('cormorant-italic', 64), '#4a3a3a', anchor='mm', rotate_=ang, opacity=0.85)
    return out


# ----------------------------------------------------------------------------- #014 35mm film grain

@effect('film_grain')
def film_grain(img):
    # 35mm negative feel: slightly muted, matte, a touch soft, gently warm
    img = saturation(img, 0.86)
    img = fade(img, 0.07, 0.03)
    img = temperature(img, 0.06)
    img = split_tone(img, shadows='#33302f', highlights='#f2e6d2', strength=0.2)
    img = soft_focus(img, sigma=2.5, mix=0.3)
    # layered grain: fine + a little coarser, luminance only with a whisper of colour
    g = grain(img, 0.09, size=1.6, mono=True, seed=14)
    g = grain(g, 0.035, size=2.4, mono=True, seed=15)
    g = grain(g, 0.012, size=2.0, mono=False, seed=16)
    # a little gentler on the face so the skin stays flattering
    img = clip(lerp(g, img, 0.3 * mask('face_skin', 8)))
    img = vignette(img, strength=0.15, radius=1.0, softness=0.8)
    return img


# ----------------------------------------------------------------------------- #015 1990s point-and-shoot

@effect('vintage_90s')
def vintage_90s(img):
    # 1. Cheap colour first: warm yellowish cast, slight green (the flash curves below then compress it — no clipped skin)
    img = temperature(img, 0.3)
    img = tint(img, -0.06)
    img = saturation(img, 0.92)
    img = color_balance(img, highlights=(0.03, 0.02, -0.04))
    # 2. Flash: subject lit brightly & flat, background falling off towards the edges
    fc = face_center()
    flash = radial(center=(fc[0], fc[1] + 120), radius=1.25, softness=0.75)
    person = mask('person', feather=12)
    lit = np.clip(0.5 * flash + 0.6 * person * (0.5 + 0.5 * flash), 0, 1)
    base_c = curve(img, [(0, 0.03), (0.5, 0.55), (1, 0.955)])                                   # overall slight overexposure
    hot = curve(img, [(0, 0.04), (0.35, 0.53), (0.6, 0.79), (0.85, 0.91), (1, 0.955)])          # flash-lit: bright and flat, soft shoulder
    img = lerp(base_c, hot, lit)
    img = clip(img * (1 - 0.12 * (1 - person) * (1 - flash))[..., None])                        # flash fall-off behind her
    # 3. Plastic lens: chromatic fringe, soft focus, bloom, grain, vignette
    img = chromatic_aberration(img, amount=3)
    img = soft_focus(img, sigma=5, mix=0.28)
    img = glow(img, sigma=40, strength=0.2, threshold=0.7)
    img = grain(img, 0.06, size=1.4, seed=15)
    img = vignette(img, strength=0.24, radius=1.0, softness=0.75)
    # 4. Orange LCD date stamp
    img = draw_text(img, '’96 8 15', (W - 64, H - 58), font('lato-bold', 56), '#ff8a1e', anchor='rb', tracking=4,
                    shadow=(0, 0, 6, '#ff8a1e', 0.9))
    return img
