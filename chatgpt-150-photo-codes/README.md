# 150 ChatGPT photo codes — PDF guide

A romantic-classic (burgundy & cream) PDF guide with 150 slash-codes (`/golden_hour`, `/polaroid`, …)
that readers send to ChatGPT to edit their photos. Every code is illustrated with the result applied to
the guide's model photo.

* `source/` — base portrait, crop, landmark metadata and segmentation masks (`tools/prepare.py`).
* `codes.json` — the 150 codes: Uzbek title/description, English prompt, designer hints (`tools/codes_src.py`).
* `effects/` — the shared helper library (`lib.py`) and 30 designer groups `g01..g30.py` (5 codes each).
* `render.py` — renders all codes to `renders/`.
* `book/` — HTML/CSS template, fonts and the Playwright build script that prints `dist/*.pdf`.
