"""Group g14 — Estetika (Aesthetic Trends): old_money, coquette, grunge, matte, indie."""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- private helpers

def _skin_mask(feather_=6.0):
    """Face + body skin, softly feathered (H,W)."""
    return np.clip(mask('face_skin', feather_) + mask('seg_body_skin', feather_), 0, 1)


def _scatter(count, seed, allowed, margin=40, min_dist=90):
    """Deterministic scatter of points where `allowed` (H,W) > 0.85, keeping them apart (rejection sampling)."""
    r = rng(seed)
    pts = []
    tries = 0
    while len(pts) < count and tries < count * 500:
        tries += 1
        px, py = r.uniform(margin, W - margin), r.uniform(margin, H - margin)
        if allowed[int(py), int(px)] < 0.85:
            continue
        if any((px - qx) ** 2 + (py - qy) ** 2 < min_dist ** 2 for qx, qy in pts):
            continue
        pts.append((px, py))
    return pts


def _sparkles(points, sizes, color_='#fff2f7', seed=0):
    """Prettier sparkles than plain crosses: tapered 4-ray stars, a 45-degree secondary star on the big ones,
    and a soft halo -> (H,W,3) layer to screen-blend."""
    r = rng(seed)
    layer = np.zeros((H, W), np.float32)
    for (px, py), s in zip(points, sizes):
        rot = r.uniform(-8, 8)
        # tiny ones are soft glitter dots (core-dominant), larger ones tapered stars
        st = star(px, py, s, thickness=0.42 if s < 16 else 0.16, rays=4, rotation=rot)
        if s >= 30:
            st = np.maximum(st, star(px, py, s * 0.45, thickness=0.14, rays=4, rotation=rot + 45) * 0.85)
        layer = np.maximum(layer, st)
    halo = blur(layer, 4) * 0.9 + blur(layer, 16) * 0.6
    layer = np.clip(layer + halo, 0, 1)
    return layer[..., None] * color(color_)


# ----------------------------------------------------------------------------- 066 old_money

@effect('old_money')
def old_money(img):
    """Quiet luxury: muted olive/brown tones, warm cream highlights, deep shadows, light grain."""
    natural = img.copy()
    # muted, elegant colour: greens -> olive/khaki, sky -> muted steel, reds -> quiet wine
    img = hsl_adjust(img, 105, width=50, sat=0.5, shift=-18, lum=-0.03)
    img = hsl_adjust(img, 200, width=40, sat=0.45, lum=-0.04)
    img = hsl_adjust(img, 0, width=25, sat=0.5, lum=-0.08)
    img = saturation(img, 0.74)
    img = temperature(img, 0.14)
    # tone: deep, rich shadows and a gentle roll-off in the highlights
    img = curve(img, [(0, 0), (0.06, 0.02), (0.22, 0.16), (0.5, 0.5), (0.8, 0.83), (1, 0.975)])
    img = s_curve(img, 0.10)
    # colour: warm near-black shadows, cream highlights
    img = split_tone(img, shadows='#1f1a18', highlights='#f2e6d2', strength=0.48)
    img = color_balance(img, shadows=(0.012, 0.0, -0.02), midtones=(0.02, 0.008, -0.015), highlights=(0.035, 0.02, -0.03))
    # skin: warm cream, softly lifted, never grey or muddy
    skin = _skin_mask(8)
    warm_skin = clip(natural * np.array([1.05, 0.99, 0.93], np.float32))
    warm_skin = split_tone(warm_skin, shadows='#3a2a22', highlights='#f6e9d4', strength=0.35)
    warm_skin = curve(warm_skin, [(0, 0), (0.5, 0.55), (1, 0.98)])
    img = apply_mask(img, lerp(img, warm_skin, 0.42), skin)
    # light: soft warm window-light from the upper left + a whisper of luxurious bloom
    img = blend(img, radial(center=(W * 0.2, H * 0.1), radius=0.9, softness=0.9) * 0.6, 'soft_light', 0.35)
    img = glow(img, sigma=45, strength=0.16, threshold=0.6)
    # finish: light film grain, classic vignette
    img = grain(img, amount=0.05, size=1.15, seed=14)
    img = vignette(img, strength=0.34, radius=1.0, softness=0.75, color_='#0d0a08')
    return img


# ----------------------------------------------------------------------------- 067 coquette

@effect('coquette')
def coquette(img):
    """Soft pink wash, dreamy glow, pastel background and delicate sparkles."""
    natural = img.copy()
    lum = luminance(img)
    # pastel base: mute the greens so pink can lead, lift the whole image a touch
    img = hsl_adjust(img, 100, width=50, sat=0.5, shift=8, lum=0.06)
    img = hsl_adjust(img, 210, width=40, sat=0.5, lum=0.05)
    img = saturation(img, 0.9)
    img = brightness(img, 0.03)
    img = fade(img, 0.04, 0.0)
    # soft pink wash, weighted to mids/highlights so the navy stays deep (plum-navy, not grey)
    wash_w = 0.25 + 0.75 * smoothstep(0.06, 0.42, lum)
    img = blend(img, '#ffc0d0', 'soft_light', 0.62, wash_w)
    img = split_tone(img, shadows='#5a3a52', highlights='#ffd9e4', strength=0.35)
    img = color_balance(img, midtones=(0.03, -0.01, 0.015), highlights=(0.025, 0.0, 0.03))
    img = s_curve(img, 0.09)
    # keep skin peachy-rosy rather than magenta, with a little life in it (highlights rolled off, no red clipping)
    skin = _skin_mask(8)
    rosy = clip(natural * np.array([1.04, 0.98, 0.99], np.float32))
    rosy = brightness(rosy, 0.03)
    rosy = curve(rosy, [(0, 0), (0.5, 0.5), (0.85, 0.83), (1, 0.95)])
    rosy = split_tone(rosy, shadows='#7a4a58', highlights='#ffe4e8', strength=0.3)
    img = apply_mask(img, lerp(img, rosy, 0.45), skin)
    # gentle glow: bloom + a touch of soft focus in the background only
    img = glow(img, sigma=38, strength=0.38, threshold=0.5)
    person = mask('person', 3)
    img = apply_mask(soft_focus(img, 9, 0.55), img, person)
    # soft pink bokeh drifting through the background
    bg = mask('background', 2)
    bokeh = bokeh_layer(count=14, seed=141, radius=(22, 60), colors=['#ffc4d8', '#ffd9e6', '#fff0f4'],
                        area=bg, softness=0.45, alpha=(0.12, 0.3))
    img = blend(img, bokeh, 'screen', 0.6)
    # delicate sparkles: glitter-small, a few medium, three heroes; background + the lower drape of the scarf
    x, y = coords()
    allowed = np.clip(bg + mask('person') * (y > 1040) * (x > 560) * (1 - mask('face', 0, grow=80)), 0, 1)
    pts = _scatter(24, seed=1407, allowed=allowed, margin=50, min_dist=105)
    r = rng(1408)
    sizes = [float(r.uniform(9, 15)) for _ in pts]
    for i in range(3, min(11, len(pts))):
        sizes[i] = float(r.uniform(20, 30))
    for i in range(min(3, len(pts))):
        sizes[i] = float(r.uniform(42, 56))
    img = blend(img, _sparkles(pts, sizes, color_='#fff2f7', seed=1409), 'screen', 0.9)
    # airy pink haze at the edges instead of a dark vignette
    img = vignette(img, strength=0.2, radius=1.0, softness=0.8, color_='#ffd6e2')
    return img


# ----------------------------------------------------------------------------- 068 grunge

@effect('grunge')
def grunge(img):
    """Gritty dark tones, heavy contrast, rough grain, scratches and dirt — face kept readable."""
    natural = img.copy()
    skin = _skin_mask(8)
    face_soft = mask('face', 25, grow=30)
    mouth = mask('mouth', 3, grow=3)
    # colour: drained, with a cool green-yellow cast in the surroundings
    img = saturation(img, 0.5)
    img = tint(img, -0.08)
    img = split_tone(img, shadows='#1a221c', highlights='#d4cfa6', strength=0.36)
    # heavy contrast: blacks crushed close to black, mids kept, highlights rolled off
    img = s_curve(img, 0.22)
    img = curve(img, [(0, 0), (0.08, 0.035), (0.25, 0.21), (0.5, 0.5), (0.85, 0.85), (1, 0.93)])
    img = clarity(img, 0.28, radius=40)
    # skin: natural complexion kept underneath — desaturated and contrasty, never chalky or green
    skin_v = saturation(natural, 0.7)
    skin_v = s_curve(skin_v, 0.16)
    skin_v = curve(skin_v, [(0, 0), (0.5, 0.49), (0.85, 0.82), (1, 0.92)])
    skin_v = split_tone(skin_v, shadows='#26241f', highlights='#e8dcc2', strength=0.25)
    img = apply_mask(img, lerp(img, skin_v, 0.65), skin)
    img = apply_mask(img, lerp(img, saturation(natural, 0.7), 0.5), mouth)   # keep the smile clean
    # dirty texture: concrete-like grime in overlay (lighter on the face) + clumpy dirt multiplied
    tex = fbm(6, seed=681, scale=2.2)
    fine = noise(seed=682, sigma=0.8)
    concrete = np.clip(0.5 + (tex - 0.5) * 0.9 + (fine - 0.5) * 0.35, 0, 1)
    img = blend(img, concrete, 'overlay', 0.45, 1 - 0.65 * face_soft)
    dirt = smoothstep(0.5, 0.85, fbm(5, seed=683, scale=3.0))
    img = clip(img * (1 - 0.28 * dirt * (1 - 0.7 * face_soft))[..., None])
    # rough grain (a little gentler on the face)
    img = apply_mask(grain(img, amount=0.12, size=1.5, seed=68), grain(img, amount=0.07, size=1.5, seed=68), skin)
    # dark specks, light dust/scuffs on the dark fabric, scratches (kept mostly off the face)
    specks_dark = dust(count=300, seed=684, size=(1, 3)) * (1 - 0.6 * face_soft)
    img = clip(img * (1 - 0.6 * specks_dark)[..., None])
    specks_light = dust(count=700, seed=685, size=(1, 2)) * (1 - 0.7 * face_soft)
    img = blend(img, specks_light * 0.55, 'screen', 0.5)
    scr = scratches(count=26, seed=686, length=(90, 700), thickness=(1, 2), vertical=True, blur_=0.8)
    scr2 = scratches(count=10, seed=687, length=(60, 260), thickness=(1, 3), vertical=False, blur_=1.1)
    scr = np.clip(scr + scr2 * 0.8, 0, 1) * (1 - 0.8 * face_soft)
    img = blend(img, scr * 0.8, 'screen', 0.42)
    # distressed dark edges + vignette, kept off the centre so the fabric folds survive
    edge_noise = fbm(4, seed=688, scale=1.2)
    burn = (1 - radial(radius=1.15, softness=0.65)) * (0.7 + 0.6 * edge_noise)
    img = clip(img * (1 - 0.45 * np.clip(burn, 0, 1))[..., None])
    return img


# ----------------------------------------------------------------------------- 069 matte

@effect('matte')
def matte(img):
    """Matte editorial: faded blacks, low contrast, slightly cool tones."""
    natural = img.copy()
    # low-contrast, matte tone curve: lifted blacks, airy mids, softened whites
    img = fade(img, 0.17, 0.06)
    img = contrast(img, 0.86, pivot=0.5)
    img = curve(img, [(0, 0.16), (0.3, 0.38), (0.6, 0.67), (1, 0.94)])
    # slightly cool, quiet colour
    img = temperature(img, -0.1)
    img = saturation(img, 0.82)
    img = split_tone(img, shadows='#4a5566', highlights='#e9eef2', strength=0.3)
    img = color_balance(img, shadows=(-0.01, 0.0, 0.03), midtones=(-0.01, 0.0, 0.015))
    # skin stays soft but alive (slightly less desaturated and less cool than the rest)
    skin = _skin_mask(8)
    skin_v = fade(natural, 0.14, 0.05)
    skin_v = contrast(skin_v, 0.9)
    skin_v = curve(skin_v, [(0, 0), (0.5, 0.55), (1, 0.97)])
    skin_v = temperature(skin_v, -0.04)
    skin_v = saturation(skin_v, 0.95)
    img = apply_mask(img, lerp(img, skin_v, 0.55), skin)
    # editorial softness: a hint of soft focus and the faintest grain so the flat areas don't band
    img = soft_focus(img, 4, 0.2)
    img = grain(img, amount=0.018, size=1.0, seed=69)
    return img


# ----------------------------------------------------------------------------- 070 indie

@effect('indie')
def indie(img):
    """Indie film: green-yellow highlights, faded colours, film grain, cool shadows."""
    natural = img.copy()
    # faded, filmic base
    img = fade(img, 0.09, 0.05)
    img = saturation(img, 0.82)
    img = s_curve(img, 0.08)
    # green-yellow highlights / cool teal shadows
    img = split_tone(img, shadows='#23303a', highlights='#e8e29a', strength=0.5)
    img = curve(img, [(0, 0), (0.5, 0.5), (0.8, 0.83), (1, 1)], channels='g')
    img = curve(img, [(0, 0), (0.5, 0.49), (0.8, 0.74), (1, 0.9)], channels='b')
    img = curve(img, [(0, 0), (0.5, 0.5), (0.8, 0.81), (1, 0.98)], channels='r')
    img = color_balance(img, shadows=(-0.02, 0.0, 0.03), highlights=(0.02, 0.03, -0.04))
    # foliage: yellow-green, a little washed
    img = hsl_adjust(img, 100, width=45, sat=0.85, shift=-10, lum=0.03)
    # skin: warm yellow rather than green — keep the face flattering
    skin = _skin_mask(8)
    skin_v = fade(natural, 0.08, 0.04)
    skin_v = saturation(skin_v, 0.9)
    skin_v = split_tone(skin_v, shadows='#2c3540', highlights='#f0e4a8', strength=0.35)
    img = apply_mask(img, lerp(img, skin_v, 0.5), skin)
    # film grain and a soft, faint halation on the brightest spots
    img = halation(img, sigma=30, strength=0.12, color_='#ffe08a', threshold=0.8)
    img = grain(img, amount=0.07, size=1.25, seed=70)
    img = vignette(img, strength=0.18, radius=1.05, softness=0.8, color_='#101820')
    return img
