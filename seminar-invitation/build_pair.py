"""Ikki spikerdan bitta jamoa surati yasaydi — ramkasiz, fonsiz.

- boshlar bir xil kenglikka keltiriladi;
- ko'z chizig'i bo'yicha tekislanadi;
- boshlar orasi belgilangan masofada turadi, ya'ni yelkalar tegib turadi;
- chetlari va pastki qismi tik kesiladi (xiralashish yo'q) — maket chetidan
  yoki pastki lentadan chiqib turadi.
"""
from PIL import Image
import numpy as np

# (fayl, ko'z chizig'i y, bosh kengligi) — asl rasm piksellarida o'lchangan
SPEAKERS = [
    ("assets/speaker1.png", 409, 453),
    ("assets/speaker2.png", 323, 332),
]
HEAD_W = 300        # umumiy bosh kengligi
EYE_Y = 330         # umumiy ko'z chizig'i
HEAD_GAP = 452      # boshlar markazlari orasidagi masofa
SIDE = 404          # chetki bosh markazidan tashqariga qoladigan kenglik
BOTTOM = 1140       # pastki kesim


def head_span(im, eye):
    """Ko'z chizig'idagi alfa chegarasi — bosh chap/o'ng qirrasi."""
    xs = np.flatnonzero(np.array(im.split()[-1])[eye] > 40)
    return int(xs[0]), int(xs[-1])


layers = []
for path, eye, head_w in SPEAKERS:
    im = Image.open(path).convert("RGBA")
    s = HEAD_W / head_w
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    eye_y = round(eye * s)
    l, r = head_span(im, eye_y)
    layers.append({"im": im, "top": EYE_Y - eye_y, "head": (l + r) / 2})

# boshlarni HEAD_GAP qadam bilan joylashtiramiz
centers = [SIDE + i * HEAD_GAP for i in range(len(layers))]
canvas = Image.new("RGBA", (SIDE * 2 + HEAD_GAP * (len(layers) - 1), BOTTOM), (0, 0, 0, 0))
for layer, cx in zip(layers, centers):
    canvas.alpha_composite(layer["im"], (round(cx - layer["head"]), layer["top"]))

# boshlar tepasidagi bo'sh joyni kesib tashlaymiz — maketda ortiqcha oraliq qolmasin
rows = np.flatnonzero((np.array(canvas.split()[-1]) > 40).any(axis=1))
canvas = canvas.crop((0, max(int(rows[0]) - 8, 0), canvas.width, BOTTOM))

canvas.save("assets/speakers-pair.png")
print(canvas.size, round(canvas.width / canvas.height, 3))
