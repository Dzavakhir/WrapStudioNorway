# Банк тем «Онно AI Academy» — 120 дней

**Версия 2.0 · аудит проведён 2026-08-15.** Формат канала: **«Один предмет»** — один предмет висит
в луче, Джавохир одним движением руки превращает его в ответ на сегодняшний вопрос об AI. Ролик
молчит. 10.00 секунд, одна генерация, одна и та же комната.

Этот файл — **единственный источник темы дня**. Ежедневная задача в 04:00 не выбирает, не сочиняет,
не переводит и не импровизирует: она вычисляет номер темы по дате, берёт блок целиком и
подставляет из него четыре готовых английских поля в `prompts/TEMPLATE.md`.

Порядок исполнения, полномочия и лимиты — в `RUNBOOK.md`. Этот файл не владеет ничем, кроме тем.

---

## 1. Детерминированное соответствие «дата → тема»

```
index      = (число суток между 2026-01-01 и датой запуска) mod 120
topic_no   = index + 1                       # 1..120, в таблице записан как 001..120
```

Псевдокод для рантайма (без памяти, без состояния, только системная дата):

```python
from datetime import date
EPOCH = date(2026, 1, 1)          # день 0 = тема 001

def topic_of(day: date) -> int:
    return (day - EPOCH).days % 120 + 1
```

Правила рантайма:

- **Дата берётся строго в часовом поясе публикации (Ташкент, UTC+5).** Единственная разрешённая
  команда получения даты: `TZ=Asia/Tashkent date +%F`. Голый `date +%F` в контейнере вернёт UTC,
  а 04:00 в Ташкенте — это 23:00 UTC предыдущих суток, то есть **вчерашняя тема, молча, каждый
  день**. Триггер в UTC-cron ставится на `0 23 * * *`.
- Даты **до 2026-01-01** дают отрицательный остаток в некоторых языках. Формула применяется только
  вперёд от эпохи; при отрицательном значении — падать с ошибкой, а не подставлять что попало.
- Тема **не пропускается и не подменяется**, даже если она кажется похожей на вчерашнюю.
  Чередование уже заложено в порядок блоков (см. §3).
- Цикл замкнут: после 120 идёт 001. Полный оборот — 120 дней ≈ 4 месяца.

### Контрольный пример — 2026-08-16

```
2026-01-01 → 2026-08-16
дни: 31 (янв) + 28 (фев) + 31 (мар) + 30 (апр) + 31 (май) + 30 (июн) + 31 (июл) = 212
     212 + 16 = 228  → это день года
     228 − 1 = 227   → суток прошло с 2026-01-01 (2026 — не високосный)

index    = 227 mod 120 = 107
topic_no = 107 + 1 = 108
```

**2026-08-16 → тема 108 — «АГЕНТЫ · Планировщик и исполнитель».**
Если ваш расчёт дал не 108 — расчёт неверен, останавливайтесь и не тратьте кредиты.
`RUNBOOK.md` §4 делает эту проверку обязательной перед любым платным вызовом.

### Таблица самопроверки

| Дата | Суток с 2026-01-01 | index | Тема |
|---|---|---|---|
| 2026-01-01 | 0 | 0 | 001 |
| 2026-04-30 | 119 | 119 | 120 |
| 2026-05-01 | 120 | 0 | 001 — начало второго круга |
| 2026-08-15 | 226 | 106 | 107 |
| **2026-08-16** | **227** | **107** | **108** |
| 2026-12-31 | 364 | 4 | 005 |
| 2027-01-01 | 365 | 5 | 006 |

---

## 2. Структура блока темы

Каждая тема — блок из семи полей. Четыре из них уже написаны по-английски и попадают в промпт
дословно; три русских не попадают в промпт никогда.

| Поле | В промпт | Куда идёт |
|---|---|---|
| `object_en` | **да** | слот `{{OBJECT}}` — предмет дня |
| `payoff_en` | **да** | слот `{{PAYOFF}}` — тело превращения, бит `05.2-07.0` |
| `rest_en` | **да** | слот `{{PAYOFF_REST}}` — что лежит на столе к 08.0 |
| `foley_en` | **да** | слот `{{FOLEY}}` — звук превращения |
| `negative_today` | **да** | слот `{{NEGATIVE_TODAY}}`; у большинства тем пусто (`—`) |
| `verb_ru` | нет | реестр глаголов, правило 21 дня |
| `hook_ru` / `payoff_ru` | нет | подпись к посту (`RUNBOOK.md` §10) |

**Рантайм ничего не переводит и ничего не разбирает.** Английские поля написаны заранее и вручную
именно потому, что перевод в 04:00 — это недетерминированный шаг внутри системы, вся ценность
которой в детерминизме. Пустое `negative_today` записано как `—` и подставляется как пустая строка.

Все 120 блоков прошли аудит 2026-08-15 по механическому списку из `prompts/TEMPLATE.md` §1:

- ровно один висящий предмет (сомкнутая пара или связка считается одним, если висит и вращается как одно целое);
- в кадр снаружи не входит ничего: ни второй предмет, ни инструмент, ни рука сверху или сбоку;
- нет огня, пламени, уголька и светящихся предметов — это второй источник света;
- нет ни одного читаемого символа: ни надписей, ни цифр, ни клейм, ни гербов;
- столешница не протыкается, не режется, не прожигается и не повреждается;
- к 08.9 всё, чем стал предмет, лежит на дубе: ничего не висит, ничего не улетело, ничего не исчезло;
- изменение читается силуэтом на превью шириной 240 px;
- глагол `verb_ru` и опорное существительное `object_en` не повторяются в окне 21 строки, включая стык 120 → 001.

---

## 3. Чередование полос

Десять полос: **ПРОМПТ · АВТОМАТИЗАЦИЯ · ИНСТРУМЕНТЫ · ПРОЦЕСС · ГЕНЕРАЦИЯ · КАРЬЕРА · МИФЫ ·
АГЕНТЫ · БИЗНЕС · ЭТИКА** (по 12 тем в каждой). Обозначим этот порядок как список `L`, индексы 0..9.

Формула, которая **действительно** описывает таблицу (проверена по всем 120 строкам):

```python
L = ["ПРОМПТ","АВТОМАТИЗАЦИЯ","ИНСТРУМЕНТЫ","ПРОЦЕСС","ГЕНЕРАЦИЯ",
     "КАРЬЕРА","МИФЫ","АГЕНТЫ","БИЗНЕС","ЭТИКА"]

def lane(n):                      # n = 1..120
    block, pos = divmod(n - 1, 10)
    return L[(pos + 7 * block) % 10]
```

Свойства, проверенные на данных, а не заявленные:

1. Каждая полоса встречается ровно 12 раз (`gcd(7,10)=1`).
2. Две подряд идущие темы никогда не из одной полосы — верно и на стыке блоков, и на стыке круга
   (120 — МИФЫ, 001 — ПРОМПТ).
3. Сдвиг на 60 строк всегда даёт другую полосу (смещение `6·7 mod 10 = 2`). Это и делает
   подстановку из §5 безопасной.

*Прежняя версия файла приводила формулу `((block + 3·position) mod 10) + 1`. Она не описывала
таблицу: применительно к первому блоку она даёт порядок 1,4,7,10,3,6,9,2,5,8, а в данных 1..10.
Формула выше — та, что реализована.*

---

## 4. Банк тем

### 001 · ПРОМПТ · Контекст важнее вежливости

- `verb_ru:` наполняется
- `object_en:` an empty thick-walled glass flask, cold and colourless, one long specular highlight running down its curved side
- `payoff_en:` dark grain pours down into the flask out of nowhere and the level climbs steadily until the glass is packed full to the neck and every trace of its clarity is gone
- `rest_en:` a glass flask packed solid with dark grain, opaque and heavy on the oak
- `foley_en:` a dry rushing hiss of grain against glass, thickening as the level rises, ending in one low settle
- `negative_today:` —
- `hook_ru:` Вы дописываете «пожалуйста», а модели не хватает трёх фактов.
- `payoff_ru:` Вместо вежливых оборотов дайте три строки контекста: кто вы, для кого текст, что уже пробовали. Это меняет ответ сильнее любой формулировки.

### 002 · АВТОМАТИЗАЦИЯ · Правило трёх

- `verb_ru:` троится
- `object_en:` a worn beechwood spoon, pale and dry, its bowl scooped thin and the grain raised along the handle
- `payoff_en:` the spoon peels a second and then a third copy of itself out of its own body, the three hang together for a moment and then run into one another and fuse into a single heavy steel paddle
- `rest_en:` one heavy steel paddle lies on the oak where three wooden spoons were
- `foley_en:` two dry wooden clacks close together, then a low metallic swallow as three become one
- `negative_today:` changing spoon count, four spoons, spoons leaving the shaft;
- `hook_ru:` Первый раз руками. Второй руками. Третий — уже нет.
- `payoff_ru:` Как только задача повторилась третий раз, потратьте час и опишите её шагами: это ваш первый кандидат на автоматизацию. Раньше третьего раза не трогайте.

### 003 · ИНСТРУМЕНТЫ · Чат, ассистент и агент — три разных инструмента

- `verb_ru:` разъезжается
- `object_en:` a heavy adjustable steel wrench, oiled dark, its jaw threaded and its handle worn bright at the grip
- `payoff_en:` the wrench draws apart along its own length into three separate wrenches, each one shortening or lengthening to a different size as it separates until no two are alike
- `rest_en:` three steel wrenches of three sizes lie side by side on the oak
- `foley_en:` one long metallic slide, then two dry threaded clicks as the sizes settle
- `negative_today:` changing wrench count, four wrenches, wrenches leaving the shaft;
- `hook_ru:` Вы носите один молоток на все три гвоздя.
- `payoff_ru:` Чат — подумать. Ассистент внутри программы — доделать в контексте файла. Агент — выполнить цепочку без вас. Выбирайте по тому, кто держит контекст.

### 004 · ПРОЦЕСС · Черновик машиной, смысл человеком

- `verb_ru:` вытягивается
- `object_en:` a fist-sized lump of wet grey potter's clay, matte and unfired, thumb drag-marks still standing on its surface
- `payoff_en:` the clay rises and opens into the body of a jug, the walls thinning and smoothing all the way up, but the neck stays lopsided and unfinished and never trues itself
- `rest_en:` a grey clay jug with a smooth body and a crooked unfinished neck stands on the oak
- `foley_en:` a wet slap and a long slurring rise of clay under pressure, ending in one soft uneven scrape
- `negative_today:` —
- `hook_ru:` Модель делает первые семьдесят процентов. Ценность в последних тридцати.
- `payoff_ru:` Никогда не отправляйте первый ответ. Перепишите начало, выкиньте половину, добавьте один свой факт, которого у модели быть не может.

### 005 · ГЕНЕРАЦИЯ · Референс сильнее описания лица

- `verb_ru:` округляется
- `object_en:` a sharply faceted block of white marble the size of a fist, every edge crisp, fine tool marks catching the light across each facet
- `payoff_en:` every facet and every edge rounds off from the outside inward, the crisp geometry going soft by degrees, until nothing is left of the cut stone but a smooth featureless pebble
- `rest_en:` a smooth featureless white pebble lies on the oak with all its edges gone
- `foley_en:` a slow dry stone grind with the edges rubbing away, settling into one soft knock
- `negative_today:` —
- `hook_ru:` Вы описываете лицо словами и спорите с собственной фотографией.
- `payoff_ru:` Есть фото — не описывайте внешность текстом вообще. Слова о лице усредняют его с миллионом чужих. Текст оставьте для одежды, действия и света.

### 006 · КАРЬЕРА · Заменит не модель, а коллега с моделью

- `verb_ru:` укорачивается
- `object_en:` a pair of identical plain white wax pillars standing side by side as one block, unlit, their sides softly ridged from the mould
- `payoff_en:` the right-hand pillar shortens smoothly and steadily down to half its height while the left-hand one does not change at all, and the wax it sheds simply thins away into nothing
- `rest_en:` two wax pillars lie on the oak, one at full height and one at exactly half of it
- `foley_en:` a soft continuous waxy compression, close and dull, ending in two light knocks on wood
- `negative_today:` flame, a lit wick, burning, smoke, melted wax pooling;
- `hook_ru:` Заменяет не машина. Заменяет тот, кто рядом и вдвое быстрее.
- `payoff_ru:` Возьмите одну свою еженедельную задачу и месяц делайте её только с ассистентом, пока не станете вдвое быстрее. Один доведённый процесс важнее десяти попробованных.

### 007 · МИФЫ · «Модель думает»

- `verb_ru:` опрокидывается
- `object_en:` one black domino tile, glossy and completely blank on both faces, its edges chamfered and one long highlight down its face
- `payoff_en:` the tile peels itself into a standing row of a dozen identical tiles that comes down onto the wood, and the fall runs from one end of the row to the other in a single unbroken wave
- `rest_en:` a dozen black domino tiles lie flat on the oak in one straight overlapping line
- `foley_en:` one sharp tick, then a fast dry clatter running away from the lens and stopping dead
- `negative_today:` spots or pips on the tiles, numbers, changing tile count;
- `hook_ru:` Она не думает. Она очень точно угадывает следующее слово.
- `payoff_ru:` Модель не знает ответ, она достраивает вероятное продолжение. Дайте материал и контекст — и вероятное совпадёт с верным.

### 008 · АГЕНТЫ · Агент — это модель с руками

- `verb_ru:` прорастает
- `object_en:` a polished steel ball the size of a plum, mirror-bright, one hard white highlight sliding across it as it turns
- `payoff_en:` short blunt spikes push out through the mirror surface all over the ball, the reflection breaking up into fragments as they lengthen, until the whole thing is a dull spiked burr
- `rest_en:` a dull steel burr covered in short blunt spikes rests on the oak
- `foley_en:` a series of tight metallic pops working outward, then a low grinding settle
- `negative_today:` changing spike count, sharp needles, the ball rolling, a reflection of the room;
- `hook_ru:` Пока у модели нет инструментов, она только советует.
- `payoff_ru:` Разница между чатом и агентом — доступ к действиям: файлы, почта, календарь, база. Начните с одного инструмента и одной задачи, а не с универсального помощника.

### 009 · БИЗНЕС · Начните с самой скучной задачи

- `verb_ru:` сортируется
- `object_en:` a loose handful of identical grey river pebbles, dry and dusty, held together in one hovering cluster
- `payoff_en:` the cluster orders itself in the air, the pebbles sliding past one another into four even columns graded by size, largest at the left and smallest at the right, and the columns square up
- `rest_en:` four even columns of grey pebbles stand on the oak, sorted from largest to smallest
- `foley_en:` a dry gravel shuffle resolving into a run of small even knocks, four groups, then silence
- `negative_today:` changing pebble count, pebbles rolling off the table;
- `hook_ru:` Внедрение проваливается там, где начали с красивого.
- `payoff_ru:` Первый кандидат — то, что все ненавидят и делают ежедневно: перенос данных, отчёт, сортировка заявок. Скучная задача даёт измеримую экономию и её не надо продавать.

### 010 · ЭТИКА · Персональные данные в промпте — уже утечка

- `verb_ru:` стекленеет
- `object_en:` a thick cream paper envelope, sealed and completely unmarked, its flap ridged and one corner slightly bent
- `payoff_en:` the paper loses its opacity from the corners inward and turns to clear glass, and through it the folded sheets inside show up entirely blank
- `rest_en:` a clear glass envelope lies on the oak with blank folded sheets visible inside it
- `foley_en:` a dry paper crackle stiffening into a thin glassy chime, then one flat settle
- `negative_today:` writing on the sheets, an address, a stamp, text showing through;
- `hook_ru:` Вставили паспорт клиента в чат — данные вышли из компании.
- `payoff_ru:` Перед вставкой заменяйте имена, телефоны и номера на метки: «Клиент А», «телефон». Модели важна структура, а не личность.

### 011 · АГЕНТЫ · Агенту нужна цель, а не задача

- `verb_ru:` осыпается
- `object_en:` a heavy brass compass with an open lid and a completely blank dial, the glass scratched, the needle swinging loose
- `payoff_en:` the swinging stops, and the glass and the blank dial around the needle crumble away into fine brass dust that drifts out of the shaft, leaving the bare needle alone in the air
- `rest_en:` one slim brass needle lies alone on the oak, pointing in a single direction
- `foley_en:` a fine whirring sweep cut short, a dry granular crumble, then one thin metallic tick
- `negative_today:` letters or numerals on the dial, compass points, changing needle count;
- `hook_ru:` «Сделай отчёт» — задача. «Чтобы к утру у команды была картина продаж» — цель.
- `payoff_ru:` Формулируйте результат и признак готовности, а не список шагов. Шаги агент выберет сам, а без критерия готовности он не остановится.

### 012 · БИЗНЕС · Считайте экономию в часах

- `verb_ru:` перевешивает
- `object_en:` a small brass balance with two shallow pans, a heap of fine grey sand in the left pan and one blank lead disc in the right
- `payoff_en:` the beam tips the wrong way, the pan holding the single lead disc sinking steadily until it reaches its stop while the heaped pan of sand rides all the way up
- `rest_en:` the brass balance lies on the oak with the lead disc pan down and the sand pan high
- `foley_en:` a fine sand hiss, one long brass creak of the beam, ending in a single flat metallic stop
- `negative_today:` markings or numerals on the disc, a face on the coin, sand spilling from the pan;
- `hook_ru:` «Стало удобнее» — это не результат.
- `payoff_ru:` До внедрения замерьте: сколько минут занимает операция и сколько раз в неделю. После — тот же замер. Разница в часах умножается на стоимость часа.

### 013 · ЭТИКА · Чужое лицо и голос — только с согласия

- `verb_ru:` обесцвечивается
- `object_en:` a black magnetic tape reel on a grey plastic hub, the tape wound tight and glossy, one loose end standing out
- `payoff_en:` the reel unwinds itself in a long spiral and every centimetre of tape loses its colour as it passes, running out clear and empty, and then the clear spiral draws back onto the hub
- `rest_en:` a reel of completely clear blank tape lies on the oak
- `foley_en:` a fast plastic whirr of unspooling, a thin dry ribbon rustle, then one hollow plastic knock
- `negative_today:` —
- `hook_ru:` Сгенерировать лицо коллеги технически легко. Юридически — нет.
- `payoff_ru:` Лицо и голос человека — его данные. Нужно письменное согласие на конкретное использование, срок и площадку. Для клипов берите своё лицо.

### 014 · ПРОМПТ · Роль работает, когда она сужает

- `verb_ru:` заостряется
- `object_en:` a wide flat painter's brush with splayed frayed bristles, the ferrule dented and the wooden handle rubbed pale
- `payoff_en:` the bristles draw together from the outside inward and twist down to a single long point, the whole head narrowing until it ends in one hair-fine tip
- `rest_en:` a brush with one perfect fine point lies on the oak
- `foley_en:` a dry bristle rasp gathering to a fine whisper, ending in one light wooden tap
- `negative_today:` —
- `hook_ru:` «Ты эксперт» не работает. «Объясни бухгалтеру, который не знает слова API» — работает.
- `payoff_ru:` Роль полезна ровно настолько, насколько сужает словарь и уровень детализации. Всегда указывайте, для кого ответ и что читатель уже знает.

### 015 · АВТОМАТИЗАЦИЯ · Сначала опишите процесс

- `verb_ru:` расплетается
- `object_en:` a tight tangled hank of coarse grey wool, loose ends standing out in every direction, the fibres catching the light
- `payoff_en:` the tangle pulls itself apart strand by strand and every strand joins end to end into one continuous thread, which winds itself into a flat even coil in the air
- `rest_en:` one flat even coil of grey thread lies on the oak
- `foley_en:` a soft fibrous unpicking with many small snags in sequence, ending in one muffled settle
- `negative_today:` —
- `hook_ru:` Нельзя автоматизировать то, что вы не можете объяснить словами.
- `payoff_ru:` Напишите процесс как рецепт: вход, шаги, кто решает, что на выходе. Половина проблем решается на этом листе — до всякой автоматизации.

### 016 · ИНСТРУМЕНТЫ · Модель для текста и модель для кода — не одно

- `verb_ru:` нарезается
- `object_en:` a plain iron nail as long as a finger, blunt-headed and slightly rough, dark with old oil
- `payoff_en:` a helical thread cuts itself into the shank from the tip upward and the head flattens and opens into a cross slot, until the nail has become a precise machine screw
- `rest_en:` a threaded iron machine screw lies on the oak where the nail was
- `foley_en:` a fine metallic cutting rasp climbing the shank, one sharp click at the head, then a light metal knock
- `negative_today:` the screw entering the table, a drill, a screwdriver, changing thread count;
- `hook_ru:` Вы просите молоток закрутить винт и обижаетесь на молоток.
- `payoff_ru:` Проверьте, какая модель стоит по умолчанию, и подбирайте под задачу: рассуждение, скорость, код, длинный контекст. Смена модели даёт больше, чем правка промпта.

### 017 · ПРОЦЕСС · Соберите контекст один раз

- `verb_ru:` спрессовывается
- `object_en:` a loose drift of pale curled wood shavings held together in one hovering cloud, dry and translucent at the edges
- `payoff_en:` the cloud draws in on itself from every side and the shavings press together into one dense rectangular block of laminated wood with clean square corners
- `rest_en:` one dense block of laminated wood with square corners rests on the oak
- `foley_en:` a dry papery rustle collapsing inward, then a deep compacted creak and one solid thud
- `negative_today:` —
- `hook_ru:` Вы объясняете модели свой проект заново каждое утро.
- `payoff_ru:` Заведите один файл-паспорт проекта: что делаем, для кого, чем ограничены, как говорим. Прикладывайте к каждому разговору — качество первого ответа вырастает сразу.

### 018 · ГЕНЕРАЦИЯ · Один референс во всех кадрах

- `verb_ru:` делится
- `object_en:` a thick disc of dark red sealing wax, blank and unstamped, its edge crimped and its face slightly domed
- `payoff_en:` the disc lifts three layers off itself one after another and each layer thickens into a full disc, the three ending up identical in every crimp and every dome down to the smallest ridge
- `rest_en:` three identical blank discs of dark red sealing wax lie in a row on the oak
- `foley_en:` three soft waxy separations in even time, then three matching dull taps on wood
- `negative_today:` a stamp, an emblem, letters or a monogram in the wax, changing disc count;
- `hook_ru:` Герой «немного другой» в каждом кадре — и серия рассыпается.
- `payoff_ru:` Один и тот же файл-референс во всех генерациях, одежда описана дословно одинаковыми словами. Меняете референс — меняете человека.

### 019 · КАРЬЕРА · Портфолио процессов, а не результатов

- `verb_ru:` разбирается
- `object_en:` a finished wooden box with a fitted lid, its corners dovetailed tight and its surface waxed to a low sheen
- `payoff_en:` the box comes apart along every joint at once and the pieces spread out flat in the air, each panel and each dovetail pin separating and turning to show its cut face
- `rest_en:` the panels and pins of the box lie flat on the oak in a neat spread-out row
- `foley_en:` a run of dry wooden releases in quick succession, then a soft scatter of flat pieces landing
- `negative_today:` —
- `hook_ru:` Красивый результат больше ничего не доказывает.
- `payoff_ru:` Показывайте, как пришли к результату: исходный запрос, три итерации, что забраковали и почему. Работодателю нужен ваш способ думать — его модель не сгенерирует.

### 020 · МИФЫ · «Модель знает, какой сегодня день»

- `verb_ru:` повисает
- `object_en:` a small hourglass in a dark wooden frame, fine pale sand running steadily through the waist, the glass clouded at the top
- `payoff_en:` the falling column of sand slows and then stops dead in mid-air between the two bulbs, the loose grains hanging exactly where they were, and nothing moves in it again
- `rest_en:` the hourglass lies on the oak with a column of sand frozen halfway down
- `foley_en:` a steady fine sand whisper thinning out to nothing, then one hollow wooden knock
- `negative_today:` —
- `hook_ru:` Она не знает ни сегодняшней даты, ни вчерашних новостей.
- `payoff_ru:` У модели есть дата обучения; всё, что позже, она додумает. Нужна свежесть — дайте ссылку, файл или включите поиск. И пишите дату прямо в промпте.

### 021 · ГЕНЕРАЦИЯ · Свет решает больше, чем разрешение

- `verb_ru:` проявляется
- `object_en:` a flat matte plaster circle the size of a saucer, chalky and unpainted, reading as a grey shape with no depth in it at all
- `payoff_en:` the circle swells outward from its centre into a full sphere, and as it thickens the beam finds it properly, a bright core coming up on one side and a hard terminator drawing across the middle
- `rest_en:` a plaster sphere rests on the oak with one hard-edged shadow cutting across it
- `foley_en:` a low airless swell with no source, rising as the shape fills out, ending in one chalky knock
- `negative_today:` —
- `hook_ru:` Кадр выглядит нейросетевым не из-за качества, а из-за света.
- `payoff_ru:` Всегда описывайте источник: откуда падает, какой жёсткости, какого цвета, что в тени. Один мотивированный источник даёт правдоподобие, которого не даст 4K.

### 022 · КАРЬЕРА · Формулировать задачу дороже, чем жать кнопки

- `verb_ru:` выпрямляется
- `object_en:` a crooked hazel branch as long as a forearm, bark still on it, knots and side-shoots standing out along its length
- `payoff_en:` the bark peels back and drops away, every knot planes itself flush and the whole branch pulls straight along its axis and squares off into a four-sided rule with nothing marked on it
- `rest_en:` a plain square unmarked wooden rule lies straight on the oak
- `foley_en:` a dry bark tear, a run of small woody snaps, then one clean flat lay-down
- `negative_today:` graduations, numbers, tick marks or scale lines on the rule;
- `hook_ru:` Интерфейсы поменяются за год. Умение ставить задачу — нет.
- `payoff_ru:` Тренируйте постановку: результат, ограничения, критерий приёмки, кому отдаём. Этот навык одинаково работает с моделью, подрядчиком и стажёром.

### 023 · МИФЫ · «Она учится на моих разговорах прямо сейчас»

- `verb_ru:` затягивается
- `object_en:` a thick slab of dark grey slate, flat and cool, its broken edge showing fine parallel layers
- `payoff_en:` a deep groove cuts itself across the face of the slab and then closes up again from both sides until the surface is whole, while everything the groove removed gathers into one small cone of grey dust beside it
- `rest_en:` an unmarked slate slab lies on the oak with a small cone of grey dust beside it
- `foley_en:` a hard stone incision, a long grinding closure, then a light powdery patter
- `negative_today:` writing or symbols in the groove, letters, a chisel;
- `hook_ru:` Ваш вчерашний чат не сделал модель умнее.
- `payoff_ru:` Веса модели от вашего разговора не меняются. Но данные могут храниться и пойти в обучение будущих версий — это настройка в аккаунте. Для рабочих данных включайте корпоративный режим.

### 024 · АГЕНТЫ · Дайте агенту право остановиться

- `verb_ru:` сматывается
- `object_en:` a heavy brass plumb bob on a waxed cord, swinging in slow wide arcs, its point machined to a fine tip
- `payoff_en:` at the widest arc the cord starts winding itself up from the top, each turn taking length out of the swing, until the arc has shrunk to nothing and the bob hangs perfectly plumb and dead still
- `rest_en:` a brass plumb bob lies on the oak with its cord coiled tight above it
- `foley_en:` a slow rhythmic air-swish narrowing in tempo, a fine cord ratchet, then one dense metallic set-down
- `negative_today:` —
- `hook_ru:` Самый безопасный агент — тот, который умеет сказать «не знаю».
- `payoff_ru:` Впишите в инструкцию: при нехватке данных или на необратимом шаге остановись и спроси. Иначе агент додумает недостающее и уверенно сделает не то.

### 025 · БИЗНЕС · AI не чинит процесс, он его обнажает

- `verb_ru:` обнажается
- `object_en:` a round grey stone plate under an even film of pale dust, its surface reading as smooth and unbroken
- `payoff_en:` the film of dust lifts away all at once in one flat sheet and drifts out of the beam, and the surface it uncovers is split from edge to edge with deep old cracks
- `rest_en:` a deeply cracked grey stone plate lies on the oak with its dust gone
- `foley_en:` one soft dry exhalation of lifting dust, then a low stone knock with a hollow ring in it
- `negative_today:` —
- `hook_ru:` Внедрили ассистента — и стало видно, что регламента никогда не было.
- `payoff_ru:` Если задача не описана, модель покажет это в первый же день. Это не провал внедрения, а бесплатный аудит: сначала правило, потом автоматизация.

### 026 · ЭТИКА · Помечайте сгенерированное

- `verb_ru:` расслаивается
- `object_en:` a ripe red apple with a short dry stalk, its skin waxy and taut, one bright highlight on the shoulder
- `payoff_en:` a dead straight line runs from stalk to base and everything on one side of it turns to matte grey unfired clay, the change stopping exactly on the line and going no further
- `rest_en:` an apple lies on the oak, one half red and waxy and the other half matte grey clay
- `foley_en:` a fine ceramic tightening travelling along one side, then a dull weighted landing with no roll in it
- `negative_today:` a symbol, a mark, a brand, a burn mark or lettering on the skin;
- `hook_ru:` Не пометил — значит выдал за снятое.
- `payoff_ru:` Одна строка в описании: «видео сгенерировано». Это снимает половину претензий, повышает доверие и уже требуется на части площадок.

### 027 · ПРОМПТ · Пример вместо описания

- `verb_ru:` отливается
- `object_en:` a rough wedge of grey clay, freshly cut, one flat wire-cut face still glossy with moisture
- `payoff_en:` the wedge collapses inward as though pressed into a form that is not there and comes back out carrying a precise deep fluting all the way round it, every flute identical to the next
- `rest_en:` a precisely fluted grey clay cylinder stands on the oak
- `foley_en:` a wet compressive squelch, one firm pneumatic thump, then a soft release and a dull set-down
- `negative_today:` a mould, a press or a tool in frame, changing flute count;
- `hook_ru:` Три абзаца требований проигрывают одному примеру.
- `payoff_ru:` Дайте образец нужного ответа — даже чужой, даже кривой — и скажите «сделай так же по структуре». Один-два примера меняют результат сильнее страницы инструкций.

### 028 · АВТОМАТИЗАЦИЯ · Триггер плюс действие

- `verb_ru:` захлопывается
- `object_en:` a wooden mousetrap set and cocked, its steel bar drawn back hard against the spring, the base plain and unmarked
- `payoff_en:` nothing touches it and the bar releases anyway, whipping over in a single blur and slamming shut against the base, and the spring rings itself out and goes quiet
- `rest_en:` a sprung mousetrap lies flat on the oak with its bar shut
- `foley_en:` a hard steel snap with a bright ring after it, then one flat wooden slap
- `negative_today:` a mouse, an animal, bait, cheese, the table shaking, writing on the base;
- `hook_ru:` Любая автоматизация — это «когда случилось X, сделай Y». Остальное украшения.
- `payoff_ru:` Опишите свою рутину этой фразой. Не получается назвать точный триггер — автоматизировать нечего: у вас пока привычка, а не процесс.

### 029 · ИНСТРУМЕНТЫ · Голосовой ввод быстрее печати

- `verb_ru:` опрокидывается
- `object_en:` a small clay jug with a pinched lip and a rough unglazed body, dry inside and out
- `payoff_en:` the jug tips over in the air and pours out a heavy unbroken rope of water that runs far longer than the jug could ever have held, until three times its volume is on the wood
- `rest_en:` an empty clay jug lies on its side on the oak in a wide flat pool of water
- `foley_en:` a hollow ceramic tip, a long thick pour with no end to it, then a broad wet slap and a slow drain
- `negative_today:` the water reaching the lens, the pool leaving the table, water on him;
- `hook_ru:` Вы печатаете промпт двумя пальцами, а можно наговорить втрое больше.
- `payoff_ru:` Наговорите задачу голосом со всеми оговорками и «э-э-э» — модель разберёт. Длинный устный контекст почти всегда точнее короткого напечатанного.

### 030 · ПРОЦЕСС · Чек-лист приёмки

- `verb_ru:` отсеивается
- `object_en:` a loose handful of walnuts in their shells, held in one hovering cluster, the shells dry and deeply ridged
- `payoff_en:` one after another the walnuts collapse into dust that drifts out of the beam, the collapses coming faster and faster, until exactly five whole shells are left hanging
- `rest_en:` five whole walnuts lie on the oak in one close group
- `foley_en:` a run of dry hollow crushes speeding up and then stopping abruptly, then five light knocks
- `negative_today:` changing walnut count, more than five remaining, shells rolling off the table;
- `hook_ru:` Как вы понимаете, что ответ хороший? Если не сформулировано — никак.
- `payoff_ru:` Три-пять пунктов, одинаковых для всех задач: факты проверены, источники существуют, длина по формату, тон нужный, воды нет. Прогоняйте каждый ответ через один и тот же список.

### 031 · АВТОМАТИЗАЦИЯ · Сначала уведомление, потом действие

- `verb_ru:` раскрывается
- `object_en:` a small brass semaphore arm folded flat against its short post, the metal dull and slightly pitted
- `payoff_en:` the arm swings up off the post and locks out dead level with a hard stop, and the post lengthens under it to carry the arm high
- `rest_en:` a brass semaphore stands upright on the oak with its arm locked out level
- `foley_en:` a spring-loaded metallic swing, one hard mechanical lock, then a brass base settling
- `negative_today:` —
- `hook_ru:` Первую неделю автоматизация должна только рассказывать, а не делать.
- `payoff_ru:` Запустите сценарий в режиме «предложи и напиши мне». Неделю сверяйте с тем, что сделали бы сами. Совпало десять раз подряд — включайте выполнение.

### 032 · ИНСТРУМЕНТЫ · Загрузите файл вместо копипаста

- `verb_ru:` сшивается
- `object_en:` a loose stack of forty blank sheets of heavy paper, the edges uneven and the corners lifting
- `payoff_en:` the edges knock themselves square, a row of stitches draws through the spine on its own and the whole stack pulls tight into one bound block with a hard cover closing over it
- `rest_en:` one tightly bound blank book lies closed on the oak
- `foley_en:` a fast paper riffle, edges tapping square, a taut thread being drawn, then one solid closing thud
- `negative_today:` text or print on the pages, a title on the cover, lettering on the spine;
- `hook_ru:` Вы вставляете документ кусками и удивляетесь, что модель теряет нить.
- `payoff_ru:` Отдайте файл целиком и спрашивайте по нему. Модель видит структуру и таблицы. И просите цитату с указанием места — так проверяется, что она читала, а не вспоминала.

### 033 · ПРОЦЕСС · Не правьте бесконечно, начните заново

- `verb_ru:` разглаживается
- `object_en:` a tightly crumpled ball of thin silver foil, every facet of it catching a different piece of the beam
- `payoff_en:` the ball opens out from the inside, every crease travelling to the edge and disappearing as it goes, until the foil is one perfectly flat unmarked sheet
- `rest_en:` one flat unmarked sheet of silver foil lies on the oak
- `foley_en:` a bright metallic crackle unfolding, thinning to a fine tick, then one weightless flutter down
- `negative_today:` a reflection of the room, a reflection of a person, a camera reflected;
- `hook_ru:` После пятой правки в одном чате ответ становится только хуже.
- `payoff_ru:` Три итерации без сдвига — открывайте новый разговор и пишите промпт с нуля, с учётом того, что поняли. Чат тащит за собой все прошлые неудачные варианты.

### 034 · ГЕНЕРАЦИЯ · Камера должна стоять

- `verb_ru:` утяжеляется
- `object_en:` a slim iron rod standing on one end and rocking slightly, its surface dark and hammer-marked
- `payoff_en:` the rod pours downward into itself, the lower half swelling out into a broad heavy four-sided base while the top stays exactly where it is, and the rocking dies out completely
- `rest_en:` an iron rod on a broad heavy base stands dead still on the oak
- `foley_en:` a low metallic slump thickening downward, the rocking tick slowing to nothing, then dense silence
- `negative_today:` —
- `hook_ru:` Половина артефактов появляется ровно тогда, когда вы просите камеру двигаться.
- `payoff_ru:` Запрещайте движение перечислением: без панорам, наездов, зума, дрожания, облёта. Масштаб и вес читаются в неподвижной рамке — наезд их убивает.

### 035 · КАРЬЕРА · Специализация плюс AI

- `verb_ru:` прорезается
- `object_en:` a plain iron key blank with no cuts in it at all, the bow round and the shaft square-shouldered
- `payoff_en:` notches cut themselves into the blank one after another along the shaft, each one deeper and more precise than the last, until the key carries a complete intricate bit
- `rest_en:` a finished iron key with a full cut bit lies on the oak
- `foley_en:` a sequence of hard precise metallic bites, evenly spaced, ending in one clean iron knock
- `negative_today:` a lock, a keyhole, a door, numbers stamped on the bow, changing notch count;
- `hook_ru:` Универсальный «AI-специалист» никому не нужен. Нужен агроном с моделью.
- `payoff_ru:` Не бросайте профессию ради нейросетей. Возьмите свою предметную область и станьте тем, кто закрывает её задачи вдвое быстрее. Дефицит именно на стыке.

### 036 · МИФЫ · «Чем длиннее промпт, тем лучше»

- `verb_ru:` сжимается
- `object_en:` a big loose wad of raw cotton, its fibres standing out in a halo, almost weightless in the beam
- `payoff_en:` the wad draws in on itself from all sides at once, the halo of fibres disappearing inward, and it keeps going long past the point where it should stop until it is a single hard pellet
- `rest_en:` one small hard white pellet lies on the oak
- `foley_en:` a soft fibrous rush inward compacting to a dry squeak, then one tiny sharp tick
- `negative_today:` —
- `hook_ru:` Страница инструкций часто работает хуже пяти точных строк.
- `payoff_ru:` Лишние слова размывают главное. Оставляйте то, что меняет ответ: задача, контекст, формат, ограничения. Что можно выкинуть без потери смысла — выкидывайте.

### 037 · АГЕНТЫ · Песочница важнее возможностей

- `verb_ru:` растекается
- `object_en:` a rounded lump of damp dark sand, its surface pitted, holding its shape in the air
- `payoff_en:` the lump loses its cohesion and the sand runs outward across the wood into a perfectly circular flat disc, and at one exact radius it stops dead as though it had hit a wall
- `rest_en:` a flat perfect circle of dark sand lies on the oak with a hard clean edge
- `foley_en:` a granular collapse spreading outward and hissing wide, then cutting off sharply into silence
- `negative_today:` sand leaving the table, sand reaching the lens, an uneven edge, a container;
- `hook_ru:` Вопрос не «что агент умеет», а «что он может сломать».
- `payoff_ru:` До запуска перечислите, к чему у агента есть доступ и что необратимо: удаление, отправка наружу, оплата. Необратимое — только через подтверждение человеком.

### 038 · БИЗНЕС · Пилот на одной команде

- `verb_ru:` прорастает
- `object_en:` a shallow mound of dry cracked earth with one pale seed sitting on its crest, the soil grey and powdery
- `payoff_en:` one green shoot pushes up out of the single seed and unrolls two leaves, while every other part of the mound stays exactly as dry and grey as it was
- `rest_en:` a dry earth mound rests on the oak with one green shoot standing out of it
- `foley_en:` a fine soil crackle from one point only, a thin fibrous stretch, then a dry crumbling settle
- `negative_today:` —
- `hook_ru:` Внедрение «для всей компании сразу» умирает за месяц.
- `payoff_ru:` Одна команда, один процесс, четыре недели, одна метрика. Успешный пилот сам становится аргументом, неуспешный стоит дёшево.

### 039 · ЭТИКА · Медицина, право, деньги — только с проверкой

- `verb_ru:` переполняется
- `object_en:` a straight-sided measuring glass half full of clear liquid with a glass pipette poised above it, both perfectly clean
- `payoff_en:` the pipette goes on releasing drops at exactly the same rate long after the glass is full, the liquid doming over the rim and then breaking and running down the outside in wide sheets
- `rest_en:` a measuring glass stands on the oak in a spreading pool with the pipette lying beside it
- `foley_en:` even drops in strict rhythm, a rising tone as the glass fills, then a continuous quiet overflow
- `negative_today:` graduation marks or numbers on the glass, coloured liquid, the pool reaching the lens;
- `hook_ru:` Модель уверенно назовёт дозировку. Отвечать будете вы.
- `payoff_ru:` В этих областях используйте ассистента для подготовки: собрать вопросы, объяснить термины, понять, что уточнить у специалиста. Решение — за человеком с лицензией.

### 040 · ПРОМПТ · Скажите, чего не надо

- `verb_ru:` рассыпается
- `object_en:` a shallow ceramic dish heaped with mixed fruit, the skins waxy and matte in the beam, one dark fig sitting at the centre
- `payoff_en:` every piece of fruit except the fig collapses into fine dust that lifts out of the beam, the dish emptying around it, until the fig is left sitting alone in the middle
- `rest_en:` one dark fig sits alone at the centre of an empty dish on the oak
- `foley_en:` a fast run of soft dry collapses, a wide powdery exhale, then one quiet ceramic touch
- `negative_today:` —
- `hook_ru:` Модель не догадается, что вы ненавидите слово «инновационный».
- `payoff_ru:` Держите личный стоп-лист: слова, обороты и структуры, которые всегда вычёркиваете. Вставляйте его в каждый промпт — экономит правку.

### 041 · БИЗНЕС · Поддержка: черновик, а не автоответ

- `verb_ru:` поднимается
- `object_en:` a flat round disc of red copper, hammer-planished all over, its edge slightly rough from the shears
- `payoff_en:` the rim of the disc lifts and curls upward all the way round and the wall rises evenly into a bowl, and then it stops halfway and goes no further, the shape left plainly unfinished
- `rest_en:` a half-raised copper bowl with a short unfinished wall sits on the oak
- `foley_en:` a rhythmic soft metallic drawing-up with the tone climbing, then a flat stop and one copper ring
- `negative_today:` —
- `hook_ru:` Автоответ бесит. Черновик за оператора экономит полдня.
- `payoff_ru:` Пусть модель готовит вариант ответа с подтянутой историей клиента, а человек правит и отправляет. Скорость растёт, ответственность остаётся у человека.

### 042 · ЭТИКА · Модель уверенно врёт

- `verb_ru:` вскрывается
- `object_en:` a ripe pomegranate with a dry crown, its skin leathery and blotched red, one bright highlight on the shoulder
- `payoff_en:` the skin splits along four lines and peels back like a flower, and inside there are no seeds at all, only a second pomegranate, perfectly smooth and glossy as poured wax
- `rest_en:` a split pomegranate husk lies on the oak with a flawless waxy pomegranate sitting in it
- `foley_en:` a wet leathery tear opening in four, then a smooth waxy squeak and a dull heavy set-down
- `negative_today:` —
- `hook_ru:` Уверенный тон — не признак правды, а признак стиля.
- `payoff_ru:` Любой факт, цифру, цитату и ссылку проверяйте отдельно. Правило: если это уйдёт в документ или к клиенту — сверьтесь с источником, а не с ощущением.

### 043 · ПРОМПТ · Один запрос — одна задача

- `verb_ru:` истончается
- `object_en:` a tight bundle of five pale dry reeds bound with twine, the reeds all the same length and thickness
- `payoff_en:` the twine unwinds and falls away, four of the reeds thin out and disappear into the air, and the one that is left thickens and lengthens until it has as much substance as all five had
- `rest_en:` one thick pale reed lies on the oak with a loose loop of twine beside it
- `foley_en:` a twine unwinding rasp, four thin papery fades, then one solid woody landing with no roll in it
- `negative_today:` flame, burning, changing reed count, reeds leaving the shaft;
- `hook_ru:` Пять задач в одном сообщении — пять посредственных ответов.
- `payoff_ru:` Разбивайте: сначала структура, потом текст, потом сокращение, потом заголовок. Каждый шаг проверяется, и итог лучше, чем от одного большого запроса.

### 044 · АВТОМАТИЗАЦИЯ · Без логов это чёрный ящик

- `verb_ru:` просветляется
- `object_en:` a black glass sphere the size of an egg, completely opaque, one hard white highlight sliding over it as it turns
- `payoff_en:` the blackness clears from the centre outward and the whole sphere goes transparent, showing a dense fine lattice of pale threads running through it that was invisible a second earlier
- `rest_en:` a clear glass sphere full of fine pale threads rests on the oak
- `foley_en:` a low glassy tone rising and thinning as it clears, then one hard bright knock on wood
- `negative_today:` the sphere rolling, a reflection of the room, circuitry, glowing lines;
- `hook_ru:` Если сценарий не пишет, что он сделал, о поломке вы узнаете от клиента.
- `payoff_ru:` Каждый запуск оставляет след: время, вход, что сделано, чем закончилось. Без этого нельзя ни починить, ни доказать, что работает.

### 045 · ИНСТРУМЕНТЫ · Локальная модель для закрытых данных

- `verb_ru:` замуровывается
- `object_en:` a small heap of dark grain held together in one hovering mound, the individual kernels dry and dull
- `payoff_en:` the outermost kernels darken and fuse into iron and the shell spreads inward and closes over the whole heap, leaving a seamless dull iron dome with nothing visible inside it
- `rest_en:` a seamless dull iron dome sits on the oak
- `foley_en:` a dry granular rustle hardening into a metallic crust, then one heavy dead iron thud
- `negative_today:` —
- `hook_ru:` Есть данные, которые не должны покидать ваш кабинет.
- `payoff_ru:` Для персональных, медицинских и коммерческих данных есть локальный запуск на своём железе: медленнее и слабее, зато наружу не уходит ничего. Разделите задачи на «можно в облако» и «только локально».

### 046 · ПРОЦЕСС · Этапы с проверкой между ними

- `verb_ru:` распиливается
- `object_en:` a length of rough pine log as long as a forearm, bark on, the end grain pale and freshly cut
- `payoff_en:` four cuts open across the log one after another with a clear pause between each, the kerf widening cleanly every time, until the log is four blocks of exactly equal length hanging in a row
- `rest_en:` four equal pine blocks lie in a row on the oak
- `foley_en:` four separate sawing passes with silence between them, each ending in a dry snap, then four knocks
- `negative_today:` a saw or blade in frame, sawdust reaching the lens, changing block count;
- `hook_ru:` Большая задача одним запросом — это ставка, а не работа.
- `payoff_ru:` Разложите на три-четыре этапа и после каждого проверяйте сами. Ошибка, пойманная на втором шаге, стоит минуту; она же в финале — весь день.

### 047 · ГЕНЕРАЦИЯ · Руки — слабое место

- `verb_ru:` отращивает
- `object_en:` a small five-spoked iron hub, the spokes set at exact even angles, the iron dark and slightly scaled
- `payoff_en:` a sixth spoke forces its way out between two of the others at a wrong angle, thicker and cruder than the rest, and the whole hub goes visibly out of true and stops looking made
- `rest_en:` a six-spoked iron hub lies on the oak with one spoke plainly wrong
- `foley_en:` a straining metallic groan, one ugly tearing pop, then an off-balance iron settle
- `negative_today:` fingers, a hand, a glove, changing spoke count beyond six;
- `hook_ru:` Модель до сих пор путается в пальцах. Не давайте ей шанса.
- `payoff_ru:` Не просите крупный план кистей и мелкую моторику. Ладонь с сомкнутыми пальцами, один простой жест, руки частично за кадром — и брака втрое меньше.

### 048 · КАРЬЕРА · Резюме: цифры, а не эпитеты

- `verb_ru:` оплывает
- `object_en:` an ornate gilded picture frame with nothing inside it, every scroll and leaf of its moulding picked out sharp
- `payoff_en:` all the gilded ornament runs down off the frame and pools away into nothing, and what is left behind draws together into one plain dense bar of grey metal with square ends
- `rest_en:` one plain grey metal bar lies on the oak where the frame was
- `foley_en:` a slow viscous metallic run with ornament dropping off in small ticks, then one heavy bar landing
- `negative_today:` a picture or canvas in the frame, a portrait, a reflection;
- `hook_ru:` Модель напишет красиво. Опыт придётся вложить вам.
- `payoff_ru:` Дайте факты: что делал, сколько, за какой срок, с каким результатом. Формулировки она соберёт. Без цифр выйдет текст, неотличимый от тысячи других.

### 049 · МИФЫ · «AI заберёт все работы завтра»

- `verb_ru:` убывает
- `object_en:` a flat bone comb with ten thick even tines, the bone yellowed and polished smooth by handling
- `payoff_en:` three of the ten tines soften and run away into nothing, and the gaps close up as the seven that remain thicken and spread out to fill the whole width of the comb
- `rest_en:` a bone comb with seven thick even tines lies on the oak
- `foley_en:` three soft waxy dissolves in sequence, a dry bone creak as the rest spread, then one light clack
- `negative_today:` changing tine count beyond seven, hair, a person's head;
- `hook_ru:` Исчезают не профессии, а отдельные задачи внутри них.
- `payoff_ru:` Выпишите свои задачи за неделю и отметьте: что модель делает лучше, что хуже, чего не может вовсе. Первую колонку отдайте, третья — то, за что вам и платят.

### 050 · АГЕНТЫ · Память: что помнить, что забыть

- `verb_ru:` выдувается
- `object_en:` a small linen sack packed tight and tied at the neck, the weave coarse and the corners bulging
- `payoff_en:` the sack opens at the neck and everything loose inside it lifts out as grey dust and drifts away, the linen collapsing around what stays until one hard dense core is left wrapped tight
- `rest_en:` a small tight linen bundle with one hard core inside it lies on the oak
- `foley_en:` a coarse fabric release, a long dusty exhalation, then a taut linen cinch and a dull drop
- `negative_today:` —
- `hook_ru:` Агент, который помнит всё, работает хуже того, который помнит нужное.
- `payoff_ru:` Постоянные факты — кто мы, правила, доступы — в инструкцию. Детали конкретной задачи — только на время задачи. Мусор в памяти всплывает в худший момент.

### 051 · КАРЬЕРА · Учитесь проверять, а не доверять

- `verb_ru:` проступает
- `object_en:` a small bar of bright gold, mirror-polished on every face, its corners crisp and its edges bevelled
- `payoff_en:` the gold thins from one corner inward and goes patchy like a worn plating, and dull grey lead comes up underneath it and spreads across every face until nothing bright is left
- `rest_en:` a dull grey lead bar lies on the oak with a few last flecks of gold on it
- `foley_en:` a fine metallic flaking with the ring dulling as it spreads, then one soft heavy leaden knock
- `negative_today:` stamps, numerals, hallmarks or lettering on the bar;
- `hook_ru:` Главный навык года — быстро проверить чужой правдоподобный ответ.
- `payoff_ru:` Три приёма: спросить источник и открыть его; задать тот же вопрос иначе и сравнить; проверить одну проверяемую деталь. Деталь не сошлась — весь ответ под подозрением.

### 052 · МИФЫ · «На русском модель хуже»

- `verb_ru:` выравнивается
- `object_en:` a solid oak wheel the width of a hand with one long flat spot worn across its rim, the grain raised where it is worn
- `payoff_en:` new wood grows out of the flat and swells until the rim is a true circle again, the grain closing over the join, and the whole wheel trues up and turns smoothly for the first time
- `rest_en:` a perfectly round oak wheel lies flat on the oak
- `foley_en:` a knocking uneven roll smoothing out to nothing, a fibrous woody growth, then one flat settle
- `negative_today:` the wheel rolling, the wheel rolling off the table;
- `hook_ru:` На русском она и правда слабее. Это лечится, а не терпится.
- `payoff_ru:` Сложное рассуждение можно вести на английском, а финальный текст просить на русском с примером стиля. И всегда проверяйте окончания, числительные и имена — там ошибки чаще всего.

### 053 · АГЕНТЫ · Один агент вместо пяти

- `verb_ru:` слипается
- `object_en:` seven small brass gears of the same size loosely meshed together in one hovering clump, the teeth bright and the gaps oil-dark
- `payoff_en:` the seven gears press into one another and their rims run together, teeth merging with teeth, until they are one single large brass gear that starts turning steadily and evenly
- `rest_en:` one large brass gear lies flat on the oak
- `foley_en:` a rattling mismatched clatter grinding into one low steady hum, then a heavy brass lay-down
- `negative_today:` changing gear count, uneven teeth, a machine, a clock;
- `hook_ru:` «Команда из семи агентов» звучит солидно и ломается на третьем.
- `payoff_ru:` Начните с одного агента и одного инструмента. Второго добавляйте, когда первый неделю работает без вас. Каждый лишний участник — новая точка отказа.

### 054 · БИЗНЕС · База знаний — это топливо

- `verb_ru:` пропитывается
- `object_en:` a dry cracked clay jar, unglazed and chalk-pale, hairline splits running down from its rim
- `payoff_en:` dark oil comes up through the clay from the base and soaks it through, the colour climbing the wall, and every crack it reaches closes and disappears behind it
- `rest_en:` a dark oil-soaked clay jar with no cracks left in it stands on the oak
- `foley_en:` a slow absorbent seep climbing the wall, small ceramic clicks as the cracks shut, then a dull set-down
- `negative_today:` flame, a wick, a lamp lit, fire, smoke;
- `hook_ru:` Ассистент отвечает плохо не потому, что глупый, а потому, что ему нечего читать.
- `payoff_ru:` Соберите в одно место регламенты, прайсы, частые вопросы и удачные ответы. Без этого любая модель отвечает «в общем», с этим — как ваш лучший сотрудник.

### 055 · ЭТИКА · Предвзятость данных даёт предвзятый ответ

- `verb_ru:` перекашивается
- `object_en:` a stone bowl turned perfectly symmetrical, the wall the same thickness all the way round, the surface honed matte
- `payoff_en:` the wall on one side thickens steadily while the other side stays exactly as it was, the weight moving off centre, and the whole bowl leans further and further out of true
- `rest_en:` a lopsided stone bowl rests on the oak, tilted and unable to sit level
- `foley_en:` a low stone growth with a grinding edge to it, then one uneven knock and a short rock that stops
- `negative_today:` —
- `hook_ru:` Модель повторяет перекос своих данных и звучит при этом нейтрально.
- `payoff_ru:` В задачах о людях — найм, оценка, отбор — не принимайте решение по ответу модели. Используйте её для черновика критериев и проверяйте на живых примерах.

### 056 · ПРОМПТ · Формат ответа задавайте заранее

- `verb_ru:` укладывается
- `object_en:` a loose handful of mismatched pebbles of every size and colour, held in one uneven hovering cluster
- `payoff_en:` the pebbles square themselves off as they hang, each one taking the same cubic shape as the next, and they slide together into a perfectly even grid five across and five deep
- `rest_en:` a flat even grid of twenty-five matched stone cubes lies on the oak
- `foley_en:` a dry gravel jostle resolving into identical clicks in strict time, then one flat mass landing
- `negative_today:` changing cube count, an incomplete grid, cubes rolling off the table;
- `hook_ru:` Не сказали, в каком виде нужен ответ, — получите стену текста.
- `payoff_ru:` Пишите прямо: таблица из трёх колонок, пять пунктов по одному предложению, письмо на 120 слов. Формат — самый дешёвый способ поднять качество.

### 057 · АВТОМАТИЗАЦИЯ · Пачкой дешевле, чем по одному

- `verb_ru:` умножается
- `object_en:` one ripe apricot with a soft downy skin and a deep crease down one side, warm orange in the beam
- `payoff_en:` the apricot peels copy after copy off itself, each one identical down to the crease, and the copies arrange themselves into an even block hanging square in the air
- `rest_en:` twenty identical apricots lie on the oak in one even block
- `foley_en:` a soft wet series of separations accelerating into a blur, then twenty dull knocks in one single sound
- `negative_today:` changing apricot count, apricots rolling off the table, bruising;
- `hook_ru:` Сто запросов по одному — сто ожиданий. Один пакет — одно.
- `payoff_ru:` Копите однотипные задачи и обрабатывайте пачкой раз в день. Дешевле по деньгам, стабильнее по качеству и проще проверять — все результаты рядом.

### 058 · ИНСТРУМЕНТЫ · Транскрибация встреч

- `verb_ru:` осыпается
- `object_en:` a small brass handbell with a worn wooden handle, the bronze dull and the lip nicked in two places
- `payoff_en:` the bell gives one ring and then loses its solidity from the lip upward, running away into fine brass dust, and the dust does not scatter but pours into one perfectly straight even ridge
- `rest_en:` one straight even ridge of brass dust lies on the oak
- `foley_en:` a single clear ring cut short, a long dry granular pour, then a fine settling patter
- `negative_today:` letters or shapes formed by the dust, writing, a clapper falling separately;
- `hook_ru:` Полтора часа совещания превращаются в шесть строк решений.
- `payoff_ru:` Записывайте встречу, расшифровывайте и просите не пересказ, а три списка: решения, задачи с именами, открытые вопросы. Именно они и нужны, а не конспект.

### 059 · ПРОЦЕСС · Десять минут своей головы

- `verb_ru:` распрямляется
- `object_en:` a green sapling bent right round into a tight curve and held there, the bark tense and shining along the outside of the bend
- `payoff_en:` the curve tightens further and further and slower and slower, and then in a single frame the whole sapling whips straight and stands rigid, quivering along its length
- `rest_en:` a straight green sapling lies rigid on the oak
- `foley_en:` a long creaking fibrous strain, then one hard whip-crack and a fading woody hum
- `negative_today:` —
- `hook_ru:` Самый плохой промпт — тот, что написан вместо размышления.
- `payoff_ru:` Сначала от руки: чего хочу, зачем, как пойму, что готово. Десять минут своего думания экономят час переписки с моделью.

### 060 · ГЕНЕРАЦИЯ · Текст в кадре не генерируйте

- `verb_ru:` сглаживается
- `object_en:` an oak board covered edge to edge in a dense carved knotwork relief, every strand undercut and catching the light
- `payoff_en:` the whole relief sinks back down into the board strand by strand, the shadows flattening out as it goes, until the face is one plain smooth unmarked plank
- `rest_en:` a plain smooth unmarked oak board lies on the oak
- `foley_en:` a fine dense woody settling all over at once, a soft sanding hush, then one flat board slap
- `negative_today:` letters, runes, symbols or lettering in the carving;
- `hook_ru:` Любая надпись внутри кадра выйдет кривой. Особенно кириллица.
- `payoff_ru:` Генерируйте чистый кадр, а титры, логотип и подписи накладывайте в монтаже. Это бесплатно, всегда читаемо и правится за секунду.

### 061 · ИНСТРУМЕНТЫ · Перевод начинается с глоссария

- `verb_ru:` перематывается
- `object_en:` a full spindle of pale silk thread beside an empty one, both turned from dark wood, one hard knot standing in the thread between them
- `payoff_en:` the thread runs off the full spindle and onto the empty one until the two have completely swapped, and the single hard knot travels the whole way across and arrives exactly as it left
- `rest_en:` two wooden spindles lie on the oak, the full one now empty and the knot still in the thread
- `foley_en:` a fast fine silken run with a steady wooden whirr, one snag as the knot passes, then two light clacks
- `negative_today:` —
- `hook_ru:` Модель переведёт гладко и переименует ваш продукт по дороге.
- `payoff_ru:` Дайте список терминов с фиксированным переводом и требование их не менять. Отдельно укажите, что не переводить вовсе: названия, единицы, коды.

### 062 · ПРОЦЕСС · Сохраняйте то, что сработало

- `verb_ru:` каменеет
- `object_en:` a soft grey clay tile with one deep clean impression pressed into its face, the edges of the impression still sharp and damp
- `payoff_en:` the whole tile tightens and darkens from the edges inward, the surface going hard and glassy as stoneware, and the impression sets permanently without losing a single edge
- `rest_en:` a hard dark stoneware tile with one crisp impression in it lies on the oak
- `foley_en:` a fine ceramic tightening with small crackles running inward, then one hard high-pitched knock
- `negative_today:` a handprint, fingers, a face, letters or symbols in the impression, flame, a kiln;
- `hook_ru:` Вы уже писали идеальный промпт. Полгода назад. И потеряли.
- `payoff_ru:` Одно место для удачных промптов с пометкой, для чего он и что дал. Через месяц это личная библиотека, которая экономит больше времени, чем любая новая модель.

### 063 · ГЕНЕРАЦИЯ · Негативный список — половина работы

- `verb_ru:` облетает
- `object_en:` a short branch carrying twenty broad leaves, the leaves dry at the edges and translucent where the beam passes through them
- `payoff_en:` the leaves let go one after another and faster and faster, each one dropping straight down out of the beam, until exactly one leaf is left standing on the bare branch
- `rest_en:` a bare branch with one leaf still on it lies on the oak
- `foley_en:` a fast dry papery detachment accelerating to a rush, then a single light woody knock
- `negative_today:` changing leaf count, more than one leaf remaining, leaves reaching the lens;
- `hook_ru:` Вы описали, что хотите. Модель добавила всё, чего вы не хотели.
- `payoff_ru:` Ведите постоянный список запретов и дописывайте туда каждый пойманный артефакт: лишние пальцы, надписи, блики, глянец кожи. Список растёт от брака, а не от фантазии.

### 064 · КАРЬЕРА · Тридцать дней на один инструмент

- `verb_ru:` вытачивается
- `object_en:` a blunt iron blade with a rounded useless edge, the steel grey and scratched all over from use
- `payoff_en:` the edge draws itself down finer and finer in one continuous movement while the spine thickens to feed it and the scratches polish out, until the edge is a single bright hairline
- `rest_en:` an iron blade with one bright hairline edge lies on the oak
- `foley_en:` a long even stone-on-steel draw repeating and tightening in pitch, then one clean ringing lay-down
- `negative_today:` a whetstone, a hand, blood, sparks;
- `hook_ru:` Попробовать двадцать инструментов — это ноль навыка.
- `payoff_ru:` Выберите один и работайте в нём месяц каждый день. Навык даёт беглость, беглость даёт скорость, скорость видна в результате. Второй инструмент — на тридцать первый день.

### 065 · МИФЫ · «Детектор AI-текста всё покажет»

- `verb_ru:` обрушивается
- `object_en:` a small iron balance with two completely empty pans, the beam level and true, the pivot clean
- `payoff_en:` with nothing in either pan the beam swings hard over and the left pan drops all the way to its stop and stays there, the empty right pan riding high, and the beam locks in that position
- `rest_en:` an iron balance lies on the oak locked hard over with both pans still empty
- `foley_en:` a sudden metallic swing with real weight in it, a hard stop, then a fading iron ring
- `negative_today:` —
- `hook_ru:` Детекторы ошибаются в обе стороны, и это уже стоило людям работы.
- `payoff_ru:` Не принимайте решений по проценту детектора. Спрашивайте о процессе: черновики, источники, правки. Проверяется происхождение работы, а не вердикт машины.

### 066 · АГЕНТЫ · Агент обязан оставлять след

- `verb_ru:` насекается
- `object_en:` a plain cylinder of pale wax the size of a candle stub, unmarked, its surface faintly ribbed from the mould
- `payoff_en:` deep even notches press themselves into the wax one at a time from one end to the other, each one at exactly the same spacing as the last, until the cylinder is scored end to end
- `rest_en:` a wax cylinder scored with an even row of deep notches lies on the oak
- `foley_en:` a series of soft precise waxy indents in strict time, then one dull light knock
- `negative_today:` letters, numerals or symbols in the notches, a stylus, changing notch count;
- `hook_ru:` Агент что-то сделал. Что именно — узнать невозможно. Это не помощник.
- `payoff_ru:` Требуйте журнал: какие шаги, какие инструменты, какие данные, чем закончилось. Без следа нельзя ни доверять, ни исправлять, ни повторить успех.

### 067 · БИЗНЕС · Продажи: подготовка, а не разговор

- `verb_ru:` разворачивается
- `object_en:` a rolled leather tool wrap tied with a thong, the leather dark and oiled, hard shapes bulging under it
- `payoff_en:` the thong unties itself and the wrap rolls out flat across the air, and every tool inside slides up out of its pocket and turns to lie in one even row with its handle toward the same side
- `rest_en:` an open leather wrap lies flat on the oak with its tools laid out in one even row
- `foley_en:` a leather creak and a long unrolling slap, then a run of metal touches settling into a line
- `negative_today:` changing tool count, brand names or lettering on the tools;
- `hook_ru:` Модель не должна говорить с клиентом. Она должна подготовить к разговору вас.
- `payoff_ru:` Перед встречей просите справку о компании, три вероятных возражения и три вопроса, которые стоит задать. Пятнадцать минут подготовки меняют разговор сильнее любого скрипта.

### 068 · ЭТИКА · Авторские права: зона серая, но не пустая

- `verb_ru:` сворачивается
- `object_en:` a small stretched canvas thick with dried oil paint, the impasto standing up in hard ridges that throw their own shadows
- `payoff_en:` the whole paint layer lifts off the weave in one continuous skin and rolls itself up tight from one edge to the other, leaving the canvas underneath completely bare and white
- `rest_en:` a bare white canvas lies on the oak with a tight roll of dried paint beside it
- `foley_en:` a slow adhesive peel across the whole surface, a leathery roll, then two separate soft landings
- `negative_today:` a recognisable painting, a portrait, a signature, lettering on the canvas;
- `hook_ru:` «Взял из интернета» — это не лицензия.
- `payoff_ru:` Для коммерции три правила: не имитируйте живого автора по имени, не используйте чужой бренд и логотип, храните доказательства своего процесса. Законы разнятся, эти три работают везде.

### 069 · ПРОМПТ · Черновик, потом правка

- `verb_ru:` обстругивается
- `object_en:` a rough-hewn block of pale wood with the axe facets still on it, the end grain torn and fibrous
- `payoff_en:` shavings lift off the block in pass after pass and fly out of the beam, each pass taking it closer, and under them a smooth deep-bowled spoon comes out of the wood
- `rest_en:` a smooth finished wooden spoon lies on the oak
- `foley_en:` a series of clean planing strokes rising in pitch with shavings ticking away, then one light set-down
- `negative_today:` a knife, a plane or a hand in frame, shavings reaching the lens;
- `hook_ru:` Идеального ответа с первого раза не бывает. И не надо.
- `payoff_ru:` Просите быстрый грубый вариант, потом по одной правке: «сократи вдвое», «убери третий пункт», «сделай проще». Пошаговая правка точнее переписанного с нуля промпта.

### 070 · АВТОМАТИЗАЦИЯ · Что делать при ошибке — решите заранее

- `verb_ru:` рвётся
- `object_en:` a short length of heavy iron chain hanging in a loose loop, the links pitted and one link visibly thinner than the rest
- `payoff_en:` the thin link opens and the chain parts, and before the two ends can fall away a doubled loop of new iron closes around the break and pulls it shut, thicker than the original ever was
- `rest_en:` a length of iron chain with one heavy doubled repair in it lies on the oak
- `foley_en:` a hard metal snap and two ends swinging, then a fast iron closure and a dense settling clank
- `negative_today:` —
- `hook_ru:` Сценарий сломается. Вопрос только — тихо или громко.
- `payoff_ru:` На каждый шаг пропишите: что если пусто, что если долго, что если отказ. Минимум — один повтор и сообщение человеку. Молчаливый сбой хуже громкого.

### 071 · ЭТИКА · Кодовое слово вместо доверия голосу

- `verb_ru:` сминается
- `object_en:` a heavy iron padlock with a thick shackle, the body scarred and rust-flecked, reading as solid as a brick
- `payoff_en:` a little dust drifts against it and the whole padlock caves in like foil at the contact, the body folding flat and the shackle collapsing with it, all of it plainly hollow
- `rest_en:` a flattened hollow shell of a padlock lies on the oak
- `foley_en:` a thin tinny crumple far too light for its size, then one hollow rattle and nothing
- `negative_today:` a key, a keyhole, a door, lettering or a brand on the lock;
- `hook_ru:` Голос вашего сына в трубке больше не доказательство, что это он.
- `payoff_ru:` Договоритесь с близкими и с бухгалтерией о кодовом слове и правиле «перезвоню сам». Любая срочная просьба о деньгах голосом или видео — сначала отбой, потом свой звонок.

### 072 · ПРОМПТ · «Задай мне пять вопросов»

- `verb_ru:` раскрывается
- `object_en:` a plain closed wooden box with no visible seams, waxed dark, its corners rounded from handling
- `payoff_en:` five small drawers push out of the box one after another on five different faces, each one further than the last, and each comes out heaped with dark grain that was not in it before
- `rest_en:` a wooden box with five loaded drawers standing open rests on the oak
- `foley_en:` five wooden slides in sequence each with a soft loaded weight in it, then one settling knock
- `negative_today:` changing drawer count, labels or numbers on the drawers, furniture;
- `hook_ru:` Одна фраза, которая поднимает качество любого запроса.
- `payoff_ru:` Добавляйте в конец: «сначала задай до пяти уточняющих вопросов, потом отвечай». Модель вытащит контекст, который вы забыли дать, — именно на нём и ломались прошлые ответы.

### 073 · АВТОМАТИЗАЦИЯ · Расписание вместо силы воли

- `verb_ru:` наращивается
- `object_en:` a short stack of three thin slate discs, the edges chipped, the faces dull and cool
- `payoff_en:` the stack pushes a new disc out of its own top face at exactly even intervals, one after another with the same pause between each, until it has grown into a tall even column
- `rest_en:` a tall even column of slate discs stands on the oak
- `foley_en:` a slow stone extrusion repeating in perfect time, each one ending in the same small click
- `negative_today:` changing disc count, the column toppling, discs sliding off;
- `hook_ru:` То, что должно случаться каждый день, не должно зависеть от настроения.
- `payoff_ru:` Поставьте задачу на конкретное время так, чтобы она выполнялась без вас, а вам приходил результат. Регулярность даёт эффект, которого не дают разовые рывки.

### 074 · ИНСТРУМЕНТЫ · Поиск с источниками против памяти

- `verb_ru:` раскалывается
- `object_en:` a dull round geode the size of a fist, its outside crusted grey and utterly ordinary, giving no hint of what is inside
- `payoff_en:` a single crack opens across it and the two halves swing apart, and the inside is packed with sharp clear crystals that pick up the beam and throw hard points of light across the wood
- `rest_en:` two halves of a crystal-lined geode lie open on the oak
- `foley_en:` one hard dry stone crack, a fine crystalline ring as the halves part, then two solid knocks
- `negative_today:` coloured crystals, purple or blue glow, glowing crystals;
- `hook_ru:` Ответ без ссылки — это пересказ по памяти. Иногда чужой.
- `payoff_ru:` Для фактов, цен, законов и новостей включайте режим с поиском и открывайте источники. Модель без доступа к сети отвечает тем, что запомнила год назад.

### 075 · ПРОЦЕСС · Держите примеры «хорошо» и «плохо»

- `verb_ru:` растрескивается
- `object_en:` two identical plain white cups standing side by side as one piece, thrown from the same clay, their rims level with each other
- `payoff_en:` the left cup fills to the brim with clear water while the right one splits from its base upward in a dry branching crack that runs all the way to the rim
- `rest_en:` two cups stand on the oak, one full to the brim and one cracked and dry
- `foley_en:` a soft rising pour on one side, a hard ceramic split running upward on the other, then two knocks
- `negative_today:` —
- `hook_ru:` Модель не знает вашего вкуса, пока вы его не показали.
- `payoff_ru:` Соберите по три образца: так хорошо, так плохо. Прикладывайте оба набора. Отрицательный пример работает не хуже положительного и экономит круги правок.

### 076 · ГЕНЕРАЦИЯ · Формат задавайте трижды

- `verb_ru:` растягивается
- `object_en:` a square wooden frame with mortised corners, the wood pale and planed, the joints tight
- `payoff_en:` the two vertical members grow longer and the two horizontals draw in, the whole frame stretching up into a tall narrow portrait rectangle, and the corners lock with one hard click
- `rest_en:` a tall narrow portrait frame lies on the oak
- `foley_en:` a woody sliding stretch with the joints creaking, then one sharp locking click and a flat settle
- `negative_today:` a picture or canvas inside the frame, glass, a reflection;
- `hook_ru:` Вы просили вертикальное видео и получили горизонтальное. Классика.
- `payoff_ru:` Пишите формат в трёх местах: первой строкой промпта словами и пикселями, в списке запретов и в настройках генерации. Одного места не хватает — проверено дорого.

### 077 · КАРЬЕРА · Побочный проект как доказательство

- `verb_ru:` складывается
- `object_en:` a loose pile of small unfired clay bricks, the edges soft and crumbly, all held in one hovering heap
- `payoff_en:` the bricks turn and find their places one by one and build themselves into a small true arch, the last wedge dropping into the crown, and the arch holds its own weight in the air
- `rest_en:` a small clay arch stands on the oak holding itself up
- `foley_en:` a run of soft gritty placements in sequence, one firm final seat, then a low load-bearing creak
- `negative_today:` changing brick count, the arch collapsing, mortar, scaffolding;
- `hook_ru:` Сертификат говорит, что вы слушали. Проект — что вы умеете.
- `payoff_ru:` Сделайте одну маленькую вещь до конца и покажите публично: бот для своей команды, разбор процесса, тридцать роликов подряд. Законченное маленькое весит больше начатого большого.

### 078 · МИФЫ · «Больше параметров — умнее»

- `verb_ru:` крошится
- `object_en:` a big porous grey rock riddled with holes hovering together with one small dense dark pebble as a single group
- `payoff_en:` the big rock starts shedding from the inside, its walls giving way and the whole mass breaking down into rubble and grit, while the small dark pebble beside it does not change in any way
- `rest_en:` a heap of grey rubble lies on the oak with one small whole dark pebble beside it
- `foley_en:` a deep internal collapse with a long gritty avalanche, then one small clean tick
- `negative_today:` —
- `hook_ru:` Маленькая модель с вашими данными часто бьёт большую без них.
- `payoff_ru:` Сравнивайте не размер, а результат на своей задаче. Большая нужна для сложного рассуждения; для типовых операций дешёвая и быстрая выигрывает по деньгам и времени.

### 079 · АГЕНТЫ · Второй проход ловит половину ошибок

- `verb_ru:` вминается
- `object_en:` a finished turned wooden disc, sanded smooth all over, its rim perfectly true and waxed to a low sheen
- `payoff_en:` three deep dents open in the rim one after another with a pause between each, each one pushing in from outside and staying there, and the true circle is plainly broken in three places
- `rest_en:` a wooden disc with three deep dents in its rim lies on the oak
- `foley_en:` three separated hollow woody compressions with silence between them, then one flat lay-down
- `negative_today:` changing dent count, more than three dents, the disc rolling;
- `hook_ru:` Тот же самый агент на проверке находит то, что сам же и напортил.
- `payoff_ru:` После результата запускайте отдельный шаг: «проверь по этим критериям и перечисли расхождения». Отдельная проверка работает лучше, чем «сделай хорошо» в первом запросе.

### 080 · БИЗНЕС · Найм: скрининг машине, решение человеку

- `verb_ru:` расслаивается
- `object_en:` a loose handful of dried beans of two clearly different sizes, mottled and matte, held in one hovering cluster
- `payoff_en:` the cluster separates in the air, all the small beans drifting to one side and all the large ones to the other, and one single bean pulls clear of both groups and hangs by itself
- `rest_en:` two separate heaps of beans lie on the oak with one bean sitting apart from both
- `foley_en:` a dry rattling separation splitting into two streams, two soft heaps landing, then one distinct tick
- `negative_today:` —
- `hook_ru:` Модель может отсеять по формальным критериям. Выбрать человека — не может.
- `payoff_ru:` Пусть проверяет соответствие жёстким требованиям и готовит вопросы к интервью. Оценка кандидата, потенциала и совместимости — только живой разговор.

### 081 · МИФЫ · «Модель ищет в интернете»

- `verb_ru:` опустошается
- `object_en:` a dry sealed gourd with a hard brown skin, plainly heavy with something loose inside that shifts as it turns
- `payoff_en:` the rattling gets louder and then the top of the gourd splits open in a ragged ring, and there is nothing inside it at all but a slow drift of grey dust that lifts out
- `rest_en:` a split empty gourd lies on the oak with its severed top beside it
- `foley_en:` a loud dry rattle building up, one husky tearing split, then a thin dusty exhale and silence
- `negative_today:` —
- `hook_ru:` По умолчанию она не ищет. Она вспоминает.
- `payoff_ru:` Проверьте, включён ли поиск в вашем инструменте. Если нет — модель отвечает по памяти обучения и может выдумать ссылку. Ссылку всегда открывайте, а не читайте глазами.

### 082 · АГЕНТЫ · Без критерия остановки агент крутится вечно

- `verb_ru:` истачивается
- `object_en:` a heavy brass spinning top already turning fast, its point machined sharp, its body polished to a bright band
- `payoff_en:` it speeds up instead of slowing and begins wearing away from the point upward, brass coming off it in a fine bright haze, the body shrinking smaller and smaller and never once losing speed
- `rest_en:` a small worn brass stub lies on the oak in a fine ring of brass dust
- `foley_en:` a rising metallic whine climbing past where it should stop, a fine abrasive hiss, then a small clatter
- `negative_today:` —
- `hook_ru:` Самый дорогой агент — тот, который не знает, что уже закончил.
- `payoff_ru:` Задайте три предела: что считается готовым, сколько попыток максимум, сколько времени и денег. Без потолка цикл съедает бюджет молча.

### 083 · БИЗНЕС · Обучение дешевле лицензий

- `verb_ru:` передаётся
- `object_en:` one closed iron ring lying against a tight bundle of ten straight iron rods, all of it hovering as one group
- `payoff_en:` each rod in turn curls round and closes into a ring exactly like the first, one after another down the bundle, and the original ring is not diminished or altered in any way
- `rest_en:` eleven identical iron rings lie on the oak in a loose pile
- `foley_en:` ten metallic bends in sequence each ending in a small closing clink, then one heavy pile settling
- `negative_today:` changing ring count, flame, fire, glowing metal;
- `hook_ru:` Компании покупают подписки и не покупают навык. Работает наоборот.
- `payoff_ru:` Два часа обучения на команду дают больше, чем ещё один инструмент. Внутренняя библиотека промптов и «час обмена» раз в две недели — это и есть внедрение.

### 084 · ЭТИКА · Пароли и ключи ассистенту не нужны

- `verb_ru:` обламывается
- `object_en:` six iron keys of different cuts hanging from a worn split hoop, the keys heavy and still
- `payoff_en:` five of the six keys break clean off at the shoulder one after another and drop away out of the beam, and the last one stays on the hoop and thins down to a much smaller simpler shape
- `rest_en:` a split hoop with one small simple key on it lies on the oak
- `foley_en:` five hard metallic snaps at uneven intervals each with a falling ring after it, then one light set-down
- `negative_today:` changing key count, a lock, a keyhole, numbers stamped on the keys;
- `hook_ru:` Ассистенту не нужен ваш пароль. Ему нужен ограниченный доступ.
- `payoff_ru:` Никогда не вставляйте пароли, ключи и коды в чат. Для интеграций заводите отдельный доступ с минимальными правами и возможностью отозвать его одним движением.

### 085 · ПРОМПТ · Критерии приёмки прямо в промпте

- `verb_ru:` подгоняется
- `object_en:` an oversized wooden peg standing inside a loose iron ring that is far too small to pass over it, both hovering as one piece
- `payoff_en:` the peg shaves itself down evenly all round with the shavings lifting away, and it goes on at exactly the same rate until the ring drops over it and then stops the instant the fit is exact
- `rest_en:` a wooden peg lies on the oak with the iron ring seated snugly around it
- `foley_en:` an even continuous shaving rasp, a soft metallic slide down the peg, then one precise stop and a knock
- `negative_today:` —
- `hook_ru:` Скажите модели, по каким признакам вы примете ответ, — и она их выполнит.
- `payoff_ru:` Дописывайте в конце: «ответ хорош, если не длиннее 200 слов, содержит три конкретных примера и не содержит общих фраз». Модель проверит себя по вашему же списку.

### 086 · АВТОМАТИЗАЦИЯ · Не автоматизируйте хаос

- `verb_ru:` стягивается
- `object_en:` a loose sprawling tangle of thin steel wire with ends sticking out everywhere, catching hard points of light
- `payoff_en:` the tangle pulls in on itself hard and fast, every loop tightening and locking against the next, and it goes on tightening until it is one dense impenetrable ball with no ends left showing
- `rest_en:` one dense impenetrable ball of steel wire lies on the oak
- `foley_en:` a fast metallic ratcheting inward with the wire singing under tension, then one hard dead landing
- `negative_today:` —
- `hook_ru:` Автоматизированный беспорядок — это просто более быстрый беспорядок.
- `payoff_ru:` Если у процесса нет описания и владельца, автоматизация лишь ускорит ошибки. Сначала порядок и правило, потом сценарий.

### 087 · ИНСТРУМЕНТЫ · Считает формула, а не модель

- `verb_ru:` выверяется
- `object_en:` a shapeless lump of soft grey lead, its surface dented and thumb-marked, no two sides of it alike
- `payoff_en:` flat faces cut themselves across the lump one after another at exact angles until it has become a perfect regular solid, every edge the same length and every face the same size
- `rest_en:` a perfect regular lead solid rests on the oak
- `foley_en:` a run of precise metallic shears each cleaner than the last, then one dense flat set-down
- `negative_today:` numbers or markings on the faces, changing face count, dice pips;
- `hook_ru:` Не просите модель складывать. Просите её написать формулу.
- `payoff_ru:` Для чисел просите не результат, а формулу или скрипт, который запустите сами. Модель отлично строит правило вычисления и плохо считает в уме.

### 088 · ПРОЦЕСС · Ретроспектива провалов

- `verb_ru:` завязывается
- `object_en:` a length of pale hemp rope, loosely coiled, its lay open and its cut ends whipped
- `payoff_en:` a knot ties itself into the rope, and then another, and another, the knots coming at even intervals along its whole length and each one pulling tight with a small jerk
- `rest_en:` a length of rope covered in evenly spaced tight knots lies on the oak
- `foley_en:` a series of fibrous cinches in even time each with a small dry snap, then a soft coil landing
- `negative_today:` —
- `hook_ru:` Раз в неделю полезно вспомнить, где вы зря доверились.
- `payoff_ru:` Держите короткий список: что просил, что получил, почему не сработало. Через месяц это личная карта границ — вы точно знаете, где модель помогает, а где мешает.

### 089 · ГЕНЕРАЦИЯ · Длинный ролик — больше дрейфа

- `verb_ru:` провисает
- `object_en:` one long thin glass cane and one short thick one hovering side by side, both drawn to the same clear finish
- `payoff_en:` the long cane begins to sag in the middle and the sag deepens until it breaks into five uneven pieces, while the short one beside it stays perfectly straight and completely unchanged
- `rest_en:` five broken pieces of glass cane lie on the oak beside one short unbroken cane
- `foley_en:` a slow glassy strain bending downward, five sharp snaps close together, then a light scatter
- `negative_today:` glass shards reaching the lens, changing piece count, blood;
- `hook_ru:` Чем дольше кадр, тем сильнее герой перестаёт быть собой.
- `payoff_ru:` Держите одну генерацию короткой, восемь-двенадцать секунд. Нужно длиннее — собирайте из кусков с одним референсом, а не просите тридцать секунд одним куском.

### 090 · КАРЬЕРА · Не гонитесь за новинками

- `verb_ru:` улетучивается
- `object_en:` a heap of bright new steel nails with one old dark hand-forged nail lying across the top of them
- `payoff_en:` every bright nail lifts off the heap and drifts up out of the beam, layer after layer of them going, while the single dark forged nail stays exactly where it is and only gets heavier
- `rest_en:` one old dark hand-forged nail lies alone on the oak
- `foley_en:` a long bright metallic rustle lifting away and thinning to nothing, then one deep heavy iron knock
- `negative_today:` —
- `hook_ru:` Каждую неделю выходит новая модель. Ваш рабочий процесс — один.
- `payoff_ru:` Смотрите новинки раз в месяц, час, списком. Всё остальное время углубляйте один процесс. Выигрывает не тот, кто попробовал всё, а тот, кто довёл одно до предела.

### 091 · ПРОЦЕСС · Знайте, когда не использовать AI

- `verb_ru:` смыкается
- `object_en:` a pair of heavy iron shears held wide open, the blades honed bright along their edges, the pivot thick with old grease
- `payoff_en:` the blades swing shut on nothing at all and then keep going, the two halves running together at the join until the shears are one solid piece of iron that can never open again
- `rest_en:` a single fused piece of iron in the shape of closed shears lies on the oak
- `foley_en:` one clean scissoring close, then a low metallic welding sound and a dead heavy landing
- `negative_today:` —
- `hook_ru:` Иногда самое профессиональное решение — закрыть чат.
- `payoff_ru:` Не отдавайте модели соболезнования, извинения, обратную связь человеку и решения о людях: там ценность именно в том, что это делали вы. В остальном пользуйтесь спокойно.

### 092 · ГЕНЕРАЦИЯ · Фактура вместо гладкости

- `verb_ru:` шершавеет
- `object_en:` a perfectly smooth white sphere with no texture on it at all, reading flat and synthetic even in the hard beam
- `payoff_en:` the surface roughens all over at once, fine pits and scratches opening across it, dust settling into them and a crust forming along one side, and only then does it start looking like an object
- `rest_en:` a pitted dusty roughened white sphere rests on the oak
- `foley_en:` a fine abrasive crackle spreading over the whole surface, then one dry gritty knock
- `negative_today:` —
- `hook_ru:` Слишком чисто — значит нарисовано. Правду делают поры, пыль и зерно.
- `payoff_ru:` Просите текстуру прямо: поры кожи, пыль в воздухе, потёртости, лёгкий шум сенсора. И запрещайте глянец, «сияющую кожу» и эффект бьюти-фильтра.

### 093 · КАРЬЕРА · Принесите на собеседование свои промпты

- `verb_ru:` развёртывается
- `object_en:` five identical steel chisels bound together in a tight bundle, their bevels ground bright and their handles worn dark
- `payoff_en:` the binding falls away and the five chisels swing apart into an even fan, each one turning as it goes so that every bright bevel ends up facing the same way
- `rest_en:` five chisels lie on the oak in an even fan with all the bevels facing the same way
- `foley_en:` a cord slipping free, five metallic swings spreading out in sequence, then five light taps
- `negative_today:` changing chisel count, the chisels standing upright in the table, brand names;
- `hook_ru:` «Пользуюсь нейросетями» — пустая строчка. Покажите пять своих промптов.
- `payoff_ru:` Возьмите на встречу рабочий набор: под какие задачи, что экономит, где не работает. Это доказательство навыка, которое проверяется за две минуты.

### 094 · МИФЫ · «Есть один правильный промпт»

- `verb_ru:` обезличивается
- `object_en:` an elaborate steel multi-tool with ten different heads folded out around it, every head a different precise shape
- `payoff_en:` all ten heads fold back in one after another and the joints close over them, and the body swells and rounds off until it is one plain featureless steel bar with nothing to grip and nothing to use
- `rest_en:` one plain featureless steel bar lies on the oak
- `foley_en:` ten mechanical folds in sequence with the joints closing tight, then a swelling groan and a dead knock
- `negative_today:` —
- `hook_ru:` Волшебной формулы нет. Есть ваш контекст и три итерации.
- `payoff_ru:` Скачанные «сто лучших промптов» дают средний результат, потому что написаны не про вашу задачу. Берите структуру, подставляйте свой контекст, правьте по результату.

### 095 · АГЕНТЫ · Доступ к данным важнее формулировки

- `verb_ru:` прочищается
- `object_en:` a length of dry copper pipe capped at both ends, the metal dulled to a dark brown, one green stain near the joint
- `payoff_en:` the near cap turns and drops away and a heavy unbroken column of clear water drives out of the pipe under real pressure, running long and steady with no sign of stopping
- `rest_en:` an open copper pipe lies on the oak in a wide flat pool of water
- `foley_en:` a metallic cap release, then a full-pressure water roar settling into a steady heavy pour
- `negative_today:` water reaching the lens, the pool leaving the table, a tap or valve;
- `hook_ru:` Не улучшайте промпт там, где не хватает доступа к данным.
- `payoff_ru:` Агент ошибается — сначала спросите, есть ли ему откуда взять правильный ответ. Подключить источник полезнее, чем десять раз переписать инструкцию.

### 096 · БИЗНЕС · Не покупайте инструмент под несуществующую задачу

- `verb_ru:` защёлкивается
- `object_en:` a big new brass padlock with its shackle standing open, the finish unworn and the keyway clean
- `payoff_en:` the shackle swings down and slams shut into the body with everything the mechanism has, and then the whole lock thickens and doubles in size around a hasp that is not there and never was
- `rest_en:` an oversized locked brass padlock lies on the oak, fastened to nothing
- `foley_en:` one heavy mechanical slam with a deep bolt throw in it, then a slow metallic growth and a dead thud
- `negative_today:` —
- `hook_ru:` Сначала подписка, потом поиск, зачем она.
- `payoff_ru:` Порядок такой: задача с измеримой болью, две недели ручного эксперимента, только потом покупка. Иначе вы платите за чужую презентацию.

### 097 · ЭТИКА · Право на отказ

- `verb_ru:` отстраняется
- `object_en:` a slender ash lath sprung between two short posts and bowed hard toward one side, the grain stretched taut along the outside of the bend
- `payoff_en:` the bow deepens until the lath is about to touch the post it is leaning toward, and then it lets go entirely, springing back the other way and settling into a slack easy curve
- `rest_en:` a slack curved ash lath lies on the oak between two short posts
- `foley_en:` a rising strained woody creak bending upward in pitch, then one release crack and a soft settle
- `negative_today:` flame, fire, straw, sparks, the lath snapping;
- `hook_ru:` «Технически возможно» и «стоит делать» — разные вещи.
- `payoff_ru:` Заведите личный красный список: чего вы не будете делать с AI даже за деньги. Оживление умерших без согласия семьи, чужие лица, поддельные отзывы. Это ваша репутация в письменном виде.

### 098 · ПРОМПТ · Дайте материал, а не просите вспомнить

- `verb_ru:` наполняется
- `object_en:` a heavy stone mortar with a stone pestle standing in it, both dry and empty, the inside worn pale and smooth
- `payoff_en:` dark grain wells up out of the floor of the mortar until the bowl is full, and the pestle turns down into it on its own and grinds the whole load to pale flour in one continuous pass
- `rest_en:` a stone mortar full of pale flour rests on the oak with its pestle standing in it
- `foley_en:` a hollow empty stone knock, then a dry grain rush and a long even grinding thickening to a powder sound
- `negative_today:` —
- `hook_ru:` Не спрашивайте «что ты знаешь о нашем продукте». Дайте документ.
- `payoff_ru:` Ответ по вашим файлам всегда точнее ответа по памяти модели. Прикладывайте исходники и добавляйте: «отвечай только по приложенному, чего нет — так и скажи».

### 099 · АВТОМАТИЗАЦИЯ · Человек на необратимых шагах

- `verb_ru:` остекловывается
- `object_en:` a thick stick of dry white chalk, blunt at both ends, powdery and matte along its whole length
- `payoff_en:` black glass creeps up the chalk from one end, hard and shining, and stops dead exactly at the midpoint, so that one half can never be rubbed away and the other is still loose powder
- `rest_en:` a stick lies on the oak, one half white chalk and one half black glass
- `foley_en:` a fine crystalline hardening travelling up the stick, one sharp stop, then a hard bright knock
- `negative_today:` —
- `hook_ru:` Отправить письмо клиенту нельзя отменить. Всё остальное — можно.
- `payoff_ru:` Разделите шаги на обратимые и необратимые. Обратимые пусть идут сами. Необратимые — только через одно подтверждение живого человека.

### 100 · ИНСТРУМЕНТЫ · Свой экзамен из трёх задач

- `verb_ru:` протискивается
- `object_en:` a rough pewter blank hovering against a single iron plate pierced by three openings, one round, one square and one triangular, the plate dull and pitted
- `payoff_en:` the blank squeezes itself through the round opening and reforms, squeezes through the square one and reforms again, and then jams solid halfway into the triangular one and stops
- `rest_en:` an iron plate lies on the oak with a pewter blank jammed halfway through one of its three openings
- `foley_en:` two thick metallic extrusions with a wet drag to them, then one hard grinding stop and a flat landing
- `negative_today:` —
- `hook_ru:` Обзоры бесполезны. Ваш тест из трёх задач — нет.
- `payoff_ru:` Держите три своих типовых задачи как личный экзамен и прогоняйте через них каждую новую модель. Пятнадцать минут заменяют месяц чтения обзоров.

### 101 · ПРОМПТ · Разбор по шагам на расчётах

- `verb_ru:` разбирается
- `object_en:` a small course of seven fired bricks laid up as one block, the mortar joints thin and even, the faces sand-rough
- `payoff_en:` the bricks lift apart one at a time from the top down and spread out in a line in the air, and the fourth one comes out split clean in two across its middle
- `rest_en:` seven bricks lie in a line on the oak with the middle one in two pieces
- `foley_en:` seven dry mortar releases in even sequence, then one distinct hollow crack among the knocks
- `negative_today:` changing brick count, lettering or a maker's mark on the bricks;
- `hook_ru:` Для чисел и логики требуйте не ответ, а разбор по шагам.
- `payoff_ru:` Пишите: «разложи по шагам и в конце проверь себя обратным счётом». Ошибка становится видимой, а часть ошибок исчезает сама — модель ловит себя.

### 102 · АВТОМАТИЗАЦИЯ · Один источник правды

- `verb_ru:` сливается
- `object_en:` three identical clay jugs standing together as one group, each holding water to a different and plainly uneven level
- `payoff_en:` the three jugs run together into each other, wall merging into wall until there is one larger jug, and inside it the water finds a single level and goes flat and still
- `rest_en:` one large clay jug stands on the oak with its water at one flat level
- `foley_en:` three ceramic bodies grinding together into one, a slosh finding its level, then a heavy wet set-down
- `negative_today:` —
- `hook_ru:` Три версии одного файла — и любая автоматизация начинает врать.
- `payoff_ru:` Один файл, одно место, одна ответственная роль. Автоматизация усиливает то, что есть: с одним источником — порядок, с тремя — три разных отчёта.

### 103 · ИНСТРУМЕНТЫ · Где ломается бесплатный тариф

- `verb_ru:` лопается
- `object_en:` a fine linen thread hanging straight down with three small lead weights already strung on it, the thread visibly stretched thin
- `payoff_en:` a fourth weight forms on the thread below the others and the thread stretches, narrows and then parts at its thinnest point, and all four weights drop together
- `rest_en:` four lead weights lie on the oak with a broken thread lying across them
- `foley_en:` a tightening fibrous creak going up in pitch, one dry snap, then four small knocks together
- `negative_today:` —
- `hook_ru:` Бесплатно ровно до того момента, когда становится по-настоящему нужно.
- `payoff_ru:` Ограничения обычно в трёх местах: длина контекста, число запросов, доступ к сильной модели. Поймите, какое из трёх бьёт по вашей задаче, — платить стоит только за него.

### 104 · ПРОЦЕСС · Одно место для всех находок

- `verb_ru:` собирается
- `object_en:` a dozen small bright brass pins spread wide apart in the air, each one catching its own hard point of light
- `payoff_en:` the pins draw together from every direction and stand themselves upright side by side, packing tighter and tighter until they are one solid brass block bristling with heads
- `rest_en:` one solid block of packed brass pins stands on the oak
- `foley_en:` a scatter of fine metallic ticks converging into a dense rattle, then one firm compacted knock
- `negative_today:` changing pin count, pins reaching the lens, needles;
- `hook_ru:` Ваши лучшие находки разбросаны по десяти чатам и не найдутся.
- `payoff_ru:` Одна папка: промпты, удачные ответы, что не сработало, ссылки. Пять минут разбора в неделю. Через год это стоит дороже подписки.

### 105 · ГЕНЕРАЦИЯ · Раскадровка по секундам

- `verb_ru:` размечается
- `object_en:` a plain brass rod as long as a forearm, drawn smooth with no markings anywhere on it, one long highlight running its length
- `payoff_en:` bright grooves cut themselves across the rod at exactly equal spacing, one after another from end to end, dividing it into ten identical segments with no segment wider than another
- `rest_en:` a brass rod divided into ten equal grooved segments lies on the oak
- `foley_en:` ten precise metallic incisions in strict even time, then one clean ringing lay-down
- `negative_today:` numerals, letters or a scale on the rod, changing segment count;
- `hook_ru:` «Сделай красивое видео» — это не задание. «0.0–1.4, 1.4–2.6» — задание.
- `payoff_ru:` Пишите таймкоды с описанием, что происходит в каждом отрезке, и добавляйте «выполняй строго по порядку, не переставляй и не сжимай». Без этого модель скомкает финал.

### 106 · КАРЬЕРА · Исчезают задачи, а не профессии

- `verb_ru:` высыпается
- `object_en:` a small wooden abacus frame strung with rows of dark beads, the frame square and solid, the rods thin and bright
- `payoff_en:` every bead slips off its rod and pours down out of the beam, row after row emptying, while the frame and the bare rods hold their shape without shifting at all
- `rest_en:` an empty wooden abacus frame with bare rods stands on the oak
- `foley_en:` a fast wooden bead cascade thinning out to single ticks, then one light frame knock
- `negative_today:` numbers, changing rod count, the frame breaking;
- `hook_ru:` Бухгалтер остался. Ручной свод отчёта — нет.
- `payoff_ru:` Смотрите на состав работы, а не на название должности. Формализуемые задачи уйдут первыми; останутся ответственность, отношения и решения в неопределённости. Двигайтесь туда.

### 107 · МИФЫ · «Генерация ничего не стоит»

- `verb_ru:` убывает
- `object_en:` a tall stack of thin lead discs, blank on both faces, the edges slightly burred and the stack leaning very slightly
- `payoff_en:` the discs go one at a time from the top, each thinning away to nothing at a steady unhurried rate, and the stack comes down and down until a single disc is left
- `rest_en:` one thin blank lead disc lies alone on the oak
- `foley_en:` a run of soft metallic dissolves in even time with the pitch dropping as the stack shortens, then one flat tick
- `negative_today:` coins, currency, faces or numerals on the discs, the discs rolling;
- `hook_ru:` Кнопка бесплатная. Секунда видео — нет.
- `payoff_ru:` Считайте себестоимость готового ролика с учётом перегенераций. Больше всего экономит не выбор модели, а точный промпт с первого раза.

### 108 · АГЕНТЫ · Планировщик и исполнитель

- `verb_ru:` раздваивается
- `object_en:` a heavy grey river stone the size of a fist, dry and matte, one flat facet worn smooth across its top
- `payoff_en:` a hairline seam opens around the stone and it draws apart into two unequal halves that hang side by side, the smaller one thinning as it goes into a fine pale shell of the larger
- `rest_en:` a solid grey stone and a thin hollow shell of the same shape lie side by side on the oak
- `foley_en:` a dry granular split, one low grinding parting of stone, settling into two separate dull knocks on wood
- `negative_today:` changing stone count, three stones, the halves merging back together, gravel, rubble;
- `hook_ru:` Один думает, другой делает — и оба работают лучше.
- `payoff_ru:` Разделите на два шага: сначала план в виде списка действий, вы его смотрите, потом выполнение по утверждённому плану. Половина плохих действий отсеивается на плане бесплатно.

### 109 · БИЗНЕС · Качество данных — это потолок

- `verb_ru:` отстаивается
- `object_en:` a tall glass cylinder full of clouded brown water, the suspension so thick that the beam barely gets through it
- `payoff_en:` the sediment comes out of suspension all at once and falls as a dense curtain to the bottom, and the water above it goes clear from the top down until the beam drives straight through
- `rest_en:` a glass cylinder of clear water with a thick layer of silt at the bottom stands on the oak
- `foley_en:` a fine sedimentary hiss falling through water, a soft dense settle at the base, then one glass knock
- `negative_today:` —
- `hook_ru:` Модель не спасёт таблицу, в которой три написания одного клиента.
- `payoff_ru:` Перед любым внедрением почистите данные: единые названия, заполненные поля, один формат дат. Час чистки даёт больше, чем месяц подбора модели.

### 110 · ЭТИКА · Ответственность остаётся на человеке

- `verb_ru:` впечатывается
- `object_en:` a pool of dark red sealing wax still soft, with a heavy brass seal hanging directly above it, the seal face completely smooth and blank
- `payoff_en:` the seal drives down into the soft wax and the wax squeezes out around it in a thick even ring, and then the whole thing hardens and grips so that seal and wax become one piece
- `rest_en:` a hardened disc of red wax with a brass seal fused into it lies on the oak
- `foley_en:` a soft heavy press into wax, a viscous squeeze around the edge, then a hardening tick and a solid knock
- `negative_today:` letters, a monogram, an emblem or a crest in the wax;
- `hook_ru:` «Так сказала нейросеть» — не оправдание ни перед клиентом, ни в суде.
- `payoff_ru:` Кто нажал «отправить», тот и автор. Введите правило: у каждого AI-результата, ушедшего наружу, есть имя человека, который его проверил.

### 111 · АГЕНТЫ · Три кнопки, которые агент не жмёт никогда

- `verb_ru:` обрастает
- `object_en:` three identical copper levers standing upright in a row on one heavy base, each one polished bright at the top
- `payoff_en:` the first two levers swing down of their own accord and lie flat, and around the third a thick cast-iron brace grows up out of the base and closes over it so that it cannot move at all
- `rest_en:` a base lies on the oak with two levers down and the third locked inside an iron brace
- `foley_en:` two clean mechanical throws, then a low iron growth and one hard clamping stop
- `negative_today:` changing lever count, labels or letters on the levers, a machine;
- `hook_ru:` Есть три действия, которые агент не должен делать сам ни при каких условиях.
- `payoff_ru:` Удаление, оплата и отправка наружу от вашего имени. Всё остальное можно отдать. Эти три — только через человека, даже если агент полгода работал идеально.

### 112 · БИЗНЕС · Метрика до внедрения

- `verb_ru:` усыхает
- `object_en:` a thick squared column of pale rock salt with one dark weathered band running round it at its widest point, the band sharply defined
- `payoff_en:` the whole column draws down and inward, losing height and bulk at a steady rate, while the dark band stays exactly where it was and ends up standing well clear of the shrunken salt
- `rest_en:` a shrunken pale salt column sits on the oak with a dark band standing proud around it
- `foley_en:` a slow gritty contraction with the pitch of the grind rising as it shrinks, then one small dry knock
- `negative_today:` —
- `hook_ru:` Не замерили «до» — доказать эффект уже нечем.
- `payoff_ru:` За неделю до старта запишите три числа: время на операцию, количество операций, число ошибок. Через месяц повторите замер. Это весь отчёт, который от вас потребуют.

### 113 · ЭТИКА · Детям — только с сопровождением

- `verb_ru:` успокаивается
- `object_en:` a small carved wooden rocking horse on curved rockers, rocking hard, the paint worn off its back and mane
- `payoff_en:` the rocking builds up until it is nearly over, and then the curved rockers thicken and flatten out under it into a broad steady base that brings the swing down to nothing
- `rest_en:` a wooden horse stands still on the oak on a broad flat base
- `foley_en:` an accelerating wooden rock knocking harder each pass, then a thickening groan and dead stillness
- `negative_today:` a hand steadying it, a child, a person's hand from above;
- `hook_ru:` Ребёнок поверит уверенному ответу быстрее взрослого.
- `payoff_ru:` Разрешайте как справочник и тренажёр, запрещайте как источник истины и как собеседника наедине. Правило простое: что модель сказала, ребёнок пересказывает вам своими словами.

### 114 · ПРОМПТ · Попросите модель улучшить ваш промпт

- `verb_ru:` перековывается
- `object_en:` a crooked hand-made nail with a lumpy head and a bent shank, the iron scaled and uneven along its length
- `payoff_en:` the shank works itself straight and the lumps travel out of the metal to its ends, the whole nail lengthening and squaring into a clean four-sided spike with a true forged head
- `rest_en:` one clean four-sided iron spike lies straight on the oak
- `foley_en:` a rhythmic muffled forging under no hammer, the ring getting truer with each pass, then a flat iron knock
- `negative_today:` —
- `hook_ru:` Самый недооценённый запрос: «перепиши мой запрос лучше и объясни, что добавил».
- `payoff_ru:` Отдайте черновик промпта и попросите доработать: где не хватает контекста, что двусмысленно. Получите и лучший промпт, и понимание, чего вы вечно не дописываете.

### 115 · АВТОМАТИЗАЦИЯ · Считайте окупаемость временем

- `verb_ru:` истощается
- `object_en:` an hourglass in a heavy iron cradle with a big charge of pale sand in the upper bulb, the waist very narrow
- `payoff_en:` the whole upper charge runs away steadily until the top bulb is completely empty, but in the lower bulb only a thin useless layer has collected, nowhere near the volume that went in
- `rest_en:` an hourglass lies on the oak with its top bulb empty and only a thin layer in the bottom
- `foley_en:` a long steady sand whisper running far longer than it should, thinning out, then one hollow iron knock
- `negative_today:` —
- `hook_ru:` Автоматизация, которую вы чинили три вечера, экономит пять минут в неделю.
- `payoff_ru:` Прежде чем строить, посчитайте: часы на настройку против сэкономленных часов за квартал. Не сходится — оставьте руками. Это честный ответ, а не поражение.

### 116 · ИНСТРУМЕНТЫ · Подключите ассистента к своим данным

- `verb_ru:` подпитывается
- `object_en:` a dry unglazed clay bowl with a short sealed stem below it, the clay chalk-pale and dusty
- `payoff_en:` the stem opens and unrolls into a long thin tube that curls out across the wood and back on itself, and dark water climbs the tube against gravity and rises into the bowl until it is full
- `rest_en:` a clay bowl full of dark water sits on the oak on its own coiled tube
- `foley_en:` a dry clay crack opening, a hollow drawing suck climbing the tube, then a filling gurgle and a wet settle
- `negative_today:` the tube entering the table, roots in the wood, a pump;
- `hook_ru:` Ассистент становится полезным в тот день, когда видит вашу почту и календарь.
- `payoff_ru:` Начните с одного подключения — календаря или диска — и одной задачи на нём, с минимальными правами. Разница между «умным собеседником» и помощником именно здесь.

### 117 · ПРОЦЕСС · Считайте время до готового

- `verb_ru:` расходуется
- `object_en:` one thick tallow candle standing unlit beside twenty short wooden splints bound in a bundle, all hovering as one group
- `payoff_en:` the twenty splints crumble away one after another in a fast run, and by the time the last of them is gone the tallow candle has worn down to exactly the same nothing in exactly the same time
- `rest_en:` a heap of splint dust and one worn candle stub lie together on the oak
- `foley_en:` a rapid run of small dry snaps over one slow continuous waxy erosion, both ending on the same beat
- `negative_today:` flame, fire, a lit wick, sparks, smoke, changing splint count;
- `hook_ru:` Двадцать быстрых генераций хуже двух продуманных.
- `payoff_ru:` Меряйте не число попыток, а время от задачи до готового результата. Часто выгоднее потратить десять минут на промпт, чем час на переборы.

### 118 · ГЕНЕРАЦИЯ · Липсинк на русском — лотерея

- `verb_ru:` заглушается
- `object_en:` a small brass bell hanging mouth-down with its clapper visible inside, the bronze polished bright along one side
- `payoff_en:` brass flows across the open mouth of the bell from the rim inward and closes it completely, sealing the clapper inside a solid dome with no opening left anywhere on it
- `rest_en:` a solid sealed brass dome with no opening in it lies on the oak
- `foley_en:` one bright ring cut off as the mouth closes, a low metallic flow, then a dead unresonant knock
- `negative_today:` a mask, a face, lips, a mouth, teeth;
- `hook_ru:` Говорящий герой на русском — самый быстрый способ получить брак.
- `payoff_ru:` Либо молчаливый кадр и текст в описании, либо готовая озвучка отдельным файлом. Просить модель говорить по-русски в ответственном ролике — риск, который не окупается.

### 119 · КАРЬЕРА · Наставник плюс модель

- `verb_ru:` обвивает
- `object_en:` a young green vine coiling loosely in the air beside a plain straight iron stake, its tendrils reaching at nothing
- `payoff_en:` the vine finds the stake and winds up it in a tight even spiral, turn after turn, thickening as it climbs and putting out leaves it plainly could not have carried on its own
- `rest_en:` an iron stake lies on the oak wrapped in a thick spiralling leafed vine
- `foley_en:` a soft fibrous creeping with small grips catching one after another, then a leafy settle and a metal knock
- `negative_today:` —
- `hook_ru:` Модель отвечает на вопросы. Человек говорит, какие вопросы задавать.
- `payoff_ru:` Используйте ассистента для скорости, а человека — для направления. Час с практиком раз в две недели плюс ежедневная практика с моделью — самая быстрая связка.

### 120 · МИФЫ · «AI объективен»

- `verb_ru:` искривляется
- `object_en:` a flat sheet of clear optical glass with perfectly parallel faces, one clean bright edge where the beam enters it
- `payoff_en:` the glass thickens unevenly, swelling on one side and thinning on the other, and the beam passing through it bends steadily further and further off its true line to that same side
- `rest_en:` a wedge of clear glass lies on the oak with the beam through it thrown well off line
- `foley_en:` a low glassy flow with a rising strain in it, then one settling optical chime and a flat knock
- `negative_today:` a reflection of the room, a reflection of a person, a camera reflected, rainbow colours, prism spectrum;
- `hook_ru:` Ровный тон и уверенность — это стиль, а не объективность.
- `payoff_ru:` У любого ответа есть источник данных и выбор формулировки. Просите альтернативную точку зрения и аргументы против — тогда получите материал для решения, а не готовое мнение.

---

## 5. Что делать, если блок не подходит

Ничего. Блок используется как есть — это условие безнадзорного запуска. Рантайм не редактирует
поля, не переставляет темы и не «подбирает похожее».

Единственное исключение — **два подряд провалившихся приёмочных теста видео** (лимит из
`RUNBOOK.md` §6). В этом случае день закрывается без публикации и без третьей генерации; тема
**не подменяется в тот же день**. Подмена делается только руками, на следующий день, и по формуле
для нумерации с единицы:

```python
substitute = ((topic_no - 1 + 60) % 120) + 1
```

Строка `n + 60` гарантированно из другой полосы и с другим глаголом (§3). *Прежняя версия файла
использовала `(topic_no + 60) mod 120`, что для `topic_no = 60` даёт несуществующую строку 000.*

Тема пропущенного дня возвращается в следующем круге автоматически — формула её всё равно вычислит.

---

## 6. Как редактировать банк

Правка — только вручную, целым блоком, и всегда с повторной проверкой:

1. Полоса блока меняться не должна, иначе ломается чередование (§3).
2. Прогнать блок по списку аудита из §2 — все восемь пунктов.
3. Проверить окно 21 строки на `verb_ru` и на опорное существительное `object_en`, циклически.
4. `payoff_en` пишется законченным предложением с собственным подлежащим и личным глаголом:
   он подставляется в бит `05.2-07.0` перед фразой о темпе.
5. `rest_en` пишется статичной фразой **без глагола движения**: он подставляется после
   «Gravity has returned.» и не должен спорить с уже описанным приземлением.
6. Обновить дату аудита в заголовке файла.
