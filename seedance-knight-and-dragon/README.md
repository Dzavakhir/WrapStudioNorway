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
Vertical 9:16 handheld selfie video, front-facing phone camera held at arm's length, 24mm wide lens, mild barrel distortion.

SUBJECT — A woman in her early twenties, East Asian features, chin-length glossy black bob, fine strands blowing across her cheek, bare skin with visible pores, natural brows, glossy coral-nude lips, one small silver drop earring. She wears full mirror-polished white steel plate armour: gorget, layered pauldrons, articulated rerebrace-couter-vambrace on the extended arm, gauntlet with segmented finger lames, breastplate engraved with fine fleur-de-lis and a cruciform motif, blackened chainmail voiders at the armpits, domed rivets. An ivory hooded cloak hangs behind her shoulders. A cruciform sword with a black leather grip rides on a wide brown leather belt at her hip.

ACTION, in strict order —
(0-2 s) She sips iced black coffee through a white straw from a clear plastic to-go cup with a domed lid, ice cubes and condensation on the plastic, gauntleted fingers wrapped around it. Her gaze wanders off-lens to the right. She looks profoundly bored. She never looks into the camera.
(2-2.6 s) Her eyes flick right. The straw leaves her lips. She has heard something.
(2.6-3.4 s) Without looking, she flicks her wrist and tosses the cup back over her right shoulder. It tumbles away behind her, the lid coming loose, dark coffee and ice arcing out, and drops into the grass out of focus. Casual, dismissive, finished.
(3.4-5 s) She turns her wrist and swings the phone away from her face, out to her right and past her shoulder, until it points away from her at the pale mass in the fog. The frame sweeps right in heavy motion blur, her pauldron and cloak whipping past the lens, and the horizon rolls over as she turns the phone onto its side. The last frames are green blur and a vast pale shape resolving ahead.

SCENE — A vast flat meadow of short green grass drowned in dense cold fog, visibility about twenty-five metres, no horizon line. Far behind her right shoulder, deeply out of focus, an enormous pale blue-grey mass lies in the grass. She never comments on it.

LIGHT — Flat overcast daylight, fully diffuse, no shadows, no visible sun, cool blue-grey ambient, milky lifted blacks.

CAMERA — Handheld selfie with small natural drift and micro-shake, no gimbal, no stabilisation. Her extended forearm and near pauldron loom huge in the lower foreground. Her head sits in the upper third. In the final beat the camera swings hard right and rolls onto its side.

STYLE — Photoreal, shot on a modern smartphone, slightly soft, low contrast, cool desaturated grade, teal-cyan shadows, fine grain. Candid social-media footage, deliberately not cinematic.
```

**Про вип.** Надёжнее собрать его в монтаже: направленный смаз плюс кадр в белое контролируются на
сто процентов, а модель вип «вверх в небо и вниз в траву» отдаёт через раз. Генерируйте клип A
чистым, на 5 секунд, без випа. Хвост ниже — только если хотите настоящий параллакс сквозь траву и
готовы к перегенерациям.

```text
ALTERNATIVE FINAL BEAT — instead of the swing, if you want the reference's original
transition: the phone whips violently upward into the blank white sky and the frame blows out
to near-white, then whips down past her shoulder into the grass at her feet, smearing into
dark green motion blur, and goes black.

Weaker choice. The swing is motivated by her, the whip is motivated by nothing.
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
Horizontal 16:9 cinematic wide shot. LOCKED-OFF STATIC CAMERA on a tripod at grass-top height, roughly 40cm above the ground, 40mm lens. The camera never moves: no pan, no tilt, no zoom, no dolly, no shake, for the entire shot. Only the creature and the grass move.

FOREGROUND — A single out-of-focus blade of green grass rises through the lower-left corner as a soft bokeh element.

SUBJECT — Dead centre, small, about one sixth of the frame height: a woman knight stands with her back three-quarters to camera in knee-high wind-rippled green grass. Ivory hooded cloak to mid-calf, drifting slowly to her left. Mirror-polished silver plate armour on arms and legs. Chin-length black bob. A long straight silver sword hangs from her right hand, tip low.

CREATURE — Filling the upper two-thirds of the frame behind her, a colossal dragon lies prone in the meadow, head resting on the ground, snout pointing right, eyes closed. Its head alone is five times her full height. Pearl-white and ice-blue hide. A broad field of opalescent dichroic scales across the neck and shoulder throwing prismatic pink, cyan, mint and gold glints. A saw-tooth ridge of tall bone-white dorsal spines runs down the neck and back. A fan of long pale spines frames the cheeks and jaw like a frill. Two thick bone-white horns sweep back from the crown, banded near the base with dark bronze metal cuffs. Two whip-thin bronze tendrils arc from behind each eye over the brow. Fine pebbled scales on the muzzle, pink nostril slits, a pink-flushed nose. An enormous folded membranous wing, semi-translucent pale grey-pink with visible finger bones, lies on the left. The far body dissolves into fog.

ACTION, in strict order —
1. Stillness. The dragon sleeps. Only the grass and her cloak move in the wind.
2. One vast amber eye opens — warm gold iris, vertical black slit pupil — and finds her.
3. She raises the sword slowly out to her side.
4. The head lifts off the ground, the grass beneath its jaw flattening and springing back, and rotates to face her front-on. Both eyes open, faintly glowing.
5. The head cranes forward and lowers toward her until it fills the frame.
6. The jaws split open into a roar — pale pink-lavender palate, rows of white conical teeth, long pink tongue — and a dense plume of hot breath vapour blasts out into the cold air. The grass lies flat in a radial wave. Her cloak snaps horizontal. She drops into a braced stance, sword raised across her body, and does not retreat.

LIGHT — Flat overcast daylight, fully diffuse, no shadows, no visible sun, cool blue-grey. Dense low ground fog. Flat pale blue-white sky. Soft bloom on the white scales.

STYLE — Photoreal cinematic, cool desaturated grade, teal-cyan shadows, lifted milky blacks, low contrast, heavy atmospheric perspective, fine 35mm grain, subtle vignette. Epic fantasy realism, live-action, not animated.
```

Если десяти секунд не хватает на шесть битов — а чаще всего не хватает — разбейте на две
генерации. В `clip-b2-roar.txt` добавлен бит, которого в референсе нет: дракон смотрит на её меч,
потом ей в лицо, и медленно моргает. Узнавание вместо голода.

Negative (первая строка — самая важная: камера обязана стоять):

```text
camera movement, camera pan, camera tilt, zoom, dolly in, dolly out, push in, pull back, handheld shake, orbit, crane, drone shot, rack focus on the camera; text, watermark, logo, subtitles, captions, UI overlay; morphing scales, drifting horn geometry, changing horn count, inconsistent wing bones, wing membrane popping, extra limbs, extra heads, two tails; the knight floating above the grass, feet not touching the ground, knight sliding; cartoon, anime, illustration, stylised, cel shading, video-game cutscene, plastic CGI sheen, rubbery skin; oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun, blue hour, night; fire breath, flames, lightning, magic glow, particle sparkles; blood, gore, the knight being eaten, the knight dying; low resolution, upscaling artifacts, frame stutter, speed ramp
```

## 9. Параметры и консистентность персонажа

```text
CLIP A    aspect 9:16   1080x1920   24 fps   5 s (6 s if offered)   seed: lock it
CLIP B1   aspect 16:9   1920x1080   24 fps   10 s                   seed: lock it
CLIP B2   aspect 16:9   1920x1080   24 fps   5 s                    seed: lock it
                                                    start image = B1's last frame

PER-BEAT PACING -- pace the prompt to these or the model rushes the payoff:

A  (5 s)    0.0-2.0   sipping, bored, gaze off-lens
            2.0-2.6   eyes flick right, straw leaves her lips
            2.6-3.4   tosses the cup back over her shoulder
            3.4-5.0   swings the phone around onto the dragon, rolls it on its side

B1 (10 s)   0.0-1.5   she walks away from the lens, the pale mass resolves
            1.5-4.0   nothing happens. dragon asleep. wind only
            4.0-5.8   amber eye opens
            5.8-7.0   she raises the sword
            7.0-10    head lifts off the ground, starts to turn

B2 (5 s)    0.0-1.5   turns front-on, looks at her sword, slow blink
            1.5-2.8   cranes forward and down
            2.8-4.3   jaws open, roar, breath plume, grass wave, she braces
            4.3-5.0   hold on the open maw

Reference image: feed the SAME character still to every clip.
Generate her once as a still (front 3/4, armour, ivory cloak, black bob,
flat overcast light, fog) and reuse that one file everywhere.
Without it the halves will not read as the same person.
```

**Честная оговорка.** Конкретные названия полей, доступные длительности и разрешения у Seedance 2.5
отличаются между интерфейсами (Dreamina / Jimeng, Volcano Engine, сторонние API). Сами промпты от
интерфейса не зависят, но длительность и формат выставляйте те, что реально доступны у вас.

Одно правило важнее всех параметров: **одно и то же референсное изображение персонажа во всех
генерациях.** И верните её лицо хотя бы на один кадр во второй половине — иначе половинки
останутся склеены гардеробом, а не личностью.

## 10. Сборка в монтаже

```text
1.  Timeline: 1080 x 1920, 24 fps.

2.  CLIP A            00:00.00 -> 00:04.67      as generated, vertical, full bleed.
                                                 Frames 0-112. Cup tossed at ~2.6 s,
                                                 phone starts swinging at ~3.4 s.

3.  THE ROLL          00:04.67 -> 00:05.00      Clip A's last 8 frames only.
                                                 Keyframe rotation 0 -> 90 degrees CW
                                                 across those 8 frames, ease-in.
                                                 Add directional blur ramping 0 -> 140 px
                                                 along the swing axis.
                                                 The model already gave you the sweep;
                                                 you are only finishing the roll, because
                                                 a generated 90-degree roll is unreliable.

4.  MASKED CUT        00:05.00 -> 00:05.12      3 frames of pure black. Scale and
                                                 framing change here.
                                                 Do not cross-dissolve. Do not lengthen
                                                 past 4 frames -- the swing already did
                                                 the work the reference needed 4 frames for.

5.  CLIP B1           00:05.12 -> 00:15.12      ROTATE 90 DEGREES CLOCKWISE.
                                                 1920x1080 rotated = 1080x1920 exactly.
                                                 Zero letterboxing, no scaling, full bleed.

6.  CLIP B2           00:15.12 -> 00:20.12      same rotation. Straight cut from B1,
                                                 no transition -- the head position matches
                                                 because B2 started from B1's last frame.

7.  OUT               00:20.12 -> 00:20.50      hard cut to black. No fade.

Total: 20.5 s.

The viewer turns the phone COUNTER-CLOCKWISE to see clip B upright. Because she
visibly turns her own phone onto its side at the end of clip A, the viewer copies
the gesture almost reflexively -- that is the whole reason this version beats the
reference, which rolls the camera for no stated reason.

TEST IT ON A REAL PHONE. Turn auto-rotate ON and confirm the player does NOT
re-rotate your clip and kill the whole gag. Upload as a single flat 9:16 file --
never as a landscape file with a "turn your phone" caption.
```

## 11. Звук

Модель звук не сделает. Ни одной реплики в референсе нет, и это правильно — но в нём нет и тишины.

```text
00:00.0 - 00:02.6   Wind bed, broadband, no music event. One sustained low drone
                     around 200-600 Hz (strings or wordless choir). Faint straw
                     and ice sounds. NO dialogue, NO voice-over, ever.

00:02.6 - 00:03.0   The cup toss. Plastic clatter and a wet splash landing in grass,
                     panned hard right and slightly behind. Keep it small and dry --
                     it is a punctuation mark, not an event.

00:03.4 - 00:04.7   Cloth-and-armour rustle as she swings the phone. Air moving
                     across the mic, filter sweeping up. Let the wind bed swell.

00:04.7 - 00:05.0   The roll. One short rising whoosh, cut off hard.

00:05.0 - 00:05.12  NEAR SILENCE over the 3 black frames. This is the whole trick.

00:05.12 - 00:11.0  The drone returns, wider and lower. Add a sub-bass bed.
                     Her footsteps in grass for the first 1.5 s, then nothing.
                     Slow strings enter underneath.

00:09.2             One low impact sting on the eye opening. Single hit,
                     no reverb tail into the mix.

00:11.0 - 00:15.0   Build: rising strings, a ticking pulse. Still no percussion hits.

00:15.0 - 00:15.3   DROP TO NEAR SILENCE for 0.3 s. The reference does not do this
                     and it costs it the whole punch. Do it.

00:15.3 - 00:20.1   The turn, the blink, then the roar: layered sub-bass growl
                     40-80 Hz, mid-range rasp, broadband breath noise, brass and
                     choir crescendo over the top.

00:20.1 - 00:20.5   Hard cut to black, roar tail in reverb only.
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
