"""Asl suratlarni EDSR (x2) bilan kattalashtiradi — 2x eksport uchun keskinlik.

Foydalanish: python3 upscale.py <kirish.jpg> <chiqish.png>
"""
import sys, time, cv2

src, dst = sys.argv[1], sys.argv[2]
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel("assets/src/EDSR_x2.pb")
sr.setModel("edsr", 2)
img = cv2.imread(src, cv2.IMREAD_COLOR)
t = time.time()
out = sr.upsample(img)
cv2.imwrite(dst, out, [cv2.IMWRITE_PNG_COMPRESSION, 3])
print(dst, img.shape[1::-1], "->", out.shape[1::-1], f"{time.time()-t:.0f}s")
