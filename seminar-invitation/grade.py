#!/usr/bin/env python3
"""
grade.py - edge clean-up + colour/tonal matching for the two speaker cutouts.

Usage:
    python3 grade.py IN.png OUT.png --profile man|woman [options]
    python3 grade.py IN.png --analyse --profile man          # measurements only

The script is resolution independent: every spatial parameter that matters is
expressed in pixels relative to a ~1200-1700 px portrait, and the face / white
reference regions are located automatically (row-width profile of the alpha
mask + skin chroma), so it can be rerun on higher-resolution cutouts.

Pipeline (see the numbered steps in grade()):
  1. alpha hygiene      remove alpha islands < 40 px, fill pinholes < 40 px,
                        fade stray low-alpha wisps (alpha < 64, > 5 px from the
                        body), optional small gaussian to smooth blocky mattes
  2. decontamination    for 0 < alpha < 255 replace RGB with colour propagated
                        from the nearest fully opaque pixels (distance transform
                        indices, then a 1 px blur of the propagated colour so the
                        fill has no nearest-neighbour streaks). Blend weight is
                        1.0 for alpha <= 160, ramps to 0 at alpha 255, and also
                        fades to 0 between 4 and 8 px away from the opaque body
                        so wide, intentional fades (the man's table fade) are not
                        smeared. Alpha itself is untouched here.
  3. alpha erosion      optional 0.5-1 px sub-pixel erosion (min-filter blend)
  4. white balance      per-channel gain from a neutral reference (the man's
                        white T-shirt); off for the woman (her original wall
                        measured neutral, R/G 1.006, B/G 0.986)
  5. skin luminance     gamma on luminance so that the mean face-skin luminance
                        hits a shared target; RGB scaled by L'/L so hue and
                        chroma ratios of hijab / jacket / skin are preserved;
                        highlights above L 175 blend back to identity so whites
                        stay white
  6. skin contrast      gentle contrast around the skin mean so the face-region
                        luminance std approaches a shared target (capped +-12 %)
  7. micro-sharpen      optional unsharp mask on the opaque interior only

Only numpy / Pillow / scipy are required.
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

# ----------------------------------------------------------------------------
# Per-image profiles. Numbers are explained in the report / README; each one
# can be overridden on the command line.
# ----------------------------------------------------------------------------
PROFILES = {
    "man": dict(
        alpha_sigma=0.0,     # matte already smooth (1706 px, soft edge)
        erosion_px=0.0,      # edge pixels measured no warmer than body: no erosion
        wb="auto",           # neutralise warm cast on the white T-shirt
        wb_strength=1.0,     # full correction (skin R/G lands at 1.40, woman is 1.34)
        sharpen=(1.0, 0.35, 3),  # (radius px, amount, threshold) unsharp mask
    ),
    "woman": dict(
        alpha_sigma=1.2,     # smooth the blocky 1178 px matte (~8 px staircase steps)
        erosion_px=0.5,      # cream jacket edge is +4..6 L brighter than body
        wb="none",           # original wall is neutral -> nothing to fix
        wb_strength=0.0,
        sharpen=None,        # low-res source, do not amplify noise
    ),
}
# Shared targets so both portraits look lit by the same light.
TARGET_SKIN_L = 128.0    # mean face-skin luminance (man 108 / woman 148 before, midpoint)
TARGET_SKIN_STD = 32.0   # face-region luminance std (man 22.6 / woman 41.2 before, midpoint; capped +-12 %)
ISLAND_PX = 40           # alpha islands / pinholes smaller than this are removed


def lum(rgb):
    """Rec.709 luminance of an (..., 3) float array."""
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


# ----------------------------------------------------------------------------
# Region finders
# ----------------------------------------------------------------------------
def find_face(rgb, alpha):
    """Return a boolean mask of face skin (eroded core) and its bbox.

    Method: the row-width profile of the alpha mask separates head from
    shoulders (first row wider than 55 % of the widest row). Inside the head
    rows we take a YCbCr skin gate tightened with R-G >= 35 so that beige caps
    or cream fabric (R-G ~ 28) are rejected while skin (R-G ~ 45) passes.
    The largest connected blob is the face; it is eroded 8 px so that edges,
    eyebrows and the hairline do not bias the mean.
    """
    op = alpha >= 250
    fg = alpha > 0
    widths = fg.sum(1)
    rows = np.where(widths > 0)[0]
    y0 = rows.min()
    shoulder = y0 + int(np.argmax(widths[y0:] > 0.55 * widths.max()))
    ycc = np.asarray(Image.fromarray(rgb.astype(np.uint8)).convert("YCbCr")).astype(np.float32)
    cb, cr = ycc[..., 1], ycc[..., 2]
    skin = (cb >= 77) & (cb <= 127) & (cr >= 138) & (cr <= 173) & ((rgb[..., 0] - rgb[..., 1]) >= 35) & op
    skin[shoulder:] = False
    skin = ndi.binary_opening(skin, iterations=3)
    lab, n = ndi.label(skin)
    if n == 0:
        raise RuntimeError("no skin blob found")
    sizes = ndi.sum(skin, lab, range(1, n + 1))
    face = lab == (int(np.argmax(sizes)) + 1)
    core = ndi.binary_erosion(face, iterations=8)
    fy, fx = np.where(face)
    return core, (int(fx.min()), int(fy.min()), int(fx.max()), int(fy.max()))


def find_white_ref(rgb, alpha, face_bbox):
    """Largest bright (max channel > 170), low-saturation (< 0.12) opaque blob
    below the face: the man's T-shirt / the woman's jacket."""
    op = alpha >= 250
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    cand = op & (mx > 170) & (sat < 0.12)
    cand[: face_bbox[3] + 20] = False
    lab, n = ndi.label(cand)
    if n == 0:
        return None, None
    sizes = ndi.sum(cand, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    wy, wx = np.where(m)
    return m, (int(wx.min()), int(wy.min()), int(wx.max()), int(wy.max()))


# ----------------------------------------------------------------------------
# Measurements
# ----------------------------------------------------------------------------
def measure(img, core=None):
    """Measure one RGBA float image. `core` lets before/after comparisons use
    the very same face pixels (the skin gate would otherwise pick a slightly
    different set after grading)."""
    rgb = img[..., :3]
    a = img[..., 3]
    op = a >= 250
    out = {}
    if core is None:
        core, fbox = find_face(rgb, a)
    else:
        fy, fx = np.where(core)
        fbox = (int(fx.min()), int(fy.min()), int(fx.max()), int(fy.max()))
    c = rgb[core]
    L = lum(c)
    out["face_bbox"] = fbox
    out["skin_rgb"] = c.mean(0)
    out["skin_L"] = float(L.mean())
    out["skin_Lstd"] = float(L.std())
    out["skin_RG"] = float(c.mean(0)[0] / c.mean(0)[1])
    out["skin_BG"] = float(c.mean(0)[2] / c.mean(0)[1])
    wm, wbox = find_white_ref(rgb, a, fbox)
    if wm is not None:
        w = rgb[wm].mean(0)
        out["white_bbox"] = wbox
        out["white_rgb"] = w
        out["white_gain"] = (w[1] / w[0], 1.0, w[1] / w[2])
    Lo = lum(rgb[op])
    out["op_L_mean"], out["op_L_std"] = float(Lo.mean()), float(Lo.std())
    out["op_L_pct"] = np.percentile(Lo, [1, 5, 50, 95, 99])
    # edge spill: semi-transparent pixels vs nearest fully opaque pixel
    semi = (a >= 30) & (a <= 220)
    d, idx = ndi.distance_transform_edt(~op, return_indices=True)
    near = rgb[idx[0], idx[1]]
    # ignore the bottom 12 % of the subject (table fade / crop) for the spill stat
    rows = np.where(a > 0)[0]
    cut = rows.max() - int((rows.max() - rows.min()) * 0.12)
    s = semi.copy()
    s[cut:] = False
    e, nb = rgb[s], near[s]
    out["edge_n"] = int(s.sum())
    out["edge_rgb"], out["edge_nb_rgb"] = e.mean(0), nb.mean(0)
    out["edge_dL"] = float(lum(e).mean() - lum(nb).mean())
    out["edge_dRB"] = float((e[:, 0] - e[:, 2]).mean() - (nb[:, 0] - nb[:, 2]).mean())
    # artefacts
    lab, n = ndi.label(a > 0)
    sizes = ndi.sum(np.ones_like(a), lab, range(1, n + 1))
    out["islands"] = int((sizes < ISLAND_PX).sum())
    lab, n = ndi.label(a == 0)
    sizes = np.sort(ndi.sum(np.ones_like(a), lab, range(1, n + 1)))[:-1]
    out["pinholes"] = int((sizes < ISLAND_PX).sum())
    fg = a > 0
    band = fg & ~ndi.binary_erosion(fg)
    band[-1] = False  # image bottom crop is a legitimate hard edge
    out["hard_edge_pct"] = float((a[band] >= 250).mean() * 100) if band.any() else 0.0
    # blockiness proxy: fraction of transition pixels whose alpha differs by
    # > 60 from a 4-neighbour -> staircase mattes score high
    tr = (a > 0) & (a < 250)
    dx = np.abs(np.diff(a, axis=1, append=a[:, -1:]))
    dy = np.abs(np.diff(a, axis=0, append=a[-1:]))
    out["alpha_step_pct"] = float((((dx > 60) | (dy > 60)) & tr).sum() / max(tr.sum(), 1) * 100)
    return out


def report(m, title):
    print(f"--- {title}")
    print("  face bbox x%d-%d y%d-%d" % (m["face_bbox"][0], m["face_bbox"][2], m["face_bbox"][1], m["face_bbox"][3]))
    print("  skin mean RGB %s  L %.1f  std %.1f  R/G %.3f  B/G %.3f" % (
        np.round(m["skin_rgb"], 1), m["skin_L"], m["skin_Lstd"], m["skin_RG"], m["skin_BG"]))
    if "white_rgb" in m:
        print("  white ref bbox x%d-%d y%d-%d  mean RGB %s  gain-to-neutral R %.3f B %.3f" % (
            m["white_bbox"][0], m["white_bbox"][2], m["white_bbox"][1], m["white_bbox"][3],
            np.round(m["white_rgb"], 1), m["white_gain"][0], m["white_gain"][2]))
    print("  opaque L mean %.1f std %.1f  p1/5/50/95/99 %s" % (m["op_L_mean"], m["op_L_std"], np.round(m["op_L_pct"], 0)))
    print("  edge(a30-220, n=%d) RGB %s vs adjacent opaque %s  dL %+.1f  d(R-B) %+.1f" % (
        m["edge_n"], np.round(m["edge_rgb"], 1), np.round(m["edge_nb_rgb"], 1), m["edge_dL"], m["edge_dRB"]))
    print("  artefacts: islands<%d px %d, pinholes %d, hard boundary %.1f%%, alpha steps>60 %.1f%% of transition px" % (
        ISLAND_PX, m["islands"], m["pinholes"], m["hard_edge_pct"], m["alpha_step_pct"]))


# ----------------------------------------------------------------------------
# Processing steps
# ----------------------------------------------------------------------------
def alpha_hygiene(a, sigma):
    """Fade stray wisps, remove small islands, fill pinholes, optionally
    smooth the matte."""
    # stray low-alpha wisps attached to the body (matting fuzz next to the
    # man's ear, mushy jacket fringe): alpha < 64 AND more than 5 px away from
    # the alpha >= 128 body is faded out with a smooth weight in both alpha
    # and distance, so no new step is created. Removes < 0.1 % of total alpha.
    d = ndi.distance_transform_edt(a < 128)
    wisp = np.clip((d - 5.0) / 4.0, 0, 1) * np.clip((64.0 - a) / 32.0, 0, 1)
    a = a * (1 - wisp)
    a = np.where(a < 1, 0.0, a)
    # islands: connected components of alpha > 0 smaller than ISLAND_PX
    fg = a > 0
    lab, n = ndi.label(fg)
    sizes = ndi.sum(np.ones_like(a), lab, range(1, n + 1))
    kill = np.isin(lab, np.where(sizes < ISLAND_PX)[0] + 1)
    a = np.where(kill, 0.0, a)
    # pinholes: components of alpha == 0 smaller than ISLAND_PX get the max
    # alpha of their 3x3 neighbourhood (usually 255)
    holes = a == 0
    lab, n = ndi.label(holes)
    sizes = ndi.sum(np.ones_like(a), lab, range(1, n + 1))
    fill = np.isin(lab, np.where(sizes < ISLAND_PX)[0] + 1)
    a = np.where(fill, ndi.maximum_filter(a, 3), a)
    if sigma > 0:
        # gaussian only changes values near transitions; the flat 0 / 255
        # regions are unaffected. Re-clamp so the body stays fully opaque.
        sm = ndi.gaussian_filter(a, sigma)
        a = np.where((a > 0) & (a < 255) | (sm != a) & (ndi.minimum_filter(a, 5) < 255), sm, a)
        a = np.clip(a, 0, 255)
    return a, int(kill.sum()), int(fill.sum())


def decontaminate(rgb, a):
    """Propagate colour from the nearest fully-opaque pixels into the
    semi-transparent band. Returns new RGB and the mean weight applied."""
    op = a >= 250
    d, idx = ndi.distance_transform_edt(~op, return_indices=True)
    fill = rgb[idx[0], idx[1]]
    # 1 px blur of the propagated colour removes nearest-neighbour streaks
    fill = np.stack([ndi.gaussian_filter(fill[..., i], 1.0) for i in range(3)], -1)
    w_alpha = np.clip((255.0 - a) / (255.0 - 160.0), 0, 1)   # full below alpha 160
    w_dist = np.clip((8.0 - d) / 4.0, 0, 1)                   # full within 4 px, 0 beyond 8 px
    w = (w_alpha * w_dist)[..., None] * (a > 0)[..., None]
    return rgb * (1 - w) + fill * w


def erode_alpha(a, px):
    """Sub-pixel erosion: blend between alpha and its 3x3 minimum."""
    if px <= 0:
        return a
    return a * (1 - px) + ndi.minimum_filter(a, 3) * px


def apply_gain(rgb, gain, strength):
    g = 1.0 + (np.asarray(gain, np.float32) - 1.0) * strength
    return np.clip(rgb * g, 0, 255), g


def skin_gamma(rgb, L_skin, target, hi0=175.0, hi1=232.0):
    """Gamma on luminance so the skin mean lands on target, RGB scaled by L'/L.

    Highlights are protected: above L=175 the curve blends smoothly back to
    identity (smoothstep 175..232), so the woman's cream jacket (L ~233) and
    the whites stay white on the white poster while her midtones come down.
    Mean skin sits at 106-148 in both portraits; only the brightest skin
    highlights are partly protected, so the mean lands within ~3 L of target.
    """
    gamma = np.log(target / 255.0) / np.log(L_skin / 255.0)
    L = np.maximum(lum(rgb), 1e-3)
    Lp = highlight_protect(L, 255.0 * (L / 255.0) ** gamma, hi0, hi1)
    return np.clip(rgb * (Lp / L)[..., None], 0, 255), gamma


def highlight_protect(L, Lp, hi0=175.0, hi1=232.0):
    """Blend an adjusted luminance Lp back to the original L above hi0 with a
    smoothstep that reaches identity at hi1, so whites stay white."""
    t = np.clip((L - hi0) / (hi1 - hi0), 0, 1)
    t = t * t * (3 - 2 * t)
    return Lp * (1 - t) + L * t


def skin_contrast(rgb, core, target_std, cap=0.12):
    """Scale luminance deviation around the skin mean; factor capped to +-cap.
    Highlights are protected exactly like in skin_gamma, otherwise a factor
    < 1 would drag the woman's white jacket down to grey."""
    L = lum(rgb)
    mean, std = L[core].mean(), L[core].std()
    f = float(np.clip(target_std / std, 1 - cap, 1 + cap))
    Lp = highlight_protect(L, np.clip(mean + (L - mean) * f, 0, 255))
    ratio = Lp / np.maximum(L, 1e-3)
    return np.clip(rgb * ratio[..., None], 0, 255), f


def micro_sharpen(rgb, a, params):
    radius, amount, thr = params
    im = Image.fromarray(rgb.astype(np.uint8))
    sh = np.asarray(im.filter(ImageFilter.UnsharpMask(radius=radius, percent=int(amount * 100), threshold=thr))).astype(np.float32)
    # opaque interior only (eroded 2 px) so no edge haloes are created
    inner = ndi.binary_erosion(a >= 250, iterations=2)[..., None]
    return np.where(inner, sh, rgb)


# ----------------------------------------------------------------------------
def grade(img, prof, target_L, target_std, wb_override=None, verbose=True):
    rgb = img[..., :3].astype(np.float32)
    a = img[..., 3].astype(np.float32)
    log = []
    # face core located once on the untouched input and reused everywhere
    core, _ = find_face(rgb, a)

    # 1. alpha hygiene
    a, killed, filled = alpha_hygiene(a, prof["alpha_sigma"])
    log.append(f"alpha hygiene: removed {killed} px in islands <{ISLAND_PX} px, filled {filled} px of pinholes, faded stray wisps, gaussian sigma {prof['alpha_sigma']}")

    # 2. edge decontamination
    rgb = decontaminate(rgb, a)
    log.append("decontamination: nearest-opaque colour propagated into 0<alpha<255 (full below alpha 160, within 4 px)")

    # 3. alpha erosion
    a = erode_alpha(a, prof["erosion_px"])
    log.append(f"alpha erosion: {prof['erosion_px']} px")

    # 4. white balance
    m = measure(np.dstack([rgb, a]))
    gain = None
    if wb_override is not None:
        gain = wb_override
    elif prof["wb"] == "auto" and "white_gain" in m:
        gain = m["white_gain"]
    if gain is not None and prof["wb_strength"] > 0:
        rgb, g = apply_gain(rgb, gain, prof["wb_strength"])
        log.append("white balance: per-channel gain R %.3f G %.3f B %.3f (strength %.2f, ref RGB %s)" % (
            g[0], g[1], g[2], prof["wb_strength"], np.round(m.get("white_rgb", [0, 0, 0]), 1)))
    else:
        log.append("white balance: none")

    # 5. skin luminance via gamma (highlights protected)
    L_skin = lum(rgb[core]).mean()
    rgb, gamma = skin_gamma(rgb, L_skin, target_L)
    log.append("skin luminance: gamma %.3f (skin L %.1f -> %.1f)" % (gamma, L_skin, lum(rgb[core]).mean()))

    # 6. skin contrast
    rgb, f = skin_contrast(rgb, core, target_std)
    log.append("skin contrast: factor %.3f around skin mean (face L std -> %.1f)" % (f, lum(rgb[core]).std()))

    # 7. micro-sharpen
    if prof["sharpen"]:
        rgb = micro_sharpen(rgb, a, prof["sharpen"])
        log.append("micro-sharpen: unsharp radius %.1f amount %.2f threshold %d, opaque interior only" % prof["sharpen"])
    else:
        log.append("micro-sharpen: none")

    if verbose:
        for l in log:
            print("  *", l)
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 255)])
    return np.rint(out).astype(np.uint8), core


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("output", nargs="?")
    p.add_argument("--profile", choices=PROFILES.keys(), required=True)
    p.add_argument("--analyse", action="store_true", help="print measurements only")
    p.add_argument("--target-skin-l", type=float, default=TARGET_SKIN_L)
    p.add_argument("--target-skin-std", type=float, default=TARGET_SKIN_STD)
    p.add_argument("--wb", type=str, default=None, help="override white balance gains 'R,G,B' or 'none'")
    p.add_argument("--wb-strength", type=float, default=None)
    p.add_argument("--erosion", type=float, default=None, help="alpha erosion in px (0-1)")
    p.add_argument("--alpha-sigma", type=float, default=None)
    p.add_argument("--no-sharpen", action="store_true")
    args = p.parse_args()

    prof = dict(PROFILES[args.profile])
    if args.wb_strength is not None:
        prof["wb_strength"] = args.wb_strength
    if args.erosion is not None:
        prof["erosion_px"] = args.erosion
    if args.alpha_sigma is not None:
        prof["alpha_sigma"] = args.alpha_sigma
    if args.no_sharpen:
        prof["sharpen"] = None
    wb_override = None
    if args.wb is not None:
        if args.wb == "none":
            prof["wb"] = "none"
        else:
            wb_override = tuple(float(x) for x in args.wb.split(","))

    img = np.asarray(Image.open(args.input).convert("RGBA")).astype(np.float32)
    core, _ = find_face(img[..., :3], img[..., 3])
    before = measure(img, core)
    report(before, f"BEFORE {args.input}")
    if args.analyse:
        return
    if not args.output:
        sys.exit("output path required unless --analyse")
    print(f"--- grading profile '{args.profile}'")
    out, core = grade(img, prof, args.target_skin_l, args.target_skin_std, wb_override)
    report(measure(out.astype(np.float32), core), f"AFTER  {args.output}")
    Image.fromarray(out, "RGBA").save(args.output, optimize=True)
    print("saved", args.output)


if __name__ == "__main__":
    main()
