# DIVA Women Networking Club — event post campaign

Nine finished social posts for the DIVA Club's **16-sentabr** meetup: three
design directions, each rendered at three ratios. This file explains which
PNG to post where, what the event copy says, how to reproduce or edit the
posts, and what everything else in this folder is for.

Two extra images live in `out/` alongside the nine posts, purely for
reviewing the set — they are **not** posts themselves:

- `out/PREVIEW-by-direction.png` — the three ratios of each direction side
  by side, one section per direction.
- `out/PREVIEW-all-nine.png` — all nine posts in one labelled grid (rows =
  direction, columns = ratio).

## 1. The nine files

All nine live in `out/`, already sized and exported — nothing to crop or
resize before posting.

| File | Direction | Ratio | Pixel size | Where to use |
|---|---|---|---|---|
| `out/diva-A-romantik-klassik-4-5.png` | A — Modern maroon | 4:5 | 1080 × 1350 | Instagram feed post |
| `out/diva-A-romantik-klassik-9-16.png` | A — Modern maroon | 9:16 | 1080 × 1920 | Stories / Reels cover, Telegram |
| `out/diva-A-romantik-klassik-1-1.png` | A — Modern maroon | 1:1 | 1080 × 1080 | Profile grid, Facebook, LinkedIn |
| `out/diva-B-ivory-blush-4-5.png` | B — Ivory & blush | 4:5 | 1080 × 1350 | Instagram feed post |
| `out/diva-B-ivory-blush-9-16.png` | B — Ivory & blush | 9:16 | 1080 × 1920 | Stories / Reels cover, Telegram |
| `out/diva-B-ivory-blush-1-1.png` | B — Ivory & blush | 1:1 | 1080 × 1080 | Profile grid, Facebook, LinkedIn |
| `out/diva-C-editorial-4-5.png` | C — Editorial | 4:5 | 1080 × 1350 | Instagram feed post |
| `out/diva-C-editorial-9-16.png` | C — Editorial | 9:16 | 1080 × 1920 | Stories / Reels cover, Telegram |
| `out/diva-C-editorial-1-1.png` | C — Editorial | 1:1 | 1080 × 1080 | Profile grid, Facebook, LinkedIn |

You don't have to use all three directions — pick the one look that fits
best and post that set of three, or mix directions across platforms. Each
direction is a self-contained set; don't mix a 4:5 from one direction with a
9:16 from another in the same post/story.

## 2. Event details (as printed on the posts)

This is the client-supplied text. It appears, word for word, on every post
(the guest-speaker line is re-ordered into a caption stack, and long lines
break across two lines — no words are added, changed, or removed):

```
Diva klubi uchrashuvi
Mohinur Abdullayeva bilan
Mehmon spiker: psixolog, vrach psixoterapevt Sarvinoz Alisherovna

Uchrashuv mavzusi:
Shukronalik hissi. 1 ta katta maqsad uchun ongni tayyorlash
16-sentabr 11:00
Toshkent sh
```

There is deliberately **no** address, venue name, phone number, @handle,
website, price, "ro'yxatdan o'ting" call-to-action, or year on the date —
none of that was supplied by the client, so none of it is on the posts. If
any of that gets added later, it has to come from the client first.

## 3. The three directions

- **A — Modern maroon**: deep maroon ground, both women placed large and
  frameless — cutouts or edge-free fades — with a clean, contemporary type
  block. Composed and confident rather than ceremonial.
- **B — Ivory & blush**: the light direction. Cream/blush ground, maroon
  ink, large frameless portraits cropped by the canvas edge, lots of air.
  Modern beauty-brand calm.
- **C — Editorial**: the dramatic direction. Photography-led and asymmetric,
  magazine-cover energy, oversized display type, a maroon wash over a
  full-bleed hero portrait, the guest standing free.

Full design rationale and the client's revision notes are in `BRIEF.md`.

## 4. Re-rendering after an edit

One command rebuilds the PNGs in `out/`:

```
./build.sh a            # variant A, all three ratios
./build.sh a:4x5         # just that one file
./build.sh all           # every variant, every ratio
```

It spins up a throwaway local server, renders each `variant-*.html` in a
real browser at 1080px-equivalent size (2× supersampled), then downsamples
to the final files with LANCZOS resampling. Nothing is uploaded anywhere —
it all runs on this machine.

What each source file does:

| File | Role |
|---|---|
| `variant-a.html`, `variant-b.html`, `variant-c.html` | The three design directions — one standalone HTML page each, with that direction's own layout, styling, and copy. |
| `base.css` | Shared design tokens (palette, fonts, the exact pixel size per ratio) and small reusable pieces (photo-crop helpers, hairline rules, grain texture). Shared by all three variants — **don't edit it** to change one post, edit the variant instead. |
| `lib.js` | Shared runtime. Reads `?r=9x16|4x5|1x1` off the URL and applies it to the page, then signals once fonts and images have actually finished loading, so the renderer never screenshots a half-painted page. |
| `render.cjs` | Playwright script: opens each `variant:ratio` pair in a headless browser and screenshots the post into `out/raw/` at 2× resolution. |
| `finalize.py` | Downsamples the 2× renders in `out/raw/` to the final 1080px-wide files in `out/`. |
| `sheet.py` | Small contact-sheet helper — put a list of PNGs side by side with labels for a quick visual check. Used to help build the two `PREVIEW-*.png` files above. |
| `build.sh` | The one command to run — starts the local server, calls `render.cjs` then `finalize.py`, and shuts the server down when it's done. |

`out/raw/` holds the intermediate 2× screenshots; it's overwritten every
render and never needs to be posted anywhere. A `scratch/` folder and a
couple of one-off helper scripts (`preview.sh`, `preview.cjs`) are the
designer's own working files from building this campaign — not part of the
hand-off, safe to ignore.

## 5. Where the assets live

- `assets/` — the club logo in several colourways (`logo*.png`) and the two
  source photographs, `mohinur.jpg` and `sarvinoz.jpg`.
- `assets/cutout/` — the same two women with the studio background removed
  (transparent PNG, real alpha edge) — what the "frameless cutout" look in
  directions A and C is built from. `INDEX-cutout.md` has the measured crop
  boxes and placement math.
- `assets/derived/` — other treatments of the two photos (soft-edge fades,
  a maroon duotone, a warm full-colour grade) — see `INDEX-photos.md`.
- `assets/ground/` — reusable background CSS: the maroon and cream/blush
  grounds, plus the grain and light-bloom textures that keep flat colour
  from banding — see `INDEX-ground.md`.
- `assets/orn/` — the small accent marks (SVGs used as CSS masks, so they
  take any brand colour) — see the three `INDEX-*.md` files inside for what
  each one is and how sparingly the brief wants them used.
- `fonts/` — the four typefaces as self-hosted `.woff2` files. `fonts.css`
  (at the project root) declares the `@font-face` rules that load them.

## 6. Brand basics

- **Maroon `#93061F`** is the anchor colour, sampled directly from the
  official logo (`assets/logo.png`).
- Full palette (tokens live in `base.css`):

  | | | |
  |---|---|---|
  | `--maroon` `#93061F` | `--maroon-rich` `#7A0519` | `--maroon-deep` `#5A0413` |
  | `--maroon-ink` `#34020C` | `--cream` `#FBF4EA` | `--ivory` `#FFFDF8` |
  | `--blush` `#F4E3DD` | `--blush-deep` `#E8CDC6` | `--rose` `#D9A8A4` |
  | `--gold` `#C9A25B` | `--gold-soft` `#E3CB99` | `--gold-deep` `#A8813C` |

  Gold is an accent (thin and precious, never a thick slab); cream and
  blush carry the romance. No colours outside this family — no purple, no
  teal, no black text.
- **Four self-hosted fonts, and only these four**: Playfair Display
  (headlines/display), Cormorant Garamond (serif body/subheads), Marcellus
  (a second display/roman face), Jost (sans — small-caps labels only, never
  a headline).

## 7. If you want to change the text

Each variant's copy is plain text sitting directly in its HTML — there's no
separate data file. Open the variant and search for the Uzbek text (e.g.
`Diva klubi` or `Shukronalik`) to find it:

- `variant-a.html` — title (`.title`), host line (`.host`), guest tag/name
  (`.tag` / `.nm`), topic (`.topic`), date (`.d`), city (`.city`).
- `variant-b.html` — title (`.title`), host (`.host`), topic (`.topic-t`),
  guest label/name (`.lbl` / `.gname`), date (`.w-date`), place (`.w-place`).
- `variant-c.html` — title (`.title`), host (`.with`), topic
  (`.theme-text`), label/name (`.label` / `.name`), date (`.date`), city
  (`.city`).

After editing, re-render that variant (`./build.sh a`, `b`, or `c`) and look
at the new PNG before sending it anywhere. Keep to the wording rules in
`BRIEF.md` §1 (no invented address/handle/CTA/year, exact spelling of both
names) and the quality bar in §6 (nothing clipped, hierarchy still reads at
a glance, text still legible) — a text edit can just as easily break those
as a design change can.
