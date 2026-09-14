#!/usr/bin/env python3
"""Downscale the 2x renders to final 1080px-wide social assets (LANCZOS)."""
import sys, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080)}
NAMES = {"a": "A-romantik-klassik", "b": "B-ivory-blush", "c": "C-editorial"}

def main(targets):
    for t in targets:
        variant, ratio = t.split(":")
        src = os.path.join(HERE, "out", "raw", f"variant-{variant}-{ratio}.png")
        if not os.path.exists(src):
            print(f"  ! missing render: {src}")
            continue
        im = Image.open(src).convert("RGB")
        im = im.resize(TARGET[ratio], Image.LANCZOS)
        label = NAMES.get(variant, variant)
        dst = os.path.join(HERE, "out", f"diva-{label}-{ratio.replace('x', '-')}.png")
        im.save(dst, optimize=True)
        kb = os.path.getsize(dst) // 1024
        print(f"  final  {os.path.relpath(dst, HERE)}  {im.size[0]}x{im.size[1]}  {kb}KB")

if __name__ == "__main__":
    main(sys.argv[1:])
