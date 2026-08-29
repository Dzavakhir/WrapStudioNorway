"""Ikkala spikerni bitta jamoa kadriga birlashtirish.

- bosh o'lchamlari tenglashtiriladi (bir xil razmer)
- yelkalar bir chiziqda turadi
- ayol spiker belidan pastda kesiladi
- ortiqcha bo'sh joy kesilib, ikkalasi bir-biriga yaqinlashtiriladi
"""
from PIL import Image
import numpy as np
from grade import apply_grade

HEAD = 320          # bir "bosh" birligi, piksel
GAP = -74           # figuralar orasidagi masofa (manfiy = yengil ustma-ust)
WOMAN_CUT = 1060    # ayol spiker uchun bel chizig'i (asl piksel)


def landmarks(im):
    a = np.asarray(im.getchannel('A')) > 128
    rows = a.sum(1)
    nz = np.nonzero(rows)[0]
    top, bot, mx = int(nz[0]), int(nz[-1]), int(rows.max())
    shoulder = int(next(y for y in range(top, bot) if rows[y] >= 0.5 * mx))
    return top, shoulder, bot


def prepare(path, grade_kw, cut=None):
    im = Image.open(path)
    top, shoulder, bot = landmarks(im)
    if cut:
        im = im.crop((0, 0, im.width, cut))
        bot = min(bot, cut - 1)
    im = apply_grade(im, **grade_kw)

    scale = HEAD / (shoulder - top)
    w, h = round(im.width * scale), round(im.height * scale)
    im = im.resize((w, h), Image.LANCZOS)
    sh, tp, bt = shoulder * scale, top * scale, bot * scale

    # gorizontal ortiqcha joyni kesish
    bbox = im.getbbox()
    im = im.crop((bbox[0], 0, bbox[2], im.height))
    return im, sh - tp, bt - tp, tp


def main():
    man, man_sh, man_bot, man_tp = prepare(
        'assets/sp1_cut.png',
        dict(mix=0.85, contrast=1.16, brightness=0.96, high=(232, 182, 152)))
    woman, wom_sh, wom_bot, wom_tp = prepare(
        'assets/sp2_cut.png',
        dict(mix=0.97, contrast=1.20, brightness=0.84, high=(196, 140, 116)),
        cut=WOMAN_CUT)

    # yuqoridagi bo'sh joyni kesib, boshdan boshlaymiz
    man = man.crop((0, round(man_tp), man.width, man.height))
    woman = woman.crop((0, round(wom_tp), woman.width, woman.height))

    # yelkalarni bir chiziqqa qo'yish
    shoulder_y = round(max(man_sh, wom_sh))
    man_y = shoulder_y - round(man_sh)
    wom_y = shoulder_y - round(wom_sh)

    height = max(man_y + man.height, wom_y + woman.height)
    width = man.width + woman.width + GAP
    canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(man, (0, man_y))
    canvas.alpha_composite(woman, (man.width + GAP, wom_y))
    canvas = canvas.crop(canvas.getbbox())
    canvas.save('assets/crew_pair.png')
    print('crew_pair', canvas.size, 'shoulder_y', shoulder_y,
          'man h', man.height, 'woman h', woman.height)


if __name__ == '__main__':
    main()
