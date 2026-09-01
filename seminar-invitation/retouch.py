"""Kepkadagi begona brend yozuvini olib tashlaydi.

Usul: yozuvning butun konturi (qavariq qobiq) bitta yaxlit maska sifatida
olinadi — harflar orasidagi soyalar qolib ketmasin; NS-inpaint fon
gradientini to'ldiradi; keyin mayin donador shovqin bilan mato bo'rtiqligi
qaytariladi va maska cheti asl rasm bilan yumshoq birlashtiriladi.

Foydalanish: python3 retouch.py <kirish.png> <chiqish.png>
Koordinatalar asl (1706 px) rasm uchun; kirish kattaroq bo'lsa masshtablanadi.
"""
import sys
import numpy as np, cv2
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
REF_W = 1706
BOX = (690, 74, 1010, 195)     # yozuv atrofidagi to'rtburchak, asl piksellarda
DARK = 112

im = Image.open(src).convert("RGBA")
k = im.width / REF_W
rgba = np.array(im); rgb, a = rgba[..., :3], rgba[..., 3]
bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

x0, y0, x1, y1 = (round(v * k) for v in BOX)
lum = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
pts = np.column_stack(np.where((lum[y0:y1, x0:x1] < DARK) & (a[y0:y1, x0:x1] > 200)))[:, ::-1] + (x0, y0)
hull = cv2.convexHull(pts.astype(np.int32))
mask = np.zeros(lum.shape, np.uint8)
cv2.fillConvexPoly(mask, hull, 255)
mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * round(7 * k) + 1,) * 2))
mask[a < 200] = 0                                     # kepka chetidan tashqariga chiqmasin
print("mask px:", int((mask > 0).sum()))

# 1) silliq to'ldirish
base = cv2.inpaint(bgr, mask, round(9 * k), cv2.INPAINT_NS)

# 2) to'qima: mayin donador shovqin (mato bo'rtiqligi) + maska chetini yumshoq birlashtirish
rng = np.random.default_rng(11)
grain = rng.normal(0, 2.6, base.shape).astype(np.float32)
grain = cv2.GaussianBlur(grain, (0, 0), 0.8 * k)
soft = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), 4 * k)[..., None]
filled = np.clip(base.astype(np.float32) + grain, 0, 255)
out = (bgr.astype(np.float32) * (1 - soft) + filled * soft).astype(np.uint8)

rgba[..., :3] = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
Image.fromarray(rgba).save(dst)

chk = Image.fromarray(rgba).crop((x0 - 80, y0 - 30, x1 + 80, y1 + 90))
bg = Image.new("RGB", chk.size, (255, 255, 255)); bg.paste(chk, (0, 0), chk)
bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save(
    "/tmp/claude-0/-home-user-WrapStudioNorway/1c2c31bd-4db5-55a3-9055-387f67183f1f/scratchpad/cap-after.png")
print(dst)
