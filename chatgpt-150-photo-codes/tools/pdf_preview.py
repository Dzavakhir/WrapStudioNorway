#!/usr/bin/env python3
"""Rasterise PDF pages to PNG contact sheets for visual QA: python3 tools/pdf_preview.py dist/x.pdf 1 2 3  (page numbers, 1-based)"""
import sys, os
import pymupdf
pdf = pymupdf.open(sys.argv[1])
pages = [int(a) for a in sys.argv[2:]] or [1]
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'previews')
os.makedirs(out_dir, exist_ok=True)
for p in pages:
    pix = pdf[p - 1].get_pixmap(dpi=110)
    fn = os.path.join(out_dir, 'page_%03d.png' % p)
    pix.save(fn); print(fn, pix.width, pix.height)
print('total pages', len(pdf), 'size %.1f MB' % (os.path.getsize(sys.argv[1]) / 1e6))
