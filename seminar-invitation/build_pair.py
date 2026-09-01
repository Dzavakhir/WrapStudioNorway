"""Ikki spikerdan bitta jamoa surati yasaydi — ramkasiz, fonsiz.

- boshlar bir xil kenglikka keltiriladi;
- ko'z chizig'i bo'yicha tekislanadi;
- boshlar markazlari HEAD_GAP masofada turadi — yelkalar tegib, ikkalasi
  bitta guruh suratidek ko'rinadi;
- gorizontal bo'yicha kontent chegarasiga qirqiladi (erkakning tirsagi to'liq
  saqlanadi — kvadrat postda uning qo'li tabiiy tugaydi, storisda kadrdan
  chiqib ketadi);
- pastdan tik kesiladi (xiralashish yo'q), qo'llar qizil lenta orqasida qoladi.

Foydalanish: python3 build_pair.py [erkak.png ayol.png]
Ko'z chizig'i va bosh kengligi asl (x1) rasm piksellarida berilgan; kirish
rasmi kattaroq bo'lsa (masalan x2 apskeyl) masshtab avtomatik hisoblanadi.
"""
import sys
from PIL import Image
import numpy as np

# (fayl, ko'z chizig'i y, bosh kengligi, asl rasm kengligi)
SPEAKERS = [
    ("assets/speaker1-graded.png", 409, 453, 1706),
    ("assets/speaker2-graded.png", 323, 332, 1178),
]
if len(sys.argv) == 3:
    SPEAKERS = [(sys.argv[1],) + SPEAKERS[0][1:], (sys.argv[2],) + SPEAKERS[1][1:]]

HEAD_W = 600        # umumiy bosh kengligi (2x eksport uchun yetarli zaxira)
EYE_Y = 660         # umumiy ko'z chizig'i
HEAD_GAP = 904      # boshlar markazlari orasidagi masofa
BOTTOM = 2280       # pastki kesim
PAD = 24


def head_span(alpha, eye):
    xs = np.flatnonzero(alpha[eye] > 40)
    return int(xs[0]), int(xs[-1])


layers = []
for path, eye, head_w, ref_w in SPEAKERS:
    im = Image.open(path).convert("RGBA")
    k = im.width / ref_w                       # kirish rasmi asldan qancha katta
    s = HEAD_W / (head_w * k)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    eye_y = round(eye * k * s)
    l, r = head_span(np.array(im.split()[-1]), eye_y)
    layers.append({"im": im, "top": EYE_Y - eye_y, "head": (l + r) / 2})

# boshlarni HEAD_GAP qadam bilan joylashtiramiz; keng ish maydoni, keyin qirqamiz
W = 4000
canvas = Image.new("RGBA", (W, BOTTOM), (0, 0, 0, 0))
x0 = W // 2 - HEAD_GAP // 2
for i, layer in enumerate(layers):
    cx = x0 + i * HEAD_GAP
    canvas.alpha_composite(layer["im"], (round(cx - layer["head"]), layer["top"]))

a = np.array(canvas.split()[-1]) > 40
cols = np.flatnonzero(a.any(axis=0)); rows = np.flatnonzero(a.any(axis=1))
canvas = canvas.crop((max(cols[0] - PAD, 0), max(rows[0] - 8, 0), min(cols[-1] + PAD, W), BOTTOM))
canvas.save("assets/speakers-pair.png")
print(canvas.size, round(canvas.width / canvas.height, 3))
