"""Spiker rasmlarini yagona uslubga keltirish uchun ranglar bilan ishlash."""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# to'q fon uchun duoton ramp: soya -> o'rta -> yorug'lik
SHADOW = (52, 10, 16)
MID = (150, 48, 30)


def ramp_lut(high):
    lut = np.zeros((256, 3), dtype=np.float32)
    for i in range(256):
        t = i / 255.0
        if t < 0.5:
            k = t / 0.5
            c = [SHADOW[j] + (MID[j] - SHADOW[j]) * k for j in range(3)]
        else:
            k = (t - 0.5) / 0.5
            c = [MID[j] + (high[j] - MID[j]) * k for j in range(3)]
        lut[i] = c
    return lut


def clean_alpha(im, res):
    """Fondagi juda past alfa qiymatlarini nolga tushiradi (hoshiya yo'qoladi)."""
    al = np.asarray(im.getchannel('A')).astype(np.float32)
    lo, hi = 26.0, 232.0
    al = ((al - lo) * (255.0 / (hi - lo))).clip(0, 255)
    res.putalpha(Image.fromarray(al.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    return res


def apply_grade(im, mix, contrast, brightness, high, saturation=0.72):
    """To'q burgundi duoton (qora-qizil fon uchun)."""
    rgb = im.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    a = np.asarray(rgb).astype(np.float32)
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).clip(0, 255).astype(np.uint8)
    duo = ramp_lut(high)[lum]
    out = (a * (1 - mix) + duo * mix).clip(0, 255).astype(np.uint8)
    return clean_alpha(im, Image.fromarray(out).convert('RGBA'))


def apply_light_grade(im, gains=(1.0, 1.0, 1.0), brightness=1.0, contrast=1.0,
                      saturation=1.0, lift=0.0):
    """Oq fon uchun: kanal balansi bilan ikkala rasmning rang harorati tenglashtiriladi."""
    rgb = im.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    a = np.asarray(rgb).astype(np.float32)
    a *= np.array(gains, dtype=np.float32)
    if lift:
        a = a + (255.0 - a) * lift          # soyalarni yumshatish
    out = a.clip(0, 255).astype(np.uint8)
    return clean_alpha(im, Image.fromarray(out).convert('RGBA'))
