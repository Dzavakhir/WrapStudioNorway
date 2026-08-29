"""Ikki spiker rasmidan bitta "jamoa" kompozitsiyasi yasaydi.

- boshlar bir xil o'lchamga keltiriladi;
- ko'z chizig'i bo'yicha tekislanadi;
- yelkalar orasidagi bo'shliq eng keng nuqta bo'yicha hisoblanib, yonma-yon qo'yiladi;
- pastki qirrasi shaffoflikka silliq o'tadi.
"""
from PIL import Image
import numpy as np

# (fayl, ko'z chizig'i y, bosh kengligi) — asl rasm piksellarida o'lchangan
SPEAKERS = [
    ("assets/speaker1.png", 409, 453),
    ("assets/speaker2.png", 323, 332),
]
HEAD_W = 300     # umumiy bosh kengligi
EYE_Y = 330      # kompozitsiyadagi umumiy ko'z chizig'i
GAP = 34         # figuralar orasidagi eng kichik bo'shliq
BOTTOM = 1150    # pastki kesim
FADE = 80        # pastki silliq o'tish balandligi
PAD = 30

layers = []
for path, eye, head_w in SPEAKERS:
    im = Image.open(path).convert("RGBA")
    s = HEAD_W / head_w
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    layers.append((im, EYE_Y - round(eye * s)))


def columns(im, top):
    """Har bir qator uchun (chap, o'ng) chegara; bo'sh qatorlar uchun None."""
    a = np.array(im.split()[-1]) > 40
    rows = {}
    for y in range(a.shape[0]):
        xs = np.flatnonzero(a[y])
        if xs.size:
            rows[y + top] = (int(xs[0]), int(xs[-1]))
    return rows


placed = [(layers[0][0], 0, layers[0][1])]
prev = columns(layers[0][0], layers[0][1])
for im, top in layers[1:]:
    cur = columns(im, top)
    shift = max(
        (prev[y][1] - cur[y][0] for y in cur.keys() & prev.keys() if y < BOTTOM - FADE - 90),
        default=0,
    )
    x = shift + GAP
    placed.append((im, x, top))
    prev = {y: (l + x, r + x) for y, (l, r) in cur.items()}

left = min(x + min(l for l, _ in columns(im, top).values()) for im, x, top in placed)
right = max(x + max(r for _, r in columns(im, top).values()) for im, x, top in placed)

canvas = Image.new("RGBA", (right - left + PAD * 2, BOTTOM), (0, 0, 0, 0))
for im, x, top in placed:
    canvas.alpha_composite(im, (x - left + PAD, top))

# pastki qirrani shaffoflikka o'tkazish
alpha = np.array(canvas.split()[-1]).astype(np.float32)
ramp = np.linspace(1.0, 0.0, FADE) ** 1.6
alpha[BOTTOM - FADE:] *= ramp[:, None]
canvas.putalpha(Image.fromarray(alpha.astype(np.uint8)))
canvas.save("assets/speakers-pair.png")
print(canvas.size)
