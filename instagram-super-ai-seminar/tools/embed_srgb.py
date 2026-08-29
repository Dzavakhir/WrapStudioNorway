"""Embed an sRGB ICC profile in the exported PNGs.

Playwright screenshots carry no colour profile. Untagged, Instagram and most
phone galleries guess -- and a poster whose whole identity is one specific
clay (#d97757) against near-black cannot afford a guess.
"""

import glob
import os

from PIL import Image, ImageCms

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")


def main():
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    for path in sorted(glob.glob(os.path.join(OUT, "*.png"))):
        im = Image.open(path)
        im.save(path, "PNG", icc_profile=profile, optimize=True)
        print("%s  %s  sRGB tagged" % (os.path.basename(path), "x".join(map(str, im.size))))


if __name__ == "__main__":
    main()
