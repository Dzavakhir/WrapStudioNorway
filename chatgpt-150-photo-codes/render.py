#!/usr/bin/env python3
"""Render effects.

    python3 render.py g07              # render group 7 (its 5 codes) + previews/g07.jpg contact sheet
    python3 render.py golden_hour      # render one or more codes by name
    python3 render.py all              # render everything (uses 4 processes) + contact sheets
    python3 render.py sheets           # only rebuild the 'all' contact sheets from existing renders

Outputs: renders/NNN_code.jpg (1152x1440, q92) and previews/*.jpg
"""
import os, sys, glob, json, time, traceback, importlib, multiprocessing as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
CODES = json.load(open(os.path.join(ROOT, 'codes.json')))['codes']
BY_CODE = {c['code']: c for c in CODES}
os.makedirs('renders', exist_ok=True); os.makedirs('previews', exist_ok=True)


def load_effects():
    from effects.registry import REGISTRY
    for f in sorted(glob.glob(os.path.join(ROOT, 'effects', 'g[0-9][0-9].py'))):
        name = os.path.splitext(os.path.basename(f))[0]
        try:
            importlib.import_module('effects.' + name)
        except Exception:
            print('!! failed to import effects/%s.py' % name); traceback.print_exc()
    return REGISTRY


def out_path(entry):
    return os.path.join('renders', '%03d_%s.jpg' % (entry['id'], entry['code']))


def render_one(code):
    from effects import lib
    reg = load_effects()
    entry = BY_CODE[code]
    if code not in reg:
        return code, None, 'NOT IMPLEMENTED (no @effect(%r) found)' % code
    t0 = time.time()
    try:
        out = reg[code](lib.base())
        out = lib.finalize(out)
        if not np.isfinite(out).all():
            return code, None, 'NaN/inf in output'
        lib.to_pil(out).save(out_path(entry), quality=92, subsampling=1)
        return code, out_path(entry), 'ok %.1fs' % (time.time() - t0)
    except Exception:
        return code, None, 'ERROR\n' + traceback.format_exc()


def contact_sheet(entries, path, cols=None, thumb=(384, 480), with_original=True):
    from effects import lib
    items = []
    if with_original:
        items.append(('ORIGINAL', os.path.join('source', 'crop.jpg')))
    for e in entries:
        items.append(('%03d /%s' % (e['id'], e['code']), out_path(e)))
    cols = cols or min(6, len(items))
    rows = (len(items) + cols - 1) // cols
    pad, label_h = 12, 34
    sheet = Image.new('RGB', (cols * (thumb[0] + pad) + pad, rows * (thumb[1] + label_h + pad) + pad), (247, 241, 232))
    d = ImageDraw.Draw(sheet)
    f = lib.font('lato-bold', 22)
    for i, (label, p) in enumerate(items):
        x = pad + (i % cols) * (thumb[0] + pad); y = pad + (i // cols) * (thumb[1] + label_h + pad)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB').resize(thumb, Image.LANCZOS)
        else:
            im = Image.new('RGB', thumb, (200, 60, 60)); ImageDraw.Draw(im).text((20, 20), 'MISSING', fill='white', font=f)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + thumb[1] + 6), label, fill=(46, 26, 31), font=f)
    sheet.save(path, quality=86)
    return path


def main():
    args = sys.argv[1:] or ['all']
    if args[0] == 'sheets':
        for g in range(30):
            grp = CODES[g * 5:(g + 1) * 5]
            contact_sheet(grp, 'previews/g%02d.jpg' % (g + 1))
        for s in range(10):
            contact_sheet(CODES[s * 15:(s + 1) * 15], 'previews/all_%02d.jpg' % (s + 1), cols=4, thumb=(288, 360))
        print('sheets rebuilt'); return
    if args[0] == 'all':
        todo = [c['code'] for c in CODES]
    elif args[0].startswith('g') and args[0][1:].isdigit():
        g = int(args[0][1:]); todo = [c['code'] for c in CODES[(g - 1) * 5:g * 5]]
    else:
        todo = [a.lstrip('/') for a in args]
        for t in todo:
            if t not in BY_CODE:
                sys.exit('unknown code %r' % t)
    if len(todo) > 6:
        with mp.Pool(4) as pool:
            results = pool.map(render_one, todo)
    else:
        results = [render_one(c) for c in todo]
    failed = 0
    for code, path, status in results:
        print('%-22s %s' % ('/' + code, status.splitlines()[0] if status.startswith('ok') else status))
        failed += status[:2] != 'ok'
    # previews
    if args[0].startswith('g') and args[0][1:].isdigit():
        g = int(args[0][1:])
        print('preview:', contact_sheet(CODES[(g - 1) * 5:g * 5], 'previews/g%02d.jpg' % g))
    elif args[0] == 'all':
        for g in range(30):
            contact_sheet(CODES[g * 5:(g + 1) * 5], 'previews/g%02d.jpg' % (g + 1))
        for s in range(10):
            contact_sheet(CODES[s * 15:(s + 1) * 15], 'previews/all_%02d.jpg' % (s + 1), cols=4, thumb=(288, 360))
        print('previews written to previews/')
    else:
        entries = [BY_CODE[c] for c in todo]
        print('preview:', contact_sheet(entries, 'previews/custom.jpg'))
    print('%d rendered, %d failed' % (len(results) - failed, failed))


if __name__ == '__main__':
    main()
