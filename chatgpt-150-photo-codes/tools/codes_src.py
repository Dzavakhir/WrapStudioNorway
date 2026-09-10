# -*- coding: utf-8 -*-
"""Master list of the 150 codes. Run: python3 tools/codes_src.py  -> writes codes.json"""
import json, os

CATS = [
    # (slug, uz name, en name, uz intro)
    ('yoruglik', 'Yorug‘lik', 'Lighting',
     'Nur — portretning kayfiyati. Bitta kod bilan oddiy selfini oltin soat, studiya yoki sham nuriga o‘tkazasiz.'),
    ('plyonka', 'Plyonka & Vintage', 'Film & Vintage',
     'Analog plyonka uslublari: Kodak iliqligi, Polaroid xiraligi, donador tekstura va eski suratlar nafosati.'),
    ('kino', 'Kinematik', 'Cinematic',
     'Kino kadrlari kabi: teal-orange gradatsiya, noir soyalar, keng ekran va dramatik kontrast.'),
    ('oq_qora', 'Oq-qora', 'Black & White',
     'Klassik monoxrom — rangni olib tashlab, his-tuyg‘u, nur va shaklni birinchi o‘ringa qo‘yamiz.'),
    ('rang', 'Rang gradatsiyasi', 'Colour Grading',
     'Rang palitrasi bilan ishlash: iliq, sovuq, pastel, to‘yingan yoki xira tuslar.'),
    ('romantik', 'Romantik', 'Romantic',
     'Yumshoq nur, mayin porlash, pushti tuslar — nafis va orzuli portretlar uchun.'),
    ('estetika', 'Estetika', 'Aesthetic Trends',
     'Ijtimoiy tarmoqlardagi eng mashhur estetikalar: dark academia, old money, coquette va boshqalar.'),
    ('retush', 'Portret retush', 'Portrait Retouch',
     'Professional retush: silliq teri, yorqin ko‘zlar, oq tishlar, yuz konturi — tabiiylikni saqlagan holda.'),
    ('fon', 'Fon', 'Background',
     'Fonni o‘zgartiring: studiya, gradient, bokeh yoki qog‘oz — odam o‘zgarmaydi, muhit o‘zgaradi.'),
    ('badiiy', 'Badiiy', 'Artistic',
     'Suratni san’at asariga aylantiring: moyli rasm, akvarel, qalam eskizi, pop-art va komiks.'),
    ('ramka', 'Ramkalar', 'Frames',
     'Polaroid, plyonka lentasi, jurnal muqovasi, vintage ramka — surat uchun tayyor «kiyim».'),
    ('effekt', 'Effektlar', 'Effects',
     'Glitch, VHS, ikki ekspozitsiya, prizma, linza chaqnashi — surat uchun kuchli vizual effektlar.'),
    ('mavsum', 'Mavsum & ob-havo', 'Season & Weather',
     'Bir surat — to‘rt fasl: kuz oltini, qish sovug‘i, bahor nafasi, yoz quyoshi, yomg‘ir va tuman.'),
    ('tekstura', 'Tekstura & nur o‘yini', 'Texture & Light Play',
     'Chang, qog‘oz, bokeh, uchqunlar, jalyuzi va barg soyalari — suratga chuqurlik beruvchi qatlamlar.'),
    ('ijodiy', 'Ijodiy', 'Creative',
     'Duotone, neon, kiberpank, retro-poster, rizograf — jasur va zamonaviy tajribalar.'),
]

# (code, category index, uz title, uz description, en prompt, implementation hint for the designer-agent)
C = []
def add(*a): C.append(a)

# ---------------------------------------------------------------- 1 Yorug‘lik (Lighting)
add('golden_hour', 0, 'Oltin soat', 'Quyosh botishidan oldingi iliq, oltin nur. Teri yumshoq porlaydi, soyalar iliq jigarrang tusga kiradi.',
    'Apply a golden-hour look: warm low sunlight from the side, soft golden glow on the skin, gentle haze and warm brown shadows.',
    'temperature +0.35; split_tone shadows #5a3626 / highlights #ffd27a strength .4; directional warm light: screen a linear() gradient from top-right tinted #ffb15a; glow(sigma 40, .35, .55); vignette .2 warm (#2a1608). Skin must stay natural, not orange-saturated.')
add('soft_light', 0, 'Yumshoq nur', 'Bulut orqali o‘tgan tarqoq, tekis nur. Qattiq soyalar yo‘qoladi, teri tekis va mayin ko‘rinadi.',
    'Relight the photo with soft, diffused light: no harsh shadows, gentle contrast, even skin, airy and clean.',
    'lift shadows with curve [(0,.06),(.3,.36),(1,.97)]; contrast .9; lighten face_skin slightly (+.04 via mask); orton(sigma 20, .3); slight desat .92; NO vignette. Must look brighter and creamier than the original.')
add('studio_light', 0, 'Studiya nuri', 'Professional studiya: toza, neytral fon, yuzga yo‘naltirilgan asosiy nur va aniq detallar.',
    'Turn this into a professional studio portrait: neutral dark-grey seamless backdrop, key light on the face, crisp detail, clean colours.',
    'replace_background with a dark grey radial gradient (#3a3436 centre behind head -> #1c1a1b edges, use radial() centred slightly above face_center); clarity .3; brighten face via radial mask centred on face (+.08); catchlight: slight brighten on iris mask; rim: edge_band(person) screen at .25 white. Keep subject colours natural.')
add('rim_light', 0, 'Kontur nuri', 'Orqadan tushayotgan nur odamning silueti bo‘ylab yorqin chiziq hosil qiladi — chuqurlik va hajm beradi.',
    'Add a backlight rim light: a bright warm-white edge of light tracing the outline of the hair/hijab and shoulders, background slightly darker.',
    'darken background (bg mask) by .35 and cool it slightly; rim = inner_edge(mask("person"), width 16, softness 7) * linear(angle 45 from top-right) -> screen with warm white #ffe9c4 at .9; add faint glow(blur of the rim). Rim must be clearly visible along hijab/shoulders.')
add('window_light', 0, 'Deraza nuri', 'Derazadan tushayotgan yumshoq kunduzgi nur va jalyuzi soyalari — tinch, uy muhiti.',
    'Relight with soft window light: gentle directional daylight from the left with faint venetian-blind shadow bands across the scene.',
    'stripes(angle 12, period 120, duty .45, softness 14) darkening at .35 (multiply), skip strongest darkening on the face (reduce by face mask *.5); light gradient from left screen #fff2dc .25; temperature +.12; contrast .95; subtle glow. Bands should read as real window light, not a texture overlay.')
add('candle_light', 0, 'Sham nuri', 'Issiq, xira sham nuri: yuz iliq-oltin, atrof qorong‘i va shirin romantik kayfiyat.',
    'Relight as if lit only by candlelight: warm orange-amber glow on the face, dark soft surroundings, intimate mood, gentle grain.',
    'darken overall exposure -1.1 stops except a radial warm light centred low-left of face (radius .55, softness .8) that keeps face near original brightness; temperature +.55; split_tone #2a0e05 / #ffb050 .5; glow .3; grain .06; vignette .5 #150804. Face must remain clearly visible.')
add('moonlight', 0, 'Oy nuri', 'Tungi sovuq ko‘k oy nuri: kumushrang yorug‘lik, chuqur soyalar va sirli sokinlik.',
    'Relight as a moonlit night: cool blue-silver light, deep soft shadows, desaturated colours, calm mysterious mood.',
    'exposure -1.2; temperature -.5; saturation .55; split_tone #0b1a3a / #cfe0ff .45; radial silver light from top-left (screen #dbe8ff .3); soft moon disc glow in top-left corner (radial small + blur); glow .25; grain .04; vignette .45 #05091a.')
add('sunset_glow', 0, 'Quyosh botishi', 'Pushti-apelsin quyosh botishi nuri: osmon shaftoli rangda, yuzda iliq shu’la.',
    'Add a sunset glow: peach-pink and orange light from behind, warm skin, soft flare and a pastel purple tint in the shadows.',
    'gradient overlay: linear(angle 90) top #ff9a6a -> bottom #7a4b8a screened at .45 (stronger on background mask); temperature +.3; split_tone #4a2a5c / #ffbe8a .45; lens_flare small at top-right (strength .5, no ghosts); glow .35.')
add('overcast', 0, 'Bulutli kun', 'Bulutli kunning sovuq, tekis va yumshoq nuri — minimalistik, tinch, skandinav uslubi.',
    'Make the light overcast: cool even daylight, low contrast, muted colours, soft grey-blue mood, no harsh highlights.',
    'temperature -.25; saturation .75; contrast .85 pivot .55; fade .05; curve pull highlights [(0,0),(.8,.74),(1,.93)]; slight blue in shadows via color_balance shadows (-.02,0,.04). Should read clearly cooler and flatter than the original.')
add('spotlight', 0, 'Projektor', 'Sahna projektori: faqat yuz yoritilgan, atrof qorong‘ilikka cho‘kadi — dramatik va teatral.',
    'Light the portrait with a single dramatic spotlight on the face; everything around falls into deep darkness, theatrical mood.',
    'light = radial(centre face_center, radius .5, softness .75); img = lerp(img*0.08, img*1.05, light); slight warm tint on the lit area; glow .2; grain .04. Face fully lit, edges near black but with soft falloff (not a hard circle).')

# ---------------------------------------------------------------- 2 Plyonka & Vintage
add('kodak_gold', 1, 'Kodak Gold', 'Mashhur Kodak Gold plyonkasi: iliq sariq-oltin tuslar, yumshoq qizil ranglar, yengil donadorlik.',
    'Emulate Kodak Gold 200 film: warm golden-yellow highlights, soft saturated reds, slightly lifted shadows, fine film grain.',
    'per-channel curves: r [(0,.02),(.5,.55),(1,1)], g [(0,.02),(.5,.52),(1,.98)], b [(0,.06),(.5,.46),(1,.9)]; hsl_adjust green hue 120 -> shift +15 sat .9 (greens go yellowish); vibrance .2; grain .05; slight warm vignette. Distinctly golden vs original.')
add('fuji_film', 1, 'Fuji plyonka', 'Fujifilm uslubi: yashil-moviy salqin tuslar, mayin teri va nostalgik ko‘rinish.',
    'Emulate Fujifilm colour negative: cool minty greens, soft cyan highlights, muted magenta shadows, gentle film grain.',
    'hsl_adjust greens 120 width 45 shift -10 sat 1.15 lum +.05 (mint); split_tone #3a2a45 / #cfeee0 .4; curves b [(0,.05),(.5,.52),(1,.97)]; saturation .9; fade .06; grain .05.')
add('polaroid', 1, 'Polaroid', 'Tezkor Polaroid surat: xira, iliq-salqin aralash tuslar, past kontrast va klassik oq ramka.',
    'Make it look like an instant Polaroid photo: washed-out faded colours, slight cyan-yellow cast, low contrast, classic white instant-film frame.',
    'look: fade .12, saturation .8, temperature +.1 with slight cyan in highlights (color_balance highlights (-.03,0,.03)), vignette .25, grain .05. Then paste() onto a beige canvas with paper(): photo size ~ (760, 950) white border 46 and bottom border 190, rotate -3, drop shadow. Add a tiny handwritten-style caption (cormorant-italic) on the bottom border e.g. "yoz ‘26".')
add('film_grain', 1, 'Plyonka donadorligi', 'Ko‘rinarli nozik plyonka donalari va biroz xira ranglar — haqiqiy analog tuyg‘u.',
    'Add authentic visible film grain across the photo, slightly muted colours and a touch of softness like real 35mm film.',
    'grain amount .13 size 1.6 mono; saturation .88; fade .05; unsharp tiny; slight warm. Grain must be clearly visible at full size but not noisy-ugly.')
add('vintage_90s', 1, '90-yillar', '90-yillar kompakt kamerasi: flesh nuri, sarg‘ish tus va burchakdagi orange sana tamg‘asi.',
    'Recreate a 1990s point-and-shoot snapshot: flash-lit look, warm yellowish cast, slight overexposure, soft focus and an orange date stamp in the corner.',
    'exposure +.25 with highlights compressed; temperature +.3; slight green tint -.08; soft_focus mix .25; grain .06; vignette .2; draw date stamp "’96 8 15" bottom-right in orange #ff8a1e using lato-bold ~54px, tracking 4, with a soft glow (shadow same colour, blur 5). ')
add('faded_film', 1, 'Xira plyonka', 'Matoviy, xira qoralar va pastel ranglar — vaqt o‘tgan surat kabi mayin ko‘rinish.',
    'Give the photo a faded matte film look: lifted milky blacks, softened whites, pastel muted colours, gentle warmth.',
    'fade .16 highlight .07; saturation .72; temperature +.08; contrast .9; grain .04; slight rose in shadows (color_balance shadows (.03,0,.01)).')
add('cinestill', 1, 'CineStill 800T', 'Tungi kino plyonkasi: yorqin joylar atrofida qizil halo (halation), volfram tuslari.',
    'Emulate CineStill 800T film: tungsten-balanced cool tones with red-orange halation glowing around bright highlights, cinematic night feel.',
    'temperature -.2 base with warm highlights (split_tone #16233f / #ffd9a0 .35); halation(sigma 50, strength .75, #ff4a2a, threshold .62) — halo must be visible around sky patches/bright spots; contrast 1.08; grain .05.')
add('sepia', 1, 'Sepiya', 'Klassik sepiya: jigarrang monoxrom, yumshoq kontrast va nozik vinetka.',
    'Convert to a classic sepia-toned photograph: warm brown monochrome, soft contrast, gentle vignette.',
    'sepia strength 1; curve s_curve .12; vignette .35 #1a0e06; grain .04; tiny fade .04.')
add('old_photo', 1, 'Eski surat', 'Eskirgan surat: sarg‘aygan qog‘oz, tirnalishlar, chang, xiralashgan burchaklar.',
    'Age the photo like a photograph from decades ago: yellowed faded tones, scratches, dust specks, worn soft corners and paper texture.',
    'tone #c8a878 strength .85 + fade .14; multiply paper(strength .25); screen scratches(30) at .45 and dust(600) at .5; vignette .5 #3a2a14 softness .9; soft_focus .2; darken/blotch corners with fbm-based stains multiply (.15). Must clearly read as aged.')
add('light_leak', 1, 'Nur sizishi', 'Plyonka kamerasidagi nur sizishi: chetdan kirgan olovrang-qizil shu’la.',
    'Add an analog light leak: warm orange-red light bleeding in from one edge, slightly faded film colours.',
    'light_leak(#ff6a2a, side right, strength .8) + a second smaller pink leak top-left (#ff9ac0 .4); fade .08; grain .04; saturation .95. The leak must be obvious.')

# ---------------------------------------------------------------- 3 Kinematik
add('teal_orange', 2, 'Teal & Orange', 'Gollivud gradatsiyasi: soyalar ko‘k-yashil, teri apelsin tusda — kino kadri.',
    'Apply the classic Hollywood teal-and-orange colour grade: teal shadows, warm orange skin tones, punchy cinematic contrast.',
    'split_tone #0f4d5c / #ff9b45 strength .55; hsl_adjust greens 120 width 50 shift +25 sat .7 (foliage toward teal-olive); s_curve .15; skin protect: reduce effect on face_skin by 30%.')
add('noir', 2, 'Noir', 'Film-noir: chuqur qora soyalar, yuqori kontrastli oq-qora va sirli kayfiyat.',
    'Turn it into a film-noir still: high-contrast black and white, deep blacks, dramatic shadows, subtle grain.',
    'bw(.25,.6,.15); s_curve .35; levels black .06 white .95; a diagonal shadow band across bottom-left (multiply .35 via linear mask); vignette .55; grain .07.')
add('moody', 2, 'Kayfiyatli (moody)', 'Qorong‘i, xira, yashil-ko‘k tusli “moody” gradatsiya — chuqur va his-tuyg‘uli.',
    'Give it a dark moody grade: darker exposure, desaturated greens and teals in the shadows, soft contrast, atmospheric mood.',
    'exposure -.5; saturation .65; split_tone #12302e / #c9b8a0 .4; hsl_adjust greens shift -10 sat .6 lum -.08; fade .05; vignette .45; clarity .15.')
add('widescreen', 2, 'Keng ekran', 'Kino formatidagi qora chiziqlar va nafis kino gradatsiyasi — kadr filmdan olingan kabi.',
    'Present the photo as a cinematic movie frame: widescreen black bars, film-like colour grade, slight grain.',
    'letterbox to visible ratio 1.0 (bars ~144px top/bottom black); inside: split_tone #1d3a4a / #f0b070 .35, s_curve .12, grain .05, slight vignette. Optional small subtitle text centred just above the lower bar in lato ~30px white: "— bu yerda hikoya boshlanadi".')
add('blockbuster', 2, 'Blokbaster', 'Katta byudjetli film uslubi: kuchli kontrast, sovuq yorug‘ joylar, iliq teri, keskin detallar.',
    'Grade like a big-budget action film: strong contrast, crushed blacks, cool highlights with warm skin, sharp crisp detail.',
    's_curve .3; levels black .05; split_tone #10253a / #ffc18a .45; clarity .45; sharpen .5; saturation 1.05; grain .03.')
add('pastel_film', 2, 'Pastel film', 'Simmetrik “pastel kino” estetikasi: pushti, yalpiz, sariq — yumshoq va nostaljik.',
    'Grade in a whimsical pastel film style: soft pink and mint palette, lifted shadows, low contrast, gentle yellow highlights.',
    'fade .12; contrast .85; hsl_adjust greens shift -25 sat .8 lum +.1 (mint); split_tone #d9a0b8 / #fff0b8 .45; saturation .9; brightness +.04.')
add('neo_noir', 2, 'Neo-noir', 'Neon shahar tuni: bir tomondan pushti-magenta, boshqa tomondan moviy nur — zamonaviy noir.',
    'Relight as neo-noir: night-dark base with magenta neon light from one side and cyan-blue from the other, glossy high contrast.',
    'exposure -.9; saturation .7; screen linear(angle 0) left->right magenta #ff2a8a .55 (weighted to left) and cyan #22c8ff .55 (weighted to right) using edge/person emphasis: multiply the neon layers by (0.5 + 0.5*inner_edge(person)); s_curve .2; glow .3; grain .04.')
add('bleach_bypass', 2, 'Bleach bypass', 'Kumushrang, kuchli kontrastli, kam to‘yingan “bleach bypass” kino texnikasi.',
    'Apply a bleach-bypass film effect: strongly desaturated silvery tones with high contrast and gritty detail.',
    'saturation .35; overlay gray(img) onto img at .7; s_curve .25; clarity .3; grain .07; slight cool.')
add('anamorphic', 2, 'Anamorf', 'Anamorf linza: gorizontal ko‘k chaqnash chizig‘i va oval bokeh — haqiqiy kino optikasi.',
    'Add anamorphic lens character: a horizontal blue lens-flare streak across the frame at eye level, oval bokeh and a subtle cinematic grade.',
    'blur_background sigma 10 (mild) then stretch bokeh: apply motion_blur(length 20, angle 0) to background only; blue streak: gaussian band across full width at eye level (y = eye_r y), thickness ~12px core + 60px soft, colour #3e8cff, screen .9; teal/orange .3; letterbox 1.0 optional (do not).')
add('epic_dark', 2, 'Epik fantaziya', 'Epik fantaziya filmi: sovuq soyalar, oltin yorug‘lik, kam to‘yingan dramatik gradatsiya.',
    'Grade like an epic dark fantasy film: desaturated cold shadows, golden highlights, dramatic vignette and crisp detail.',
    'saturation .6; split_tone #0e1a2e / #d9a64a .55; s_curve .2; clarity .4; vignette .5; rays() from top-right screen .25 gold; grain .04.')

# ---------------------------------------------------------------- 4 Oq-qora
add('bw_classic', 3, 'Klassik oq-qora', 'Muvozanatli, toza klassik oq-qora portret — har doim dolzarb.',
    'Convert to a classic balanced black-and-white portrait with natural tonal range and clean detail.',
    'bw(.3,.59,.11); s_curve .1; slight clarity .15. Nothing else.')
add('bw_contrast', 3, 'Kontrastli oq-qora', 'Yuqori kontrast: to‘q qoralar, yorqin oqlar, keskin, jasur portret.',
    'Convert to high-contrast black and white: deep blacks, bright whites, punchy and bold.',
    'bw(.35,.5,.15); s_curve .35; levels black .05 white .96; clarity .35; sharpen .3.')
add('bw_soft', 3, 'Yumshoq oq-qora', 'Havodor, yorug‘ va mayin oq-qora — yumshoq soyalar va yengil porlash.',
    'Convert to a soft, airy high-key black and white: light tones, gentle shadows, subtle glow.',
    'bw; fade .1; brightness +.06; contrast .9; glow .3 threshold .5; NO vignette.')
add('bw_film', 3, 'Oq-qora plyonka', 'Donador oq-qora plyonka (Ilford uslubi): boy yarim tuslar va analog tekstura.',
    'Convert to grainy black-and-white 35mm film (Ilford style): rich midtones, visible grain, slight vignette.',
    'bw(.28,.6,.12); s_curve .18; grain .12 size 1.5; vignette .35; fade .04.')
add('red_pop', 3, 'Qizil urg‘u', 'Surat oq-qora, faqat qizil ranglar (kiyim, lablar) rangli qoladi — kuchli vizual urg‘u.',
    'Make the photo black and white but keep only the red colours (the red sleeve and lips) in full colour.',
    'isolate_hue(hue 0, width 28) — verify the red sleeve and lips stay red and everything else is grey; boost kept reds sat 1.15; s_curve .1.')
add('silver', 3, 'Kumush', 'Kumush-jelatin bosma: salqin kumushrang tuslar, boy yarim tonlar, qog‘oz oqligi.',
    'Convert to a silver-gelatin print look: cool silvery tones, rich midtones, paper-white highlights.',
    'bw; split_tone #1a2230 / #e8eef5 .35 (cool); s_curve .15; levels white .97; very fine grain .03.')
add('bw_matte', 3, 'Matoviy oq-qora', 'Matoviy, xira qoralar bilan oq-qora — zamonaviy tahririy uslub.',
    'Convert to a matte black and white: lifted faded blacks, softened whites, modern editorial feel.',
    'bw; fade .17 highlight .06; contrast .95; grain .03.')
add('bw_glow', 3, 'Porloq oq-qora', 'Nurli, yuqori kalitli oq-qora: yorug‘ joylar mayin porlaydi.',
    'Convert to a glowing high-key black and white with soft bloom on the highlights.',
    'bw; brightness +.05; glow(35, .6, .5); orton .25; contrast .95.')
add('bw_infrared', 3, 'Infraqizil', 'Infraqizil surat: barglar oppoq, osmon qora, yuz mayin porlaydi — sirli ko‘rinish.',
    'Simulate infrared black-and-white photography: foliage turns bright white, sky goes dark, skin glows softly.',
    'lighten greens strongly before bw: hsl_adjust hue 120 width 50 lum +.6 sat 0; darken blues/cyan hue 210 width 50 lum -.5; then bw(.2,.7,.1); glow .35; grain .05; s_curve .1. Foliage must be near white.')
add('bw_warm', 3, 'Iliq oq-qora', 'Selen tusli iliq-jigarrang oq-qora — klassik va nafis.',
    'Convert to a warm-toned black and white (selenium/brown tint), classic and elegant.',
    'bw; split_tone #2b1810 / #f3e4cf .45; s_curve .12; fine grain .03; vignette .2.')

# ---------------------------------------------------------------- 5 Rang gradatsiyasi
add('warm_tone', 4, 'Iliq tuslar', 'Uyg‘un iliq palitra: oltin yorug‘ joylar, mayin jigarrang soyalar.',
    'Colour grade with cosy warm tones: golden highlights, soft brown shadows, gentle warmth on the skin.',
    'temperature +.3; split_tone #4a2e20 / #ffd9a0 .35; vibrance .1.')
add('cool_tone', 4, 'Sovuq tuslar', 'Toza sovuq palitra: moviy soyalar, kumushrang yorug‘lik — zamonaviy va tinch.',
    'Colour grade with clean cool tones: blue-tinted shadows, silvery highlights, modern calm feel.',
    'temperature -.3; split_tone #1a3050 / #dfeeff .35; saturation .9.')
add('pastel', 4, 'Pastel', 'Yumshoq pastel ranglar: yengil pushti va yalpiz tuslar, past kontrast.',
    'Grade into soft pastel colours: light pink and mint tints, lifted shadows, low contrast, dreamy.',
    'fade .12; contrast .85; saturation .85; split_tone #c8a8d8 / #ffe6ee .4; hsl greens shift -20 lum +.1.')
add('vibrant', 4, 'Yorqin', 'To‘yingan, yorqin va jonli ranglar — yoz kayfiyati.',
    'Make the colours vibrant and punchy: boosted saturation, clarity and contrast, lively summer feel.',
    'vibrance .5; saturation 1.15; clarity .3; s_curve .12. Skin must not turn orange — reduce saturation gain on face_skin by half.')
add('muted', 4, 'Xira ranglar', 'Kam to‘yingan, tinch va nafis ranglar — “quiet luxury” kayfiyati.',
    'Mute the colours: low saturation, soft contrast, warm brownish shadows, calm elegant mood.',
    'saturation .6; contrast .92; split_tone #3a2a22 / #e8dcc8 .3; fade .06.')
add('earthy', 4, 'Yer tuslari', 'Terrakota, zaytun, qum ranglari — tabiiy, iliq “earthy” palitra.',
    'Shift the palette to earthy tones: terracotta, olive, sand and warm brown; natural and organic.',
    'hsl greens 120 width 50 shift +30 sat .7 (olive); reds/oranges sat 1.1 shift -5; temperature +.2; split_tone #3d2b1f / #d9b48a .35; saturation .9.')
add('peach', 4, 'Shaftoli', 'Shaftoli-pushti iliq tuslar: yumshoq, tabiiy va nafis teri rangi.',
    'Grade with peachy warm tones: soft peach highlights, rosy warmth on the skin, gentle fade.',
    'split_tone #6a3a3a / #ffc9a8 .45; temperature +.15; fade .06; brightness +.03.')
add('rose_gold', 4, 'Pushti oltin', 'Pushti-oltin jilo: nafis pushti yarim tuslar va oltin yorug‘ joylar.',
    'Grade in rose-gold tones: pink midtones, golden shimmering highlights, soft glow.',
    'split_tone #6b2f45 / #ffd8b0 .5; color_balance midtones (.05,0,.02); glow .25; vibrance .1.')
add('emerald', 4, 'Zumrad', 'Chuqur zumrad yashil tuslar: boy, hashamatli va teatral.',
    'Grade with deep emerald tones: rich saturated greens, dark teal shadows, luxurious contrast.',
    'hsl greens 120 width 50 sat 1.5 shift -5 lum -.05; split_tone #0a3328 / #d9ecd0 .4; s_curve .15; skin protected.')
add('lavender', 4, 'Lavanda', 'Orzuli lavanda-binafsha tus: sovuq, mayin va romantik.',
    'Grade with a dreamy lavender tint: soft purple in the shadows and highlights, cool and romantic.',
    'split_tone #3a2a6a / #e6d8ff .45; temperature -.1; saturation .9; fade .05; glow .2.')

# ---------------------------------------------------------------- 6 Romantik
add('soft_glow', 5, 'Mayin porlash', 'Teri va yorug‘ joylarda orzuli mayin porlash — romantik portretning klassikasi.',
    'Add a soft dreamy glow: gentle bloom on the skin and highlights, slightly softened detail, romantic feel.',
    'orton(sigma 30, .45); glow(40, .4, .55); brightness +.02. Visible but not blurry-blind.')
add('dreamy_haze', 5, 'Orzuli tuman', 'Yengil oq tuman va past kontrast: xuddi tushdagi kabi yumshoq kadr.',
    'Add a dreamy haze: soft white mist, lowered contrast, glowing light, ethereal atmosphere.',
    'screen a haze: linear(angle 90 top->bottom) inverted * #fff4e8 at .35 plus uniform .12; contrast .85; glow .3; slight warm.')
add('bloom', 5, 'Bloom', 'Yorug‘ joylar kuchli porlaydi — nur atrofga tarqaladi.',
    'Add strong highlight bloom: bright areas glow and spill soft light into the surroundings.',
    'glow(sigma 55, strength .8, threshold .5) + glow(sigma 15, .4, .7); slight brightness. Should be clearly stronger than /soft_glow.')
add('rose_tint', 5, 'Pushti tus', 'Butun suratga nozik pushti parda — muloyim va romantik.',
    'Add a delicate rose-pink tint over the whole image, warm and romantic.',
    'blend #ffb6c8 soft_light .5 + screen .12; temperature +.1; fade .04.')
add('vintage_romance', 5, 'Vintage romantika', 'Iliq, xira, mayin porlagan plyonka — eski sevgi hikoyasi kabi.',
    'Create a vintage romantic film look: warm faded tones, soft glow, gentle vignette, nostalgic.',
    'fade .12; temperature +.25; split_tone #5a3040 / #ffd9b8 .4; orton .3; vignette .35 #2a1418; grain .04.')
add('pearl', 5, 'Marvarid', 'Marvariddek nurli teri: yorug‘, salqin-oq yorug‘ joylar va mayin tekstura.',
    'Make the skin look pearly and luminous: brightened soft highlights, cool-white glow, refined texture.',
    'skin_smooth .5; brighten face_skin +.06; split_tone #4a4a5a / #f4f6ff .3 on skin; glow .3 threshold .6; saturation .92.')
add('angelic', 5, 'Farishta', 'Yorug‘, efirdek portret: boshning orqasida yumshoq oq halo va nurli fon.',
    'Make it ethereal and angelic: bright airy light, a soft white halo of light behind the head, glowing highlights.',
    'halo = radial(centre at face_center shifted up by 120px, radius .75, softness .9) * background mask -> screen white .8; brightness +.06; glow .4; saturation .9; fade .06.')
add('love_letter', 5, 'Sevgi maktubi', 'Eski qog‘oz teksturasi, krem tus va yumshoq chetlar — maktub ichidagi surat.',
    'Style it like a photo tucked into an old love letter: cream paper texture, warm faded tone, soft worn edges.',
    'tone #d8b990 strength .5 + fade .1; multiply paper(strength .22); vignette .45 #c9b28a softness .95 (light, not dark); small drawn corner flourishes optional; grain .03.')
add('whisper', 5, 'Shivir', 'Juda yumshoq, oqargan, sokin tuslar — pichirlashdek nozik portret.',
    'Make the image very soft, pale and quiet: low contrast, pale cream and pink tones, hushed and delicate.',
    'fade .2 highlight .08; contrast .8; saturation .7; brightness +.06; split_tone #b89aa0 / #fff3ec .4; orton .2.')
add('blush', 5, 'Qizarish', 'Yonoqlarda tabiiy pushti qizarish va iliq-pushti umumiy tus.',
    'Add a natural rosy blush on the cheeks and a warm pink overall tone.',
    'cheek points: between eye and mouth (from meta: eye_l/eye_r and mouth), place two soft radial blobs (radius ~.14, softness .9) tinted #ff7a8a soft_light .6 restricted by face_skin; overall split_tone #5a3a45 / #ffe0e0 .3; slight warm.')

# ---------------------------------------------------------------- 7 Estetika
add('dark_academia', 6, 'Dark academia', 'Eski kutubxona kayfiyati: jigarrang, qorong‘i, vintage donadorlik.',
    'Grade in dark-academia aesthetic: moody brown tones, darker exposure, vintage grain, old-library feel.',
    'exposure -.4; saturation .7; split_tone #2a1a10 / #c8a878 .5; s_curve .15; grain .07; vignette .45; temperature +.15.')
add('light_academia', 6, 'Light academia', 'Krem-bejeviy, yorug‘, yumshoq va iliq — nafis “light academia” uslubi.',
    'Grade in light-academia aesthetic: creamy beige tones, bright soft light, low saturation, warm elegance.',
    'brightness +.08; saturation .75; split_tone #7a6a58 / #fff2dc .45; fade .08; contrast .9.')
add('cottagecore', 6, 'Cottagecore', 'Qishloq nostalgiyasi: yumshoq yashil, iliq nur, yengil tuman va plyonka.',
    'Grade in cottagecore aesthetic: soft warm greens, gentle sunlight, light haze, nostalgic film feel.',
    'hsl greens shift +12 sat .85 lum +.05; temperature +.2; screen haze #fff0d0 .15 top; glow .25; grain .04; fade .05.')
add('y2k', 6, 'Y2K', '2000-yillar jilosi: yuqori to‘yinganlik, magenta-cyan, uchqunlar va chaqnash.',
    'Style in Y2K aesthetic: glossy high saturation, magenta and cyan tints, sparkles and a lens flare.',
    'saturation 1.3; split_tone #2a1a60 / #ff9ad0 .4; chromatic_aberration 4; sparkle_layer at eyes/teeth/highlights + random 8 sparkles screen; lens_flare small top-left .5; glow .3.')
add('clean_girl', 6, 'Clean girl', 'Toza, yorug‘, minimalistik: tabiiy teri porlashi, neytral oqlar.',
    'Style in clean-girl aesthetic: bright clean light, natural glowing skin, neutral whites, minimal and fresh.',
    'brightness +.06; skin_smooth .35; saturation .95; temperature -.05; glow .2 threshold .65; clarity .1.')
add('old_money', 6, 'Old money', 'Sokin hashamat: xira, nafis, iliq-krem yorug‘lik, chuqur soyalar, yengil plyonka.',
    'Grade in old-money quiet-luxury aesthetic: muted elegant tones, warm cream highlights, deep shadows, light film grain.',
    'saturation .72; split_tone #1f1a18 / #f2e6d2 .4; s_curve .12; grain .04; vignette .3; temperature +.1.')
add('coquette', 6, 'Coquette', 'Pushti, nozik, porloq: yengil pushti parda, uchqunlar va yumshoq nur.',
    'Style in coquette aesthetic: soft pink wash, delicate sparkles, gentle glow, sweet and feminine.',
    'blend #ffc0d0 soft_light .55; brightness +.04; glow .35; sparkle_layer 10 small sparkles screen; fade .05.')
add('grunge', 6, 'Grunge', 'Qo‘pol, qorong‘i, teksturali: kuchli kontrast, donadorlik, tirnalishlar.',
    'Style in grunge aesthetic: gritty dark tones, heavy contrast, rough grain, scratches and dirty texture.',
    'saturation .6; s_curve .3; grain .12 size 1.4; screen scratches(40) .5; multiply fbm-based dirt (.25); vignette .5; slight green-yellow tint.')
add('matte', 6, 'Matoviy', 'Matoviy tahririy uslub: xira qoralar, past kontrast, salqin tus.',
    'Give the photo a matte editorial look: faded blacks, low contrast, slightly cool tones.',
    'fade .15 highlight .05; contrast .9; temperature -.08; saturation .9.')
add('indie', 6, 'Indie film', 'Mustaqil kino estetikasi: yashil-sariq tus, xira ranglar, plyonka donalari.',
    'Grade like an indie film: green-yellow tinted highlights, faded colours, film grain, slightly cool shadows.',
    'split_tone #23303a / #e8e29a .45; fade .08; saturation .85; grain .07; s_curve .08.')

# ---------------------------------------------------------------- 8 Portret retush
add('skin_smooth', 7, 'Silliq teri', 'Teri tekis va silliq, lekin tabiiy tekstura saqlanadi — professional retush.',
    'Retouch the skin: smooth and even it out while keeping natural texture and pores, no plastic look.',
    'skin_smooth strength .85 radius 16 keep_texture .3; slight brighten skin +.02. Compare with original: visibly smoother cheeks, still natural.')
add('bright_eyes', 7, 'Yorqin ko‘zlar', 'Ko‘zlar yorqinroq va aniqroq: oqi tozalanadi, rangdor pardasi jonlanadi.',
    'Brighten and sharpen the eyes: whiten the eye whites slightly, enhance iris colour and contrast, add sparkle.',
    'eyes mask: brightness +.1, saturation .95 on whites; iris mask: saturation 1.4, contrast 1.25, sharpen .8; small catchlight sparkle (sparkle_layer tiny at iris centres, size 14) screen .7. Rest untouched.')
add('white_teeth', 7, 'Oq tishlar', 'Tishlar tabiiy oqartiriladi: sarg‘ish tus ketadi, kulgi yorqinroq bo‘ladi.',
    'Whiten the teeth naturally: remove yellow tint and brighten them without looking fake.',
    'mouth mask: hsl desaturate yellows (sat .35) + brightness +.12 + slight cool; feather 1.5. Verify on the smile — teeth clearly whiter, lips unchanged.')
add('dodge_burn', 7, 'Dodge & Burn', 'Yuz konturi: yonoq suyaklari va burun ko‘prigi yoritiladi, yuz cheti va jag‘ chizig‘i soyalanadi.',
    'Contour the face with dodge and burn: brighten cheekbones, nose bridge and forehead centre; softly darken jawline and face edges.',
    'dodge (screen white .18) on soft blobs: forehead centre, nose bridge, upper cheeks under eyes, chin; burn (multiply #5a4030 .25) on inner_edge(face mask, width 60, softness 30) and under cheekbones; all restricted to face_skin; subtle but visible. Use meta() points.')
add('soft_focus', 7, 'Yumshoq fokus', 'Klassik “soft focus” portret: yumshoq, romantik, nurli.',
    'Apply a classic soft-focus portrait effect: gently softened detail with a luminous glow, still sharp enough.',
    'soft_focus sigma 14 mix .45; glow .3; brightness +.02.')
add('clarity', 7, 'Aniqlik', 'Mahalliy kontrast va detallar kuchayadi — surat aniq va “chuqur” ko‘rinadi.',
    'Boost clarity: enhance local contrast and midtone detail so the photo looks crisp and dimensional.',
    'clarity .55 radius 40; sharpen .3; vibrance .1. Avoid halos on the face — reduce on face_skin by 40%.')
add('sharpen', 7, 'Keskinlashtirish', 'Nozik detallar (ko‘z, ro‘mol to‘qimasi, barglar) keskin va tiniq bo‘ladi.',
    'Sharpen the photo: crisp fine detail in the eyes, fabric and background, without artifacts.',
    'unsharp radius 1.5 amount 1.1 threshold .01 + detail_enhance blended .35. Compare: visibly crisper.')
add('glow_skin', 7, 'Porloq teri', 'Nam, porloq “dewy” teri: yonoq va burun ustida yorug‘ shu’la.',
    'Give the skin a dewy glow: luminous highlights on the cheekbones and nose, healthy radiant look.',
    'on face_skin: glow(20, .6, .55) + add highlights: smoothstep(.6,.9,lum)*.25 screen white; warm +.08; skin_smooth .3.')
add('matte_skin', 7, 'Matoviy teri', 'Yog‘li yaltirash olib tashlanadi, teri tekis matoviy bo‘ladi.',
    'Mattify the skin: remove shine and specular highlights, even out the tone, soft matte finish.',
    'on face_skin: compress highlights (curve [(0,0),(.7,.66),(1,.9)]); skin_smooth .5; saturation .95; slight powder tint. Nothing outside the skin changes.')
add('portrait_pro', 7, 'Pro retush', 'To‘liq professional retush: silliq teri, yorqin ko‘zlar, oq tishlar, kontur va nafis rang.',
    'Do a complete professional portrait retouch: smooth skin, bright eyes, white teeth, subtle contouring and refined colour, natural result.',
    'combine: skin_smooth .7; eyes brighten/sharpen; teeth whiten; light dodge&burn; clarity .15; split_tone warm .15; vignette .15.')

# ---------------------------------------------------------------- 9 Fon
add('blur_bg', 8, 'Xira fon', 'Portret rejimi: fon chiroyli xiralashadi, odam keskin qoladi.',
    'Blur the background like a portrait-mode lens: subject stays sharp, background softly out of focus.',
    'blur_background sigma 22; slight clarity on person .15. Edges of hijab must stay clean (no halo).')
add('bokeh_bg', 8, 'Bokeh fon', 'Yumshoq, kremdek bokeh: fondagi yorug‘ nuqtalar dumaloq disklarga aylanadi.',
    'Replace the background focus with creamy bokeh: round bright discs from the light spots, dreamy shallow depth of field.',
    'blur_background method bokeh radius 26 highlight_boost 4; then screen bokeh_layer(25, colors warm/gold, area=background mask) .5; slight warm.')
add('studio_white', 8, 'Oq studiya', 'Toza oq studiya foni — katalog va rasmiy portretlar uchun.',
    'Replace the background with a clean white studio backdrop with a soft natural shadow, keep the subject perfectly cut out.',
    'replace_background with white gradient (#ffffff centre -> #ebe8e4 bottom/edges via radial), add soft shadow under the shoulders (blur of person mask shifted down, multiply .25); slight brighten subject +.02. Cut-out must look clean.')
add('studio_cream', 8, 'Krem studiya', 'Iliq krem-bejeviy studiya foni — yumshoq va nafis.',
    'Replace the background with a warm cream studio backdrop, soft vignette, elegant and calm.',
    'replace_background with cream #F3EADB -> #DCCDB7 radial; shadow like studio_white; temperature +.08 on subject.')
add('gradient_bg', 8, 'Gradient fon', 'Bordo-pushti gradient fon — zamonaviy va jasur.',
    'Replace the background with a smooth burgundy-to-rose gradient backdrop.',
    'linear gradient angle 60: #4a1522 -> #a8556b -> #e8c4c8; replace_background; add subtle radial light behind head; slight rim light on person edge.')
add('color_pop', 8, 'Rangli urg‘u', 'Odam rangli, fon oq-qora — diqqat butunlay portretga qaratiladi.',
    'Keep the subject in full colour and make the background black and white.',
    'lerp(gray(img), img, person mask); slight bg contrast .95; subject vibrance .1.')
add('spotlight_bg', 8, 'Projektorli fon', 'Qorong‘i studiya va boshning orqasida yumshoq nur doirasi.',
    'Replace the background with a dark studio and a soft circular spotlight glow behind the head.',
    'bg = canvas #141012 + radial(centre above face, radius .55, softness .8) * #6b4a3a screen; replace_background; rim light on person edges .3; warm subject slightly.')
add('paper_bg', 8, 'Qog‘oz fon', 'Fon krem rangli teksturali qog‘ozga almashadi — badiiy va issiq.',
    'Replace the background with textured cream paper, subject unchanged.',
    'bg = canvas(#efe4d2, paper(strength .28)) with soft vignette; replace_background; soft shadow under subject.')
add('dark_bg', 8, 'Qorong‘i fon', 'Fon qorong‘ilashadi va xiralashadi — odam yorqin ajralib turadi.',
    'Darken and desaturate the background so the subject stands out bright.',
    'on background mask: exposure -1.6, saturation .3, blur 4; subject +.03; vignette .2.')
add('pattern_bg', 8, 'Naqshli fon', 'Nafis bej naqshli fon (damask/lattice) — klassik interyer.',
    'Replace the background with an elegant subtle beige damask-style pattern.',
    'procedural pattern: diagonal lattice (stripes at +45 and -45 period 90 thin) + small dots at intersections, colours #e6d9c4 on #efe5d5, low contrast, multiply paper; replace_background; soft shadow. Must read as wallpaper.')

# ---------------------------------------------------------------- 10 Badiiy
add('oil_painting', 9, 'Moyli rasm', 'Klassik moyli bo‘yoq: mo‘yqalam izlari, boy ranglar, kanvas teksturasi.',
    'Turn the photo into a classic oil painting with visible brush strokes, rich colours and canvas texture.',
    'cv_oil size 9 dyn 1 blended with detail; saturation 1.15; s_curve .1; multiply canvas texture (fbm fine + stripes weave cross-hatch low contrast .12); slight vignette. Brush look must be evident.')
add('watercolor', 9, 'Akvarel', 'Yumshoq akvarel: oqib ketgan ranglar, qog‘oz teksturasi va och konturlar.',
    'Turn the photo into a watercolour painting: soft bleeding colours, paper texture, light pencil outlines.',
    'cv_stylization(80, .5) lightened & desaturated .85; multiply paper(strength .3); multiply xdog line layer at .6 (soft grey lines); white-ish paper vignette; lift blacks .1.')
add('pencil_sketch', 9, 'Qalam eskizi', 'Grafit qalam bilan chizilgan portret: nozik chiziqlar va shtrixlar.',
    'Turn the photo into a graphite pencil sketch with fine lines and delicate shading.',
    'cv_pencil gray (sigma_s 70, sigma_r .08, shade .06); multiply paper .15; add xdog lines multiply .7; slight warm paper tint #f5f0e6.')
add('charcoal', 9, 'Ko‘mir', 'Qo‘pol ko‘mir chizmasi: to‘q soyalar, teksturali shtrixlar.',
    'Turn the photo into a bold charcoal drawing with dark rough shading and textured strokes.',
    'bw; s_curve .3; multiply cv_pencil gray with gamma; add grain .15 size 2; xdog lines phi 20 multiply; paper texture; darker overall than pencil_sketch.')
add('pop_art', 9, 'Pop-art', 'Uorhol uslubidagi 2×2 panel: posterlangan jasur ranglar, har panel o‘z palitrasida.',
    'Turn the photo into Warhol-style pop art: a 2x2 grid of posterized versions in bold contrasting colour palettes.',
    'posterize luminance 4 levels; 4 gradient_maps with palettes e.g. (#2a0a3a,#ff2e7a,#ffe200), (#0a2a4a,#00c2ff,#ffffff), (#3a1a00,#ff7a00,#fff0a0), (#0a3a2a,#00e07a,#ffc0e0); tile 2x2 (each resized to W/2 x H/2), thin black gutters.')
add('comic', 9, 'Komiks', 'Komiks uslubi: qora konturlar, nuqtali (halftone) soyalar, to‘yingan ranglar.',
    'Turn the photo into a comic-book illustration: black ink outlines, halftone dot shading, saturated flat colours.',
    'posterize 5; saturation 1.3; multiply halftone(cell 12) at .5 only in shadows (weight by 1-lum); multiply edges (Canny dilate 2) black; slight paper.')
add('halftone', 9, 'Halftone', 'Gazeta bosmasi: surat turli o‘lchamdagi nuqtalardan iborat.',
    'Turn the photo into a newspaper halftone print made of dots of varying size.',
    'halftone(cell 16, angle 25) in burgundy ink (#43121D) on cream (#F7F1E8) paper; add paper texture. Dots must be clearly visible.')
add('pointillism', 9, 'Puantilizm', 'Minglab rangli nuqtalardan yig‘ilgan rasm — impressionistlar uslubi.',
    'Turn the photo into a pointillism painting made of thousands of small coloured dots.',
    'draw ~50k random circles r 4-8 sampling colour from a slightly blurred image with saturation 1.2, on a cream canvas; sample colour jitter; smaller dots in face region (r 3-5) for detail.')
add('impressionist', 9, 'Impressionizm', 'Yumshoq mo‘yqalam zarbalari, nurli ranglar — Mone uslubi.',
    'Turn the photo into an impressionist painting with soft directional brush dabs and luminous colours.',
    'stroke painting: many random short ellipses/lines (length 14-30, angle from local gradient or random), colours sampled from the image (sat 1.15, brightness +.05); base = cv_stylization; canvas texture. Recognisable face, painterly everywhere.')
add('ink', 9, 'Siyoh chizma', 'Minimalistik qora siyoh chiziqlari krem qog‘ozda — nafis illyustratsiya.',
    'Turn the photo into a minimal black ink line drawing on cream paper.',
    'xdog(sigma 1.2, p 18, eps .015, phi 12) lines in ink #1a1214 on cream canvas with paper(); add light wash of tone (gray*.15 multiply) so the face reads; small ink splatter optional.')

# ---------------------------------------------------------------- 11 Ramkalar
add('polaroid_frame', 10, 'Polaroid ramka', 'Bej stol ustidagi Polaroid: oq ramka, qo‘lyozma yozuv, biroz burilgan.',
    'Put the photo in an instant-camera frame lying on a beige table, slightly tilted, with a handwritten caption.',
    'paste onto canvas(BEIGE, paper) size (760,950) border 44 bottom 200 rotate +4 shadow; caption cormorant-italic 64px #3a2a2a "yozgi kunlar ♡" on the bottom border; keep colours of the photo slightly warm.')
add('film_strip', 10, 'Plyonka lentasi', '35 mm plyonka lentasi: qora chetlar, perforatsiya teshiklari, kadr raqami.',
    'Present the photo as a frame on a 35mm film strip with sprocket holes and frame numbers.',
    'black canvas #111; photo inset centred (W-140 wide); rows of rounded rectangles (sprocket holes) top & bottom in cream #e8e0d0; small text "KODAK 400  ▸ 24A" style in lato-bold 26px orange-ish along the edge; slight warm grade on the photo.')
add('white_border', 10, 'Oq ramka', 'Galereya uslubidagi toza oq ramka va nozik ichki chiziq.',
    'Add a clean white gallery-style border with a thin inner keyline.',
    'inset 70 white; then thin burgundy keyline at 52px inset (2px). Photo slightly contrast+.')
add('rounded_card', 10, 'Yumaloq karta', 'Krem fonda yumaloq burchakli karta va yumshoq soya — ilova (app) uslubi.',
    'Present the photo as a rounded-corner card with a soft shadow on a cream background.',
    'paste onto canvas(CREAM) size (960,1200) radius 60 shadow (.3, 40, (0,24)); no border.')
add('magazine', 10, 'Jurnal muqovasi', 'Moda jurnali muqovasi: masthead, sarlavhalar, shtrix-kod — bordo va krem uslubda.',
    'Design the photo as a fashion-magazine cover with a masthead title, cover lines and a barcode.',
    'masthead "ÉLÉGANCE" playfair-bold ~150px cream #F7F1E8 top centre (behind head partly OK); cover lines left/right bottom in lato-bold 34px + playfair-italic 44px; issue text "SENTABR 2026 · № 09"; barcode: thin vertical bars bottom-right; slight grade s_curve .1 ; small burgundy accent bar.')
add('vintage_frame', 10, 'Vintage ramka', 'Klassik ikki chiziqli ramka va burchak naqshlari — antiqa surat.',
    'Put the photo inside an ornate classic frame with double lines and corner flourishes, vintage style.',
    'inset 90 on cream paper canvas; draw double lines (burgundy 3px + 1px) at 60/74px; corner ornaments: small drawn curls/lozenges (use ImageDraw arcs) in burgundy; photo grade: slight sepia .3 + vignette.')
add('passport', 10, 'Foto-sessiya varag‘i', 'Bir varaqda 4 ta bir xil surat — foto-budka (photo booth) uslubi.',
    'Lay out the photo as a photo-booth sheet: 4 identical copies in a 2x2 grid with white gaps.',
    'canvas white; 4 copies resized (W/2-60, H/2-60) with 40px gaps; slight bw or colour? keep colour with mild contrast; thin grey cut lines.')
add('torn_paper', 10, 'Yirtilgan qog‘oz', 'Yirtilgan qog‘oz chetlari — kollaj uslubi, bej fonda.',
    'Style the photo as a torn paper cut-out collaged onto a beige background with rough white fibrous edges.',
    'torn mask: rectangle inset ~70px with edges displaced by fbm noise (amplitude 25px) -> mask; white fibrous edge = dilate(mask,10)-mask tinted #f4efe6; paste over canvas(BEIGE, paper) with shadow; rotate 2 deg.')
add('double_border', 10, 'Ikki qavat ramka', 'Bordo va krem ikki qavatli ramka — gaydning o‘z uslubida.',
    'Add a double border: an outer cream mat and an inner burgundy frame line.',
    'inset 80 cream; border ring burgundy 14px at 56px inset; thin inner line 2px cream inside it. Elegant.')
add('postcard', 10, 'Otkritka', 'Vintage otkritka: marka, pochta muhri va “Salom!” yozuvi.',
    'Turn the photo into a vintage postcard with a stamp, a postmark and a greeting text.',
    'canvas cream paper; photo inset with white border 30, slight sepia .25 + fade; stamp: small rectangle with perforated edge top-right containing a mini copy of the photo (bw); postmark: circles + wavy lines in grey-black at low opacity; text "Salom!" playfair-italic 90px burgundy bottom-left.')

# ---------------------------------------------------------------- 12 Effektlar
add('glitch', 11, 'Glitch', 'Raqamli buzilish: RGB kanallar surilgan, gorizontal bo‘laklar siljigan.',
    'Apply a digital glitch effect: RGB channel splitting, shifted horizontal slices, small blocks of corruption.',
    'chromatic flat shift 14; ~12 random horizontal bands shifted ±20..80px (some with inverted or single-channel); a few thin scanline bands; small colour-block noise; keep face mostly readable.')
add('vhs', 11, 'VHS', 'VHS kasseta: skan chiziqlari, rang oqishi, shovqin va “PLAY ▶” yozuvi.',
    'Apply a VHS tape look: scanlines, colour bleeding, tape noise, slight distortion and a "PLAY" overlay.',
    'chroma bleed: blur chroma (blur only colour, keep luma) sigma 6 + shift 6px; scanlines period 4 .25; grain .08 colour; wobble: small horizontal jitter per line bands; text "▶ PLAY" top-left and "SP 0:12:47" bottom in lato-bold 46px white with slight glow; saturation .9; vignette .3.')
add('double_exposure', 11, 'Ikki ekspozitsiya', 'Siluet ichida daraxtlar: portret va tabiat bir kadrda uyg‘unlashadi.',
    'Create a double-exposure: the silhouette of the person filled with the trees/foliage of the background, over a light background.',
    'inside = person mask; trees = the original background region (blur_background trick not needed): take img zoomed 1.3 (trees region), screen-blend into person area with weight .75; person area base brightened (levels) so trees show; outside person -> near-white #f2eee8 gradient; slight bw or muted colour; face must still be visible (weight less on face mask).')
add('reflection', 11, 'Suvdagi aks', 'Suratning pastki qismida suvdagi aks va yengil to‘lqinlar.',
    'Add a water reflection below the portrait: the image mirrored at the bottom with soft ripples fading out.',
    'compose: top 62% = img resized; bottom = vertically flipped copy with sinusoidal horizontal displacement (ripples), blurred slightly, darkened .8, fading to a dark blue #0d1b2a at the very bottom; thin horizon line.')
add('prism', 11, 'Prizma', 'Prizma orqali o‘tgan kamalak nur chiziqlari — jozibali refraktsiya.',
    'Add prism light effects: rainbow light streaks refracted across the photo, subtle chromatic edges.',
    'diagonal rainbow bands: gradient through hues along an axis at 35deg, softened, screened .6 restricted to 2 bands; chromatic_aberration 6; glow .2; slight brighten.')
add('chromatic', 11, 'Xromatik aberratsiya', 'Linza rang chetlanishi: RGB kanallarning chetlarda ajralishi.',
    'Add strong chromatic aberration: red and blue colour fringing increasing toward the edges of the frame.',
    'chromatic_aberration amount 22 radial; slight vignette; keep centre sharp. Must be clearly visible at the edges (hijab outline, trees).')
add('pixel_art', 11, '8-bit', 'Retro o‘yin uslubi: yirik piksellar va cheklangan rang palitrasi.',
    'Turn the photo into 8-bit pixel art with large pixels and a limited retro colour palette.',
    'pixelate block 18 then posterize 5 + saturation 1.2; optional 1px darker grid lines multiply .15.')
add('motion_blur', 11, 'Harakat', 'Radial harakat xiraligi: fon harakatda, yuz keskin — dinamika.',
    'Add radial motion blur to the background while the face stays sharp — dynamic energy.',
    'zoom_blur strength .12 centred on face; then restore face/person via mask(person) feather 20 (person sharp); slight contrast.')
add('lens_flare', 11, 'Linza chaqnashi', 'Quyoshdan tushgan linza chaqnashi: yorqin markaz, chiziqlar va ko‘pburchak sharpalar.',
    'Add a realistic sun lens flare from the top corner with a bright core, light streaks and polygon ghost artifacts.',
    'lens_flare(pos top-right, strength 1.0) + temperature +.15 + slight haze; make the flare prominent.')
add('film_burn', 11, 'Plyonka kuyishi', 'Kuygan plyonka chetlari: to‘q sariq-qizil olovli chetlar va oq kuyish nuqtalari.',
    'Add a film-burn effect: orange-red burning edges creeping in from the corners with bright white hot spots.',
    'burn mask from fbm thresholded near two corners (top-right, bottom-left); layer: white core -> yellow -> orange -> dark red rings by distance; screen/add; slight warm overall, faded grain.')

# ---------------------------------------------------------------- 13 Mavsum & ob-havo
add('autumn', 12, 'Kuz', 'Oltin kuz: yashil barglar apelsin-sariqqa aylanadi, iliq nur.',
    'Turn the scene into golden autumn: green foliage becomes orange and amber, warm low sunlight.',
    'hsl greens hue 120 width 55 shift -75 (toward orange) sat 1.15 lum +.02; temperature +.25; split_tone #4a2a14 / #ffcf7a .35; glow .2. Foliage must be clearly orange.')
add('winter', 12, 'Qish', 'Sovuq qish: kumush-moviy tuslar, yengil qor yog‘ishi, ayozli havo.',
    'Turn the scene into a cold winter day: silvery-blue tones, desaturated foliage, gently falling snow.',
    'hsl greens sat .15 lum +.25 (frosted); temperature -.35; brightness +.05; snow: 2 layers of blurred white dots (sizes 3-8 and 8-16, some motion_blur) screen .9 across whole image; slight haze; cool split_tone.')
add('spring', 12, 'Bahor', 'Yangi bahor: yorqin yashil, pushti gullar tusi, havodor nur.',
    'Turn the scene into fresh spring: bright vivid greens, soft pink blossom tint, airy light.',
    'hsl greens sat 1.3 lum +.08 shift -8; split_tone #4a5a3a / #ffe0ea .35; brightness +.04; scatter ~60 soft pink petal shapes (small rotated ellipses #ffb7c5, blurred 1-2px) mostly in the top/background; glow .2.')
add('summer', 12, 'Yoz', 'Quyoshli yoz: jonli ranglar, iliq yorqin nur va quyosh shu’lasi.',
    'Make it a bright sunny summer day: vivid colours, warm bright light and a sun glow.',
    'vibrance .4; temperature +.2; brightness +.05; lens_flare small (.4, no ghosts) top-right; s_curve .08.')
add('rain', 12, 'Yomg‘ir', 'Yomg‘ir chiziqlari va nam shisha: moviy-kulrang, sokin kayfiyat.',
    'Add rain: streaks of falling rain, wet-glass droplets on the lens, cool blue-grey mood.',
    'temperature -.25; saturation .8; exposure -.2; rain streaks: ~600 thin semi-transparent lines length 40-120 angle ~78deg, motion-blurred, screen .35; droplets: ~120 small refracting circles (slightly brighter rim); slight blur .8.')
add('fog', 12, 'Tuman', 'Yumshoq tuman: fon oq tumanga cho‘madi, odam oldinda aniq.',
    'Add soft fog: the background fades into white mist while the subject stays clear in front.',
    'fog = (background mask * .75 + .12) * (fbm(4) *.4 + .6) -> screen #eef0f2; desaturate background .6; contrast .9. Depth must be obvious.')
add('golden_leaves', 12, 'Oltin barglar', 'Tushayotgan oltin barglar va iliq kuz nuri — ertakdagi kabi.',
    'Add falling golden leaves drifting through warm autumn light.',
    'base autumn grade (lighter); draw ~45 leaf shapes (ellipse with pointed ends via polygon, small vein line) colours #e8a33a/#d97a2b/#f2c65a, sizes 30-110, random rotation, some blurred (depth), a few in front of subject; warm glow.')
add('frost', 12, 'Ayoz', 'Kadr chetlarida muz kristallari va sovuq moviy tus.',
    'Add frost: icy crystal patterns creeping in from the edges of the frame and a cold blue tint.',
    'edge weight = 1 - radial(radius 1.0, softness .7); frost = smoothstep on fbm(6, scale 3) high frequency * edge weight -> screen white-blue #e8f4ff .85; plus tiny sparkles; temperature -.3; saturation .85.')
add('sunrays', 12, 'Quyosh nurlari', 'Yuqori burchakdan tushayotgan quyosh nurlari (god rays) — ilohiy nur.',
    'Add sun rays (god rays) streaming diagonally from the top corner through the scene.',
    'rays(centre top-right, count 18, sharpness) screen #ffe9b0 .7 with glow; warm +.15; slight haze; rays clearly visible across the face/background.')
add('night', 12, 'Tun', 'Tungi sahna: to‘q ko‘k osmon, yulduzlar, odam yumshoq iliq nur bilan yoritilgan.',
    'Turn the scene into night: deep blue darkness, stars in the sky, the person softly lit by warm light.',
    'background: exposure -2.2, temperature -.5, blue split; stars: ~150 tiny bright dots + 10 sparkles in the upper background (area = background mask * (y < 45%)); person: exposure -.5, warm radial light on face; glow; vignette .4.')

# ---------------------------------------------------------------- 14 Tekstura & nur o‘yini
add('dust_scratches', 13, 'Chang & tirnalish', 'Eski plyonkadagi chang zarralari va tirnalishlar qatlami.',
    'Overlay vintage dust particles and scratches like an old film scan.',
    'screen scratches(35, length (300,1200)) .55 + dust(900, size (1,3)) .6 + few hairs (curved lines); slight fade .06; grain .04.')
add('paper_texture', 13, 'Qog‘oz teksturasi', 'Surat teksturali qog‘ozga bosilgandek — tolalar va donachalar.',
    'Make the photo look printed on textured fibrous paper.',
    'multiply paper(strength .35, fibers) ; fade .06; slight desat .92; edges slightly lighter (paper vignette light).')
add('bokeh_lights', 13, 'Bokeh nurlari', 'Havoda suzayotgan oltin bokeh doiralari — bayram kayfiyati.',
    'Add floating golden bokeh light circles across the photo, festive and warm.',
    'screen bokeh_layer(45, radius (25,110), colors gold/peach/white, softness .3) .8; warm +.1; slight glow. Discs must be visible over the whole frame, fewer over the face.')
add('sparkle', 13, 'Uchqunlar', 'Yorug‘ nuqtalarda porlab turgan yulduzchalar — ko‘z va tabassumda.',
    'Add twinkling sparkle stars on the bright points (eyes, smile) and a few in the scene.',
    'sparkle_layer at iris centres (size 40), teeth (2 points, 30), + 12 random on highlights (lum>.8) sizes 20-70; screen .9 with glow; slight brightness.')
add('glitter', 13, 'Glitter', 'Nozik glitter yaltirog‘i butun surat bo‘ylab — bayramona jilo.',
    'Add fine glitter shimmer scattered across the image, with a subtle warm sheen.',
    'thousands of tiny 1-3px bright specks (white/gold/pink) with slight blur, density higher on clothing/background, screen .85; a few small sparkles; temperature +.08; glow .15.')
add('light_rays', 13, 'Nur chiziqlari', 'Diagonal yumshoq nur tasmalari kadr bo‘ylab o‘tadi.',
    'Add soft diagonal beams of light passing across the frame.',
    'two or three wide soft bands via stripes(angle 30, period 500, duty .3, softness 120) * linear gradient from top-left -> screen #fff0d0 .5; warm +.1; slight haze.')
add('blinds_shadow', 13, 'Jalyuzi soyasi', 'Jalyuzi orqali tushgan nur va soya chiziqlari — klassik noir/estetik kadr.',
    'Add venetian-blind light and shadow stripes across the subject and background.',
    'stripes(angle -8, period 110, duty .5, softness 10) multiply .55 (darken between stripes) + lit stripes screen warm #ffe6c0 .2; contrast 1.05; skip nothing — stripes cross the face too (that is the look).')
add('leaf_shadow', 13, 'Barg soyalari', 'Daraxt barglari orqali tushgan quyosh soyalari (gobo) — yoz tushi.',
    'Add dappled sunlight through leaves: leaf-shaped shadows and warm light patches across the image.',
    'leaf shadow mask: draw ~200 leaf shapes (rotated ellipses with pointed ends) union, blur 8; multiply shadow #4a3a2a at .5; lit areas screen warm .2; temperature +.15.')
add('lace_shadow', 13, 'Dantel soyasi', 'Dantel naqshli soya — romantik, nafis nur o‘yini.',
    'Add a lace-pattern shadow falling across the photo, romantic and delicate.',
    'procedural lace: grid of circles (rings) + scallops + small dots, period ~120px, rotated 12 deg, blur 5 -> multiply .45; warm light in gaps; optional slight perspective (rotate 5).')
add('haze', 13, 'Quyosh tumani', 'Iliq quyosh tumani: kontrast pasayadi, yorug‘lik havoda tarqaladi.',
    'Add warm sun haze: reduced contrast, warm light scattered through the air, dreamy summer atmosphere.',
    'screen linear(top->bottom inverted) * #ffd9a8 .4 + uniform .1; contrast .85; temperature +.2; glow .25; slight lens flare (no ghosts) .3.')

# ---------------------------------------------------------------- 15 Ijodiy
add('duotone', 14, 'Duotone', 'Ikki rangli portret: bordo soyalar va krem yorug‘lik — gaydning imzo uslubi.',
    'Convert to a two-colour duotone: burgundy shadows and cream highlights.',
    'duotone(#43121D, #F7F1E8) via gradient_map with mid stop #A8556B at .55; s_curve .1; slight grain .03.')
add('neon', 14, 'Neon kontur', 'Qorong‘i fonda odamning neon porlovchi konturi — pushti va moviy.',
    'Draw glowing neon outlines of the subject in pink and cyan on a dark background.',
    'base: exposure -1.4 desat .5 dark; outline = edges of person mask + Canny of face details -> dilate 2 -> glow (blur 3 + blur 12 + blur 30) coloured #ff2fa0 on the left half, #22d3ff on the right half; screen strongly. Face still visible in the dark.')
add('cyberpunk', 14, 'Kiberpank', 'Kelajak shahar: magenta-cyan neon gradatsiya, yuqori kontrast, yengil skan chiziqlar.',
    'Grade in cyberpunk style: magenta and cyan neon split tones, high contrast, glow and faint scanlines.',
    'split_tone #12d0ff / #ff2fa0 .6 (cool shadows magenta highlights) then hsl greens shift -60 sat .8; s_curve .25; glow .35; scanlines period 6 .12; grain .03.')
add('retro_poster', 14, 'Retro poster', 'Trafaret (screen-print) poster: 4 rangli posterizatsiya, halftone va qog‘oz.',
    'Turn the photo into a retro screen-printed poster: 4-colour posterized palette, halftone shading, paper texture.',
    'posterize lum 4 -> gradient_map (#2b1a1a, #6B1F2E, #d98a4a, #F2E4C8); multiply halftone(cell 10) .35 in mid/dark; paper multiply .3; misregister slightly one colour layer (+3px). Bold poster feel.')
add('vaporwave', 14, 'Vaporwave', 'Pushti-binafsha-cyan gradient, pastda neon to‘r — 80-yillar kelajagi.',
    'Style in vaporwave aesthetic: pink-purple-cyan gradient tones, a neon perspective grid at the bottom, retro glow.',
    'gradient_map (#1a0b3a, #7a2a9a, #ff6ec7, #8ef5ff) .8 mixed with original .35; perspective grid in the lower 30% (converging lines, magenta) screen; sun-stripe circle top optional; glow .3; chromatic 4.')
add('thermal', 14, 'Termal kamera', 'Issiqlik kamerasi: ko‘k → binafsha → qizil → sariq → oq spektri.',
    'Render as a thermal-camera image: heat-map colours from blue through purple, red and yellow to white.',
    'gradient_map on luminance (blur 3): (#000428 0, #2a0a6a .2, #8a0a8a .4, #ff2a2a .6, #ffb020 .8, #ffffff 1); slight posterize 12; small text "FLIR 36.6°C" corner optional.')
add('negative', 14, 'Negativ', 'Plyonka negativi: ranglar teskari, apelsin plyonka asosi.',
    'Turn the photo into a colour film negative with inverted colours and an orange film base tint.',
    'invert; then multiply with orange base #ffa050 at .35 + slight fade; add film-strip edge text optional; contrast .95.')
add('solarize', 14, 'Solarizatsiya', 'Sabattier effekti: yorug‘ joylar qisman teskari — syurreal metall jilo.',
    'Apply solarization (Sabattier effect): partially inverted highlights for a surreal metallic look.',
    'solarize threshold .55 on a slightly desaturated image; then s_curve .15; slight cool split; grain .03.')
add('risograph', 14, 'Rizograf', 'Ikki rangli rizograf bosma: bordo + ko‘k qatlamlar biroz siljigan, donador.',
    'Turn the photo into a two-colour risograph print: burgundy and navy ink layers slightly misregistered, grainy.',
    'two ink layers: layer1 = gradient_map bw-> (#F2E8DA, #6B1F2E) from luminance; layer2 = (#F2E8DA,#1f3a6b) from (1-red channel) shifted +6px; multiply layers over paper; grain .1 size 2; halftone-ish noise; paper texture.')
add('stamp', 14, 'Pochta markasi', 'Perforatsiyali pochta markasi: bordo gravyura uslubi va “POST” yozuvi.',
    'Turn the photo into a postage stamp: perforated edges, engraved-line monochrome look in burgundy ink, and a denomination text.',
    'engraving: bw + s_curve; multiply stripes(angle 20, period 6, duty .5) modulated by luminance (lines thicker in dark areas) -> burgundy ink on cream; stamp perforation: canvas cream with a rounded-perforation edge (row of circles cut out) around inset 70; text "O‘ZBEKISTON  ·  2026" lato-bold and "150" playfair-bold in burgundy.')

assert len(C) == 150, len(C)
codes = []
for i, (code, cat, title, desc, prompt, hint) in enumerate(C, 1):
    codes.append(dict(id=i, code=code, group='g%02d' % ((i - 1) // 5 + 1), category=CATS[cat][0], category_uz=CATS[cat][1],
                      title_uz=title, desc_uz=desc, prompt_en=prompt, hint=hint))
assert len({c['code'] for c in codes}) == 150, 'duplicate codes'
cats = [dict(slug=s, name_uz=n, name_en=e, intro_uz=i, index=k + 1) for k, (s, n, e, i) in enumerate(CATS)]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json.dump(dict(categories=cats, codes=codes), open(os.path.join(root, 'codes.json'), 'w'), ensure_ascii=False, indent=1)
print('codes.json written:', len(codes), 'codes,', len(cats), 'categories')
