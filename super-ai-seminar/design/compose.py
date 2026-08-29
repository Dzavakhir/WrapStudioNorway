"""Ikkala spikerni bitta jamoa kadriga birlashtirish.

- bosh o'lchamlari tenglashtiriladi (bir xil razmer)
- yelkalar bir chiziqda turadi
- ortiqcha bo'sh joy kesilib, ikkalasi yonma-yon yaqinlashtiriladi
- kerak bo'lsa, o'ngdagi spiker belidan pastda kesiladi

Ishlatilishi:  python3 compose.py [dark|light|both]
"""
import sys
from PIL import Image
import numpy as np
from grade import apply_grade, apply_light_grade

HEAD = 320    # bir "bosh" birligi, piksel
GAP = -74     # figuralar orasidagi masofa (manfiy = yengil ustma-ust)

PROFILES = {
    # qora-qizil fonli variant
    'dark': dict(
        out='assets/crew_pair.png',
        man=dict(src='assets/sp1_cut.png', cut=None, grade=apply_grade,
                 kw=dict(mix=0.85, contrast=1.16, brightness=0.96, high=(232, 182, 152))),
        woman=dict(src='assets/sp2_cut.png', cut=1060, grade=apply_grade,
                   kw=dict(mix=0.97, contrast=1.20, brightness=0.84, high=(196, 140, 116))),
    ),
    # oq fonli variant: rang harorati tenglashtiriladi, teri rangi tabiiy qoladi
    'light': dict(
        out='assets/crew_pair_light.png',
        man=dict(src='assets/w1_cut.png', cut=None, grade=apply_light_grade,
                 kw=dict(gains=(1.025, 1.0, 0.985), brightness=1.06, contrast=1.08,
                         saturation=1.0)),
        woman=dict(src='assets/w2_cut.png', cut=None, grade=apply_light_grade,
                   kw=dict(gains=(1.02, 0.995, 0.97), brightness=0.98, contrast=1.05,
                           saturation=0.94)),
    ),
}


def landmarks(im):
    a = np.asarray(im.getchannel('A')) > 128
    rows = a.sum(1)
    nz = np.nonzero(rows)[0]
    top, bot, mx = int(nz[0]), int(nz[-1]), int(rows.max())
    shoulder = int(next(y for y in range(top, bot) if rows[y] >= 0.5 * mx))
    return top, shoulder, bot


def prepare(spec):
    im = Image.open(spec['src'])
    top, shoulder, bot = landmarks(im)
    if spec['cut']:
        im = im.crop((0, 0, im.width, spec['cut']))
    im = spec['grade'](im, **spec['kw'])

    scale = HEAD / (shoulder - top)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    tp, sh = top * scale, shoulder * scale

    # gorizontal ortiqcha joyni kesish + yuqoridagi bo'shliqni olib tashlash
    bbox = im.getbbox()
    im = im.crop((bbox[0], round(tp), bbox[2], im.height))
    return im, sh - tp


def build(profile):
    p = PROFILES[profile]
    man, man_sh = prepare(p['man'])
    woman, wom_sh = prepare(p['woman'])

    # yelkalarni bir chiziqqa qo'yish
    shoulder_y = round(max(man_sh, wom_sh))
    man_y, wom_y = shoulder_y - round(man_sh), shoulder_y - round(wom_sh)

    canvas = Image.new('RGBA', (man.width + woman.width + GAP,
                                max(man_y + man.height, wom_y + woman.height)), (0, 0, 0, 0))
    canvas.alpha_composite(man, (0, man_y))
    canvas.alpha_composite(woman, (man.width + GAP, wom_y))
    canvas = canvas.crop(canvas.getbbox())
    canvas.save(p['out'])
    print(profile, p['out'], canvas.size, 'man', man.size, 'woman', woman.size)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    for name in (PROFILES if which == 'both' else [which]):
        build(name)
