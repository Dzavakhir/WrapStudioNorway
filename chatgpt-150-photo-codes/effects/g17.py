"""Group g17 - Fon (Background): blur_bg, bokeh_bg, studio_white, studio_cream, gradient_bg.

All five codes keep the person untouched and change only her surroundings.  The shared helpers below
deal with the one thing these codes live or die on - the cut-out edge:

* the person mask PNG has a floor of ~0.035 and a ceiling of ~0.996, so it is re-levelled to a true 0..1
  (otherwise 3.5 % of the park bleeds through every studio backdrop);
* its 9-17 px soft edge band contains foliage/sky-contaminated pixels, so for plain backdrops the interior
  colours are pulled outward into that band (colour decontamination) before compositing;
* for depth-of-field codes the blurred background is computed from clean background pixels only, so no
  navy from the hijab smears into the blur (no dark halo) and no sharp ring of background survives.
"""
from effects.lib import *
from effects.registry import effect


# ----------------------------------------------------------------------------- shared helpers

def _person():
    """Person mask re-levelled to a true 0..1."""
    p = mask('person')
    lo, hi = float(p.min()), float(p.max())
    return np.clip((p - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)


def _alpha(p, lo=0.3, hi=0.85, soft=0.8):
    """Composite alpha: the wide mask ramp tightened around the true silhouette, then lightly feathered."""
    return feather(smoothstep(lo, hi, p), soft)


def _cutout(img, p):
    """Colour-decontaminated foreground: colours from 3+ px inside the silhouette are spread outward into the
    soft edge band, so no green/sky fringe from the park survives a composite onto a plain backdrop."""
    core = cv2.erode((p > 0.98).astype(np.float32), np.ones((7, 7), np.uint8))
    num = blur(img * core[..., None], 8)
    den = blur(core, 8)
    spread = clip(num / np.maximum(den, 1e-3)[..., None])
    return lerp(spread, img, core)


def _clean_bg_weight(p):
    """1 on clean background pixels, 0 on the person and on the mixed edge band."""
    return 1 - smoothstep(0.03, 0.25, p)


def _masked_blur(img, w, blur_fn):
    """Normalised blur that only samples pixels weighted by w (no subject colour bleeds into the background)."""
    num = blur_fn(img * w[..., None])
    den = blur_fn(w)
    return clip(num / np.maximum(den, 1e-3)[..., None])


def _studio_shadow(img, alpha, dx=28, dy=40, sigma=36, strength=0.22):
    """Soft natural shadow thrown onto the backdrop by a key light from the upper left."""
    sh = translate(alpha, dx, dy, border=cv2.BORDER_CONSTANT)
    sh = blur(sh, sigma) * (1 - alpha)
    return clip(img * (1 - strength * sh)[..., None])


def _backdrop(centre_col, edge_col, center=(620, 470), radius=1.2, softness=0.85, seed=17, tex=0.01):
    """Seamless studio paper: lit hot-spot behind the subject fading to the edge colour, with a whisper of
    texture and a dither so the smooth gradient never bands."""
    g = radial(center=center, radius=radius, softness=softness)
    layer = lerp(as_layer(edge_col), as_layer(centre_col), g)
    layer = layer * (1 + tex * (fbm(4, seed, 0.6) - 0.5))[..., None]
    layer = layer + (noise(seed + 1) - 0.5)[..., None] * 0.006
    return clip(layer)


def _fill_light(img, lift=0.02):
    """Studio fill: opens the deepest shadows a touch (white/cream walls bounce light back)."""
    return curve(img, [(0, 0), (0.12, 0.12 + lift), (0.5, 0.5 + lift * 0.5), (1, 1)])


# ----------------------------------------------------------------------------- 081 blur_bg

@effect('blur_bg')
def blur_bg(img):
    """Portrait-mode lens blur: background softly out of focus, subject tack sharp, no halo."""
    p = _person()
    a = _alpha(p)
    w = _clean_bg_weight(p)
    far = _masked_blur(img, w, lambda x: blur(x, 26))      # trees / sky
    near = _masked_blur(img, w, lambda x: blur(x, 15))     # ground closer to the camera
    bgb = lerp(far, near, linear(90, 0.55, 1.0))
    subj = clarity(img, 0.15, 40)
    subj = unsharp(subj, 1.4, 0.35)
    out = clip(lerp(bgb, subj, a))
    return vignette(out, 0.12, radius=1.0, softness=0.8)


# ----------------------------------------------------------------------------- 082 bokeh_bg

@effect('bokeh_bg')
def bokeh_bg(img):
    """Creamy bokeh: light spots become round bright discs, dreamy shallow depth of field."""
    p = _person()
    a = _alpha(p)
    w = _clean_bg_weight(p)
    k = disc_kernel(30)
    boost = 4.0

    def disc(x):
        return cv2.filter2D(x, -1, k, borderType=cv2.BORDER_REFLECT)

    bok = _masked_blur(clip(img) ** boost, w, disc) ** (1.0 / boost)   # lens-like disc blur, highlights kept
    bok = blur(bok, 1.6)                                               # takes the digital edge off the discs
    bok = temperature(bok, 0.23)                                       # creamy warmth
    bok = exposure(bok, 0.18)
    bok = fade(bok, 0.11, 0.0)
    bok = saturation(bok, 0.9)                                         # pastel, not garish
    bok = glow(bok, 30, 0.38, 0.65)
    discs = bokeh_layer(count=30, seed=17, radius=(20, 44), colors=['#ffd9a0', '#ffe8c2', '#f7c98c', '#fff3dc'],
                        area=(w > 0.5).astype(np.float32), softness=0.18, alpha=(0.3, 0.7))
    bok = blend(bok, discs, 'screen', 0.7)
    subj = unsharp(temperature(img, 0.05), 1.4, 0.25)
    out = clip(lerp(bok, subj, a))
    return vignette(out, 0.15, radius=1.0, softness=0.8)


# ----------------------------------------------------------------------------- 083 studio_white

@effect('studio_white')
def studio_white(img):
    """Clean white studio backdrop with a soft natural shadow, subject perfectly cut out."""
    p = _person()
    a = _alpha(p)
    fg = _cutout(img, p)
    bg = _backdrop('#ffffff', '#ebe8e4', center=(620, 470), radius=1.2, softness=0.85, seed=21, tex=0.008)
    bg = clip(bg * (1 - 0.05 * linear(90, 0.55, 1.0))[..., None])   # sweep darkens slightly towards the floor
    fg = brightness(_fill_light(fg, 0.02), 0.02)
    out = clip(lerp(bg, fg, a))
    return _studio_shadow(out, a, strength=0.24)


# ----------------------------------------------------------------------------- 084 studio_cream

@effect('studio_cream')
def studio_cream(img):
    """Warm cream studio backdrop, soft vignette, elegant and calm."""
    p = _person()
    a = _alpha(p)
    fg = _cutout(img, p)
    bg = _backdrop('#F5ECDD', '#DCCBB0', center=(620, 470), radius=1.3, softness=0.85, seed=23, tex=0.015)
    fg = temperature(_fill_light(fg, 0.015), 0.08)
    out = clip(lerp(bg, fg, a))
    out = _studio_shadow(out, a, strength=0.2)
    return vignette(out, 0.22, radius=1.0, softness=0.75, color_='#7a6146')


# ----------------------------------------------------------------------------- 085 gradient_bg

@effect('gradient_bg')
def gradient_bg(img):
    """Smooth burgundy-to-rose gradient backdrop, soft light behind the head, rim light on the silhouette."""
    p = _person()
    a = _alpha(p)
    fg = _cutout(img, p)
    angle = -32.0                                     # 0 = bottom-left (burgundy) -> 1 = top-right (blush)
    t = linear(angle)
    pos = [0.0, 0.55, 1.0]
    cols = np.array([color('#4a1522'), color('#a8556b'), color('#e8c4c8')], np.float32)
    bg = np.stack([np.interp(t, pos, cols[:, c]) for c in range(3)], axis=-1).astype(np.float32)
    bg = blend(bg, '#f2c6cf', 'screen', 0.35, radial(center=(680, 420), radius=0.75, softness=0.9))
    bg = clip(bg + (noise(31) - 0.5)[..., None] * 0.008)      # dither: no banding in the smooth gradient
    out = clip(lerp(bg, fg, a))
    # rim light: strongest on the silhouette edges that face the bright top-right corner
    sm = blur(a, 10)
    gx = cv2.Sobel(sm, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(sm, cv2.CV_32F, 0, 1, ksize=3)
    n = np.sqrt(gx * gx + gy * gy) + 1e-6
    lx, ly = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    facing = np.clip((-gx / n) * lx + (-gy / n) * ly, 0, 1)
    rim = inner_edge(a, width=12, softness=5) * (0.2 + 0.8 * facing ** 0.8)
    return blend(out, '#f6cbd4', 'screen', 0.65, rim)
