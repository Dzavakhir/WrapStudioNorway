# TEMPLATE.md — «Один предмет» · daily Seedance 2.5 prompt architecture

Format: **«Один предмет» / ONE OBJECT** · Онно AI Academy
Model: `seedance_2_5` on ONNO · one generation · 10.00 s · 9:16 · unattended, 04:00 daily.
**Version 2.0 · 2026-08-15.** This file is the single normative source for prompt text and for the
`generate_video` parameter block. `brand/style-bible.md` states the reasons; it stores no prompt
strings. `RUNBOOK.md` owns the runtime procedure. If those files ever disagree with this one about a
literal string or a parameter value, **this file wins** and the other is a bug.

---

## 0. Hard contract — read before touching anything below

1. **Everything in `## 2. THE TEMPLATE` is literal and locked** except the six `{{SLOTS}}`. Locked text is not a draft. It is not "a starting point". It is the format. Do not reword it, do not "improve" it, do not shorten it to save tokens.
2. **Four slots carry the day's content, two carry the negative.** `{{OBJECT}}`, `{{PAYOFF}}`, `{{PAYOFF_REST}}`, `{{FOLEY}}` come from the day's topic block, already in English. `{{NEGATIVE}}` and `{{NEGATIVE_TODAY}}` come from `prompts/negative.txt` and from the day's topic block. Nothing else is substituted, nothing is translated at runtime, nothing is invented at runtime.
3. **The prompt is English. The caption is Russian.** Always. No exceptions, no mixing. Russian text never enters `params.prompt` — Cyrillic in the prompt is the fastest route to garbled Cyrillic burned into the frame.
4. **The face comes from the element token and from nothing else.** `<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>` is embedded literally inside `params.prompt`. It is **not** passed in `medias`. Never write a facial description on top of it — the model averages the photo against the words and you lose the likeness. The one permitted sentence about his appearance is in the SUBJECT block and is not extended.
5. **The negative block is not stored here.** It lives in `prompts/negative.txt`, one source of truth, appended verbatim at assembly time (§5). Never retype it, never paraphrase it inline. `seedance_2_5` on ONNO exposes no `negative_prompt` field, so the negative rides as a trailing block inside the prompt string.
6. **Prompt text, timeline, negative list and parameter block are ONE versioned unit.** Change any one of them and re-derive the other three in the same pass. A stale negative silently fights the positive prompt and is close to undiagnosable from the output.

---

## 1. Slot table

| Slot | Reaches model | Language | What it is | Length |
|---|---|---|---|---|
| `{{OBJECT}}` | yes | EN | **The object of the day.** One real physical thing a hand could pick up, authored in English in the topic bank. Never a screen, a device, or anything carrying a readable mark. Carries at least three concrete material facts: substance, surface, and one specific detail. | 12–22 words |
| `{{PAYOFF}}` | yes | EN | **The body of the transformation**, dropped into the 1.8 s beat `05.2-07.0` — the longest and fastest beat in the film. Present tense, one physical process, obeying weight, light and dust. Impossible in fact, coherent in physics. Must read as a *continuing* action, not a completed one. | 15–28 words |
| `{{PAYOFF_REST}}` | yes | EN | **The end state**, one static clause: what is lying on the oak at 08.0. No verb of motion, no "then", no "and now". Without it the model leaves the landing ambiguous and the beat dissolves. | 6–14 words |
| `{{FOLEY}}` | yes | EN | **The sound of the transformation only.** Dry, close, no music under it. The single variable sound of the day. | 8–18 words |
| `{{NEGATIVE}}` | yes | EN | `flatten(prompts/negative.txt)`. Never hand-typed. | ~600 words |
| `{{NEGATIVE_TODAY}}` | yes | EN | Per-day situational negatives from the topic block. **Usually the empty string.** Present for the days whose object has a countable feature or a plausible wrong reading. Appended after the standing list with its own `;`. | 0–25 words |

Metadata fields in the topic block that **never reach the model**: `lane`, `topic_ru`, `verb_ru`
(the 21-day registry), `hook_ru` and `payoff_ru` (the caption).

### Slot authoring rules — these govern editing the topic bank, never runtime

Runtime substitutes and does not judge. The rules below apply when a human edits a topic block.

- **Verb registry.** `verb_ru` may not repeat inside a window of 21 rows in cycle order, including across the 120→001 wrap. The head noun of `{{OBJECT}}` obeys the same 21-row window. This is the single defence against the format going stale.
- **One hovering thing.** A matched pair or a small bound set counts as one thing only if it hovers and rotates as a single unit and `{{OBJECT}}` names it as one.
- **Nothing arrives.** `{{PAYOFF}}` transforms the thing already in the shaft. Nothing new enters the shaft, nothing enters frame from outside, no hand or tool arrives from anywhere. If the idea needs a second thing, the second thing must *come out of* the first.
- **It always lands.** By 08.9 whatever the object has become is lying on the oak — one piece or several, but all of it resting. An idea that ends with nothing on the table, with the object gone, or with anything still airborne is not usable in this format.
- **No fire, no flame, no ember, no glow.** A flame is a second light source and the LIGHT block forbids one.
- **No text-bearing objects.** No books with legible spines, no labelled jars, no clock faces with numerals, no signs, no engraved marks, no keyboards.
- **No fine finger work.** The hand never touches the object. Nothing hinges on individual fingers.
- **No damage to the room.** The tabletop is never pierced, notched, burned, grown into or worn through; the ROOM block and the negative both hold it rigid.
- **Silhouette legibility.** The change must be visible in outline at a 240 px preview width. A change of surface texture alone does not qualify.

---

## 2. THE TEMPLATE

Everything below is the literal prompt body. Slots in `{{DOUBLE_BRACES}}`. Blocks in this order,
always — format before identity, identity before world, everything static before TIMELINE, STYLE
last, NEGATIVE trailing.

```text
VERTICAL 9:16 video, 1080x1920, portrait orientation for the entire film. ONE CONTINUOUS 10-SECOND TAKE. One shot, one locked camera, no cut, no transition, no fade and no dissolve at any point. 50mm lens in portrait orientation, vertical field of view about forty degrees, moderately shallow depth of field. NO dialogue, NO speech, NO voice-over, NO singing, NO humming, NO lip movement and NO mouth opening at any point — his mouth stays closed for the entire ten seconds. NO text of any kind anywhere in frame: no letters, no numbers, no captions, no subtitles, no logo, no watermark, no timestamp. No screen, monitor, laptop, phone or device of any kind ever appears. There is no camera, no tripod, no light stand, no microphone and no other piece of equipment anywhere in the room or on the table.

SUBJECT — <<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>> stands behind the table, centred, facing camera, shoulders in the light, his face half in the light and half in shadow but always clearly readable. Do not restyle, beautify or re-describe his face; it comes from the reference. Plain black crew-neck sweater in matte fine-knit wool, sleeves down to the wrist, no logo, no print, no pattern, no zip, no buttons, no visible collar, no watch, no ring, no bracelet, no glasses. His expression is neutral and unimpressed for the entire ten seconds: he never smiles, never raises an eyebrow, never nods, never widens his eyes, never reacts in any way to what happens on the table. Only his RIGHT hand acts, and only in the one beat where the timeline says so. His left arm hangs straight down at his side, motionless, in shadow outside the shaft, for the whole film. He never speaks, never opens his mouth, never leans in and never turns away.

ROOM — A bare empty room with rough dark plaster walls falling away into soft neutral black about three metres behind him. No furniture, no window in frame, no door, no decoration, nothing on the walls, nothing on the floor. One heavy dark oak table, matte and unvarnished, deeply grained, standing between him and the camera: its near edge crosses the frame low, at about eight percent of the frame height, and the far edge of the tabletop reads as the line where wood meets darkness at about twenty-seven percent of the frame height.

LIGHT — ONE single hard shaft of daylight entering from high camera-left at about forty degrees, cutting diagonally across the frame and lighting dense airborne dust along its whole length. There is no second light source anywhere in the room, no lamp, no flame, no ember, no glowing object. Everything outside the shaft falls away into deep neutral black. Bone-white light at the source, warming to amber inside the shaft itself. High contrast, hard-edged beam, deep true blacks, no lift, no fill, no bounce. This is a DARK frame with one bright beam in it: NOT a bright room, NOT flat, NOT evenly lit, NOT overcast, NOT a softbox, NOT a warm golden-hour wash across the whole frame — the amber lives inside the shaft only and nowhere else.

OBJECT — {{OBJECT}}, hovering exactly two centimetres above the tabletop, dead centre in the shaft, rotating slowly and steadily, one revolution every six seconds. It is a real solid physical thing with real weight and real inertia, casting a soft contact shadow on the wood directly below it. The shaft rakes across it and it is the brightest thing in the frame; he is the second brightest and everything else is black. That contrast is the whole point of the shot. Nothing else is in the shaft. Nothing else is on the table.

FOREGROUND — A few individual dust motes drift through the shaft close to the lens, large and far out of focus, as soft bright specks in the lower half of the frame.

CAMERA — The framing is fixed and never changes. Nobody is holding the viewpoint, nobody is behind it, nothing in the room supports it or moves it, and no camera object exists anywhere in the scene. From the first frame to the last the framing is completely LOCKED: no pan, no tilt, no zoom, no dolly, no push in, no pull back, no drift, no float, no sway, no wobble, no orbit, no crane, no handheld motion, no micro-shake, no rack focus, no reframe — not for a single frame, not by one pixel. The viewpoint sits 1.05 metres above the floor, twenty-seven centimetres above the tabletop, level, looking straight at him along the length of the table. Only three things in this film move: the object, the dust, and his right hand in its one beat. Everything else is still.

SCALE — The object stands about one fifth of the frame height: its base sits at about twenty-two percent of the frame height and its top reaches about forty-two percent, dead centre horizontally. He stands about a metre and a half behind it; his shoulders cross the frame at about seventy-two percent and the top of his head at about eighty-four percent, with dark air above him. The middle of the frame is empty black between the object and his chest. Whatever the object is that day it is scaled to those marks: a matchstick is not rendered life-size and a stack of paper is not rendered monumental.

TIMELINE — follow exactly, in this order, and do not reorder, compress, rush or skip any beat. Every beat below is load-bearing.
00.0-01.4  Locked frame. The object hovers two centimetres above the wood and turns slowly. He is completely still, looking down at it, mouth closed, face neutral. Nothing else in the entire frame moves except the dust in the shaft.
01.4-02.6  He raises ONLY HIS EYES to the lens. His head does not turn, his chin does not lift, his shoulders do not move, his mouth stays closed. He holds the look for the full beat.
02.6-03.7  His right hand rises into the shaft from the lower edge of frame and comes to rest open, palm DOWN, FINGERS TOGETHER and straight, held flat about fifteen centimetres above the object, and from there it stays perfectly still for the rest of the beat. His eyes drop back down to the object as the hand arrives. The hand never touches the object.
03.7-04.2  The wrist turns over exactly once, palm down to palm up, one smooth continuous move. The hand does not grab, does not point, does not touch the object.
04.2-04.6  EVERYTHING STOPS. The object freezes mid-rotation and hangs dead still. His right hand lowers straight back out of the bottom of frame and is gone. The frame is clean and completely motionless for the whole beat.
04.6-05.2  The change begins. The first visible movement appears on the surface of the object — slow, small, barely more than a shiver — and the object does not leave its place.
05.2-07.0  The change continues: {{PAYOFF}}. This is the main body of the change and the fastest part of the film; it must fill this entire beat and must NOT be finished before 07.0. As it happens a radial wave rolls outward through the dust in the shaft away from the object, the dust nearest the lens flares and is pushed aside, and a fine wash of dust lifts off the tabletop below.
07.0-08.9  The change is complete. The object descends the last two centimetres and comes to rest on the table with its real weight; it does not bounce, does not roll and does not slide. Gravity has returned and, at the end of the beat, {{PAYOFF_REST}}. The dust settles back down through the shaft. He has not moved once during the whole change and does not move now.
08.9-10.0  He raises his eyes to the lens a second and final time and holds. His head does not turn, his expression does not change, his mouth stays closed. This look must fill the entire final beat and must NOT be finished or broken before the clip ends. The shot is still live on the last frame: it does not fade, does not darken and does not resolve.

AUDIO — Sound design only. There is no speech anywhere in this film.
00.0-02.6  <the room tone of a large empty stone room, one quiet low sustained drone, and a thin glassy overtone from the hovering object drifting slightly in pitch as it turns>
02.6-04.2  <cloth and skin as the arm rises, the drone thickening very slightly, the object's overtone climbing in pitch>
04.2-04.6  The audio is COMPLETELY SILENT for this window. Every element cuts out instantly at 04.2 and nothing at all plays until 04.6. This is a hard cut in the sound, not a fade, and the gap is not filled with anything.
04.6-08.9  <{{FOLEY}} — dry, close, no music underneath, ending with the weight of the object settling onto solid oak>
08.9-10.0  <the room tone returns, the drone returns an octave lower and wider, dust settling; the sound is still running at 10.0 and does not fade out>
No music at any point. No beat, no melody, no score, no trending track. No voice, no breath, no vocalisation of any kind from him.

STYLE — Photoreal live action. Chiaroscuro, single-source, high contrast, deep neutral blacks, bone-white key warming to amber inside the shaft, fine true sensor grain, 50mm portrait framing, moderately shallow depth of field with the focus on the object and his face still clearly readable, real skin texture with visible pores. Calm, still, deadpan, unhurried. Live action, not animated, not stylised, not a 3D render, not a game cinematic.

NEGATIVE — {{NEGATIVE}} {{NEGATIVE_TODAY}}
```

---

## 3. Why each block is where it is

| Block | Why it exists / why here |
|---|---|
| Header, unlabelled | Format triple-lock: format word + ratio + pixel dimensions + the word *orientation* + *for the entire film*. Stated first because a format stated late gets ignored. Take-length, lens and the global prohibitions ride here too, and every one of them is repeated in the negative — belt and braces. |
| SUBJECT before ROOM | Identity is bound before the model starts inventing a world to put him in. |
| Identity clause, one sentence, no face description | House rule. The element supplies the face; words on top of it make the model average. Only wardrobe, behaviour and hand allocation come from text. |
| Hand allocation named explicitly | Right hand acts, left arm parked and named as motionless. An unassigned hand grows a third arm. |
| LIGHT as its own block, with inline NOTs | A colour-temperature word with no exposure anchor renders as a murky dusk. The `NOT bright / NOT flat / NOT evenly lit` line and the exposure anchor sit in the same block, next to each other. |
| OBJECT with a category assertion and the brightness intent line | A large under-described thing gets completed by the model's favourite guess. Three material facts, the real-weight/contact-shadow assertion, and the sentence that says why the contrast matters — an intent line is respected more reliably than a number alone. |
| CAMERA as its own block, with no camera in it | Camera behaviour is the thing most likely to be overridden by the model's cinematic priors, so the forbidden moves are enumerated one by one and the *closed list of what may move* does the rest. The lock is deliberately **not** motivated by a physical camera object: naming the viewpoint device as a noun in the scene is the documented way to make the model draw it. |
| SCALE with fractions and an intent line | Scale is never an adjective. Every number here is derived from the geometry in `style-bible.md` §2 and they are mutually consistent. |
| TIMELINE with an enforcement clause | Without `do not reorder, compress, rush or skip`, the model reorders and crushes the payoff into the last half-second. |
| Nothing-happens beats written explicitly | `04.2-04.6` and the second half of `07.0-08.9` are written out because unwritten pauses get filled. |
| The payoff in the 1.8 s beat, not the 0.6 s beat | `04.6-05.2` carries a locked generic *onset* sentence; the day's transformation goes in `05.2-07.0` with an explicit non-completion clause. Putting 25 words of transformation into a 0.6 s beat is an instruction to finish it in 600 ms, which is the documented way to get a crushed payoff. |
| Three responders per force event | The transformation moves the dust in the shaft (mid), the dust at the lens (near) and the dust on the tabletop (ground plane). One responder reads as fake; three read as physical. |
| Terminal beat with a non-completion clause and no cut | `must NOT be finished or broken before the clip ends`, and the last frame is still live. The cut to black is an **edit** instruction and lives in `RUNBOOK.md`, not in a prompt — asking a 10.000 s generation to "cut to black at 10.0" gets you baked black tail frames. |
| AUDIO bracket taxonomy | `<…>` marks sound effects. `(…)` music, `{…}` dialogue and `【…】` on-screen subtitle are **never used in this format** — do not introduce them, they will be rendered as what they mean. The 0.4 s silence is deliberately written as plain prose *outside* any bracket, because an absence placed inside a sound-effect tag gets rendered as an event. |
| STYLE last | Grade words placed earlier contaminate the action parsing. |
| NEGATIVE trailing | ONNO's `seedance_2_5` exposes no negative field. The list rides inside the prompt string. |

### Two conventions deliberately overridden, so nobody "fixes" them later

- **ONNO's UGC anti-cinematic bans do not apply here.** The house UGC rules ban `cinematic grade`, `film grain`, `shallow depth of field` and `chiaroscuro`-adjacent language because they are written for a phone-shot creator register. This format is cinematic by design. The only thing kept from that ruleset is the anti-plastic-skin clause, which is in the negative.
- **The warm-light ban is scoped, not dropped.** `golden hour / warm wash / amber cast` is banned as a *global grade*. Amber inside the shaft is the format's signature. The LIGHT block says both halves in the same breath so they cannot be confused.

---

## 4. Beat-compression fallback

Nine beats in ten seconds is already the compressed form — the palm-hold and the dust-settle beats
were merged into their neighbours in v2.0 rather than shipped as separate sub-0.5 s beats. If a
render still comes back with the payoff crushed or a beat dropped, there is exactly **one**
remaining merge, and it is applied by editing this file, not at runtime:

1. Shorten `00.0-01.4` to `00.0-01.0` and give the 0.4 s to `05.2-07.0`.

**Never touch:** the 0.4 s silence at `04.2-04.6`, the transformation body `04.6-08.9`, or the second
look `08.9-10.0`. Those three are the film.

Do not fix a crushed payoff by editing — regenerate, once, inside the day's retry cap. There is
nothing in post to fix it with.

---

## 5. Assembly — how the final prompt string is built

```
prompt = TEMPLATE_BODY
           .replace("{{OBJECT}}",         topic.object_en)
           .replace("{{PAYOFF}}",         topic.payoff_en)
           .replace("{{PAYOFF_REST}}",    topic.rest_en)
           .replace("{{FOLEY}}",          topic.foley_en)
           .replace("{{NEGATIVE}}",       flatten(read("prompts/negative.txt")))
           .replace("{{NEGATIVE_TODAY}}", topic.negative_today)   # "" on most days
```

`flatten()` is deterministic and is the **only** transform applied to `negative.txt`:

1. Drop every line whose first non-space character is `#`.
2. Drop empty lines.
3. Join the remaining lines with a single space.
4. Collapse runs of whitespace to one space, strip the ends.

Semicolons in `negative.txt` are the category separators in the flattened string — they survive, the
`#` labels do not. `negative_today`, when non-empty, is written in the topic block already terminated
with `;`.

**Pre-flight assertions the runner must make on the assembled string, and fail loudly on:**

- `<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>` appears exactly once.
- No `{{` and no `}}` remain anywhere.
- No Cyrillic character appears anywhere in the string.
- The standing portion of the negative is byte-identical to `flatten(negative.txt)` — never a hand-typed copy.
- Neither `(`…`)`, `{`…`}` nor `【`…`】` is used as an audio bracket; only `<`…`>`.
- Total assembled length is between 14 000 and 17 000 characters. Outside that band something was substituted wrong. (Measured on topic 108: 15 262 characters, of which 5 668 are the flattened negative.)

---

## 6. WORKED EXAMPLE — Sunday 2026-08-16, topic 108, lane АГЕНТЫ

This is the reference rendering. A day's output that does not look structurally like this is wrong.

### 6.1 Daily variables (copied from the topic block, nothing computed)

```json
{
  "date": "2026-08-16",
  "topic_no": 108,
  "lane": "АГЕНТЫ",
  "topic_ru": "Планировщик и исполнитель",
  "verb_ru": "раздваивается",
  "object_en": "a heavy grey river stone the size of a fist, dry and matte, one flat facet worn smooth across its top",
  "payoff_en": "a hairline seam opens around the stone and it draws apart into two unequal halves that hang side by side, the smaller one thinning into a fine pale outline of the larger",
  "rest_en": "a solid grey stone and a thin hollow shell of the same shape lie side by side on the oak",
  "foley_en": "a dry granular split, one low grinding parting of stone, settling into two separate dull knocks on wood",
  "negative_today": "changing stone count, three stones, the halves merging back together, gravel, rubble;",
  "hook_ru": "Один думает, другой делает — и оба работают лучше.",
  "payoff_ru": "Разделите на два шага: сначала план в виде списка действий, вы его смотрите, потом выполнение по утверждённому плану. Половина плохих действий отсеивается на плане бесплатно."
}
```

`verb_ru` goes to the 21-day registry. `topic_ru`, `hook_ru` and `payoff_ru` go to the post caption.
None of the four reaches the model.

### 6.2 The three lines that change

Everything else in §2 renders byte-identical every day. These are the only lines that differ:

```text
OBJECT — a heavy grey river stone the size of a fist, dry and matte, one flat facet worn smooth across its top, hovering exactly two centimetres above the tabletop, dead centre in the shaft, rotating slowly and steadily, one revolution every six seconds. …

05.2-07.0  The change continues: a hairline seam opens around the stone and it draws apart into two unequal halves that hang side by side, the smaller one thinning as it goes into a fine pale shell of the larger. This is the main body of the change and the fastest part of the film; it must fill this entire beat and must NOT be finished before 07.0. …

07.0-08.9  The change is complete. The object descends the last two centimetres and comes to rest on the table with its real weight; it does not bounce, does not roll and does not slide. Gravity has returned and, at the end of the beat, a solid grey stone and a thin hollow shell of the same shape lie side by side on the oak. The dust settles back down through the shaft. …

04.6-08.9  <a dry granular split, one low grinding parting of stone, settling into two separate dull knocks on wood — dry, close, no music underneath, ending with the weight of the object settling onto solid oak>

NEGATIVE — speech, dialogue, talking, … [ flatten(negative.txt) in full ] … changing stone count, three stones, the halves merging back together, gravel, rubble;
```

> **The abbreviation of the negative above is a documentation convenience and nothing else.** At
> runtime `{{NEGATIVE}}` is filled by `flatten(negative.txt)` in full. Nobody ever types the negative
> by hand — that is exactly how a negative goes stale and starts fighting the positive prompt.

### 6.3 Note on grammar

Two things make the substituted beats grammatical without any runtime string surgery, and both are
authoring rules on the topic bank rather than runtime logic:

- **`payoff_en` and `rest_en` are written lower-case, with no terminating full stop.** The template
  supplies the capital and the full stop around them — `The change continues: {{PAYOFF}}.` and
  `Gravity has returned and, at the end of the beat, {{PAYOFF_REST}}.` A field that arrives already
  capitalised or already punctuated produces a visible seam.
- **`payoff_en` is a complete clause with its own subject and finite verb; `rest_en` is a static
  clause with no verb of motion.** `rest_en` lands *after* the descent has been described, so a verb
  of motion in it would contradict the sentence in front of it.

v1.0 shipped a dangling `{{PAYOFF}} begins.` construction that rendered as a run-on every single
day, on the most load-bearing beat in the film, and rationalised it as harmless. It was not. There
is no such construction left anywhere in this template.

---

## 7. Exact `generate_video` parameters

```json
{
  "model": "seedance_2_5",
  "params": {
    "mode": "omni_reference",
    "prompt": "<the assembled string from §5 — element token inline, negative appended>",
    "duration": 10,
    "resolution": "1080p",
    "aspect_ratio": "9:16",
    "generate_audio": true,
    "bitrate_mode": "high",
    "use_unlim": "<decided at runtime by RUNBOOK.md §6 — always a literal true or false, never omitted>"
  }
}
```

There is **no `medias` key.** It is absent on purpose — see the `medias` row below.

| Param | Value | Why, and what must never change |
|---|---|---|
| `model` | `seedance_2_5` | Locked. |
| `mode` | `omni_reference` | The element is a character reference. **There is no fallback.** If the backend rejects `omni_reference`, the run aborts and logs `MODE_REJECTED`; it does not silently retry in `t2v`, because whether the element token binds in `t2v` is unverified and the failure mode is publishing a stranger's face under the founder's brand. Promoting a `t2v` fallback requires one daylight test and a documented result. |
| `duration` | `10` | Locked at exactly 10. The TIMELINE is written to the tenth of a second against this number. Changing duration invalidates the timeline; re-derive both together or not at all. |
| `resolution` | `1080p` | **Measured 2026-08-15:** 10 s at `1080p` = **90 credits**, at `720p` = **65 credits**. 1080×1920 is the delivery standard and 720p gets visibly re-compressed by the feeds, so the 25-credit premium buys delivery conformance. `720p` is the documented austerity lever if the balance gets tight (see `README.md`). |
| `aspect_ratio` | `9:16` | Passed explicitly. **Never `auto`.** |
| `generate_audio` | `true` | The model supplies the foley, the drone and the silence. Mouth motion is coupled to voice in this model, so *no voice + no mouth movement* is the internally consistent pair — which is exactly what this format asks for. |
| `bitrate_mode` | `high` | Not a nice-to-have. The frame is dark with grain and dust in a beam; `standard` bands it visibly. **Measured 2026-08-15: credit-neutral** — `standard` and `high` both quote 90 credits at 1080p. Settled, do not re-check. |
| `use_unlim` | **runtime** — `true` or `false`, never omitted | **Owned by `RUNBOOK.md` §6, not by this file.** Every run first asks `models_explore(action="get", model_id="seedance_2_5")` whether an unlim allowance covers the model today: yes → `true` and the generation is free, which is the owner's stated intent. No → the `config.json` spend gate decides between paying credits (`false`) and reporting without generating. **Omitting the field is the one thing that is always wrong** — the server then returns an interactive `unlim_choice` question instead of generating, which is fatal at 04:00. That is why the branch resolves to a literal boolean *before* the call rather than being left to the server. Measured 2026-08-15: `seedance_2_5` carries no `supports_unlim` flag and the account allowance reads `{available:false}`. |
| `medias` | **absent** | The element is not a media (see below), and the daily `start_image` QC gate was **removed in v2.0**: whether `omni_reference` accepts a `start_image` alongside an inline element token is unverified, it doubles the number of generations that can fail at 04:00, and its pass/fail criteria were vision judgements no unattended run can make. Room consistency is carried instead by byte-identical locked blocks. Reinstating the gate requires a daylight test and a written spec. |

**Not in `params`:** the element. `<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>` lives inside
`params.prompt` and is never passed in `medias`. The backend swaps in the image and rewrites the
token to `@Javokhir`.

**Always preflight with `get_cost: true`** before the real submission and compare the quote against
the ceiling in `RUNBOOK.md` §6 (95 credits per job, 190 credits per day). Above the ceiling the run
logs and exits without spending.

---

## 8. Acceptance tests

The single test table lives in `RUNBOOK.md` §9. It is not duplicated here, because two copies of a
test table is how two thresholds for the same test come to exist. Every test there is numeric,
runnable by `ffmpeg`/`ffprobe`, and tied to a load-bearing claim in §2.

---

## 9. Change discipline

- Anything in §2 that is not a `{{SLOT}}` changes **only** with an explicit human decision, and when it changes, §4 (trim priority), `prompts/negative.txt`, §7 (params) and `RUNBOOK.md` §9 (tests) are re-derived in the same commit.
- **Closed decision — his hair is never described.** The prompt says nothing about hair length, colour, texture or hairline; it comes from the element like the rest of the face. The reference repo's rule that "hair length is the one physical attribute text may fix" was written for a workflow with no persistent element; here the element carries it, and a guessed hair clause would fight the reference every single day. The hair-drift tokens in `negative.txt` category 06 stay — they defend against *change within one clip*, which does not require a stated value. If a human ever visually confirms the hair from the element image, one clause may be added to SUBJECT and locked; until then this is settled, not open.
- **Corrections applied in v2.0, recorded so they are not reverted:**
  1. The camera is no longer a physical object standing on the table. Naming the viewpoint device as a noun in the scene is the documented way to make the model draw it, and it contradicted both "nothing else is on the table" and the negative.
  2. The day's transformation moved out of the 0.6 s beat and into the 1.8 s beat, with a non-completion clause.
  3. `HOOK` was deleted as a slot: the salience mechanism is locked ("the shaft rakes across it and it is the brightest thing in the frame"), so only the material differed, and that already lives in `{{OBJECT}}`.
  4. The whole geometry (camera height, table lines, object marks, his position) was recomputed so that the numbers in §2 and in `style-bible.md` §2 are one consistent solution rather than two guesses.
  5. `Hard cut at 10.0` was removed from the prompt and moved to the assembly step in `RUNBOOK.md`.
  6. Wardrobe resolved to **matte fine-knit wool** (was "cotton knit" here, "wool" in the style bible).
