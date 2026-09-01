"""Spiker suratidan fonni olib tashlaydi (rembg, isnet-general-use + alpha matting).

Foydalanish: python3 cutout.py <kirish> <chiqish.png>
Yuqori aniqlikdagi (x2) kirish rasm bilan qirralar ancha toza chiqadi.
"""
import sys
from PIL import Image
from rembg import remove, new_session

src, dst = sys.argv[1], sys.argv[2]
session = new_session("isnet-general-use")
im = Image.open(src).convert("RGB")
out = remove(
    im, session=session,
    alpha_matting=True,
    alpha_matting_foreground_threshold=250,
    alpha_matting_background_threshold=15,
    alpha_matting_erode_size=12,
)
out.save(dst)
print(dst, out.size)
