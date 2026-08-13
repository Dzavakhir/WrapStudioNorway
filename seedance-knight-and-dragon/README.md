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

Вам нужно то же: генерация A, генерация B и монтаж, который их сшивает. На практике B удобнее взять
двумя кусками, так что генераций три. Плюс одно референсное изображение персонажа, общее для всех.

## 7. Один промпт на всё

`prompts/ONE-SHOT-21s.txt` · `prompts/ONE-SHOT-21s.negative.txt`

Весь фильм одной генерацией, 21 секунда, вертикаль от начала до конца. Если нужен только результат и
не нужен монтаж — берите этот раздел и дальше можно не читать.

**Чего этот вариант не может, и почему.** Одна генерация — это одно соотношение сторон. Трюк с
поворотом телефона требует вертикального и горизонтального кадра в одном файле, поэтому в один промпт
он не влезает физически: либо вторая половина будет горизонтальной картинкой в чёрных полях внутри
вертикали, либо начало перестанет быть вертикальным селфи. Здесь вертикаль все 21 секунду: разворот
камеры, посадка кадра, масштаб, пробуждение и рёв на месте, поворота телефона нет. Нужен он —
минимум две генерации, разделы 8–10.

Вертикальная композиция во второй половине не хуже, а местами злее: голова и шея уходят вверх по
кадру, она стоит в нижней трети, и пасть опускается на неё сверху.

```text
VERTICAL 9:16 video, 1080x1920, portrait orientation for the entire film. One continuous 21-second take. The camera is her point of view for the first 3.7 seconds and is then thrown away and left lying in the grass, still recording, for the rest of the film. The camera object itself is NEVER visible in frame — no phone, no device, no hand holding anything up to film with. No dialogue, no speech, no voice-over at any point.

CHARACTER — Take her face, skin tone and features from the reference image and do not restyle them. Dark hair to just past the collarbone, loose, lifting across her cheek in the wind. Full mirror-polished white steel plate armour, bright and reflective like a mirror: gorget, layered pauldrons, articulated arm harness, gauntlets with segmented finger lames, breastplate engraved with fine fleur-de-lis and a cruciform motif, blackened chainmail voiders at the armpits, domed rivets. An ivory hooded cloak to mid-calf. A long straight sword in a plain scabbard on a wide brown leather belt at her hip.

WORLD — A vast flat meadow of knee-high green grass drowned in dense cold fog, visibility about thirty metres, no horizon line. Bright flat overcast daylight, high-key, luminous glowing white fog, fully diffuse, no shadows, no visible sun. Pale, airy and light. NOT dark, NOT dusk, NOT moody, NOT low-key.

THE CREATURE — A colossal dragon, pearl-white and ice-blue, lying prone and asleep in the meadow. Its head alone is five times a person's full height. Opalescent dichroic scales across the neck and shoulder throwing prismatic pink, cyan, mint and gold glints. A saw-tooth ridge of tall bone-white dorsal spines down the neck and back. A fan of long pale spines framing the cheeks and jaw like a frill. Two thick bone-white horns sweeping back from the crown, banded near the base with dark bronze metal cuffs. Two whip-thin bronze tendrils arcing from behind each eye over the brow. Fine pebbled scales on the muzzle, pink nostril slits, a pink-flushed nose. Enormous folded membranous wings, semi-translucent pale grey-pink with visible finger bones. Amber-gold eyes with vertical black slit pupils. Slow plumes of breath vapour drifting from the nostrils into the cold air. It is a living animal of hide and bone — NOT a vehicle, NOT a machine, NOT a spacecraft, NOT a dome, no lights, no windows.

TIMELINE — follow exactly, in this order, and do not reorder or compress:

00.0-02.5  SELFIE. Handheld at arm's length, 24mm wide, micro-shake, no stabilisation.
           Her near forearm and pauldron loom huge in the lower foreground, running out
           of frame toward the lens; her head sits in the upper third. She sips iced
           black coffee through a white straw from a clear plastic to-go cup with a
           domed lid, ice cubes and condensation, gauntleted fingers wrapped around it.
           Her gaze wanders off past the lens to the right, unfocused. Profoundly bored.
           She never makes eye contact with the lens. Far behind her right shoulder,
           deep in the fog and far out of focus, the pale scaled flank and spine-ridge
           of the sleeping creature. She never looks at it, never mentions it.

02.5-03.0  Her eyes snap right. The straw leaves her lips.

03.0-03.3  Without looking, she flicks her wrist and throws the cup back over her right
           shoulder. Her hand is now EMPTY.

03.3-03.7  Then, in the same dismissive motion, she throws THE CAMERA ITSELF backwards
           over her right shoulder. Her arm swings back and releases. Nobody is holding
           it any more.

03.7-04.8  THE CAMERA IS IN THE AIR, tumbling backwards away from her. The frame spins
           end over end — grass, white sky, grass, white sky — in heavy motion blur,
           while she and the creature recede and shrink rapidly into the distance.

04.8-05.4  It hits the ground, bounces once in the stems, and comes to rest lying in
           the grass, lens pointing forward at her back. A few blades of grass fall
           across the lens, close and far out of focus.

05.4-05.9  The image steadies and LOCKS. From this moment the camera NEVER MOVES AGAIN
           for the rest of the film: it is lying abandoned in the grass, nobody is
           holding it, there is no pan, no tilt, no zoom, no dolly, no drift. Only she,
           the creature and the grass move. The shot is now a LOW WIDE at grass-top
           height, roughly 30cm above the ground, blades of grass crossing the bottom
           of frame right at the lens. SHE IS NOW SMALL — about one sixth of the frame
           height, standing in the lower third, back three-quarters to camera, feet
           hidden among the stems, cloak drifting. The creature's head and neck rise up
           the frame above and behind her, filling the upper two-thirds. Her small size
           against it is the whole point of the shot.

05.9-08.5  Stillness. The creature sleeps. Nothing happens. Only the grass and her cloak
           move in the wind.

08.5-10.5  One vast amber eye opens — warm gold iris, vertical black slit pupil — and
           finds her. The head does not move.

10.5-11.8  She draws the sword and raises it slowly out to her side.

11.8-14.5  The head lifts off the ground, the grass beneath its jaw flattening and
           springing back, and rotates to face her front-on. Both eyes open, faintly
           glowing.

14.5-15.8  The pupils flick down to the sword in her hand, then back up to her face.
           One slow blink. Recognition, not hunger.

15.8-17.3  The head cranes forward and lowers toward her until it fills the upper frame,
           breath fogging the cold air in slow pulses from the nostrils.

17.3-20.0  The jaws split open into a roar — pale pink-lavender palate, rows of white
           conical teeth, long pink tongue, thin strands of saliva — and a dense plume of
           hot breath vapour blasts out into the cold air. The grass lies flat in a
           radial wave rolling outward from the jaw; it reaches the lens and the stems
           in the foreground flatten away from the blast while the fallen camera
           trembles in the grass without moving from where it landed. Her cloak snaps
           horizontal. She drops into a braced stance, sword raised across her body,
           and does not retreat.

20.0-21.0  Hold on the open maw. Cut.

STYLE — Photoreal live action throughout. Up to 05.4: consumer-camera look, slightly soft,
candid social-media footage, deliberately not cinematic. From 05.4 onward, once the camera
is lying in the grass: the same camera and the same grade, but the framing is now
cinematic — heavy atmospheric perspective, subtle vignette. Throughout: cool desaturated
grade, teal-cyan shadows, lifted milky blacks, low contrast, fine grain. Live action, not
animated, not stylised.
```

Negative:

```text
smartphone, phone, mobile phone, holding a phone, a phone in her hand, phone appearing in her hand, black rectangle in her hand, screen, tablet, device visible in frame, selfie stick, picking an object up, holding anything after the throw;

UFO, flying saucer, spacecraft, spaceship, alien ship, dome, glass dome, lit windows, glowing windows, landing legs, building, hangar, tent, vehicle, machine, boulder;

camera being picked up again, hand reaching for the camera, someone catching the camera, the camera landing face-down in the dirt, the camera landing lens-up at the sky, the camera continuing to fly, the camera rolling on after it lands, the camera sliding;

camera pan after the whip, camera tilt after the whip, zoom, dolly in, dolly out, push in, pull back, handheld shake in the second half, camera drift, orbit, crane, drone shot, cinematic camera move after the settle;

horizontal frame, landscape orientation, 16:9, widescreen, black bars, letterbox, aspect ratio change mid-shot;

dark, underexposed, dusk, twilight, night, blue hour, murky, gloomy, heavy shadows, low-key moody grade, crushed blacks;

the knight large in frame after the whip, close-up of the knight after the whip, her face visible after the whip, front view of the knight, knight floating above the grass, feet not touching the ground, knight sliding, knight walking away, knight running, knight retreating, knight falling over;

looking into the lens, eye contact with camera, smiling, posing, winking, talking to camera, dialogue, speech, lip sync, singing;

text, watermark, logo, subtitles, captions, UI overlay, timestamp;

extra fingers, six fingers, malformed hands, warped gauntlet, melted armour plates, floating armour, duplicate limbs, two heads, two swords, distorted face, asymmetric eyes, repeating chainmail pattern; morphing scales, drifting horn geometry, changing horn count, inconsistent wing bones, wing membrane popping, extra limbs, two tails;

cartoon, anime, illustration, 3D render, stylised, cel shading, video-game cutscene, plastic costume armour, matte white plastic, waxy skin, CGI sheen, beauty-filter smoothing;

oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun; fire breath, flames, lightning, magic glow, particle sparkles; blood, gore, being eaten, dying;

low resolution, upscaling artifacts, frame stutter, slow motion, speed ramp
```

**Если 21 секунда недоступна.** Промпт устоит и на 15, но резать надо в правильных местах. По
приоритету: сначала пауза `05.6-08.5` (оставьте 1 секунду вместо трёх), потом бит с моргáнием
`14.5-15.8` целиком, потом глоток до 1.5 s. Рёв и посадку кадра не трогайте. На 10 секундах этот
подход уже не работает — делите на два клипа.

**Самое хрупкое место — 04.6.** Именно там кадр должен сесть, запереться и сделать её маленькой.
Модель охотно оставляет камеру в руке и держит героиню крупно; тогда масштаб пропадает и ролик
рассыпается. Осталась крупной или камера продолжает дышать — перегенерируйте, доводить это в монтаже
нечем.

## 8. Промпт · Клип A

_Разделы 8-13 — маршрут с разворотом телефона: две-три генерации плюс монтаж._

`prompts/clip-a.txt` · `prompts/clip-a.negative.txt`

```text
VERTICAL 9:16 selfie video, 1080x1920, portrait orientation. Wide front-facing lens at arm's length, 24mm, mild barrel distortion. The camera is her point of view, and at the end of this shot she throws it away. The camera object itself is NEVER visible in frame — no phone, no device, no hand holding anything up to film with.

SUBJECT — Take her face, skin tone and features from the supplied reference image and do not restyle them. Dark hair to just past the collarbone, loose, lifting and crossing her cheek in the wind. She wears full mirror-polished white steel plate armour, bright and reflective like a mirror: gorget, layered pauldrons, articulated rerebrace-couter-vambrace on the near arm, gauntlet with segmented finger lames, breastplate engraved with fine fleur-de-lis and a cruciform motif, blackened chainmail voiders at the armpits, domed rivets. An ivory hooded cloak sits over her shoulders behind her neck. A long straight sword in a plain scabbard rides on a wide brown leather belt at her hip, untouched throughout.

ACTION, in strict order —
(0-2.2 s) She sips iced black coffee through a white straw from a clear plastic to-go cup with a domed lid, ice cubes and condensation on the plastic, gauntleted fingers wrapped around it. Her gaze wanders off past the lens to the right, unfocused. She looks profoundly bored. She never makes eye contact with the lens.
(2.2-2.5 s) Her eyes snap right. The straw leaves her lips.
(2.5-2.9 s) Without looking, she flicks her wrist and throws the cup back over her right shoulder. Her hand is now EMPTY. She picks nothing up.
(2.9-3.3 s) IMMEDIATELY, with no pause, in the same dismissive motion, she throws THE CAMERA ITSELF backwards over her right shoulder. Her arm swings back and releases. Nobody is holding it any more.
(3.3-5 s) THE CAMERA IS IN THE AIR, tumbling backwards away from her. The frame spins end over end — grass, white sky, grass, white sky — in heavy motion blur, while she and the pale shape behind her recede and shrink rapidly into the distance.

END OF SHOT — The clip ENDS while the camera is still in the air, still tumbling, still heavily blurred, before it lands. It does not land, does not settle, does not slow down, does not fade.

SCENE — A vast flat meadow of short green grass drowned in dense cold fog, visibility about twenty-five metres, no horizon line. About thirty metres behind her right shoulder, mostly swallowed by fog and far out of focus, lies the flank of an ENORMOUS SLEEPING ANIMAL: a long low ridge of pale scaled hide, a row of bone-white spines running along its back, the curve of a huge jaw resting in the grass. It is a living creature, unmistakably organic, made of hide and bone. It is NOT a vehicle, NOT a machine, NOT a spacecraft, NOT a dome, NOT a tent, NOT a rock, NOT a building, and it has NO lights and NO windows. She never looks at it and never mentions it.

LIGHT — Bright flat overcast daylight, high-key, luminous glowing white fog, fully diffuse, no shadows, no visible sun. Pale, airy and light. Cool blue-grey ambient with milky lifted blacks. NOT dark, NOT dusk, NOT moody, NOT low-key.

CAMERA — Handheld selfie framing with small natural drift and micro-shake, no gimbal, no stabilisation. Her near forearm and pauldron loom huge in the lower foreground, running out of frame toward the lens. Her head sits in the upper third. From 2.9 s the camera is an object in flight: it tumbles freely, end over end, and the framing is whatever a thrown camera would record.

STYLE — Photoreal, consumer-camera look, slightly soft, low contrast, cool desaturated grade, teal-cyan shadows, fine sensor noise. Candid social-media footage, deliberately not cinematic.
```

**Критично одно:** клип обязан закончиться в середине випа, в смазе. Не устояться, не доехать до
существа. От этого зависит вся склейка — смаз с обеих сторон единственное, что её прячет.

И ни слова про телефон. Слово «phone» в описании действия заставляет модель нарисовать телефон в
руке — это ровно то, что случилось на первом прогоне. Описывается только движение камеры.

Negative:

```text
smartphone, phone, mobile phone, cell phone, iphone, holding a phone, a phone in her hand, phone appearing in her hand, black rectangle in her hand, screen, tablet, device, camera visible in frame, selfie stick, picking an object up, holding anything after the throw;

UFO, flying saucer, spacecraft, spaceship, alien ship, dome, glass dome, lit windows, glowing windows, landing legs, building, hangar, tent, vehicle, machine, boulder, rock formation;

camera roll, rolling camera, camera tumbling, spinning camera, barrel roll, upside down, inverted frame, 180 degree rotation, full rotation, camera dropped, camera falling, dutch angle;

horizontal frame, landscape orientation, 16:9, widescreen, black bars, letterbox;

dark, underexposed, dusk, twilight, night, murky, gloomy, heavy shadows, low-key moody grade, crushed blacks;

looking into the lens, eye contact with camera, smiling, posing, winking, talking to camera; tripod, static camera, locked-off, gimbal, smooth stabilised motion, dolly, crane, orbit; drawing the sword, raised sword, sword in her hand; coffee splashing the lens, coffee on her face; text, watermark, logo, subtitles, captions, UI overlay, timestamp; extra fingers, six fingers, malformed hands, warped gauntlet, melted armour plates, floating armour; duplicate limbs, two heads, distorted face, asymmetric eyes; cartoon, anime, illustration, 3D render, plastic costume armour, matte white plastic, waxy skin, CGI sheen, beauty-filter smoothing; oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun; blurry face, low resolution, upscaling artifacts, repeating chainmail pattern; fire, smoke, sparks; blood, gore
```

## 9. Что сломалось в первой генерации

Шесть отказов на первом реальном прогоне клипа A. Три из них — прямые баги промпта, все шесть
закрыты в тексте выше.

| Что вышло | Причина | Фикс |
|---|---|---|
| **В руке из ниоткуда возникает смартфон** — На 3.0 s рука пустая — стакан ещё летит в воздухе. На 3.5 s в той же руке уже чёрный смартфон. | Промпт называл телефон предметом, который она держит и поворачивает. Модель честно его нарисовала. | Слово «phone» вычищено из действия во всех клипах. Осталась только камера как точка зрения. После броска рука **пустая**, уходит вниз из кадра и не возвращается, плюс прямые запреты: «She picks nothing up. She holds nothing.» И весь блок телефонов в самом начале negative. |
| **Вместо дракона — летающая тарелка** — В тумане за её плечом висит диск с подсвеченными синими окнами и опорами. | Промпт говорил только «enormous pale blue-grey mass lies in the grass». Модель добила пустое место самым частым большим объектом в тумане. | Теперь описана живая туша: гребень бледной чешуйчатой шкуры, ряд костяных шипов вдоль спины, изгиб челюсти в траве, плюс явное «NOT a vehicle, NOT a spacecraft, NOT a dome, no lights, no windows». В negative — UFO, flying saucer, dome, lit windows. |
| **Кадр горизонтальный, 1920×1080** — Клип A сгенерирован в 16:9. | Формат стоял в шапке промпта, но недостаточно жёстко, и мог быть просто не выставлен в интерфейсе. | Шапка начинается с «VERTICAL 9:16, 1080x1920, portrait orientation», а landscape / 16:9 / widescreen / letterbox добавлены в negative. Без вертикали весь трюк с разворотом телефона невозможен. |
| **Камера кувыркается и уходит за 180°** — В последние 8 кадров камера переворачивается вверх ногами и продолжает вращаться. | Я просил у модели крен ровно на 90°. Модель не удерживает четверть оборота — она либо не доворачивает, либо улетает дальше. | Крен убран из промпта совсем. Модель делает только **плоский вип вправо**, камера остаётся ровной («does not roll, does not tumble, does not spin»). Четверть оборота — шесть ключевых кадров в монтаже, шаг 3. |
| **Темно, мутно, похоже на сумерки** — Общая яркость намного ниже референса, туман серый, доспех сел в тень. | «Cool desaturated grade» без указания уровня яркости — модель прочитала это как low-key. | Явно: «Bright flat overcast daylight, high-key, luminous glowing white fog, pale and airy», и рядом «NOT dark, NOT dusk, NOT moody». В negative — dark, underexposed, dusk, murky, crushed blacks. |
| **Вип втиснут в последние 0.3 s** — Первые 4.7 s она пьёт и держит телефон, а разворот успевает начаться только в самом конце. | Промпт отдавал випу 1.2 s из пяти, и модель растянула всё, что было до него. | Випу отдана вся последняя треть с прямым требованием: «This movement must fill the entire final two seconds and must NOT be finished before the clip ends.» |

**Что получилось хорошо и менять не надо:**

- Доспех, лилии и чернёная кольчуга — попадание. Гравировка читается.
- Длина волос теперь правильная: ниже ключиц, пряди летят по лицу.
- Геометрия селфи верная: ближняя рука и наплечник уходят к линзе, голова в верхней трети.
- Бросок стакана есть, и рука действительно разжимается.
- Клип кончается в движении, в смазе — то есть под склейку. Это главное, и это сработало.

**Отдельно про формат.** Если интерфейс не предлагает 9:16 — трюк в исходном виде собрать нельзя,
вертикаль обязательна. Обходной путь: генерировать A в 16:9 и кропать в 1080x1920 в монтаже. Для
селфи-крупняка центральный кроп переживается терпимо, но существо придётся сдвинуть ближе к центру,
за её плечо. Это компромисс, а не решение.

## 10. Промпт · Клип B

`prompts/clip-b.txt` · `prompts/clip-b1-wake.txt` · `prompts/clip-b2-roar.txt` · `prompts/clip-b.negative.txt`

Тот самый кадр из референса: запертая камера у самой травы, крошечная фигурка со спины и
колоссальная туша за ней. Ради него всё и делается.

Клип начинается в смазе, доезжающем справа — это стык с клипом A, — и за первые 0.8 s движение
гаснет, кадр встаёт в широкий план и **больше не двигается вообще**. Голова растёт в кадре потому,
что дракон поднимается, а не потому, что камера наезжает.

Здесь же исправлены выдох в холодный воздух, приминание травы под челюстью, радиальная волна от рёва
и стойка вместо отшатывания — всего этого в референсе нет.

```text
HORIZONTAL 16:9 video, 1920x1080, landscape orientation. 40mm lens.

OPENING — The clip BEGINS with the camera still in the air, tumbling end over end in heavy motion blur — grass, white sky, grass — as if it had just been thrown. Over the first second it hits the ground, bounces once in the stems, and comes to rest LYING ON ITS SIDE in the grass, which is why this shot is horizontal. Do not start from a still frame.

CAMERA — From the moment it lands, the camera is completely LOCKED for the rest of the shot: it is lying abandoned in the grass, nobody is holding it, and there is no pan, no tilt, no zoom, no dolly, no shake, no drift. It rests low, at grass-top height, roughly 30cm above the ground, with blades of grass crossing the bottom of frame right at the lens, close and far out of focus. Only the woman, the creature and the grass move. The camera object itself is never visible in frame.

FOREGROUND — A single out-of-focus blade of green grass rises through the lower-left corner as a soft bokeh element.

SUBJECT — Dead centre, SMALL, about one sixth of the frame height: a woman knight stands with her back three-quarters to camera in knee-high wind-rippled green grass, her feet hidden among the stems. Ivory hooded cloak to mid-calf, drifting slowly to her left. Mirror-polished silver plate armour on arms and legs. Dark hair to just past the collarbone. A long straight silver sword hangs from her right hand, tip low. Her small size against the creature is the whole point of the shot.

CREATURE — Filling the upper two-thirds of the frame behind her, a colossal dragon lies prone in the meadow, head resting on the ground, snout pointing right, eyes closed. Its head alone is five times her full height. Pearl-white and ice-blue hide. A broad field of opalescent dichroic scales across the neck and shoulder throwing prismatic pink, cyan, mint and gold glints. A saw-tooth ridge of tall bone-white dorsal spines runs down the neck and back. A fan of long pale spines frames the cheeks and jaw like a frill. Two thick bone-white horns sweep back from the crown, banded near the base with dark bronze metal cuffs. Two whip-thin bronze tendrils arc from behind each eye over the brow. Fine pebbled scales on the muzzle, pink nostril slits, a pink-flushed nose. An enormous folded membranous wing, semi-translucent pale grey-pink with visible finger bones, lies on the left. The far body dissolves into fog. Slow faint plumes of breath vapour drift from the nostrils into the cold air.

ACTION, in strict order —
(0-1 s) The tumbling camera lands, bounces once and comes to rest on its side in the grass. The image steadies and locks.
(0.8-3.5 s) Nothing happens. The dragon sleeps. Only the grass and her cloak move in the wind.
(3.5-5.5 s) One vast amber eye opens — warm gold iris, vertical black slit pupil — and finds her. The head does not move.
(5.5-6.5 s) She raises the sword slowly out to her side.
(6.5-8.5 s) The head lifts off the ground, the grass beneath its jaw flattening and springing back, and rotates to face her front-on. Both eyes open, faintly glowing.
(8.5-9.5 s) The pupils flick down to the sword in her hand, then back up to her face. One slow blink. Recognition, not hunger.
(9.5-10 s) The head begins to crane forward and lower toward her.

LIGHT — Bright flat overcast daylight, high-key, luminous glowing white fog, fully diffuse, no shadows, no visible sun. Pale, airy and light. Dense low ground fog. Flat pale blue-white sky. Soft bloom on the white scales. NOT dark, NOT dusk, NOT moody, NOT low-key.

STYLE — Photoreal cinematic, cool desaturated grade, teal-cyan shadows, lifted milky blacks, low contrast, heavy atmospheric perspective, fine grain, subtle vignette. Epic fantasy realism, live-action, not animated.
```

**Она должна быть маленькой** — одна шестая высоты кадра, не больше. Это самое хрупкое место
промпта: модель любит подтащить героиню ближе. Если вышла крупной — перегенерируйте, кадр без этого
не работает.

Рабочая схема — два куска: `clip-b1-wake.txt` (10 s, до поднятой головы) и `clip-b2-roar.txt`
(5 s, моргание, наклон, рёв), второй с последнего кадра первого. `clip-b.txt` — то же одной
генерацией на 10 s, но заканчивается на начале наклона, без рёва.

В B2 добавлен бит, которого в референсе нет: зрачки опускаются на её меч, потом возвращаются к лицу,
и одно медленное моргание. Узнавание вместо голода.

Negative (первые две строки — самые важные):

```text
camera pan, camera tilt, zoom, dolly in, dolly out, push in, pull back, handheld shake, camera drift, orbit, crane, drone shot, cinematic camera move after it lands; camera being picked up again, hand reaching for the camera, someone catching the camera, the camera landing face-down, the camera landing lens-up at the sky, the camera sliding or rolling on after it lands;

smartphone, phone, mobile phone, holding a phone, a phone in her hand, phone in frame, black rectangle, screen, tablet, device visible in frame, selfie stick;

UFO, flying saucer, spacecraft, dome, glass dome, lit windows, glowing windows, building, hangar, tent, vehicle, machine;

dark, underexposed, dusk, twilight, night, blue hour, murky, gloomy, heavy shadows, low-key moody grade, crushed blacks;

the knight large in frame, close-up of the knight, the knight filling the frame, her face visible, front view of the knight, the knight floating above the grass, feet not touching the ground, knight sliding, knight walking away, knight running, knight retreating, knight falling over;

first-person point of view, POV shot, found footage, phone footage look;

text, watermark, logo, subtitles, captions, UI overlay, timestamp; morphing scales, drifting horn geometry, changing horn count, inconsistent wing bones, wing membrane popping, extra limbs, extra heads, two tails, two swords; cartoon, anime, illustration, stylised, cel shading, video-game cutscene, plastic CGI sheen, rubbery skin; oversaturated, warm orange grade, golden hour, sunlight, hard shadows, lens flare, visible sun; fire breath, flames, lightning, magic glow, particle sparkles; blood, gore, being eaten, dying; low resolution, upscaling artifacts, frame stutter, slow motion, speed ramp
```

## 11. Длительности, параметры и консистентность персонажа

```text
THREE GENERATIONS.

CLIP A    aspect 9:16   1080x1920   24 fps   5 s
CLIP B1   aspect 16:9   1920x1080   24 fps   10 s
CLIP B2   aspect 16:9   1920x1080   24 fps   5 s
                                             start image = B1's last frame

          reference image = your own photo of her, the SAME file in all three

PER-BEAT PACING -- pace the prompt to these or the model rushes the payoff:

A (5 s)     0.0-2.4   sipping, bored, gaze off past the lens
            2.4-2.9   eyes snap right, straw leaves her lips
            2.9-3.4   throws the cup back over her shoulder, hand empties
            3.4-5.0   camera whips flat right onto the creature. ENDS MID-WHIP.

B1 (10 s)   0.0-0.8   blur dies out, frame settles into the wide and LOCKS
            0.8-3.5   nothing happens. dragon asleep. wind only
            3.5-5.5   amber eye opens, finds her. head does not move
            5.5-6.5   she raises the sword
            6.5-10    head lifts off the ground, rotates front-on, holds

B2 (5 s)    0.0-1.0   pupils drop to her sword, back up, one slow blink
            1.0-2.3   cranes forward and down until the head fills the frame
            2.3-4.3   roar, breath plume, radial grass wave, she braces
            4.3-5.0   hold on the open maw

IF YOU ONLY WANT A 15 s CUT: run A + B1 only and end on the lifted head.
It is a tighter edit than the full 20 s and loses nothing structural.

CHARACTER: her face comes from YOUR reference photo, not from the prompt.
The prompt only fixes the hair length, the armour and what she does. Do not
add facial description on top of the photo, you will only fight the image.
```

**Честная оговорка.** Конкретные названия полей, доступные длительности и разрешения у Seedance 2.5
отличаются между интерфейсами (Dreamina / Jimeng, Volcano Engine, сторонние API). Сами промпты от
интерфейса не зависят, но длительность и формат выставляйте те, что реально доступны у вас.

Одно правило важнее всех параметров: **одно и то же референсное изображение персонажа в обоих
клипах.** И лицо должно приходить из вашей фотографии, а не из текста — поэтому словесного описания
внешности в промптах больше нет, осталась только длина волос, доспех и действие. Не дописывайте
описание лица поверх фото: будете бороться с собственным референсом.

## 12. Сборка в монтаже

```text
ONE CUT. No flash, no black frames, no rotation keyframes, no blur plugin,
no transition of any kind. The thrown camera does all of it for you.

1.  Timeline: 1080 x 1920, 24 fps.

2.  CLIP A            00:00.00 -> 00:05.00      as generated, vertical, full bleed.
                                                 She throws the cup at ~2.4 s and the
                                                 camera at ~2.9 s. Trim the out-point to
                                                 a frame where the tumble blur is
                                                 HEAVIEST and the camera is still in
                                                 the air.

3.  CLIP B1           00:05.00 -> 00:15.00      ROTATE 90 DEGREES CLOCKWISE.
                                                 1920x1080 rotated = 1080x1920 exactly.
                                                 Zero letterboxing, no scaling, full bleed.
                                                 Trim the in-point to ITS heaviest tumble
                                                 frame, then butt it straight against A.

4.  CLIP B2           00:15.00 -> 00:20.00      same rotation. Straight cut from B1, no
                                                 transition -- the head position matches
                                                 because B2 started from B1's last frame.

5.  OUT               00:20.00 -> 00:20.40      hard cut to black. No fade.

Total: ~20.4 s.  (A + B1 only = ~15.4 s, and that is the tighter cut.)

WHY THERE ARE NO ROTATION KEYFRAMES ANY MORE. The camera is tumbling on both sides
of the cut, so the eye cannot find the join AND the 90-degree change of orientation
is already motivated: the camera lands on its side in the grass. That is why clip A
must END with the camera still in the air and clip B1 must BEGIN with it still in
the air. If clip A lands, you lose both the invisible cut and the reason the frame
is sideways.

The viewer turns the phone COUNTER-CLOCKWISE to see clip B upright, and does it
without being told, because they just watched the camera fall on its side.

TEST IT ON A REAL PHONE. Turn auto-rotate ON and confirm the player does NOT
re-rotate your clip and kill the whole gag. Upload as a single flat 9:16 file --
never as a landscape file with a "turn your phone" caption.
```

## 13. Звук

Модель звук не сделает. Реплик нет и не надо. Главное: **ветер должен идти непрерывно через
склейку** — именно он и склеивает два клипа в один дубль. И провал в тишину на 0.3 s перед рёвом,
чего в референсе нет.

```text
NO dialogue, NO voice-over, ever.

00:00.0 - 00:02.4   Wind across the mic, broadband, slightly clipping in the gusts.
                     Faint straw and ice. Nothing else. No music yet.

00:02.4 - 00:02.9   Wind drops for half a second, the way it does when someone stops
                     moving. This is your only warning cue.

00:02.9 - 00:03.4   The cup toss. Plastic clatter and a wet splash landing in grass,
                     panned hard right and behind. Small and dry -- a punctuation
                     mark, not an event.

00:02.9 - 00:05.0   The camera throw. Armour and cloth as her arm swings, then air
                     roaring across the mic in pulses as the camera tumbles -- the wind
                     noise should wobble in time with the spin. Loud, ugly, real.

00:05.0 - 00:05.4   IMPACT. One dull thud into soft ground, a short rustle of stems, and
                     the air noise stops dead. This is the best sound in the film -- do
                     not soften it and do not reverb it.

00:05.4 - 00:08.5   Wind bed continues UNBROKEN ACROSS THE CUT -- do not dip the audio
                     at the join, the continuous sound is what sells the two clips as
                     one take. But it is a DIFFERENT wind now: the mic is lying in the
                     grass, so add close stem rustle and cut the high end slightly, as
                     though the mic were half buried. A low sustained drone fades in
                     underneath, around 200-600 Hz.

00:08.5             One low impact sting on the eye opening. Single hit.

00:08.5 - 00:14.5   Build: the drone widens, a sub-bass bed enters, a slow ticking
                     pulse. Still no percussion hits.

00:17.0 - 00:17.3   DROP TO NEAR SILENCE for 0.3 s before the roar. Wind out, bass
                     out. This is the whole punch, and the reference does not do it.

00:17.3 - 00:20.0   Roar: layered sub-bass growl 40-80 Hz, mid-range rasp, broadband
                     breath noise, brass and choir crescendo over the top. Add the blast
                     wave arriving at the fallen mic a beat late -- a low thump and a
                     hard gust of stem rustle right at the lens.

00:20.0 - 00:20.4   Hard cut to black, roar tail in reverb only.
```

## 14. Как сделать это своим

Копировать содержание бессмысленно — рыцарь с айс-кофе уже занят. Копировать нужно конструкцию:
бытовой регистр, посаженная улика, разворот телефона, финал без развязки. Всё остальное — переменные.

| Слот | В референсе | Чем можно заменить |
|---|---|---|
| Локация | туманный луг | солёная отмель на отливе · вулканический пепел · затопленное рисовое поле · снежная тундра · подземная парковка |
| Существо | белый перламутровый дракон | костяной левиафан · кит, лежащий в поле · механический голем · гигантский олень с гниющими рогами · нечто, чего не видно целиком |
| Реквизит-якорь | айс-кофе в пластиковом стакане | энергетик · сигарета · наушники · доедаемая лапша · зарядка от повербанка |
| Костюм | латы XV века, лилии | самурайское о-ёрой · скафандр · форма курьера · подрясник · тактическая экипировка |
| Первый регистр | скука | усталость после смены · раздражение на звонок · слёзы, которые она вытирает · смех в чей-то адрес |
| Слом | рёв в лицо | существо кладёт голову ей в ноги · открывает глаз и снова закрывает · встаёт и уходит · её называют по имени |
| Ось разворота | вертикаль → горизонт | горизонт → вертикаль (эпос сжимается в селфи) · разворот на 180° · два разворота в одном ролике |

**Что менять нельзя.** Три вещи. Клип A обязан кончаться в середине випа, а клип B — начинаться в
середине випа: на этом держится невидимая склейка. Подписи «поверни телефон» быть не должно. И финал
без развязки: ни победы, ни смерти, ни объяснения.

**И запертая камера во второй половине.** Она названа главным техническим решением в разделе 1, и
это измерено, а не на глаз: рост фигуры на экране держится в пределах ±5% с 7 по 17 секунду. Стоит
дать камере наезд — и масштаб рассыпается.

---

## Как получены цифры

Разбор построен на измерениях исходного файла, а не на просмотре:

- детекция склеек фильтром `select='gt(scene,N)'` при двух порогах (0.25 и 0.10);
- покадровая средняя яркость по сетке 32×32 в оттенках серого, 24 fps, окно 4.8–6.8 с;
- трекинг экранного размера фигуры по маске плаща (яркие низконасыщенные пиксели в полосе кадра),
  7 → 17.8 с — именно он доказывает, что камера в клипе B заперта;
- спектрограмма 44.1 кГц и профиль RMS для звука (речи нет, крещендо монотонное, +5 дБ с 3 по 20 с).

Кадры в `frames/` — выдержки из присланного референса, приведены для целей технического анализа.
Раздел 8 построен на разборе первой реальной генерации по этим промптам.
