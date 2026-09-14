#!/usr/bin/env python3
"""Contact sheet: tile finished posts side by side for review.
   python3 sheet.py out/a.png out/b.png ... -o scratch/sheet.png [-h 900]"""
import sys, os
from PIL import Image, ImageDraw

args = sys.argv[1:]
out = "scratch/sheet.png"; maxh = 820
if "-o" in args: i = args.index("-o"); out = args[i+1]; del args[i:i+2]
if "-h" in args: i = args.index("-h"); maxh = int(args[i+1]); del args[i:i+2]
ims, labels = [], []
for p in args:
    im = Image.open(p).convert("RGB")
    s = maxh / im.height
    ims.append(im.resize((max(1,int(im.width*s)), maxh), Image.LANCZOS))
    labels.append(os.path.basename(p))
pad, top = 18, 26
W = sum(i.width for i in ims) + pad*(len(ims)+1)
H = maxh + top + pad
sheet = Image.new("RGB", (W, H), (28, 28, 30))
d = ImageDraw.Draw(sheet)
x = pad
for im, lb in zip(ims, labels):
    sheet.paste(im, (x, top))
    d.text((x+2, 8), lb, fill=(190, 190, 195))
    x += im.width + pad
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
sheet.save(out)
print(f"{out}  {sheet.size[0]}x{sheet.size[1]}")
