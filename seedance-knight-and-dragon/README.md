# Поверни телефон

Покадровый разбор вирусного вертикального ролика («девушка-рыцарь с айс-кофе → колоссальный
белый дракон») и готовые промпты, чтобы пересобрать его лучше на Seedance 2.5.

Отчёт с картинками и кнопками копирования: `report/index.html`.
Промпты по отдельным файлам, готовые к вставке: `prompts/`.

---

## Главное в одну строку

Это **не одно видео, а два**, сшитые четырьмя чёрными кадрами. Первая половина — нативная
вертикаль 9:16. Вторая — кадр **16:9, положенный на бок внутри вертикального файла**, так что
смотреть его можно только физически повернув телефон. Никакой подписи «поверни телефон» нет и
не нужно — кадр требует сам.

## Структура

```
0.00 ──────────────── 5.05 ── 5.87 ─┬─ 6.01 ─────────────────────── 20.00 ─── 20.55
     clip A · 9:16          whip    │     clip B · 16:9 rotated 90°        blk
                            + flash │
                                    └─ 4 чёрных кадра: здесь меняется всё
```

## 1. Технический паспорт

Всё измерено по файлу, а не на глаз.

| | |
|---|---|
| Container | MP4 / H.264 High, yuv420p, bt709 |
| Frame | 720 x 1280 (9:16 portrait), 24.00 fps |
| Duration | 20.55 s — 493 frames |
| Bitrate | 858 kb/s total, 821 kb/s video |
| Audio | AAC HE-AAC, 44.1 kHz stereo, 37 kb/s |
| Cuts detected | Two only: 5.08–6.17 s and 19.71–20.17 s |
| Clip A | 0.00 – 5.87 s, native vertical |
| Clip B | 6.01 – 20.55 s, a 16:9 landscape image rotated 90° inside the portrait frame |
| Camera, clip B | Locked. Knight's on-screen height holds 111–123 px of 720 from 7 s to 17 s — under ±5% |
| Dialogue | None. Score and SFX only |

**Ключевая находка.** В клипе B камера **не двигается вообще**. Экранная высота фигуры рыцаря
держится в диапазоне 111–123 px из 720 с 7-й по 17-ю секунду — разброс меньше ±5%, горизонт не
шевелится. Значит, весь рост головы дракона в кадре — это движение самого дракона в неподвижной
рамке, а не наезд. Это главное техническое решение ролика: масштаб читается по параллаксу в
фиксированной рамке. Наезд бы его убил.

## 2. Раскадровка

| Таймкод | Длит. | Режим | Что происходит |
|---|---|---|---|
| `00:00.0` | 05.0 s | Vertical | Selfie. She sips iced coffee, gaze off-lens, bored. The pale mass behind her right shoulder is already in frame, out of focus, unremarked. |
| `00:04.5` | 0.5 s | Vertical | Her eyes flick right, then her head turns. The only warning in the whole film. |
| `00:05.05` | 0.82 s | Whip | Whip up into blank sky, blown to near-white, then down through her shoulder into the grass. |
| `00:05.87` | 0.17 s | Black | Four black frames. Orientation, scale and register all change inside them. |
| `00:06.0` | 4.5 s | Landscape | Camera emerges through the grass and settles. She is now one sixth of frame height, back to us, in front of a sleeping dragon whose head alone is five times her height. |
| `00:10.5` | 1.7 s | Landscape | She raises the sword. Nothing has threatened her yet. |
| `00:12.2` | 2.8 s | Landscape | The amber eye opens. Vertical slit pupil. Head still on the ground. |
| `00:15.0` | 2.3 s | Landscape | Head lifted and rotated front-on. Both eyes open. It looms without moving toward her. |
| `00:17.3` | 2.2 s | Landscape | Jaws open. Her cloak snaps horizontal. She braces and holds. |
| `00:19.5` | 1.05 s | Out | Whip away, into the grass, to black. No resolution, no victory, no death. |

## 3. Механика перехода

Переход собран из двух випов подряд. Сначала камера уходит вверх в пустое небо и кадр выбивает
почти в белое — это сбрасывает адаптацию глаза. Затем она падает вниз, мимо её плеча, в траву — и
обрывается в чёрное. Внутри четырёх чёрных кадров происходит подмена: ориентация, масштаб,
регистр. Трава работает естественной вытирающей маской на обоих концах.

Средняя яркость кадра (сетка 32×32, оттенки серого, 24 fps), база экспозиции 124:

```
4.80 → 5.05   124            ровно
5.05 → 5.38   124 → 212      вип вверх, выбивание в белое
5.38 → 5.55   212 → 160      возврат
5.59 → 5.63   160 → 15       падение в траву
5.72 → 5.80   86 → 156       отскок (мимо её плеча)
5.88 → 6.01   6 / 7 / 6 / 10 ЧЕТЫРЕ ЧЁРНЫХ КАДРА — здесь склейка
6.05 → 6.22   29 → 139       выход в повёрнутый мир
6.26 → 6.51   133 → 61       проход за стеблем травы
6.55 → 6.80   68 → 125       кадр установился
```

## 4. Почему это работает

1. **Вертикальный селфи-код усыпляет** — 9:16, дрожащая рука, взгляд мимо линзы. Мозг помечает это как «бытовое видео» и перестаёт искать зрелище. Всё дальнейшее падает в снятую защиту.
2. **Несовпадение без шутки** — Полный латный доспех и айс-кофе. Ни подмигивания, ни панчлайна — она просто скучает. Комедия держится на отказе её признавать.
3. **Улика посажена в первом кадре** — Бледная масса за правым плечом видна с 0.2 секунды, вне фокуса, и никогда не упоминается. Поэтому разворот читается как расплата, а не как произвол.
4. **Ровно одно предупреждение** — Поворот головы на 4.5. Больше подготовки нет — и не нужно.
5. **Чёрные кадры стирают память кадрирования** — Вспышка в белое сбивает адаптацию глаза, четыре чёрных кадра обнуляют короткую зрительную память. За 0.17 секунды меняются масштаб, формат и регистр — и шва не видно.
6. **Разворот требует физического действия** — Картинка лежит на боку — значит телефон надо повернуть. Никакой подписи «поверни телефон» не нужно, кадр требует сам. И пока зритель поворачивает телефон, он не может пролистнуть.
7. **Камера заперта — двигается только существо** — Рост фигуры на экране держится в пределах ±5% с 7 по 17 секунду. Всё увеличение головы — это движение дракона в неподвижной рамке. Именно так глаз и определяет размер: по параллаксу относительно фиксированной рамки, а не по трансфокатору.
8. **Расплата стоит после точки невозврата** — Шесть секунд, где не происходит ничего. Потом пять секунд пробуждения. Рёв — на 17.3, когда зритель уже держит телефон боком и вложился.
9. **Финал без развязки** — Ни победы, ни смерти. Открытая пасть и чёрное. Это и есть двигатель пересмотров и комментариев.

## 5. Что в референсе сделано плохо

Одиннадцать мест, где референс слабее, чем может быть. Все исправления вшиты в промпты в `prompts/`.

1. **Дракон ничего не играет** — Он просыпается, нависает, ревёт. Ни одной мысли, ни узнавания, ни отношения. Самое дорогое в кадре существо использовано как погодное явление.
2. **Два клипа склеены гардеробом, а не личностью** — Её лицо после 5.05 не возвращается ни на кадр. Половинки держатся на цвете плаща и стрижке. Зритель узнаёт костюм, а не человека.
3. **Меч поднят до угрозы** — На 10.5 она поднимает клинок, а глаз открывается только на 12.2. Реакция раньше причины — и открытие глаза обесценено.
4. **Рука на стакане не сходится** — Пальцевые ламели латной рукавицы не артикулируются вокруг стакана, пластины плывут. Это самый заметный AI-тэлл в первой половине; кольчуга под мышкой тоже даёт повторяющийся паттерн.
5. **Геометрия дракона дрейфует** — Между 12.4 и 18.4 меняются форма и число бронзовых обручей на рогах, усы-тендрилы переползают, структура пальцевых костей крыла не совпадает между кадрами.
6. **Пасть анатомически плоская** — Ровные конусы зубов, язык-плита, ни слюны, ни пара. В холодном туманном воздухе рёв обязан дать плотный выхлоп дыхания — это самая большая упущенная возможность всего видео.
7. **Трава не взаимодействует** — Существо на пятьдесят метров поднимает голову — и трава под челюстью не приминается. Рёв не кладёт траву радиальной волной. Реагирует только плащ. Это главный сигнал «не настоящее».
8. **Она стоит на траве, а не в траве** — Стопы не перекрываются стеблями. Контакта с землёй нет.
9. **Нет ни одной контактной тени** — Полностью рассеянный свет — законный выбор, но он же удобно прячет самое трудное: посадку масштаба в среду.
10. **В звуке нет тишины** — Громкость растёт монотонно с 3 до 20 секунды, примерно на 5 дБ. Перед рёвом нет провала. Кульминация приходит на уже полную полку — и поэтому не бьёт.
11. **Финальный вип выбрасывает кадр** — Вместо того чтобы додержать открытую пасть, монтаж уносит камеру. Ещё 0.8 секунды на пасти и жёсткий срез в чёрное — и удар был бы вдвое сильнее.

## 6. Как это собрано

Две отдельные генерации, а не один непрерывный кадр. Доказательство: ориентация меняется ровно на
чёрных кадрах, а детектор склеек находит всего две зоны смены за весь ролик. Клип B повёрнут на 90°
уже в монтаже — 1920×1080, положенные на бок, дают ровно 1080×1920 без единого чёрного поля.

Значит, нужно три вещи: генерация A, генерация B и монтаж, который их сшивает. Плюс одно
референсное изображение персонажа, общее для обеих генераций.

## 7. Промпт · Клип A

`prompts/clip-a.txt` · `prompts/clip-a.negative.txt`

```text
Vertical 9:16 handheld selfie video, front-facing phone camera held at arm's length, 24mm wide lens, mild barrel distortion. Every shot in this film is her own phone. There is no other camera.

SUBJECT — Take her face, skin tone and features from the supplied reference image and do not restyle them. Dark hair to just past the collarbone, loose and slightly windblown, fine strands lifting across her cheek. She wears full mirror-polished white steel plate armour: gorget, layered pauldrons, articulated rerebrace-couter-vambrace on the extended arm, gauntlet with segmented finger lames, breastplate engraved with fine fleur-de-lis and a cruciform motif, blackened chainmail voiders at the armpits, domed rivets. An ivory hooded cloak hangs behind her shoulders. No sword, no weapon, no scabbard.

ACTION, in strict order —
(0-1.8 s) She sips iced black coffee through a white straw from a clear plastic to-go cup with a domed lid, ice cubes and condensation on the plastic, gauntleted fingers wrapped around it. Her gaze wanders off-lens to the right. She looks profoundly bored. She never looks into the camera.
(1.8-2.3 s) Her eyes snap right. The straw leaves her lips.
(2.3-2.8 s) Without looking, she flicks her wrist and throws the cup back over her right shoulder. It tumbles away behind her, the lid coming loose, dark coffee and ice arcing out.
(2.8-4 s) IMMEDIATELY, with no pause, in one hard continuous motion, she swings the phone away from her face out to her right and past her shoulder until it points away from her into the fog. The frame sweeps right in heavy motion blur, her pauldron and cloak whipping past the lens, and the horizon rolls over as she turns the phone onto its side.

END OF SHOT — The clip ENDS mid-swing, still heavily blurred, still moving. It does not settle, does not come to rest, does not slow down, does not fade.

SCENE — A vast flat meadow of short green grass drowned in dense cold fog, visibility about twenty-five metres, no horizon line. Far behind her right shoulder, deeply out of focus, an enormous pale blue-grey mass lies in the grass. She never comments on it.

LIGHT — Flat overcast daylight, fully diffuse, no shadows, no visible sun, cool blue-grey ambient, milky lifted blacks.

CAMERA — Handheld selfie with small natural drift and micro-shake, no gimbal, no stabilisation. Her extended forearm and near pauldron loom huge in the lower foreground. Her head sits in the upper third.

STYLE — Photoreal, shot on a modern smartphone, slightly soft, low contrast, cool desaturated grade, teal-cyan shadows, fine sensor noise. Candid social-media footage, deliberately not cinematic.
```

**Про вип.** Надёжнее собрать его в монтаже: направленный смаз плюс кадр в белое контролируются на
сто процентов, а модель вип «вверх в небо и вниз в траву» отдаёт через раз. Генерируйте клип A
чистым, на 5 секунд, без випа. Хвост ниже — только если хотите настоящий параллакс сквозь траву и
готовы к перегенерациям.

```text
NOT RECOMMENDED — the reference's original transition, kept here only for comparison:
the phone whips upward into the blank white sky and the frame blows out to near-white, then
whips down past her shoulder into the grass and goes black.

It needs a white flash, four black frames and a rotation done by hand in the edit. The swing
out of her own hand needs none of that: one straight cut on the blur and you are done.
```

Negative:

```text
tripod, static camera, locked-off, gimbal, smooth stabilised motion, dolly, crane, orbit; looking into the camera, smiling, posing, winking, talking to camera; still holding the cup at the end, throwing the cup at the camera, coffee splashing the lens, coffee on her face or armour; text, watermark, logo, subtitles, captions, UI overlay, timestamp; extra fingers, six fingers, malformed hands, warped gauntlet, melted armour plates, floating armour, plates clipping through the cup; duplicate limbs, two heads, distorted face, asymmetric eyes; cartoon, anime, illustration, 3D render, plastic skin, waxy skin, CGI sheen, beauty-filter smoothing, airbrushed skin; oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun; blurry face, low resolution, upscaling artifacts, repeating chainmail pattern; fire, smoke, sparks; blood, gore
```

## 8. Промпт · Клип B

`prompts/clip-b.txt` · `prompts/clip-b1-wake.txt` · `prompts/clip-b2-roar.txt` · `prompts/clip-b.negative.txt`

Здесь исправлены выдох в холодный воздух, приминание травы под челюстью, радиальная волна от рёва
и стойка вместо отшатывания.

```text
Horizontal 16:9 handheld phone video, shot on the same phone as the previous clip, now turned onto its side and pointing away from her. FIRST PERSON: she is behind the camera, filming with one hand. She is not in the shot. 24mm wide lens.

OPENING — The clip BEGINS mid-swing, heavily motion-blurred, sweeping in from the left, and settles over the first half-second onto what is ahead of her. Do not start from a still frame.

FRAMING — Low, roughly chest height, handheld, never locked. In the lower right corner, close to the lens and slightly out of focus, the edge of her gauntleted hand and the rim of her polished pauldron stay visible — the only thing in frame that gives the creature its scale.

CREATURE — Ahead of her across open grass, a colossal dragon lies prone in the meadow, head resting on the ground and turned slightly toward her, eyes closed. At the start its head alone occupies the centre and right of the frame and stands about half the frame height; the body recedes away to the left and dissolves into fog. Pearl-white and ice-blue hide. A broad field of opalescent dichroic scales across the neck and shoulder throwing prismatic pink, cyan, mint and gold glints. A saw-tooth ridge of tall bone-white dorsal spines runs down the neck and back. A fan of long pale spines frames the cheeks and jaw like a frill. Two thick bone-white horns sweep back from the crown, banded near the base with dark bronze metal cuffs. Two whip-thin bronze tendrils arc from behind each eye over the brow. Fine pebbled scales on the muzzle, pink nostril slits, a pink-flushed nose. An enormous folded membranous wing, semi-translucent pale grey-pink with visible finger bones, lies beyond it. Slow faint plumes of breath vapour drift from the nostrils into the cold air.

ACTION, in strict order —
(0-0.8 s) The frame settles out of the blur onto the sleeping creature.
(0.8-3 s) Nothing happens. The phone drifts with her breathing, small involuntary handheld shake, one tiny correction of the framing.
(3-4.5 s) One vast amber eye opens — warm gold iris, vertical black slit pupil — and looks straight into the lens.
(4.5-6.5 s) The head lifts off the ground, the grass beneath its jaw flattening and springing back, and turns to face the camera. Both eyes open. The phone tilts up to keep the head in frame and sags a few centimetres as her arm drops.
(6.5-8 s) The head cranes down toward the phone until one amber eye alone fills half the frame. The frame jerks backward as she takes a step back, but she keeps filming.
(8-10 s) The jaws split open into a roar directly into the lens — pale pink-lavender palate, rows of white conical teeth, long pink tongue. Hot breath vapour blasts across the glass and briefly fogs it. The grass lies flat in a radial wave. The phone shakes hard and tips, the frame swinging down toward the grass at her feet, where one polished greave and boot show for a moment, tiny against the creature above.

LIGHT — Flat overcast daylight, fully diffuse, no shadows, no visible sun, cool blue-grey. Dense low ground fog. Flat pale blue-white sky. Soft bloom on the white scales.

STYLE — Photoreal, shot on a modern smartphone, handheld, slightly soft, low contrast, cool desaturated grade, teal-cyan shadows, fine sensor noise, mild rolling-shutter wobble on the fast moves. Found-footage realism. NOT cinematic, no film look, no tripod, no colour-graded blockbuster look.
```

Если десяти секунд не хватает на шесть битов — а чаще всего не хватает — разбейте на две
генерации. В `clip-b2-roar.txt` добавлен бит, которого в референсе нет: дракон смотрит на её меч,
потом ей в лицо, и медленно моргает. Узнавание вместо голода.

Negative (первая строка — самая важная: камера обязана стоять):

```text
tripod, locked-off camera, static camera, gimbal, steadicam, smooth stabilised motion, dolly, crane, drone shot, orbit, cinematic camera move; third-person shot, the woman visible in frame, her face, her full body, seeing her from behind, over-the-shoulder shot, reverse angle; sword, weapon, blade, scabbard, raised sword; film look, anamorphic, letterbox bars, black bars, 35mm grain, colour-graded blockbuster look, shallow cinema depth of field; text, watermark, logo, subtitles, captions, UI overlay, phone recording indicator, phone interface, timestamp; morphing scales, drifting horn geometry, changing horn count, inconsistent wing bones, wing membrane popping, extra limbs, extra heads, two tails; cartoon, anime, illustration, stylised, cel shading, video-game cutscene, plastic CGI sheen, rubbery skin; oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun, blue hour, night; fire breath, flames, lightning, magic glow, particle sparkles; blood, gore, being eaten, dying; low resolution, upscaling artifacts, frame stutter, slow motion, speed ramp
```

## 9. Параметры и консистентность персонажа

```text
TWO GENERATIONS. That is the whole film.

CLIP A   aspect 9:16   1080x1920   24 fps   4 s (5 s if 4 is not offered)
CLIP B   aspect 16:9   1920x1080   24 fps   10 s
         reference image = your own photo of her, same file in both clips

PER-BEAT PACING -- pace the prompt to these or the model rushes the payoff:

A (4 s)     0.0-1.8   sipping, bored, gaze off-lens
            1.8-2.3   eyes snap right, straw leaves her lips
            2.3-2.8   throws the cup back over her shoulder
            2.8-4.0   swings the phone straight onto the creature. ENDS MID-SWING.

B (10 s)    0.0-0.8   settles out of the blur onto the sleeping creature
            0.8-3.0   nothing happens. breathing, handheld drift
            3.0-4.5   amber eye opens, looks into the lens
            4.5-6.5   head lifts off the ground, turns to the camera
            6.5-8.0   cranes down, one eye fills half the frame, she steps back
            8.0-10    roar into the lens, breath fogs the glass, phone tips down

IF 10 s IS NOT AVAILABLE, split B into two:
CLIP B1  16:9  6 s   settle -> eye opens -> head lifts (use the B1 prompt)
CLIP B2  16:9  5 s   blink -> crane down -> roar (use the B2 prompt,
                     start image = B1's last frame)

CHARACTER: her face comes from YOUR reference photo, not from the prompt.
Feed the same file to both clips. The prompt only fixes the hair length,
the armour and what she does -- everything about her face, skin and build
should come from the photo. Do not add facial description on top of it,
you will only fight the image.
```

**Честная оговорка.** Конкретные названия полей, доступные длительности и разрешения у Seedance 2.5
отличаются между интерфейсами (Dreamina / Jimeng, Volcano Engine, сторонние API). Сами промпты от
интерфейса не зависят, но длительность и формат выставляйте те, что реально доступны у вас.

Одно правило важнее всех параметров: **одно и то же референсное изображение персонажа во всех
генерациях.** И верните её лицо хотя бы на один кадр во второй половине — иначе половинки
останутся склеены гардеробом, а не личностью.

## 10. Сборка в монтаже

```text
ONE CUT. No flash, no black frames, no rotation keyframes, no blur plugin,
no transition of any kind. That is the point.

1.  Timeline: 1080 x 1920, 24 fps.

2.  CLIP A            00:00.00 -> 00:04.00      as generated, vertical, full bleed.
                                                 Trim the out-point to the frame where
                                                 the swing blur is HEAVIEST -- usually
                                                 2 or 3 frames before the clip ends.

3.  CLIP B            00:04.00 -> 00:14.00      ROTATE 90 DEGREES CLOCKWISE.
                                                 1920x1080 rotated = 1080x1920 exactly.
                                                 Zero letterboxing, no scaling, full bleed.
                                                 Trim the in-point to ITS heaviest blur
                                                 frame, then butt it straight against A.

4.  OUT               00:14.00 -> 00:14.40      hard cut to black. No fade.

Total: ~14.4 s.

WHY THERE IS NOTHING ELSE TO DO. Both sides of the cut are heavy motion blur
travelling in the same direction, so the eye cannot find the join and fills in the
90-degree roll by itself. That is why clip A must END mid-swing and clip B must
BEGIN mid-swing -- if either one settles, you lose the invisible cut and you are
back to needing a flash and black frames to hide the seam.

The viewer turns the phone COUNTER-CLOCKWISE to see clip B upright, and does it
without being told, because they just watched her turn her own phone.

TEST IT ON A REAL PHONE. Turn auto-rotate ON and confirm the player does NOT
re-rotate your clip and kill the whole gag. Upload as a single flat 9:16 file --
never as a landscape file with a "turn your phone" caption.
```

## 11. Звук

Модель звук не сделает. Ни одной реплики в референсе нет, и это правильно — но в нём нет и тишины.

```text
Everything here is phone-mic sound. No score until the very end -- a scored
opening would give away that this is a film. NO dialogue, NO voice-over, ever.

00:00.0 - 00:01.8   Wind across the phone mic, broadband, slightly clipping in the
                     gusts. Faint straw and ice. Nothing else. No music.

00:01.8 - 00:02.3   Wind drops for half a second, the way it does when someone
                     stops moving. This is your only warning cue.

00:02.3 - 00:02.8   The cup toss. Plastic clatter and a wet splash landing in grass,
                     panned hard right and behind. Small and dry -- a punctuation
                     mark, not an event.

00:02.8 - 00:04.0   Armour and cloth rustle, air roaring across the mic as she
                     swings the phone. Loud, ugly, real.

00:04.0 - 00:07.0   The swing lands. Wind bed continues unbroken ACROSS THE CUT --
                     do not dip the audio at the join, the continuous sound is what
                     sells the two clips as one take. Her breathing, close on the mic.

00:07.0 - 00:08.5   A very low sub-bass bed fades in under the wind as the head
                     lifts. Almost inaudible. No melody, no strings yet.

00:09.5 - 00:09.8   DROP TO NEAR SILENCE for 0.3 s before the roar. Wind out,
                     bass out, breath only. This is the whole punch.

00:09.8 - 00:14.0   Roar: layered sub-bass growl 40-80 Hz, mid-range rasp,
                     broadband breath noise, phone mic overloading and distorting.
                     Bring the score in HERE and only here if you want it.

00:14.0 - 00:14.4   Hard cut to black, roar tail in reverb only.
```

## 12. Как сделать это своим

Копировать содержание бессмысленно — рыцарь с айс-кофе уже занят. Копировать нужно конструкцию:
бытовой регистр, посаженная улика, замаскированный срез, разворот телефона, запертая камера, финал
без развязки. Всё остальное — переменные.

| Слот | В референсе | Чем можно заменить |
|---|---|---|
| Локация | туманный луг | солёная отмель на отливе · вулканический пепел · затопленное рисовое поле · снежная тундра · подземная парковка |
| Существо | белый перламутровый дракон | костяной левиафан · кит, лежащий в поле · механический голем · гигантский олень с гниющими рогами · нечто, чего не видно целиком |
| Реквизит-якорь | айс-кофе в пластиковом стакане | энергетик · сигарета · наушники · доедаемая лапша · зарядка от повербанка |
| Костюм | латы XV века, лилии | самурайское о-ёрой · скафандр · форма курьера · подрясник · тактическая экипировка |
| Первый регистр | скука | усталость после смены · раздражение на звонок · слёзы, которые она вытирает · смех в чей-то адрес |
| Слом | рёв в лицо | существо кладёт голову ей в ноги · открывает глаз и снова закрывает · встаёт и уходит · её называют по имени |
| Ось разворота | вертикаль → горизонт | горизонт → вертикаль (эпос сжимается в селфи) · разворот на 180° · два разворота в одном ролике |

**Что менять нельзя:** четыре чёрных кадра, запертую камеру во второй половине и отсутствие
подписи «поверни телефон». Это несущие элементы.

---

## Как получены цифры

Разбор построен на измерениях исходного файла, а не на просмотре:

- детекция склеек фильтром `select='gt(scene,N)'` при двух порогах (0.25 и 0.10);
- покадровая средняя яркость по сетке 32×32 в оттенках серого, 24 fps, окно 4.8–6.8 с;
- трекинг экранного размера фигуры по маске плаща (яркие низконасыщенные пиксели в полосе кадра),
  7 → 17.8 с — именно он доказывает, что камера в клипе B заперта;
- спектрограмма 44.1 кГц и профиль RMS для звука (речи нет, крещендо монотонное, +5 дБ с 3 по 20 с).

Кадры в `frames/` — выдержки из присланного референса, приведены для целей технического анализа.
