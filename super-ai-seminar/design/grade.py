"""Ikkala spiker rasmini yagona (jamoa) uslubga keltirish: iliq burgundi-duoton grading."""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# duoton ramp: soya -> o'rta -> yorug'lik
SHADOW = (52, 10, 16)
MID = (150, 48, 30)
HIGH = (245, 205, 176)


def ramp_lut():
    lut = np.zeros((256, 3), dtype=np.float32)
    for i in range(256):
        t = i / 255.0
        if t < 0.5:
            k = t / 0.5
            c = [SHADOW[j] + (MID[j] - SHADOW[j]) * k for j in range(3)]
        else:
            k = (t - 0.5) / 0.5
            c = [MID[j] + (HIGH[j] - MID[j]) * k for j in range(3)]
        lut[i] = c
    return lut


def grade(src, dst, mix=0.55, contrast=1.12, brightness=1.0, max_h=1600):
    im = Image.open(src)
    im = im.crop(im.getbbox())
    if im.height > max_h:
        im = im.resize((round(im.width * max_h / im.height), max_h), Image.LANCZOS)
    rgb = im.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(0.72)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    a = np.asarray(rgb).astype(np.float32)
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).clip(0, 255).astype(np.uint8)
    duo = ramp_lut()[lum]
    out = (a * (1 - mix) + duo * mix).clip(0, 255).astype(np.uint8)
    res = Image.fromarray(out).convert('RGBA')
    # alfa kanalini tozalash: fondagi juda past qiymatlar nol qilinadi (hoshiya yo'qoladi)
    al = np.asarray(im.getchannel('A')).astype(np.float32)
    lo, hi = 26.0, 232.0
    al = ((al - lo) * (255.0 / (hi - lo))).clip(0, 255)
    alpha = Image.fromarray(al.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    res.putalpha(alpha)
    res = res.crop(res.getbbox())
    res.save(dst)
    print(dst, res.size)


grade('assets/sp1_cut.png', 'assets/sp1_g.png', mix=0.55, contrast=1.10, brightness=1.02)
grade('assets/sp2_cut.png', 'assets/sp2_g.png', mix=0.58, contrast=1.12, brightness=0.94)
