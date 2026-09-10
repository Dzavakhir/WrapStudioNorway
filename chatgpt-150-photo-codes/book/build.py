#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build book/index.html (A4 pages) from codes.json + renders/.  Then: node book/print.js"""
import json, os, sys, html
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, 'book')
IMG = os.path.join(BOOK, 'img')
os.makedirs(IMG, exist_ok=True)
D = json.load(open(os.path.join(ROOT, 'codes.json')))
CATS, CODES = D['categories'], D['codes']
BY_CAT = {c['slug']: [x for x in CODES if x['category'] == c['slug']] for c in CATS}
COVER_CODE = 'vintage_romance'
HERO_PICK = {  # category slug -> code shown large on the divider page
    'yoruglik': 'golden_hour', 'plyonka': 'polaroid', 'kino': 'teal_orange', 'oq_qora': 'red_pop', 'rang': 'rose_gold',
    'romantik': 'soft_glow', 'estetika': 'old_money', 'retush': 'portrait_pro', 'fon': 'studio_cream', 'badiiy': 'watercolor',
    'ramka': 'polaroid_frame', 'effekt': 'double_exposure', 'mavsum': 'autumn', 'tekstura': 'bokeh_lights', 'ijodiy': 'duotone'}

TIPS = {
 'yoruglik': ("Yorug‘lik kodlarini har doim birinchi qo‘llang — nur asos, qolgani bezak. Bir xabarda ikkita kodni yozish mumkin: ChatGPT ularni ketma-ket bajaradi. Natija sun’iy ko‘rinsa, «keep it natural, soft transition» deb qo‘shing.",
               ['/golden_hour + /soft_glow', '/studio_light + /skin_smooth', '/moonlight + /film_grain']),
 'plyonka': ("Plyonka uslublari tabiiy nurdagi suratlarda eng chiroyli chiqadi. Natija haddan tashqari xira bo‘lsa — «30% less faded», donadorlik ko‘p bo‘lsa — «finer grain» deb yozing.",
             ['/kodak_gold + /light_leak', '/polaroid + /vintage_90s', '/old_photo + /sepia']),
 'kino': ("Kino gradatsiyasi uchun «cinematic 2.39:1 frame» deb qo‘shsangiz, ChatGPT kadrni keng formatga ham keltiradi. Teal-orange uslubida teri rangini himoya qiling: «protect skin tones».",
          ['/teal_orange + /widescreen', '/noir + /blinds_shadow', '/moody + /rain']),
 'oq_qora': ("Oq-qora suratda nur va shakl hal qiluvchi. Kontrast oshirishdan oldin /clarity, keyin plyonka teksturasi qo‘shing — natija «bosma surat» kabi bo‘ladi.",
             ['/bw_film + /dust_scratches', '/red_pop + /blur_bg', '/noir + /bw_contrast']),
 'rang': ("Rang gradatsiyasini teri rangini saqlagan holda so‘rang: «keep natural skin tones». Kuchini foizda boshqaring — «apply at 60% strength».",
          ['/warm_tone + /golden_hour', '/pastel + /dreamy_haze', '/emerald + /studio_light']),
 'romantik': ("Romantik effektlarni yumshoq nur bilan juftlang. Ortiqcha porlash detallarni yo‘qotadi — «subtle glow, keep the eyes sharp» deb qo‘shing.",
              ['/soft_glow + /rose_tint', '/vintage_romance + /polaroid_frame', '/angelic + /pearl']),
 'estetika': ("Estetika kodlari to‘liq kayfiyat beradi. Trend nomiga «aesthetic» so‘zini qo‘shing — ChatGPT bu uslublarni juda yaxshi biladi.",
              ['/old_money + /film_grain', '/coquette + /sparkle', '/dark_academia + /paper_texture']),
 'retush': ("Retushda eng muhim qoida — tabiiylik. Har doim «keep skin texture, natural result» deb qo‘shing. /portrait_pro barcha retush qadamlarini bitta kodda beradi.",
            ['/skin_smooth + /bright_eyes', '/portrait_pro + /studio_light', '/white_teeth + /glow_skin']),
 'fon': ("Fon almashtirishda ro‘mol va soch chetlari muhim: «clean, precise edges around the hair and hijab» deb yozing. Yorug‘lik yo‘nalishi fonga mos bo‘lishini so‘rang.",
         ['/studio_cream + /soft_light', '/blur_bg + /color_pop', '/gradient_bg + /rim_light']),
 'badiiy': ("Badiiy uslublarda yuz tanib olinishi shart — «keep the face recognizable» deb qo‘shing. Chop etish uchun «high resolution, fine detail» so‘rang.",
            ['/watercolor + /paper_texture', '/pencil_sketch + /vintage_frame', '/pop_art + /double_border']),
 'ramka': ("Ramka kodlarini eng oxirida qo‘llang: avval rang va nur, keyin ramka. Yozuv matnini o‘zingiz bering — «caption: yozgi kunlar».",
           ['/polaroid_frame + /kodak_gold', '/magazine + /studio_light', '/postcard + /sepia']),
 'effekt': ("Kuchli effektlarda me’yor muhim: «medium intensity» yoki «strong» deb kuchini boshqaring. Yuz aniq qolishini so‘rang — «keep the face clear».",
            ['/double_exposure + /bw_soft', '/lens_flare + /golden_hour', '/glitch + /cyberpunk']),
 'mavsum': ("Mavsum kodlari fon va nurni birga o‘zgartiradi. Kiyim mavsumga mos bo‘lmasa, «keep the outfit exactly as is» deb ta’kidlang.",
            ['/autumn + /golden_leaves', '/winter + /frost', '/night + /bokeh_lights']),
 'tekstura': ("Teksturalar qatlam sifatida ishlaydi: «overlay at 40% opacity» deb kuchini aniq ayting. Yuz ustida teksturani kamaytirishni so‘rash mumkin.",
              ['/bokeh_lights + /soft_glow', '/leaf_shadow + /summer', '/paper_texture + /old_photo']),
 'ijodiy': ("Ijodiy kodlar ijtimoiy tarmoq uchun ideal. Rang palitrasini o‘zingiz ko‘rsating: «use burgundy and cream colours». Poster uchun «add a title text» so‘rang.",
            ['/duotone + /halftone', '/neon + /cyberpunk', '/stamp + /postcard']),
}
STARTER_PROMPT = ("You are a professional photo retoucher. I will send you photos together with style codes such as /golden_hour. "
                  "Apply only the described style. Always keep my face, identity, expression, body, hijab/hair and clothing exactly the same — "
                  "change only lighting, colour, texture, background or frame as the code describes. Return the edited photo in the same resolution and aspect ratio.")
SUFFIX = 'Keep the person, face and clothing unchanged.'


def esc(s):
    return html.escape(s, quote=False)


def render_path(c):
    return os.path.join(ROOT, 'renders', '%03d_%s.jpg' % (c['id'], c['code']))


def book_image(c, size=(720, 900), name=None, quality=80):
    """Downscaled copy of the render (falls back to the source crop when a render is missing)."""
    src = render_path(c)
    missing = not os.path.exists(src)
    if missing:
        src = os.path.join(ROOT, 'source', 'crop.jpg')
    out = os.path.join(IMG, name or ('%03d.jpg' % c['id']))
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        im = Image.open(src).convert('RGB')
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        im.save(out, quality=quality, optimize=True, subsampling=1)
    return 'img/' + os.path.basename(out), missing


ORN = '''<svg class="orn" viewBox="0 0 240 24" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round">
<path d="M4 12 C 40 12, 70 12, 96 12 C 104 12, 108 6, 112 6"/><path d="M236 12 C 200 12, 170 12, 144 12 C 136 12, 132 6, 128 6"/>
<path d="M96 12 C 100 12, 104 18, 110 18"/><path d="M144 12 C 140 12, 136 18, 130 18"/>
<path d="M120 5 L 126 12 L 120 19 L 114 12 Z" fill="currentColor" stroke="none"/><circle cx="4" cy="12" r="1.6" fill="currentColor" stroke="none"/><circle cx="236" cy="12" r="1.6" fill="currentColor" stroke="none"/></svg>'''
ORN_SMALL = '''<svg class="orn-s" viewBox="0 0 120 16" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round">
<path d="M2 8 H 46 C 50 8, 52 4, 54 4"/><path d="M118 8 H 74 C 70 8, 68 4, 66 4"/><path d="M60 3 L 64 8 L 60 13 L 56 8 Z" fill="currentColor" stroke="none"/></svg>'''
CORNER = '''<svg class="corner %s" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
<path d="M2 58 V 12 Q 2 2 12 2 H 58"/><path d="M8 58 V 16 Q 8 8 16 8 H 58" stroke-width="0.7"/>
<path d="M14 20 C 20 14, 26 16, 24 22 C 22 28, 14 26, 16 20" stroke-width="0.9"/></svg>'''

CSS = r'''
@font-face-placeholder
:root{--burgundy:#6B1F2E;--deep:#43121D;--rose:#A8556B;--blush:#E8C4C8;--cream:#F7F1E8;--beige:#EDE3D3;--beige2:#E3D6C2;--taupe:#C9B9A3;--ink:#2E1A1F;--ink2:#6E585C;}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--cream);color:var(--ink);font-family:'Lato',sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:210mm 297mm;margin:0}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;padding:8mm 19mm 6mm;background:var(--cream)}
.page:last-child{page-break-after:auto}
h1,h2,h3,.serif{font-family:'Playfair Display',serif;font-weight:500;margin:0}
.it{font-family:'Cormorant Garamond',serif;font-style:italic}
.eyebrow{font-family:'Lato',sans-serif;font-size:7.2pt;letter-spacing:.22em;text-transform:uppercase;color:var(--rose);font-weight:700}
.orn{width:60mm;height:6mm;color:var(--burgundy);display:block;margin:0 auto}
.orn-s{width:32mm;height:4.2mm;color:var(--rose);display:block;margin:0 auto}
.rule{height:0;border-top:.25mm solid var(--taupe)}
/* header / footer */
.hdr{display:flex;justify-content:space-between;align-items:baseline;height:7mm;border-bottom:.25mm solid var(--taupe);margin-bottom:2.5mm}
.hdr .cat{font-family:'Playfair Display',serif;font-style:italic;font-size:10.5pt;color:var(--burgundy)}
.hdr .rng{font-size:7pt;letter-spacing:.2em;color:var(--ink2);text-transform:uppercase}
.ftr{position:absolute;left:19mm;right:19mm;bottom:3.5mm;height:6mm;display:flex;justify-content:space-between;align-items:center;font-size:6.8pt;letter-spacing:.14em;text-transform:uppercase;color:var(--taupe)}
.ftr .num{font-family:'Playfair Display',serif;font-size:9.5pt;letter-spacing:0;color:var(--burgundy);text-transform:none}
/* cards */
.grid{display:grid;grid-template-columns:80.5mm 80.5mm;column-gap:7mm;row-gap:4mm;justify-content:center}
.card{width:80.5mm;height:133mm;overflow:hidden}
.frame{border:.35mm solid var(--burgundy);padding:1.7mm;background:#fff;}
.frame img{display:block;width:100%;height:95.5mm;object-fit:cover;border:.2mm solid var(--taupe)}
.ct{padding-top:2.2mm}
.meta{display:flex;align-items:center;gap:2.2mm;margin-bottom:1.2mm}
.no{font-size:6.8pt;letter-spacing:.16em;color:var(--taupe);font-weight:700}
.code{font-family:'Lato',sans-serif;font-weight:700;font-size:9.6pt;color:var(--cream);background:var(--burgundy);padding:.5mm 2.4mm .7mm;border-radius:1.2mm;letter-spacing:.03em}
.title{font-family:'Playfair Display',serif;font-size:11.2pt;font-weight:600;color:var(--deep);line-height:1.15;margin-bottom:1mm}
.desc{font-size:7.8pt;line-height:1.3;color:var(--ink);margin-bottom:1.2mm}
.prompt{font-size:6.9pt;line-height:1.3;color:var(--ink2)}
.prompt b{font-weight:700;font-size:6.2pt;letter-spacing:.18em;color:var(--rose);text-transform:uppercase;margin-right:1.2mm}
.prompt i{font-style:italic}
/* tip panel */
.tip{grid-column:1/3;height:133mm;width:168mm;border:.35mm solid var(--burgundy);padding:6mm 9mm;background:var(--beige);position:relative;display:flex;flex-direction:column;justify-content:center}
.tip .corner{position:absolute;width:11mm;height:11mm;color:var(--burgundy)}
.tip .corner.tl{left:2.2mm;top:2.2mm}.tip .corner.tr{right:2.2mm;top:2.2mm;transform:scaleX(-1)}
.tip .corner.bl{left:2.2mm;bottom:2.2mm;transform:scaleY(-1)}.tip .corner.br{right:2.2mm;bottom:2.2mm;transform:scale(-1)}
.tip h3{font-size:17pt;color:var(--burgundy);margin-bottom:2.2mm;font-weight:500}
.tip p{font-size:9.4pt;line-height:1.45;margin:0 0 3.2mm;color:var(--ink);max-width:150mm}
.tip .lbl{font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:var(--rose);font-weight:700;margin-bottom:2mm}
.combos{display:flex;flex-wrap:wrap;gap:2.5mm}
.combos span{font-weight:700;font-size:9pt;color:var(--burgundy);border:.3mm solid var(--burgundy);padding:1.2mm 3.4mm;border-radius:1.2mm;background:#fff}
.strip{display:flex;gap:4.4mm;margin-top:4.5mm}
.strip div{width:34mm}
.strip img{display:block;width:100%;height:42.5mm;object-fit:cover;border:.3mm solid var(--burgundy);padding:1mm;background:#fff}
.strip span{display:block;text-align:center;font-size:7.2pt;font-weight:700;color:var(--burgundy);margin-top:1.4mm}
.strip span.o{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500;font-size:9.5pt;color:var(--ink2)}
/* cover */
.cover{padding:0;background:var(--cream)}
.cover .band{position:absolute;left:0;top:0;bottom:0;width:80mm;background:var(--burgundy)}
.cover .band2{position:absolute;left:80mm;top:0;bottom:0;width:1.2mm;background:var(--rose)}
.cover .photo{position:absolute;left:15mm;top:54mm;width:86mm;height:106.5mm;background:#fff;padding:3mm;border:.4mm solid var(--deep);box-shadow:0 8mm 18mm rgba(67,18,29,.35)}
.cover .photo img{width:100%;height:100%;object-fit:cover;display:block;border:.25mm solid var(--taupe)}
.cover .photo .cap{position:absolute;left:0;right:0;bottom:-10mm;text-align:center}
.cover .photo .cap span{font-family:'Lato',sans-serif;font-weight:700;font-size:9.5pt;color:var(--cream);background:var(--deep);padding:1mm 3.4mm;border-radius:1.2mm}
.cover .ttl{position:absolute;left:110mm;right:14mm;top:44mm}
.cover .ttl .eyebrow{color:var(--burgundy)}
.cover .big{font-family:'Playfair Display',serif;font-weight:700;font-size:100pt;line-height:.9;color:var(--burgundy);letter-spacing:-.02em;margin:5mm 0 0 -2mm}
.cover .sub1{font-family:'Playfair Display',serif;font-style:italic;font-size:24pt;color:var(--deep);margin-top:2mm;line-height:1.05}
.cover .sub2{font-size:10pt;line-height:1.55;color:var(--ink2);margin-top:7mm;max-width:80mm}
.cover .bottom{position:absolute;left:110mm;right:14mm;bottom:26mm}
.cover .feat{position:absolute;left:110mm;right:14mm;top:150mm}
.cover .feat div{font-family:'Cormorant Garamond',serif;font-size:13.5pt;color:var(--deep);line-height:1.3;padding:2.2mm 0;border-bottom:.2mm dotted var(--taupe);display:flex;gap:3mm;align-items:baseline}
.cover .feat div b{font-family:'Playfair Display',serif;font-weight:600;color:var(--burgundy);font-size:12pt}
.cover .bottom .line{font-size:7.5pt;letter-spacing:.24em;text-transform:uppercase;color:var(--burgundy);font-weight:700;margin-top:3mm;text-align:center}
.cover .band .v{position:absolute;left:8mm;bottom:14mm;transform-origin:left bottom;transform:rotate(-90deg);white-space:nowrap;font-size:8pt;letter-spacing:.32em;text-transform:uppercase;color:var(--blush)}
.cover .band .v2{position:absolute;left:8mm;top:12mm;font-family:'Playfair Display',serif;font-style:italic;font-size:14pt;color:var(--cream)}
/* intro */
.intro h1{font-size:28pt;color:var(--burgundy);line-height:1.1;margin:3mm 0 1.5mm}
.intro .lead{font-family:'Cormorant Garamond',serif;font-size:14.5pt;line-height:1.32;color:var(--ink);max-width:150mm;margin-bottom:4.5mm}
.two{display:grid;grid-template-columns:96mm 66mm;column-gap:10mm}
.steps{counter-reset:s;display:flex;flex-direction:column;gap:3.2mm;margin-top:2.5mm}
.step{display:flex;gap:4mm;align-items:flex-start}
.step .n{flex:0 0 9mm;height:9mm;border-radius:50%;border:.35mm solid var(--burgundy);color:var(--burgundy);font-family:'Playfair Display',serif;font-size:12pt;display:flex;align-items:center;justify-content:center;background:#fff}
.step .t{font-size:9.8pt;line-height:1.45}
.step .t b{font-family:'Playfair Display',serif;font-weight:600;font-size:11pt;display:block;color:var(--deep);margin-bottom:.6mm}
.box{border:.35mm solid var(--burgundy);background:var(--beige);padding:4mm 5.5mm;margin-top:4.5mm}
.box .lbl{font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:var(--rose);font-weight:700;margin-bottom:2mm}
.box .en{font-size:8.6pt;line-height:1.45;color:var(--ink);font-style:italic}
.box .uz{font-size:8.4pt;line-height:1.4;color:var(--ink2);margin-top:2.5mm}
.orig{border:.35mm solid var(--burgundy);padding:1.7mm;background:#fff}
.orig img{display:block;width:100%;border:.2mm solid var(--taupe)}
.orig .c{text-align:center;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:11pt;color:var(--burgundy);padding:2mm 0 .5mm}
.side-note{font-size:8.4pt;line-height:1.45;color:var(--ink2);margin-top:4mm}
.side-note b{color:var(--burgundy)}
.anatomy{display:flex;gap:8mm;align-items:center;margin-top:5mm;border-top:.25mm solid var(--taupe);padding-top:4mm}
.miniwrap{width:32.2mm;height:53.2mm;flex:0 0 32.2mm;position:relative}
.miniwrap .card{transform:scale(.4);transform-origin:top left;position:absolute;left:0;top:0}
.ann{flex:1}
.ann .lbl{font-size:7pt;letter-spacing:.2em;text-transform:uppercase;color:var(--rose);font-weight:700;margin-bottom:2.5mm}
.ann ul{list-style:none;margin:0;padding:0;columns:2;column-gap:6mm}
.ann li{font-size:8.6pt;line-height:1.4;margin-bottom:2.2mm;break-inside:avoid;display:flex;gap:2mm}
.ann li b{font-family:'Playfair Display',serif;color:var(--burgundy);font-weight:600;flex:0 0 4mm}
/* contents */
.toc h1{font-size:30pt;color:var(--burgundy);text-align:center;margin:6mm 0 2mm}
.toc .sub{text-align:center;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:14pt;color:var(--ink2);margin-bottom:8mm}
.toc ol{list-style:none;padding:0;margin:0 auto;width:150mm}
.toc li{display:flex;align-items:baseline;gap:3mm;padding:2.55mm 0;border-bottom:.2mm dotted var(--taupe)}
.toc li .i{font-family:'Playfair Display',serif;font-size:11pt;color:var(--rose);width:9mm}
.toc li .n{font-family:'Playfair Display',serif;font-size:13.5pt;color:var(--deep);font-weight:500}
.toc li .r{font-size:7.4pt;letter-spacing:.14em;color:var(--taupe);text-transform:uppercase;margin-left:2mm;flex:1}
.toc li .p{font-family:'Playfair Display',serif;font-size:11.5pt;color:var(--burgundy)}
.toc li.x .n{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500;font-size:14pt}
/* divider */
.div{padding:0}
.div .top{position:absolute;left:0;right:0;top:0;height:64mm;background:var(--burgundy)}
.div .top .k{position:absolute;left:19mm;top:12mm;font-family:'Playfair Display',serif;font-size:11pt;color:var(--blush);letter-spacing:.12em}
.div .top h1{position:absolute;left:19mm;right:19mm;top:22mm;font-size:34pt;color:var(--cream);line-height:1.05;font-weight:500}
.div .top .in{position:absolute;left:19mm;right:19mm;top:44mm;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:13.5pt;color:#f1dfe0;line-height:1.3;max-width:160mm}
.div .hero{position:absolute;left:19mm;top:74mm;width:106mm;height:138.5mm;background:#fff;padding:2.4mm;border:.4mm solid var(--burgundy);box-shadow:0 6mm 14mm rgba(67,18,29,.22)}
.div .hero img{width:100%;height:100%;object-fit:cover;display:block;border:.25mm solid var(--taupe)}
.div .hero .cap{position:absolute;left:0;right:0;bottom:-8mm;text-align:center}
.div .hero .cap span{font-weight:700;font-size:9.5pt;color:var(--cream);background:var(--burgundy);padding:.9mm 3.2mm;border-radius:1.2mm}
.div .list{position:absolute;left:133mm;right:19mm;top:74mm}
.div .list .lbl{font-size:7pt;letter-spacing:.22em;text-transform:uppercase;color:var(--rose);font-weight:700;margin-bottom:3mm}
.div .list ul{list-style:none;margin:0;padding:0}
.div .list li{display:flex;align-items:baseline;gap:2.2mm;padding:2.05mm 0;border-bottom:.2mm dotted var(--taupe)}
.div .list li .i{font-size:6.8pt;color:var(--taupe);width:7mm;letter-spacing:.1em}
.div .list li .c{font-weight:700;font-size:8.6pt;color:var(--burgundy)}
.div .list li .t{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:10pt;color:var(--ink2);margin-left:auto;text-align:right}
.div .list li .c{font-size:8.2pt}
.div .list li{padding:2.6mm 0}
.div .foot{position:absolute;left:19mm;right:19mm;bottom:16mm;text-align:center}
.div .foot .q{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:14pt;color:var(--burgundy);margin-top:3mm}
/* master prompt */
.mp h1{font-size:24pt;color:var(--burgundy);margin:2mm 0 1.5mm}
.mp .lead{font-size:9.4pt;line-height:1.45;color:var(--ink2);margin-bottom:4mm;max-width:172mm}
.mp .cols{column-count:2;column-gap:7mm;font-size:6.9pt;line-height:1.36;color:var(--ink)}
.mp .cols p{margin:0 0 1.5mm;break-inside:avoid}
.mp .cols p b{color:var(--burgundy)}
.mp .head{font-size:7.4pt;line-height:1.4;font-style:italic;color:var(--ink);border:.3mm solid var(--burgundy);background:var(--beige);padding:3mm 4mm;margin-bottom:4mm}
/* closing */
.end{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 30mm}
.end h1{font-size:40pt;color:var(--burgundy);margin:6mm 0 4mm}
.end p{font-family:'Cormorant Garamond',serif;font-size:15pt;line-height:1.4;color:var(--ink);max-width:130mm;margin:0 0 4mm}
.end .small{font-family:'Lato',sans-serif;font-size:8.4pt;color:var(--ink2);line-height:1.5;max-width:120mm;margin-top:10mm}
.end .sig{font-size:7.5pt;letter-spacing:.26em;text-transform:uppercase;color:var(--rose);font-weight:700;margin-top:14mm}
'''


def footer(page_no):
    return ('<div class="ftr"><span>150 ta ChatGPT kod</span><span class="num">%d</span><span>Romantik-klassik nashr · 2026</span></div>' % page_no)


def card(c):
    src, missing = book_image(c)
    flag = ' data-missing="1"' if missing else ''
    return ('<div class="card"%s><div class="frame"><img src="%s" alt=""></div><div class="ct">'
            '<div class="meta"><span class="no">№ %03d</span><span class="code">/%s</span></div>'
            '<div class="title">%s</div><div class="desc">%s</div>'
            '<div class="prompt"><b>Prompt</b><i>%s %s</i></div></div></div>'
            % (flag, src, c['id'], c['code'], esc(c['title_uz']), esc(c['desc_uz']), esc(c['prompt_en']), SUFFIX))


def tip_panel(cat, hero_code):
    t, combos = TIPS[cat['slug']]
    corners = ''.join(CORNER % k for k in ('tl', 'tr', 'bl', 'br'))
    pills = ''.join('<span>%s</span>' % esc(x) for x in combos)
    codes = BY_CAT[cat['slug']]
    picks = [codes[i] for i in (0, 4, 8)]
    strip = '<div><img src="img/original.jpg" alt=""><span class="o">Asl surat</span></div>' + ''.join(
        '<div><img src="%s" alt=""><span>/%s</span></div>' % (book_image(c)[0], c['code']) for c in picks)
    return ('<div class="tip">%s<div class="lbl">Pro maslahat · %s</div><h3>Yanada yaxshi natija uchun</h3><p>%s</p>'
            '<div class="lbl">Tavsiya etilgan kombinatsiyalar</div><div class="combos">%s</div>'
            '<div class="lbl" style="margin-top:4.5mm">Taqqoslang: asl surat va bo‘limning uchta kodi</div><div class="strip">%s</div></div>'
            % (corners, esc(cat['name_uz']), esc(t), pills, strip))


def content_page(cat, cards, rng, page_no, tip=False, hero_code=None):
    body = ''.join(card(c) for c in cards)
    if tip:
        body += tip_panel(cat, hero_code)
    return ('<section class="page"><div class="hdr"><span class="cat">%s</span><span class="rng">Kodlar %s</span></div>'
            '<div class="grid">%s</div>%s</section>' % (esc(cat['name_uz']), rng, body, footer(page_no)))


def divider_page(cat, codes, page_no):
    hero = next(c for c in codes if c['code'] == HERO_PICK[cat['slug']])
    src, _ = book_image(hero, size=(900, 1125), name='hero_%02d.jpg' % cat['index'], quality=82)
    items = ''.join('<li><span class="i">%03d</span><span class="c">/%s</span><span class="t">%s</span></li>' % (c['id'], c['code'], esc(c['title_uz'])) for c in codes)
    return ('<section class="page div"><div class="top"><div class="k">%02d / 15</div><h1>%s</h1><div class="in">%s</div></div>'
            '<div class="hero"><img src="%s" alt=""><div class="cap"><span>/%s</span></div></div>'
            '<div class="list"><div class="lbl">Bu bo‘limdagi kodlar</div><ul>%s</ul></div>'
            '<div class="foot">%s<div class="q">%s</div></div>%s</section>'
            % (cat['index'], esc(cat['name_uz']), esc(cat['intro_uz']), src, hero['code'], items, ORN_SMALL, esc(cat['name_en']), footer(page_no)))


def cover_page():
    c = next(x for x in CODES if x['code'] == COVER_CODE)
    src, _ = book_image(c, size=(960, 1200), name='cover.jpg', quality=84)
    return ('<section class="page cover"><div class="band"><div class="v2">Romantik-klassik nashr</div><div class="v">ChatGPT · rasm tahriri · 2026</div></div><div class="band2"></div>'
            '<div class="photo"><img src="%s" alt=""><div class="cap"><span>/%s</span></div></div>'
            '<div class="ttl"><div class="eyebrow">ChatGPT · rasm tahriri</div><div class="big">150</div>'
            '<div class="sub1">ta maxsus<br>/kod</div>'
            '<div class="sub2">Rasmlaringizni ChatGPT yordamida professional tahrirlash uchun tayyor buyruqlar to‘plami. Har bir kod — namunali natija bilan.</div></div>'
            '<div class="feat"><div><b>15</b> bo‘lim · <b>150</b> tayyor kod</div><div>Har bir kod uchun namunali natija</div><div>ChatGPT uchun inglizcha promptlar</div><div>Master prompt — barcha kodlar bitta xabarda</div></div>'
            '<div class="bottom">%s<div class="line">Professional gayd</div></div></section>' % (src, c['code'], ORN))


def intro_page(page_no):
    steps = [
        ('ChatGPT’ni oching va rasmingizni yuklang', 'Suhbatda «+» (biriktirish) tugmasini bosib, tahrir qilmoqchi bo‘lgan suratni tanlang. Rasm sifati qanchalik yaxshi bo‘lsa, natija shunchalik chiroyli.'),
        ('Gayddan yoqqan kodni tanlang', 'Har bir kod yonida namunali natija turibdi — masalan, <b style="display:inline;font-family:Lato;font-size:9.8pt;color:var(--burgundy)">/golden_hour</b>. Bo‘limlar bo‘yicha o‘zingizga kerakli uslubni toping.'),
        ('Kodni va promptni yuboring', 'Rasm bilan birga kodni va uning yonidagi inglizcha promptni ko‘chirib yuboring. Kod — sizning ko‘rsatmangiz, prompt — ChatGPT uchun aniq texnik tavsif.'),
        ('Natijani yuklab oling va sozlang', 'Natija yoqmasa: «stronger», «softer», «more natural» yoki «keep the background» kabi qisqa izohlar bilan sozlang. Ikki kodni birga ham yozish mumkin.'),
    ]
    steps_html = ''.join('<div class="step"><div class="n">%d</div><div class="t"><b>%s</b>%s</div></div>' % (i + 1, esc(a), b) for i, (a, b) in enumerate(steps))
    return ('<section class="page intro"><div class="eyebrow">Gayd haqida</div><h1>Bu gayd qanday ishlaydi</h1>'
            '<div class="lead">Bu gayddagi har bir <span style="font-family:Lato;font-weight:700;font-style:normal;font-size:12pt;color:var(--burgundy)">/kod</span> — ChatGPT’ga rasm tahriri uchun beriladigan tayyor buyruq. '
            'Kod yonida shu buyruq qo‘llangan namuna surat turibdi: siz natijani oldindan ko‘rasiz, keyin o‘z rasmingizga qo‘llaysiz.</div>'
            '<div class="two"><div><div class="eyebrow">Qanday ishlatiladi</div><div class="steps">%s</div>'
            '<div class="box"><div class="lbl">Boshlang‘ich prompt — suhbat boshida bir marta yuboring</div><div class="en">%s</div>'
            '<div class="uz">Bu matn ChatGPT’ga sizning yuzingiz, kiyimingiz va ro‘molingizni o‘zgartirmasdan faqat uslubni qo‘llashni o‘rgatadi.</div></div></div>'
            '<div><div class="orig"><img src="img/original.jpg" alt=""><div class="c">Asl surat</div></div>'
            '<div class="side-note"><b>Barcha 150 ta namuna</b> aynan shu bitta suratdan yaratilgan — shuning uchun kodlar orasidagi farqni aniq ko‘rasiz. '
            'Sizning suratingizda natija nur va sifatga qarab biroz farq qilishi mumkin.</div>'
            '<div class="side-note"><b>Master prompt.</b> Gayd oxirida barcha 150 kod bitta ro‘yxatda berilgan: uni ChatGPT’ga bir marta yuborsangiz, keyin har safar faqat kodni yozish kifoya.</div></div></div>'
            '<div class="anatomy"><div class="miniwrap">%s</div><div class="ann"><div class="lbl">Karta qanday o‘qiladi</div><ul>'
            '<li><b>1</b><span><b style="font-family:Lato;font-size:8.6pt">№</b> — kodning tartib raqami (001–150).</span></li>'
            '<li><b>2</b><span><b style="font-family:Lato;font-size:8.6pt">/kod</b> — ChatGPT’ga yuboriladigan buyruq.</span></li>'
            '<li><b>3</b><span><b style="font-family:Playfair Display;font-size:9pt">Nom va tavsif</b> — natija qanday ko‘rinishini o‘zbekcha tushuntiradi.</span></li>'
            '<li><b>4</b><span><b style="font-family:Lato;font-size:8.6pt">Prompt</b> — tayyor inglizcha matn: kod bilan birga ko‘chirib yuboring.</span></li>'
            '</ul></div></div>%s</section>'
            % (steps_html, esc(STARTER_PROMPT), card(CODES[0]), footer(page_no)))


def toc_page(entries, page_no):
    lis = ''.join('<li class="%s"><span class="i">%s</span><span class="n">%s</span><span class="r">%s</span><span class="p">%d</span></li>' % (cls, i, esc(n), r, p) for cls, i, n, r, p in entries)
    return ('<section class="page toc"><div class="eyebrow" style="text-align:center">Mundarija</div><h1>15 bo‘lim · 150 kod</h1>'
            '<div class="sub">Har bir bo‘lim: tanishuv sahifasi, 10 ta kod va pro maslahat</div>%s<ol style="margin-top:6mm">%s</ol>%s</section>' % (ORN, lis, footer(page_no)))


def master_pages(start_page):
    lines = ['<p><b>/%s</b> — %s</p>' % (c['code'], esc(c['prompt_en'])) for c in CODES]
    chunks = [lines[i:i + 50] for i in range(0, 150, 50)]
    head = ('From now on you are my photo editor. I will send a photo followed by one or more codes from the list below (for example: /golden_hour). '
            'Apply exactly the style described for that code. Always keep the face, identity, expression, body, hijab/hair and clothing unchanged; '
            'edit only lighting, colour, texture, background or frame. Return the edited photo at the same resolution and aspect ratio. Codes:')
    out = []
    for i, ch in enumerate(chunks):
        first = i == 0
        out.append('<section class="page mp">' + ('<div class="eyebrow">Ilova</div><h1>Master prompt — barcha kodlar bitta xabarda</h1>'
                   '<div class="lead">Quyidagi matnni (uch sahifa) ChatGPT’ga bir marta yuboring. Shundan keyin rasm bilan birga faqat kodni yozasiz — masalan, «/polaroid» — va ChatGPT ro‘yxatdagi tavsifni o‘zi qo‘llaydi.</div>'
                   '<div class="head">%s</div>' % esc(head) if first else '<div class="hdr"><span class="cat">Master prompt</span><span class="rng">davomi · %d / 3</span></div>' % (i + 1))
                   + '<div class="cols">%s</div>%s</section>' % (''.join(ch), footer(start_page + i)))
    return out, start_page + len(chunks)


def end_page(page_no):
    return ('<section class="page end">%s<h1>Rahmat!</h1>'
            '<p>Har bir kod — bu boshlang‘ich nuqta. O‘z so‘zlaringizni qo‘shing, kodlarni birlashtiring va faqat sizga xos uslubni yarating.</p>'
            '<p>Gayd yoqqan bo‘lsa, uni do‘stlaringiz bilan ulashing — chiroyli suratlar ko‘paysin.</p>'
            '<div class="small">Namunalar bitta asl suratdan yaratilgan; ChatGPT natijasi sizning suratingiz nuri, sifati va so‘rovingizga qarab farq qilishi mumkin. '
            'Boshqa odamlarning suratlarini faqat ularning roziligi bilan tahrirlang.</div>'
            '<div class="sig">150 ta ChatGPT kod · Romantik-klassik nashr</div>%s</section>' % (ORN, footer(page_no)))


def build():
    # original for the intro page
    orig_out = os.path.join(IMG, 'original.jpg')
    if not os.path.exists(orig_out):
        Image.open(os.path.join(ROOT, 'source', 'crop.jpg')).resize((720, 900), Image.LANCZOS).save(orig_out, quality=86)
    pages = []
    page_no = 1
    pages.append(cover_page()); page_no += 1
    pages.append(intro_page(page_no)); page_no += 1
    toc_no = page_no; page_no += 1  # contents placeholder
    toc_entries = []
    for cat in CATS:
        codes = BY_CAT[cat['slug']]
        toc_entries.append(('', '%02d' % cat['index'], cat['name_uz'], 'kod %03d – %03d' % (codes[0]['id'], codes[-1]['id']), page_no))
        pages.append(divider_page(cat, codes, page_no)); page_no += 1
        hero = HERO_PICK[cat['slug']]
        for i in range(0, 10, 4):
            chunk = codes[i:i + 4]
            rng = '%03d – %03d' % (chunk[0]['id'], chunk[-1]['id'])
            pages.append(content_page(cat, chunk, rng, page_no, tip=(len(chunk) == 2), hero_code=hero)); page_no += 1
    mp, page_no = master_pages(page_no)
    toc_entries.append(('x', '', 'Master prompt — barcha kodlar bitta xabarda', 'ilova', mp and page_no - len(mp)))
    pages.extend(mp)
    toc_entries.append(('x', '', 'Yakuniy so‘z', '', page_no))
    pages.append(end_page(page_no))
    pages.insert(2, toc_page(toc_entries, toc_no))
    fonts_css = open(os.path.join(BOOK, 'fonts.css')).read()
    doc = ('<!doctype html><html lang="uz"><head><meta charset="utf-8"><title>150 ta ChatGPT kod</title><style>%s</style></head><body>%s</body></html>'
           % (CSS.replace('@font-face-placeholder', fonts_css), ''.join(pages)))
    open(os.path.join(BOOK, 'index.html'), 'w').write(doc)
    missing = [c['code'] for c in CODES if not os.path.exists(render_path(c))]
    print('index.html written: %d pages; %d renders missing%s' % (len(pages), len(missing), (': ' + ', '.join(missing[:12]) + (' …' if len(missing) > 12 else '')) if missing else ''))


if __name__ == '__main__':
    build()
