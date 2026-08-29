"""Normalize the two speaker photos into one matched portrait system.

The two source frames were shot in different studios (a white block wall vs. a
warm orange set), at different distances and with different framing. For them
to read as one team on the poster they have to share three things: the same
aspect ratio, the same head size and the same eye line. This script resamples
each source around its face so all three match, and writes 3:4 panels.

The face metrics below were measured off the source frames rather than
detected: OpenCV's frontal cascade mis-locates the second subject (it latches
onto the jacket/hands area), and a wrong centre shifts the whole crop.
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "assets", "speakers")
UPLOADS = "/root/.claude/uploads/2e71a54d-199c-5807-8781-d8e4963aad1b"

# Panel geometry: 3:4 portrait at retina size, so the layouts can crop into it.
PANEL_W, PANEL_H = 1200, 1600
# Face width as a fraction of panel width -- tight enough that the experts read
# as close and clear, loose enough to keep the shoulders in frame.
FACE_RATIO = 0.38
# Vertical position of the face centre inside the panel: a shared eye line.
FACE_Y = 0.33

SOURCES = [
    {
        "key": "zilola",
        "src": os.path.join(UPLOADS, "0d4b561b-image.jpg"),
        # cheek-to-cheek width, and the centre of the face, in source pixels
        "face": {"cx": 580.0, "cy": 350.0, "w": 250.0},
    },
    {
        "key": "javohir",
        "src": os.path.join(UPLOADS, "3d68276a-image.jpg"),
        # 365 rather than his measured 350: detected face boxes came back 5.7%
        # wider than Zilola's at equal scale, and the cap adds silhouette on
        # top of that, so he reads as the bigger head unless he is pulled back.
        "face": {"cx": 872.0, "cy": 430.0, "w": 365.0},
    },
]


def build_panel(src, face):
    """Crop and scale so every panel shares head size and eye line."""
    im = Image.open(src).convert("RGB")

    scale = (PANEL_W * FACE_RATIO) / face["w"]
    crop_w, crop_h = PANEL_W / scale, PANEL_H / scale
    if crop_w > im.width or crop_h > im.height:
        # Not enough frame at the requested head size: zoom in rather than
        # padding, so no panel ever gets a dead border.
        fit = min(im.width / crop_w, im.height / crop_h)
        crop_w, crop_h = crop_w * fit, crop_h * fit

    left = face["cx"] - crop_w / 2.0
    top = face["cy"] - crop_h * FACE_Y
    left = max(0.0, min(left, im.width - crop_w))
    top = max(0.0, min(top, im.height - crop_h))

    box = (int(round(left)), int(round(top)),
           int(round(left + crop_w)), int(round(top + crop_h)))
    panel = im.crop(box).resize((PANEL_W, PANEL_H), Image.LANCZOS)
    # Where the face centre actually landed. Clamping above can quietly pull it
    # away from FACE_Y when a source has too little headroom, which breaks the
    # shared eye line without breaking the script -- so report it and check it.
    realized_y = (face["cy"] - top) / crop_h
    return panel, box, realized_y


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    report = {}
    for entry in SOURCES:
        panel, box, realized_y = build_panel(entry["src"], entry["face"])
        out = os.path.join(OUT_DIR, "%s-panel.jpg" % entry["key"])
        panel.save(out, "JPEG", quality=94, subsampling=0)
        report[entry["key"]] = {
            "crop_box": box,
            "size": panel.size,
            "face_y": round(realized_y, 4),
        }
    json.dump(report, sys.stdout, indent=2)
    print()

    eye_lines = [r["face_y"] for r in report.values()]
    if max(eye_lines) - min(eye_lines) > 0.005:
        raise SystemExit(
            "eye lines drifted apart (%s) -- a crop got clamped; lower FACE_Y "
            "or FACE_RATIO until both land on %.3f" % (eye_lines, FACE_Y)
        )


if __name__ == "__main__":
    main()
