"""Shared helper library for the 150 photo effects.

Conventions
-----------
* Images are float32 numpy arrays, RGB, values in [0, 1], shape (H, W, 3) = (1440, 1152, 3).
* Masks are float32 arrays, shape (H, W), values in [0, 1] (1 = selected).
* Colours can be given as '#RRGGBB', (r, g, b) in 0..255 ints, or floats in 0..1.
* Every helper returns a NEW array; nothing mutates its input.

Quick start (inside effects/gNN.py):

    from effects.lib import *
    from effects.registry import effect

    @effect('golden_hour')
    def golden_hour(img):
        img = temperature(img, 0.35)
        img = split_tone(img, shadows='#5a3a2a', highlights='#ffd27a', strength=0.35)
        img = glow(img, sigma=40, strength=0.35, threshold=0.55)
        return vignette(img, strength=0.25)
"""
import os, json, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')
FONT_DIR = os.path.join(ROOT, 'book', 'fonts')
H, W = 1440, 1152

# Guide palette (for effects that want to echo the book's look)
BURGUNDY = '#6B1F2E'
BURGUNDY_DEEP = '#43121D'
ROSE = '#A8556B'
BLUSH = '#E8C4C8'
CREAM = '#F7F1E8'
BEIGE = '#E9DDCB'
TAUPE = '#C9B9A3'
INK = '#2E1A1F'
GOLD = '#C9A15C'

# ----------------------------------------------------------------------------- I/O

@functools.lru_cache(None)
def _base_u8():
    return np.array(Image.open(os.path.join(SRC, 'crop.jpg')).convert('RGB'))


def base():
    """Fresh float32 copy of the source portrait (1440 x 1152 x 3, values 0..1)."""
    return _base_u8().astype(np.float32) / 255.0


@functools.lru_cache(None)
def _mask_u8(name):
    p = os.path.join(SRC, 'masks', name + '.png')
    if not os.path.exists(p):
        raise FileNotFoundError('unknown mask %r; available: %s' % (name, sorted(os.listdir(os.path.join(SRC, 'masks')))))
    return np.array(Image.open(p).convert('L'))


def mask(name, feather=0.0, grow=0):
    """Load a mask by name as float32 (H, W) in [0, 1].

    Names: person, background, face, face_skin, eyes, iris, iris_l, iris_r, lips, mouth (teeth/inner mouth),
    brows, seg_hair, seg_clothes, seg_accessories, seg_body_skin, seg_face_skin, seg_bg.
    feather: gaussian sigma in px applied to the mask.  grow: dilate (>0) or erode (<0) in px.
    """
    m = _mask_u8(name).astype(np.float32) / 255.0
    if grow:
        k = np.ones((abs(grow) * 2 + 1,) * 2, np.uint8)
        m = cv2.dilate(m, k) if grow > 0 else cv2.erode(m, k)
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


@functools.lru_cache(None)
def meta():
    """Landmark metadata: face_box [x0,y0,x1,y1], face_center, eye_l, eye_r, mouth, nose, chin, forehead (all in px)."""
    return json.load(open(os.path.join(SRC, 'meta.json')))


def to_pil(img):
    return Image.fromarray(to_u8(img))


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def from_pil(pil):
    return np.array(pil.convert('RGB')).astype(np.float32) / 255.0


def from_u8(a):
    return a.astype(np.float32) / 255.0


def finalize(img):
    """Clip, fix shape/size and return a float32 (H, W, 3) array."""
    if isinstance(img, Image.Image):
        img = from_pil(img)
    img = np.asarray(img, dtype=np.float32)
    if img.ndim == 2:
        img = np.repeat(img[..., None], 3, axis=2)
    if img.shape[2] == 4:
        img = img[..., :3]
    if img.shape[:2] != (H, W):
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    return np.clip(img, 0, 1).astype(np.float32)


# ----------------------------------------------------------------------------- basics

def color(c):
    """Any colour spec -> float32 array (3,) in [0,1]."""
    if isinstance(c, str):
        c = c.lstrip('#')
        return np.array([int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)
    c = np.array(c, np.float32)
    if c.max() > 1.0:
        c = c / 255.0
    return c[:3]


def color255(c):
    return tuple(int(round(v * 255)) for v in color(c))


def clip(img):
    return np.clip(img, 0, 1)


def lerp(a, b, t):
    """Linear blend a->b by t (scalar, (H,W) mask, or (H,W,3))."""
    t = np.asarray(t, np.float32)
    if t.ndim == 2:
        t = t[..., None]
    return a * (1 - t) + b * t


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def luminance(img):
    """Rec.709 luminance, (H, W)."""
    return img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722


def gray(img):
    """Desaturated 3-channel image."""
    return np.repeat(luminance(img)[..., None], 3, axis=2)


def as_layer(x):
    """Colour / (H,W) / (H,W,3) -> (H,W,3) float32 layer."""
    if isinstance(x, (str, tuple, list)) or (isinstance(x, np.ndarray) and x.ndim == 1):
        return np.ones((H, W, 3), np.float32) * color(x)
    x = np.asarray(x, np.float32)
    if x.ndim == 2:
        x = np.repeat(x[..., None], 3, axis=2)
    return x


def rgb2hsv(img):
    """float32 HSV: H in [0,360), S,V in [0,1]."""
    return cv2.cvtColor(np.ascontiguousarray(clip(img), dtype=np.float32), cv2.COLOR_RGB2HSV)


def hsv2rgb(hsv):
    hsv = hsv.copy()
    hsv[..., 0] = hsv[..., 0] % 360.0
    hsv[..., 1:] = np.clip(hsv[..., 1:], 0, 1)
    return cv2.cvtColor(np.ascontiguousarray(hsv, dtype=np.float32), cv2.COLOR_HSV2RGB)


# ----------------------------------------------------------------------------- tone & colour

def brightness(img, amount):
    return clip(img + amount)


def exposure(img, stops):
    return clip(img * (2.0 ** stops))


def gamma(img, g):
    return clip(img) ** (1.0 / g)


def contrast(img, factor, pivot=0.5):
    return clip((img - pivot) * factor + pivot)


def levels(img, black=0.0, white=1.0, gamma_=1.0, out_black=0.0, out_white=1.0):
    x = np.clip((img - black) / max(white - black, 1e-6), 0, 1) ** (1.0 / gamma_)
    return clip(out_black + x * (out_white - out_black))


def curve(img, points, channels='rgb'):
    """Smooth tone curve through points [(x, y), ...] in 0..1 (endpoints added if missing).
    channels: any of 'r','g','b' (e.g. 'rgb', 'r', 'gb')."""
    from scipy.interpolate import PchipInterpolator
    pts = sorted(points)
    if pts[0][0] > 0:
        pts.insert(0, (0.0, 0.0))
    if pts[-1][0] < 1:
        pts.append((1.0, 1.0))
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    grid = np.linspace(0, 1, 1024)
    lut = np.clip(PchipInterpolator(xs, ys)(grid), 0, 1).astype(np.float32)
    out = img.copy()
    for c, ch in enumerate('rgb'):
        if ch in channels:
            out[..., c] = np.interp(np.clip(out[..., c], 0, 1), grid, lut)
    return out


def s_curve(img, amount=0.2):
    """Contrast S-curve; amount 0..0.5."""
    return curve(img, [(0, 0), (0.25, 0.25 - amount * 0.5), (0.75, 0.75 + amount * 0.5), (1, 1)])


def fade(img, amount=0.12, highlight=0.04):
    """Matte / faded film look: lifts blacks, slightly lowers whites."""
    return curve(img, [(0, amount), (0.5, 0.5 + amount * 0.25), (1, 1 - highlight)])


def saturation(img, factor):
    return clip(lerp(gray(img), img, factor))


def vibrance(img, amount=0.3):
    """Boost saturation more where it is low (protects skin)."""
    hsv = rgb2hsv(img)
    s = hsv[..., 1]
    hsv[..., 1] = np.clip(s + amount * s * (1 - s) * 2, 0, 1)
    return hsv2rgb(hsv)


def hue_shift(img, degrees):
    hsv = rgb2hsv(img)
    hsv[..., 0] = (hsv[..., 0] + degrees) % 360
    return hsv2rgb(hsv)


def hsl_adjust(img, hue, width=30.0, sat=1.0, lum=0.0, shift=0.0, min_sat=0.08):
    """Selective colour: pixels within +-width degrees of `hue` get sat multiplied, lum added, hue shifted (deg).
    hue reference: red 0, orange 30, yellow 60, green 120, cyan 180, blue 240, magenta 300."""
    hsv = rgb2hsv(img)
    d = np.abs(((hsv[..., 0] - hue + 180.0) % 360.0) - 180.0)
    w = smoothstep(width, 0.0, d) * smoothstep(0.0, min_sat * 3, hsv[..., 1])
    hsv[..., 0] = (hsv[..., 0] + shift * w) % 360
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + (sat - 1) * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] + lum * w, 0, 1)
    return hsv2rgb(hsv)


def isolate_hue(img, hue=0.0, width=25.0, keep=1.0):
    """Colour-pop: keep only hues near `hue`, desaturate everything else."""
    hsv = rgb2hsv(img)
    d = np.abs(((hsv[..., 0] - hue + 180.0) % 360.0) - 180.0)
    w = smoothstep(width, width * 0.5, d) * smoothstep(0.12, 0.35, hsv[..., 1]) * keep
    return lerp(gray(img), img, w)


def temperature(img, amount):
    """Warm (+) / cool (-) shift, typical |amount| 0.1..0.5."""
    gains = np.array([1 + 0.45 * amount, 1 + 0.08 * amount, 1 - 0.45 * amount], np.float32)
    return clip(img * gains)


def tint(img, amount):
    """Magenta (+) / green (-) shift."""
    gains = np.array([1 + 0.15 * amount, 1 - 0.3 * amount, 1 + 0.15 * amount], np.float32)
    return clip(img * gains)


def channel_mixer(img, r=(1, 0, 0), g=(0, 1, 0), b=(0, 0, 1)):
    M = np.array([r, g, b], np.float32)
    return clip(img @ M.T)


def bw(img, r=0.3, g=0.59, b=0.11):
    """Black & white with channel weights (sum ~1)."""
    l = img[..., 0] * r + img[..., 1] * g + img[..., 2] * b
    return np.repeat(np.clip(l, 0, 1)[..., None], 3, axis=2)


def tone(img, c, strength=1.0):
    """Monochrome tint: colourises luminance with colour c (sepia etc.)."""
    l = luminance(img)[..., None]
    col = color(c)
    toned = clip(l * col / max(luminance(col[None, None])[0, 0], 1e-6))
    return clip(lerp(img, toned, strength))


def sepia(img, strength=1.0):
    return tone(img, '#c9a06a', strength)


def split_tone(img, shadows='#2b4a6b', highlights='#f0c080', balance=0.0, strength=0.3):
    """Colour shadows and highlights separately (Lightroom-style)."""
    l = luminance(img)
    w = smoothstep(0.2 + balance, 0.8 + balance, l)[..., None]
    layer = (1 - w) * color(shadows) + w * color(highlights)
    return blend(img, layer, 'soft_light', strength)


def color_balance(img, shadows=(0, 0, 0), midtones=(0, 0, 0), highlights=(0, 0, 0)):
    """Additive RGB offsets (in -1..1, small values like 0.05) weighted by tonal range."""
    l = luminance(img)
    ws = (1 - smoothstep(0.0, 0.5, l))[..., None]
    wh = smoothstep(0.5, 1.0, l)[..., None]
    wm = 1 - ws - wh
    off = ws * np.array(shadows, np.float32) + wm * np.array(midtones, np.float32) + wh * np.array(highlights, np.float32)
    return clip(img + off)


def gradient_map(img, stops, strength=1.0):
    """Map luminance through colour stops [(pos, colour), ...]; pos in 0..1."""
    l = luminance(img)
    pos = [s[0] for s in stops]
    cols = np.array([color(s[1]) for s in stops], np.float32)
    mapped = np.stack([np.interp(l, pos, cols[:, c]) for c in range(3)], axis=-1).astype(np.float32)
    return clip(lerp(img, mapped, strength))


def duotone(img, dark, light, strength=1.0):
    return gradient_map(img, [(0, dark), (1, light)], strength)


def posterize(img, levels_=6):
    return np.floor(clip(img) * (levels_ - 1) + 0.5) / (levels_ - 1)


def solarize(img, threshold=0.5):
    return np.where(img > threshold, 1 - img, img)


def invert(img):
    return 1 - img


def threshold(img, t=0.5, soft=0.02):
    return np.repeat(smoothstep(t - soft, t + soft, luminance(img))[..., None], 3, axis=2)


# ----------------------------------------------------------------------------- blend modes

def _bm(mode, a, b):
    if mode == 'normal':
        return b
    if mode == 'multiply':
        return a * b
    if mode == 'screen':
        return 1 - (1 - a) * (1 - b)
    if mode == 'overlay':
        return np.where(a < 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))
    if mode == 'hard_light':
        return np.where(b < 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))
    if mode == 'soft_light':
        return np.where(b < 0.5, a - (1 - 2 * b) * a * (1 - a), a + (2 * b - 1) * (np.sqrt(np.clip(a, 0, 1)) - a))
    if mode == 'lighten':
        return np.maximum(a, b)
    if mode == 'darken':
        return np.minimum(a, b)
    if mode == 'add':
        return a + b
    if mode == 'subtract':
        return a - b
    if mode == 'difference':
        return np.abs(a - b)
    if mode == 'color_dodge':
        return np.where(b >= 1, 1, np.minimum(1, a / np.maximum(1 - b, 1e-4)))
    if mode == 'color_burn':
        return np.where(b <= 0, 0, 1 - np.minimum(1, (1 - a) / np.maximum(b, 1e-4)))
    if mode == 'luminosity':
        return clip(a + (luminance(b) - luminance(a))[..., None])
    if mode == 'color':  # hue+sat of b with luminance of a
        return clip(b + (luminance(a) - luminance(b))[..., None])
    raise ValueError('unknown blend mode ' + mode)


def blend(base_img, layer, mode='normal', opacity=1.0, mask_=None):
    """Photoshop-style blend of `layer` (colour, (H,W) or (H,W,3)) onto base_img."""
    layer = as_layer(layer)
    out = clip(_bm(mode, base_img, layer))
    t = opacity if mask_ is None else opacity * np.asarray(mask_, np.float32)
    return clip(lerp(base_img, out, t))


def screen(a, b, opacity=1.0): return blend(a, b, 'screen', opacity)
def multiply(a, b, opacity=1.0): return blend(a, b, 'multiply', opacity)
def overlay(a, b, opacity=1.0): return blend(a, b, 'overlay', opacity)
def soft_light(a, b, opacity=1.0): return blend(a, b, 'soft_light', opacity)


# ----------------------------------------------------------------------------- structure / blur / sharpen

def blur(img, sigma):
    if sigma <= 0:
        return img.copy()
    return cv2.GaussianBlur(img, (0, 0), sigma)


def box_blur(img, k):
    return cv2.blur(img, (k, k))


def median(img, k=5):
    return from_u8(cv2.medianBlur(to_u8(img), k | 1))


def bilateral(img, d=9, sigma_color=0.1, sigma_space=12):
    return cv2.bilateralFilter(np.ascontiguousarray(img), d, sigma_color, sigma_space)


def guided(img, radius=12, eps=0.004, guide=None):
    g = np.ascontiguousarray(img if guide is None else guide, dtype=np.float32)
    return cv2.ximgproc.guidedFilter(g, np.ascontiguousarray(img, dtype=np.float32), radius, eps)


def unsharp(img, radius=2.0, amount=0.6, threshold=0.0):
    b = blur(img, radius)
    d = img - b
    if threshold:
        d = np.where(np.abs(d) < threshold, 0, d)
    return clip(img + amount * d)


def sharpen(img, amount=0.5):
    return unsharp(img, 1.2, amount)


def clarity(img, amount=0.4, radius=40):
    """Local contrast (midtone punch) on luminance."""
    l = luminance(img)
    d = l - blur(l, radius)
    return clip(img + (amount * d)[..., None])


def detail_enhance(img, sigma_s=10, sigma_r=0.15):
    return from_u8(cv2.cvtColor(cv2.detailEnhance(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2BGR), sigma_s=sigma_s, sigma_r=sigma_r), cv2.COLOR_BGR2RGB))


def cv_stylization(img, sigma_s=60, sigma_r=0.45):
    """OpenCV painterly stylization (watercolour-ish)."""
    return from_u8(cv2.cvtColor(cv2.stylization(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2BGR), sigma_s=sigma_s, sigma_r=sigma_r), cv2.COLOR_BGR2RGB))


def cv_pencil(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05):
    """OpenCV pencil sketch -> (gray_sketch (H,W,3), colour_sketch (H,W,3))."""
    g, c = cv2.pencilSketch(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2BGR), sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
    return from_u8(np.repeat(g[..., None], 3, axis=2)), from_u8(cv2.cvtColor(c, cv2.COLOR_BGR2RGB))


def cv_oil(img, size=7, dyn_ratio=1):
    return from_u8(cv2.cvtColor(cv2.xphoto.oilPainting(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2BGR), size, dyn_ratio), cv2.COLOR_BGR2RGB))


def edges(img, low=60, high=160, sigma=1.0):
    """Canny edge mask (H,W) in [0,1]."""
    g = cv2.GaussianBlur(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2GRAY), (0, 0), sigma)
    return cv2.Canny(g, low, high).astype(np.float32) / 255.0


def xdog(img, sigma=1.0, k=1.6, p=20.0, eps=0.02, phi=10.0):
    """XDoG line drawing -> (H,W) in [0,1], 1 = white paper, 0 = ink."""
    l = luminance(img)
    g1 = blur(l, sigma); g2 = blur(l, sigma * k)
    d = g1 - g2
    u = g1 + p * d
    out = np.where(u >= eps, 1.0, 1.0 + np.tanh(phi * (u - eps)))
    return np.clip(out, 0, 1).astype(np.float32)


def glow(img, sigma=30, strength=0.5, threshold=0.6):
    """Bloom: blur the highlights and screen them back."""
    l = luminance(img)
    hi = smoothstep(threshold, 1.0, l)[..., None] * img
    return blend(img, blur(hi, sigma), 'screen', strength)


def orton(img, sigma=25, strength=0.5):
    """Dreamy Orton effect (blurred copy multiplied/screened)."""
    b = blur(img, sigma)
    d = 1 - (1 - img) * (1 - b)  # screen
    return clip(lerp(img, d * 0.85 + img * b * 0.15, strength))


def halation(img, sigma=45, strength=0.5, color_='#ff5a33', threshold=0.7):
    """Cinestill-style red halo around bright highlights."""
    l = luminance(img)
    hi = smoothstep(threshold, 1.0, l)
    layer = blur(hi, sigma)[..., None] * color(color_)
    return blend(img, layer, 'screen', strength)


def soft_focus(img, sigma=12, mix=0.5):
    return clip(lerp(img, blur(img, sigma), mix))


def motion_blur(img, length=40, angle=0.0):
    k = np.zeros((length, length), np.float32)
    k[length // 2, :] = 1.0
    M = cv2.getRotationMatrix2D((length / 2 - 0.5, length / 2 - 0.5), angle, 1.0)
    k = cv2.warpAffine(k, M, (length, length))
    k /= max(k.sum(), 1e-6)
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)


def zoom_blur(img, center=None, strength=0.08, steps=14):
    cx, cy = center or (W / 2, H / 2)
    acc = np.zeros_like(img)
    for i in range(steps):
        s = 1 + strength * i / (steps - 1)
        M = cv2.getRotationMatrix2D((cx, cy), 0, s)
        acc += cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / steps


def spin_blur(img, center=None, degrees=6.0, steps=14):
    cx, cy = center or (W / 2, H / 2)
    acc = np.zeros_like(img)
    for i in range(steps):
        a = -degrees / 2 + degrees * i / (steps - 1)
        M = cv2.getRotationMatrix2D((cx, cy), a, 1.0)
        acc += cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / steps


def disc_kernel(radius):
    r = int(radius)
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    k = ((x * x + y * y) <= r * r).astype(np.float32)
    return k / k.sum()


def bokeh_blur(img, radius=18, highlight_boost=3.0):
    """Lens-like blur with bright, round bokeh discs."""
    k = disc_kernel(radius)
    boosted = np.clip(img, 0, 1) ** highlight_boost
    b = cv2.filter2D(boosted, -1, k, borderType=cv2.BORDER_REFLECT)
    return np.clip(b, 0, 1) ** (1.0 / highlight_boost)


def skin_smooth(img, strength=0.7, mask_=None, radius=14, keep_texture=0.35):
    """Frequency-separation style skin smoothing restricted to the skin mask."""
    m = mask_ if mask_ is not None else np.clip(mask('face_skin', 3) + mask('seg_body_skin', 3), 0, 1)
    low = guided(img, radius, 0.004)
    high = img - blur(img, 2.0)
    smooth = clip(low + keep_texture * high)
    return clip(lerp(img, smooth, strength * m))


# ----------------------------------------------------------------------------- geometry & spatial masks

def coords():
    """Pixel coordinate grids (x, y) as float32 (H, W)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    return x, y


def radial(center=None, radius=0.85, softness=0.5, aspect=1.0):
    """Elliptical mask: 1 in the centre, fading to 0 at `radius` (1.0 = frame edge)."""
    cx, cy = center or (W / 2, H / 2)
    x, y = coords()
    d = np.sqrt(((x - cx) / (W / 2)) ** 2 * aspect + ((y - cy) / (H / 2)) ** 2 / aspect)
    inner = radius * (1 - softness)
    return (1 - smoothstep(inner, radius, d)).astype(np.float32)


def linear(angle=90.0, start=0.0, end=1.0):
    """Linear gradient mask 0->1 along `angle` degrees (90 = top to bottom, 0 = left to right)."""
    x, y = coords()
    a = math.radians(angle)
    t = (x * math.cos(a) + y * math.sin(a))
    t = (t - t.min()) / (t.max() - t.min() + 1e-6)
    return smoothstep(start, end, t).astype(np.float32)


def vignette(img, strength=0.5, radius=0.95, softness=0.7, color_='#000000', center=None):
    m = 1 - radial(center, radius, softness)
    return clip(lerp(img, as_layer(color_), strength * m))


def feather(m, sigma):
    return cv2.GaussianBlur(np.asarray(m, np.float32), (0, 0), sigma) if sigma > 0 else m


def edge_band(m, width=12, softness=6):
    """Band along the border of a mask (e.g. person silhouette for rim light)."""
    k = np.ones((width * 2 + 1,) * 2, np.uint8)
    band = cv2.dilate(m, k) - cv2.erode(m, k)
    return feather(np.clip(band, 0, 1), softness)


def inner_edge(m, width=14, softness=6):
    k = np.ones((width * 2 + 1,) * 2, np.uint8)
    return feather(np.clip(m - cv2.erode(m, k), 0, 1), softness)


def apply_mask(original, edited, m):
    """Use `edited` where mask is 1, `original` elsewhere."""
    return clip(lerp(original, edited, m))


def blur_background(img, sigma=18, person=None, method='gaussian', radius=18):
    """Portrait-mode blur: blurs only the background without haloing the subject."""
    p = person if person is not None else mask('person')
    bg = (1 - p)[..., None]
    if method == 'bokeh':
        num = bokeh_blur(img * bg, radius); den = bokeh_blur(np.repeat(bg, 3, 2), radius)
    else:
        num = blur(img * bg, sigma); den = blur(np.repeat(bg, 3, 2), sigma)
    bgb = num / np.maximum(den, 1e-3)
    return clip(lerp(img, bgb, 1 - p))


def replace_background(img, background, person=None, feather_=1.5):
    """Composite the subject over a new background (colour, (H,W) or (H,W,3))."""
    p = person if person is not None else mask('person')
    if feather_:
        p = feather(p, feather_)
    return clip(lerp(as_layer(background), img, p))


def zoom(img, factor=1.1, center=None):
    cx, cy = center or (W / 2, H / 2)
    M = cv2.getRotationMatrix2D((cx, cy), 0, factor)
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def rotate(img, degrees, scale=1.0, center=None, border=cv2.BORDER_REFLECT):
    cx, cy = center or (W / 2, H / 2)
    M = cv2.getRotationMatrix2D((cx, cy), degrees, scale)
    return cv2.warpAffine(img, M, (W, H), borderMode=border)


def translate(img, dx, dy, border=cv2.BORDER_REFLECT):
    M = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), borderMode=border)


def barrel(img, k=0.15):
    """Lens distortion (k>0 barrel/fisheye, k<0 pincushion)."""
    x, y = coords()
    nx = (x - W / 2) / (W / 2); ny = (y - H / 2) / (H / 2)
    r2 = nx * nx + ny * ny
    f = 1 + k * r2
    mx = (nx * f * (W / 2) + W / 2).astype(np.float32); my = (ny * f * (H / 2) + H / 2).astype(np.float32)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def letterbox(img, ratio=1.0, color_='#000000'):
    """Bars top/bottom so that the visible area has aspect ratio `ratio` (w/h)."""
    vis_h = int(W / ratio)
    pad = max(0, (H - vis_h) // 2)
    out = img.copy()
    out[:pad] = color(color_); out[H - pad:] = color(color_)
    return out


def resize(img, w, h):
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA if w < img.shape[1] else cv2.INTER_CUBIC)


# ----------------------------------------------------------------------------- procedural textures & overlays

def rng(seed=0):
    return np.random.default_rng(seed)


def noise(seed=0, sigma=0.0, shape=(H, W)):
    """White noise (H,W) in [0,1], optionally blurred."""
    n = rng(seed).random(shape).astype(np.float32)
    if sigma:
        n = cv2.GaussianBlur(n, (0, 0), sigma)
        n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    return n


def fbm(octaves=5, seed=0, scale=1.0, shape=(H, W)):
    """Fractal cloud noise (H,W) in [0,1]. scale>1 = finer detail."""
    h, w = shape
    r = rng(seed)
    acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        res_h = max(2, int(3 * (2 ** o) * scale)); res_w = max(2, int(res_h * w / h))
        small = r.random((res_h, res_w)).astype(np.float32)
        acc += amp * cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp; amp *= 0.5
    acc /= tot
    return ((acc - acc.min()) / (acc.max() - acc.min() + 1e-6)).astype(np.float32)


def grain(img, amount=0.08, size=1.0, mono=True, seed=0, shadows=1.0):
    """Film grain. amount ~0.03 subtle .. 0.15 heavy; size>1 = coarser."""
    r = rng(seed)
    if size != 1.0:
        sh = (int(H / size) + 1, int(W / size) + 1)
        n = r.standard_normal(sh + ((1,) if mono else (3,))).astype(np.float32)
        n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
        if n.ndim == 2:
            n = n[..., None]
    else:
        n = r.standard_normal((H, W, 1 if mono else 3)).astype(np.float32)
    l = luminance(img)[..., None]
    weight = 1 - (1 - shadows) * l  # more grain in shadows when shadows>0 ... keep simple
    weight = weight * (0.35 + 0.65 * (1 - np.abs(l - 0.5) * 2) ** 0.7)  # midtone-weighted like real film
    return clip(img + amount * n * weight)


def paper(seed=1, strength=0.18, fibers=True):
    """Paper texture (H,W) centred on 1.0 -> multiply with an image."""
    base_n = fbm(6, seed, 1.5)
    fine = noise(seed + 7)
    tex = (base_n - 0.5) * 0.9 + (fine - 0.5) * 0.35
    if fibers:
        f = noise(seed + 11)
        f = cv2.GaussianBlur(f, (0, 0), sigmaX=0.6, sigmaY=5.0)
        f = (f - f.mean()) / (f.std() + 1e-6)
        tex += f * 0.08
    return (1 + strength * tex).astype(np.float32)


def scratches(count=25, seed=0, length=(200, 900), thickness=(1, 3), vertical=True, blur_=0.6):
    """Random scratch lines -> (H,W) mask in [0,1]."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(count):
        L = r.uniform(*length)
        ang = math.radians(r.uniform(-12, 12) + (90 if vertical else r.uniform(0, 180)))
        x0, y0 = r.uniform(0, W), r.uniform(0, H)
        x1, y1 = x0 + L * math.cos(ang), y0 + L * math.sin(ang)
        cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), float(r.uniform(0.4, 1.0)), int(r.integers(thickness[0], thickness[1] + 1)), cv2.LINE_AA)
    return feather(m, blur_) if blur_ else m


def dust(count=500, seed=0, size=(1, 4)):
    """Dust specks -> (H,W) mask."""
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for _ in range(count):
        x, y = int(r.uniform(0, W)), int(r.uniform(0, H))
        s = r.uniform(*size)
        cv2.ellipse(m, (x, y), (int(max(1, s)), int(max(1, s * r.uniform(0.4, 1)))), float(r.uniform(0, 180)), 0, 360, float(r.uniform(0.4, 1)), -1, cv2.LINE_AA)
    return feather(m, 0.5)


def light_leak(img, color_='#ff7a2a', side='right', strength=0.6, seed=0, size=0.55):
    """Warm light leak blob bleeding in from one side (left/right/top/bottom)."""
    r = rng(seed)
    x, y = coords()
    if side == 'right':
        cx, cy = W * (1 + 0.15), H * r.uniform(0.2, 0.8)
    elif side == 'left':
        cx, cy = -W * 0.15, H * r.uniform(0.2, 0.8)
    elif side == 'top':
        cx, cy = W * r.uniform(0.2, 0.8), -H * 0.15
    else:
        cx, cy = W * r.uniform(0.2, 0.8), H * 1.15
    d = np.sqrt(((x - cx) / (W * size)) ** 2 + ((y - cy) / (H * size * 1.3)) ** 2)
    m = (1 - smoothstep(0.0, 1.0, d)) ** 1.5
    m = m * (0.8 + 0.4 * fbm(4, seed + 3, 0.5))
    layer = m[..., None] * color(color_)
    return blend(img, layer, 'screen', strength)


def bokeh_layer(count=40, seed=0, radius=(20, 90), color_='#ffd58a', colors=None, area=None, softness=0.35, alpha=(0.25, 0.7)):
    """Floating bokeh discs -> (H,W,3) layer to screen-blend. `area` optional (H,W) mask limiting placement."""
    r = rng(seed)
    layer = np.zeros((H, W, 3), np.float32)
    x, y = coords()
    tries = 0
    n = 0
    while n < count and tries < count * 20:
        tries += 1
        cx, cy = r.uniform(0, W), r.uniform(0, H)
        if area is not None and area[int(cy), int(cx)] < 0.5:
            continue
        rad = r.uniform(*radius)
        col = color(colors[r.integers(len(colors))]) if colors else color(color_)
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / rad
        disc = (1 - smoothstep(1 - softness, 1.0, d)) * (0.8 + 0.2 * smoothstep(0.0, 1.0, d))  # brighter rim
        layer += disc[..., None] * col * r.uniform(*alpha)
        n += 1
    return np.clip(layer, 0, 1)


def star(cx, cy, size=40, thickness=0.12, rays=4, rotation=0.0):
    """Sparkle star shape -> (H,W) mask."""
    x, y = coords()
    dx, dy = x - cx, y - cy
    ang = np.arctan2(dy, dx) - math.radians(rotation)
    d = np.sqrt(dx * dx + dy * dy)
    shape = np.abs(np.cos(ang * rays / 2)) ** 8  # pointy lobes
    rad = size * (0.15 + 0.85 * shape)
    core = 1 - smoothstep(0, size * thickness, d)
    return np.clip((1 - smoothstep(rad * 0.5, rad, d)) * 0.9 + core, 0, 1).astype(np.float32)


def sparkle_layer(points, sizes=None, color_='#fff6dc', seed=0, glow_=True):
    """Stars at given (x,y) points -> (H,W,3) layer (screen-blend it)."""
    r = rng(seed)
    layer = np.zeros((H, W), np.float32)
    for i, (px, py) in enumerate(points):
        s = sizes[i] if sizes is not None else r.uniform(18, 60)
        layer = np.maximum(layer, star(px, py, s, rotation=r.uniform(-10, 10)))
    if glow_:
        layer = np.clip(layer + blur(layer, 6) * 0.8, 0, 1)
    return layer[..., None] * color(color_)


def stripes(angle=0.0, period=90, duty=0.5, softness=6.0, offset=0.0):
    """Repeating stripes mask (H,W) in [0,1] (1 = stripe)."""
    x, y = coords()
    a = math.radians(angle)
    t = (x * math.sin(a) + y * math.cos(a) + offset) % period
    edge = softness
    m = smoothstep(0, edge, t) * (1 - smoothstep(period * duty - edge, period * duty, t))
    return m.astype(np.float32)


def rays(center=(W * 1.05, -H * 0.05), count=14, seed=0, sharpness=8.0, spread=1.0):
    """God-rays mask emanating from `center` -> (H,W)."""
    x, y = coords()
    ang = np.arctan2(y - center[1], x - center[0])
    r = rng(seed)
    m = np.zeros((H, W), np.float32)
    for i in range(count):
        a0 = r.uniform(-math.pi, math.pi)
        width = r.uniform(0.02, 0.06) * spread
        d = np.abs(((ang - a0 + math.pi) % (2 * math.pi)) - math.pi)
        m += np.exp(-(d / width) ** 2) * r.uniform(0.4, 1.0)
    dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    m *= 1 - smoothstep(0, np.hypot(W, H) * 1.1, dist)
    return np.clip(m / max(m.max(), 1e-6), 0, 1).astype(np.float32)


def scanlines(img, period=4, strength=0.18, offset=0):
    x, y = coords()
    m = ((y.astype(np.int32) + offset) % period < period // 2).astype(np.float32)
    return clip(img * (1 - strength * m[..., None]))


def chromatic_aberration(img, amount=6, radial_=True):
    """RGB fringing. amount in px at the frame corners (radial) or as a flat shift."""
    if radial_:
        r = zoom(img[..., 0:1].repeat(3, 2), 1 + amount / W)[..., 0]
        b = zoom(img[..., 2:3].repeat(3, 2), 1 - amount / W)[..., 2]
    else:
        r = translate(img, amount, 0)[..., 0]
        b = translate(img, -amount, 0)[..., 2]
    return np.stack([r, img[..., 1], b], axis=-1)


def pixelate(img, block=16):
    small = cv2.resize(img, (W // block, H // block), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_NEAREST)


def halftone(img, cell=14, angle=25.0, gamma_=1.0):
    """Mono halftone: black dots on white -> (H,W,3)."""
    l = np.clip(luminance(img), 0, 1) ** gamma_
    x, y = coords()
    a = math.radians(angle)
    u = x * math.cos(a) + y * math.sin(a); v = -x * math.sin(a) + y * math.cos(a)
    cu = np.round(u / cell) * cell; cv_ = np.round(v / cell) * cell
    cx = cu * math.cos(a) - cv_ * math.sin(a); cy = cu * math.sin(a) + cv_ * math.cos(a)
    lb = cv2.blur(l, (cell, cell))
    samp = cv2.remap(lb, cx.astype(np.float32), cy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rad = cell * 0.58 * np.sqrt(np.clip(1 - samp, 0, 1))
    dist = np.sqrt((u - cu) ** 2 + (v - cv_) ** 2)
    dot = 1 - smoothstep(rad - 0.8, rad + 0.8, dist)
    return np.repeat((1 - dot)[..., None], 3, axis=2).astype(np.float32)


def lens_flare(img, pos=(W * 0.88, H * 0.1), strength=0.8, color_='#fff1c8', ghosts=True, streak=True, seed=0):
    """Sun flare: bright core, soft glow, horizontal streak and polygon ghosts along the axis."""
    x, y = coords()
    px, py = pos
    d = np.sqrt((x - px) ** 2 + (y - py) ** 2)
    layer = np.zeros((H, W, 3), np.float32)
    layer += ((1 - smoothstep(0, 60, d)) ** 2)[..., None] * 1.0
    layer += (np.exp(-(d / 260) ** 2) * 0.7)[..., None] * color(color_)
    layer += (np.exp(-(d / 700) ** 2) * 0.25)[..., None] * color(color_)
    if streak:
        s = np.exp(-((y - py) / 14) ** 2) * np.exp(-(np.abs(x - px) / (W * 0.7)) ** 1.5)
        layer += s[..., None] * np.array([0.6, 0.75, 1.0], np.float32) * 0.9
    if ghosts:
        r = rng(seed)
        cx, cy = W / 2, H / 2
        vx, vy = cx - px, cy - py
        for t, rad, alpha, col in ((0.35, 40, 0.18, '#ffb0c0'), (0.6, 70, 0.14, '#b0ffd8'), (0.85, 30, 0.22, '#ffe6a0'), (1.25, 110, 0.10, '#c0d8ff'), (1.55, 55, 0.16, '#ffc8a0')):
            gx, gy = px + vx * t, py + vy * t
            dd = np.sqrt((x - gx) ** 2 + (y - gy) ** 2)
            ring = (1 - smoothstep(rad * 0.85, rad, dd)) * (0.5 + 0.5 * smoothstep(rad * 0.5, rad * 0.95, dd))
            layer += ring[..., None] * color(col) * alpha
    return blend(img, np.clip(layer, 0, 1), 'screen', strength)


# ----------------------------------------------------------------------------- canvas, frames & text

def canvas(color_=CREAM, texture=None, size=(W, H)):
    """Solid canvas (H,W,3). texture: optional (H,W) multiplier (e.g. paper())."""
    c = np.ones((size[1], size[0], 3), np.float32) * color(color_)
    if texture is not None:
        c = clip(c * texture[..., None])
    return c


def rounded_mask(w, h, radius):
    """(h,w) float mask with rounded corners."""
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    return np.array(m).astype(np.float32) / 255.0


def paste(canvas_img, img, size, center=None, rotate_=0.0, border=0, border_color='#ffffff', radius=0,
          shadow=(0.35, 28, (10, 18)), border_bottom=None):
    """Place `img` (resized to size=(w,h)) onto canvas_img with optional border, rounded corners, rotation & drop shadow.
    border_bottom: extra bottom border (e.g. polaroid). shadow=(opacity, blur, (dx,dy)) or None."""
    w, h = size
    pil = to_pil(img).resize((w, h), Image.LANCZOS).convert('RGBA')
    if border or border_bottom:
        bb = border if border_bottom is None else border_bottom
        card = Image.new('RGBA', (w + 2 * border, h + border + bb), color255(border_color) + (255,))
        card.paste(pil, (border, border))
        pil = card
    if radius:
        m = Image.fromarray((rounded_mask(pil.width, pil.height, radius) * 255).astype(np.uint8))
        pil.putalpha(m)
    if rotate_:
        pil = pil.rotate(rotate_, resample=Image.BICUBIC, expand=True)
    cx, cy = center or (W / 2, H / 2)
    x0, y0 = int(cx - pil.width / 2), int(cy - pil.height / 2)
    out = to_pil(canvas_img).convert('RGBA')
    if shadow:
        op, sb, (dx, dy) = shadow
        sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
        a = pil.split()[3].point(lambda v: int(v * op))
        sh.paste(Image.new('RGBA', pil.size, (0, 0, 0, 255)), (x0 + dx, y0 + dy), a)
        sh = sh.filter(ImageFilter.GaussianBlur(sb))
        out = Image.alpha_composite(out, sh)
    layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    layer.paste(pil, (x0, y0), pil)
    out = Image.alpha_composite(out, layer)
    return from_pil(out)


def border(img, px=24, color_='#ffffff', inner=0, inner_color='#6B1F2E', inner_gap=8):
    """Draw a border over the image (keeps size). inner: thin inner line width."""
    pil = to_pil(img)
    d = ImageDraw.Draw(pil)
    for i in range(px):
        d.rectangle((i, i, W - 1 - i, H - 1 - i), outline=color255(color_))
    if inner:
        g = px + inner_gap
        for i in range(inner):
            d.rectangle((g + i, g + i, W - 1 - g - i, H - 1 - g - i), outline=color255(inner_color))
    return from_pil(pil)


def inset(img, px=60, color_=CREAM, texture=None):
    """Shrink the photo inside a coloured mat of `px` pixels (keeps canvas size)."""
    c = canvas(color_, texture)
    small = resize(img, W - 2 * px, H - 2 * px)
    c[px:H - px, px:W - px] = small
    return c


_FONT_FILES = {
    'playfair': ('PlayfairDisplay[wght].ttf', 'Regular'), 'playfair-bold': ('PlayfairDisplay[wght].ttf', 'Bold'),
    'playfair-black': ('PlayfairDisplay[wght].ttf', 'Black'), 'playfair-italic': ('PlayfairDisplay-Italic[wght].ttf', 'Italic'),
    'playfair-bolditalic': ('PlayfairDisplay-Italic[wght].ttf', 'Bold Italic'),
    'lato': ('Lato-Regular.ttf', None), 'lato-bold': ('Lato-Bold.ttf', None), 'lato-italic': ('Lato-Italic.ttf', None), 'lato-light': ('Lato-Light.ttf', None),
    'cormorant': ('CormorantGaramond[wght].ttf', 'Medium'), 'cormorant-bold': ('CormorantGaramond[wght].ttf', 'Bold'),
    'cormorant-italic': ('CormorantGaramond-Italic[wght].ttf', 'Medium Italic'), 'cormorant-light': ('CormorantGaramond[wght].ttf', 'Light'),
}


def font(name='playfair', size=48):
    """ImageFont: playfair, playfair-bold, playfair-black, playfair-italic, playfair-bolditalic,
    lato, lato-bold, lato-italic, lato-light, cormorant, cormorant-bold, cormorant-italic, cormorant-light."""
    fn, var = _FONT_FILES[name]
    f = ImageFont.truetype(os.path.join(FONT_DIR, fn), size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            try:
                names = [n.decode() if isinstance(n, bytes) else n for n in f.get_variation_names()]
                for cand in (var, var.replace(' Italic', ''), 'Regular', 'Italic'):
                    if cand in names:
                        f.set_variation_by_name(cand); break
            except Exception:
                pass
    return f


def draw_text(img, text, xy, font_, color_='#2E1A1F', anchor='la', tracking=0.0, opacity=1.0, rotate_=0.0, shadow=None):
    """Draw text onto an image (returns a new image). anchor: PIL anchor ('la' left-top, 'mm' centre, 'ra' right-top, 'ls' left-baseline ...).
    tracking: extra letter spacing in px. shadow: (dx, dy, blur, colour, opacity)."""
    base_pil = to_pil(img).convert('RGBA')
    layer = Image.new('RGBA', base_pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fill = color255(color_) + (int(255 * opacity),)
    x, y = xy
    if tracking:
        widths = [font_.getlength(ch) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        h_anchor = anchor[0]
        start = x - (total / 2 if h_anchor == 'm' else total if h_anchor == 'r' else 0)
        cx = start
        for ch, wch in zip(text, widths):
            d.text((cx, y), ch, font=font_, fill=fill, anchor='l' + anchor[1])
            cx += wch + tracking
    else:
        d.text((x, y), text, font=font_, fill=fill, anchor=anchor)
    if rotate_:
        layer = layer.rotate(rotate_, resample=Image.BICUBIC, center=(x, y))
    if shadow:
        dx, dy, sb, scol, sop = shadow
        sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
        a = layer.split()[3].point(lambda v: int(v * sop))
        sh.paste(Image.new('RGBA', layer.size, color255(scol) + (255,)), (dx, dy), a)
        sh = sh.filter(ImageFilter.GaussianBlur(sb))
        base_pil = Image.alpha_composite(base_pil, sh)
    return from_pil(Image.alpha_composite(base_pil, layer))


def text_width(text, font_, tracking=0.0):
    return sum(font_.getlength(ch) for ch in text) + tracking * (len(text) - 1)


def draw_shapes(img, fn):
    """Helper: fn(ImageDraw) draws onto an RGBA layer over the image; returns new image."""
    base_pil = to_pil(img).convert('RGBA')
    layer = Image.new('RGBA', base_pil.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    return from_pil(Image.alpha_composite(base_pil, layer))


def rgba(c, alpha=1.0):
    return color255(c) + (int(255 * alpha),)


def face_center():
    m = meta(); return tuple(m['face_center'])


def face_box():
    return tuple(meta()['face_box'])
