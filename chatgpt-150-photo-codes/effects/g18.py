"""Group g18 - Fon (Background): color_pop, spotlight_bg, paper_bg, dark_bg, pattern_bg."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- shared cut-out helpers

def _person():
    """Clean subject matte.  The raw mask sits on a 0.04 floor / 0.98 ceiling and its ~8 px soft ramp straddles
    the true outline (outer half = green foliage fringe).  Pull the edge 3 px inside, re-level, then feather:
    crisp on the in-focus head/hijab, softer on the out-of-focus sleeve at the bottom-left."""
    p = mask('person', grow=-3)
    p = np.clip((p - 0.05) / 0.91, 0, 1)
    sharp = feather(p, 1.2)
    soft = feather(p, 3.5)
    x, y = coords()
    w = smoothstep(0, 1, (y - 760) / 220.0) * smoothstep(0, 1, (430 - x) / 200.0)
    return (sharp * (1 - w) + soft * w).astype(np.float32)


def _decontaminate(img, p, band=6):
    """Outside a 6 px core, replace the subject's colour with the colour just inside (blurred, normalised), so the
    matte's ramp only ever mixes clean subject colour with the new background - no fringe, no halo."""
    hard = (p > 0.5).astype(np.float32)
    core = cv2.erode(hard, np.ones((band * 2 + 1,) * 2, np.uint8))
    den = blur(core, 8)
    inner = blur(img * core[..., None], 8) / np.maximum(den, 1e-3)[..., None]
    w = feather(1 - core, 1.5) * 0.9 * (den > 0.02)
    return lerp(img, inner, w)


def _ground(bg, p, strength=0.3, offset=(14, 20), sigma=24, colour='#3b2c22'):
    """Soft contact shadow + offset drop shadow of the subject on the new backdrop (outside the subject only)."""
    ao = feather(p, 16)
    drop = feather(translate(p, *offset), sigma)
    s = np.clip(ao * 0.55 + drop * 0.75, 0, 1) * strength * (1 - p)
    return blend(bg, colour, 'multiply', 1.0, s)


def _composite(img, bg, p=None, shadow=True, **kw):
    p = _person() if p is None else p
    if shadow:
        bg = _ground(bg, p, **kw)
    return clip(lerp(bg, _decontaminate(img, p), p))


def _facing_up(p):
    """(H,W) weight 1 where the subject's outline faces upward, 0 where it faces down."""
    pm = feather(p, 6)
    gx = cv2.Sobel(pm, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(pm, cv2.CV_32F, 0, 1, ksize=3)
    return np.clip(gy / (np.sqrt(gx * gx + gy * gy) + 1e-6), 0, 1)


# ----------------------------------------------------------------------------- 086 color_pop

@effect('color_pop')
def color_pop(img):
    """Subject in full colour, background black & white."""
    p = _person()
    mono = bw(img, 0.34, 0.54, 0.12)          # red/yellow-weighted so the foliage stays luminous, not muddy
    mono = gamma(contrast(mono, 0.95), 1.06)  # slightly softer, airier B&W so the colour subject pops
    subj = vibrance(img, 0.1)
    return clip(lerp(mono, subj, p))


# ----------------------------------------------------------------------------- 087 spotlight_bg

@effect('spotlight_bg')
def spotlight_bg(img):
    """Dark studio backdrop with a soft circular spotlight glow behind the head, thin warm rim on the subject."""
    p = _person()
    cx, cy = 620, 400                                                   # behind and a little above the head
    spot = radial((cx, cy), radius=1.0, softness=0.8, aspect=W / H) ** 1.2   # aspect -> truly circular
    halo = radial((cx, cy), radius=1.7, softness=1.0, aspect=W / H) * 0.3    # faint ambient spill
    glow = np.clip(spot * 0.9 + halo, 0, 1) * (0.9 + 0.2 * fbm(4, seed=8, scale=0.6))   # cloth-like unevenness
    bg = canvas('#141012')
    bg = blend(bg, glow[..., None] * color('#86604a'), 'screen', 1.0)
    bg = clip(bg + ((noise(5) - 0.5) * 0.006)[..., None])              # dither against banding
    out = _composite(img, bg, p, shadow=False)
    # thin rim light wrapping from the backdrop: strongest on the top of the head / shoulders, none underneath
    rim = inner_edge(p, width=6, softness=3) * (0.3 + 0.7 * _facing_up(p)) * np.clip(glow * 1.3, 0, 1)
    out = blend(out, '#ffd9b3', 'screen', 0.6, rim)
    out = lerp(out, temperature(out, 0.08), p)                          # warm the subject slightly
    return vignette(out, 0.28, radius=1.1, softness=0.8, center=(600, 600))


# ----------------------------------------------------------------------------- 088 paper_bg

@effect('paper_bg')
def paper_bg(img):
    """Background replaced by textured cream paper; subject unchanged, grounded by a soft shadow."""
    p = _person()
    bg = canvas('#efe4d2', paper(seed=3, strength=0.28))
    bg = vignette(bg, 0.2, radius=1.2, softness=0.9, color_='#a88c6c')
    return _composite(img, bg, p, strength=0.32)


# ----------------------------------------------------------------------------- 089 dark_bg

@effect('dark_bg')
def dark_bg(img):
    """Background darkened, desaturated and softened; subject a touch brighter and crisper."""
    p = _person()
    bg = blur_background(img, sigma=5, person=p)
    bg = saturation(exposure(bg, -1.5), 0.25)
    bg = curve(bg, [(0, 0.02), (0.5, 0.5), (1, 0.96)])           # soft matte darkness, not crushed
    subj = clarity(brightness(img, 0.03), 0.1, 30)
    out = lerp(bg, subj, p)
    rim = inner_edge(p, width=8, softness=4)
    out = blend(out, '#e8e0d8', 'screen', 0.12, rim)                   # whisper of separation on the navy
    return vignette(out, 0.2)


# ----------------------------------------------------------------------------- 090 pattern_bg

def _ell(d, cx, cy, a, b, angle, fill, n=48):
    """Rotated ellipse polygon: semi-axis a along `angle` (deg, 0 = up, clockwise), b across."""
    t = math.radians(angle)
    ca, sa = math.cos(t), math.sin(t)
    pts = []
    for i in range(n):
        ph = 2 * math.pi * i / n
        v, u = a * math.cos(ph), b * math.sin(ph)
        pts.append((cx + v * sa + u * ca, cy - v * ca + u * sa))
    d.polygon(pts, fill=fill)


def _ornament(d, cx, cy, R):
    """Rounded acanthus-style damask element (white ink, black hollows) of radius ~R."""
    for sx in (-1, 1):                                              # four curling leaves (crescents)
        for sy, ang in ((-1, 40), (1, 140)):
            ox, oy = cx + sx * 0.55 * R, cy + sy * 0.35 * R
            _ell(d, ox, oy, 0.50 * R, 0.20 * R, sx * ang, 255)
            _ell(d, ox - sx * 0.11 * R, oy - sy * 0.07 * R, 0.44 * R, 0.14 * R, sx * ang, 0)
        _ell(d, cx + sx * 0.80 * R, cy, 0.20 * R, 0.09 * R, 90, 255)   # side buds
    _ell(d, cx, cy, 0.64 * R, 0.30 * R, 0, 255)                     # central bud
    _ell(d, cx, cy, 0.42 * R, 0.11 * R, 0, 0)                       # its hollow
    for sy in (-1, 1):
        r = 0.065 * R
        d.ellipse((cx - r, cy + sy * 0.88 * R - r, cx + r, cy + sy * 0.88 * R + r), fill=255)


def _damask_tiles(period=236, R=74, line_w=2.2, dot_r=4.5, ss=4):
    """Seamless wallpaper alphas (motifs, lattice) as (H, W) arrays: diagonal lattice with dots at the nodes and
    an ornament in every diamond cell."""
    T = period * ss
    motif = Image.new('L', (T, T), 0)
    lattice = Image.new('L', (T, T), 0)
    dm, dl = ImageDraw.Draw(motif), ImageDraw.Draw(lattice)
    lw = max(1, int(round(line_w * ss)))
    for c in (0, T, 2 * T):                                         # x + y = c
        dl.line([(c, 0), (0, c)], fill=255, width=lw)
    for c in (-T, 0, T):                                            # x - y = c
        dl.line([(c, 0), (c + T, T)], fill=255, width=lw)
    rr = dot_r * ss
    for (nx, ny) in ((0, 0), (T, 0), (0, T), (T, T), (T / 2, T / 2)):
        dl.ellipse((nx - rr, ny - rr, nx + rr, ny + rr), fill=255)
    for (mx, my) in ((T / 2, 0), (T / 2, T), (0, T / 2), (T, T / 2)):
        _ornament(dm, mx, my, R * ss)
    reps = (H // period + 2, W // period + 2)
    out = []
    for im in (motif, lattice):
        small = cv2.resize(np.array(im).astype(np.float32) / 255.0, (period, period), interpolation=cv2.INTER_AREA)
        out.append(np.tile(small, reps)[:H, :W])
    return out


@effect('pattern_bg')
def pattern_bg(img):
    """Background replaced by an elegant, subtle beige damask wallpaper with soft room light."""
    p = _person()
    motif, lattice = _damask_tiles()
    wall = as_layer('#efe5d5')
    wall = lerp(wall, as_layer('#e3d6bf'), lattice)
    wall = lerp(wall, as_layer('#dac8ab'), motif)
    wall = clip(wall * paper(seed=4, strength=0.10)[..., None])
    wall = blur(wall, 1.3)                                                   # sits a little behind the focal plane
    wall = vignette(wall, 0.22, radius=1.2, softness=0.9, color_='#8f7658', center=(600, 480))
    return _composite(img, wall, p, strength=0.32)
