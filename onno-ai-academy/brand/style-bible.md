# Онно AI Academy — STYLE BIBLE

**Format:** «Один предмет» (One Object) · **Set:** «Комната» (The Room)
**Status:** LOCKED · **Version:** 2.0 · **Locked on:** 2026-08-15
**Scope:** every video the daily 04:00 run produces, day 1 through day 365.

---

## 0. What this file is, and what it is not

This file states the **reasons**. It contains **no prompt strings**, no parameter values a runner
could copy, and no negative list.

That is the single most important change in v2.0. Version 1.0 carried its own copies of the HEADER,
SUBJECT, ROOM, LIGHT, CAMERA, STYLE and NEGATIVE blocks, described them as "LOCKED, copy verbatim",
and they had already drifted away from `prompts/TEMPLATE.md` on eight separate invariants before day
one — wool against cotton, 1.10 m against 1.15 m, a tripod that the negative list banned. Two copies
of a locked string is not redundancy, it is a fork.

| What | Who owns it | Where |
|---|---|---|
| Every literal word of the prompt | **`prompts/TEMPLATE.md` §2** | the only normative copy |
| The negative list | **`prompts/negative.txt`** | the only normative copy |
| The `generate_video` parameter block | **`prompts/TEMPLATE.md` §7** | the only normative copy |
| The runtime procedure, limits, tests, caption, logging | **`RUNBOOK.md`** | the only normative copy |
| The day's object and transformation | **`topics/topic-bank.md`** | the only normative copy |
| Why all of the above is the way it is | **this file** | rationale only |

If this file ever appears to disagree with `TEMPLATE.md` about a fact, `TEMPLATE.md` is right and
this file has a bug. Report it, do not act on it.

**Exactly one thing changes from day to day inside the frame:** the object in the shaft and what it
becomes. Four English fields carry it, and they are authored in advance in `topics/topic-bank.md` —
never composed, translated or improvised at 04:00.

**Change control.** Prompt text, negative text, parameter block, acceptance tests and this file are
ONE versioned unit. Change any one and re-derive the others in the same commit, bump the version and
record the reason. This rule exists because the reference repo
(`/home/user/WrapStudioNorway/seedance-knight-and-dragon/`) shipped a negative list that silently
fought its own positive prompt for a whole generation of work, and it is nearly impossible to
diagnose from the output.

**Language.** All prompt text is **English**, always. Russian exists only in the post caption, never
inside `params.prompt`. Two languages in one prompt degrades Seedance output, and Cyrillic inside a
generation garbles. There is no speech and no on-screen text in this format, so the frame is
language-independent by construction.

---

## 1. THE MAN — identity, and the one rule that outranks every parameter

### 1.1 The element placeholder

His face enters the generation **only** through the reference element
`<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>`. The literal usage is in `TEMPLATE.md` §2; the rules
behind it:

| Rule | Why |
|---|---|
| Exactly once per prompt, at the first mention of the man | A second occurrence is a second identity signal and they compete. |
| It occupies a **proper-noun slot** | The backend rewrites it to `@Javokhir`, so the sentence must still parse with a name in it. Never place it where a name would be ungrammatical. |
| Later mentions are `he` / `his` / `him` | Never repeat the UUID, never write the name in prose. |
| Bare — no quotes, brackets, backticks or spaces inside the angle brackets | Any wrapper breaks the server-side match. Six angle brackets, three each side. |
| **Never in `medias`** | An element image placed in `medias` is a duplicate identity signal and fights the swap-in. `medias` is absent from this format's call entirely (§6). |
| `mode: omni_reference` | The element is a character reference. There is no fallback to `t2v` — see §6. |

Element facts (verified, do not re-check): name `Javokhir`, category `character`, description
`man hero of the video`, workspace `Javokhir`, plan `ultra`.

### 1.2 What the prompt may NEVER say about his face

**The face comes from the image. The prompt describes only what he does.** Writing facial
description on top of a photographic reference makes the model average between the words and the
photo, and you lose the likeness you are paying for. This is stated independently by both source
bodies — the house repo README §11 and Seedance's own character-consistency guidance (*describe what
the character does, not what they look like*) — and it outranks every numeric parameter in this
project.

**BANNED from `params.prompt`, permanently — any word about:**

- age, ethnicity, nationality, "young", "middle-aged"
- eye colour, eye shape, brow shape, nose, lips, mouth shape, jawline, cheekbones, bone structure
- skin tone, complexion, skin condition, "glowing skin", "flawless skin"
- hairline, hair colour, hair texture, hair style, beard, stubble, moustache
- height, build, weight, "handsome", "charismatic", "attractive", "photogenic"
- any identity-lock boilerplate ("reproduce this exact person", "same bone structure as the
  reference", "photographic identity match"). That phrasing belongs to still-image models with no
  persistent element. Here it is redundant at best and drift-inducing at worst.

`TEMPLATE.md` §2 carries **one** sentence about his appearance and it uses none of those words. It
is not extended, softened or supplemented.

**Hair is a closed decision, not an open question.** The prompt says nothing about it. The reference
repo's rule that hair length is the one physical attribute text may fix was written for a workflow
with no persistent element; here the element carries it, and a guessed hair clause would fight the
reference every single day for 365 days. The hair tokens in `negative.txt` category 06 stay: they
ban hair *changing within one clip*, which needs no stated value. See `TEMPLATE.md` §9.

**The permitted behavioural descriptors** (state, not physiognomy): `still`, `neutral`,
`unimpressed`, `looking down at the object`, `raises only his eyes`, `holds`, `has not moved`.

### 1.3 Wardrobe — the continuity carrier

Wardrobe is the one thing the prompt is allowed to over-specify, because the face is not. It is what
a viewer recognises across 365 videos when the face is half in shadow.

**The garment is a plain black crew-neck sweater in matte fine-knit wool.** Wool, not cotton — v1.0
of this file and v1.0 of the template disagreed and wool won, because the reason is the stronger
one: it has no sheen, and in this lighting a shiny black garment blows out along the shaft edge and
destroys the chiaroscuro. Not leather, not satin, not a hoodie, not a turtleneck, not a t-shirt, not
a jacket. No logo, no print, no pattern, no zip, no buttons, no visible collar. No watch, ring,
bracelet, necklace, glasses or earpiece.

Below the table edge nothing is described. Trousers, shoes and belt do not exist in this format.

### 1.4 Performance

**He makes exactly four movements in ten seconds:** eyes up (01.4), right hand up into the shaft
(02.6), wrist turn (03.7), eyes up (08.9). Nothing else. He does not move at all during the
transformation.

- **Expression: neutral and unimpressed throughout. He never smiles.** Not once, not in one frame,
  not in 365 videos. The deadpan is the brand. Hyperbolic register is the standard tone of AI
  content and it burns out in weeks; unimpressed holds for years.
- No nod, no eyebrow raise, no head tilt, no head turn, no shrug, no reaction of any kind to the
  impossible thing happening in front of him.
- **Mouth closed for all ten seconds.** Lip articulation and voice are tightly coupled in this
  model; a moving mouth with no voice is unreliable, so the mouth simply does not move.
- **Hand law:** exactly **one** hand ever acts — the **right** hand, entering the shaft from the
  lower edge of frame, **open, fingers together, palm flat**. The left arm hangs at his side,
  motionless and in shadow, and is named as such so it is not left unassigned: an unassigned or
  spread hand is where extra fingers are born.
- He never touches the object, never picks anything up, never leaves frame, never sits, never walks,
  never looks around.

---

## 2. THE ROOM — geometry, computed once

Every number below is one solution to one set of constraints, and `TEMPLATE.md` §2 states the same
numbers. v1.0 carried three mutually impossible geometries across two files (a lens at tabletop
height that also framed a standing man mid-chest up, a table edge at 72% and at 25% of frame height,
an object 2 cm above the wood floating at 45% of frame height). A prompt whose geometry cannot be
satisfied is resolved differently by the model on every render — which is the one thing a format
built on an identical frame cannot absorb.

**Constraints that had to hold simultaneously:** the whole tabletop visible as a shallow band low in
frame · his head inside the frame with air above it · nothing load-bearing in the top 14% or bottom
20% (platform UI safe areas) · the object reading at one fifth of frame height · the camera axis
level, because a tilt is a camera decision and this format has none.

**The solution, in metres:**

| Element | Value |
|---|---|
| Lens | 50 mm in **portrait orientation** (vertical field of view ≈ 40°, half-angle tan ≈ 0.36) |
| Camera height | **1.05 m** above the floor, axis level, no tilt |
| Tabletop height | 0.78 m — so the lens sits **27 cm above the tabletop** |
| Camera → near table edge | 0.90 m |
| Table depth | 0.70 m — far edge at 1.60 m |
| Camera → object | 1.25 m, hovering **exactly two centimetres** above the tabletop, dead centre of frame width |
| Camera → the man | 2.85 m — he stands 1.25 m behind the far table edge |
| Back wall | ≈ 3 m behind him, unlit, reading as soft black rather than as a surface |

**The frame that produces, as fractions of frame height from the bottom:**

| Feature | Position |
|---|---|
| Near table edge | **8 %** |
| Far edge of the tabletop (wood meets darkness) | **27 %** |
| Object base | **22 %** |
| Object top | **42 %** (the object is **one fifth of frame height**) |
| Empty black air | 42 % – 72 % |
| His shoulders | **72 %** |
| Top of his head | **84 %** — clear of the top-14% UI band |
| He is visible from | mid-thigh up; the table band hides everything below |

**Object scale is a target, not a ceiling.** One fifth of frame height, not one eighth: at a 240 px
preview width the object is the only thing in the frame that changes from day to day, and one eighth
puts it at roughly 50 px of preview height. Whatever the object is that day it is scaled to those
marks — a matchstick is not rendered life-size and a stack of paper is not rendered monumental.

**The intent line stays in the prompt.** *The object is the brightest thing in the frame and he is
the second brightest; that contrast is the whole point of the shot.* An intent sentence is respected
more reliably than a number alone, and this one defends the hook.

**Dust is the signature.** The air in the shaft carries dense visible dust, always. It drifts idly at
rest and **reacts to the transformation with a radial wave rolling outward through the shaft**. This
is the format's answer to the single most common tell of generated video — a world that does not
react to its own event. Every force beat gets responders at three distances: the dust at the lens,
the object at centre, the dust lifting off the tabletop.

---

## 3. THE LIGHT — one rig

1. **One motivated source, named, with a direction and an angle.** "Dramatic lighting" produces
   nothing; "a single hard shaft from high camera-left at forty degrees" produces the shot.
2. **The exposure anchor is mandatory and it points DOWN here.** In a bright format you pin
   "bright / high-key" next to the colour words or the model drifts dark. This format is the
   inverse: it is deliberately dark, so the anchors are `deep true blacks`, `no lift`, `no fill`,
   `no bounce`, `chiaroscuro`, plus the inline `NOT flat, NOT evenly lit, NOT a bright room`. The
   failure mode to defend against is the model *lifting* the room into a normally-exposed interior.
3. **The face must stay readable.** Half-lit, never lost. State it in the positive block; the
   negative list cannot recover a face that fell into black.
4. **No second source.** No practical, no rim, no kicker, no bounce card, no window in frame — and
   **no flame, no ember, no glowing object**, which is why the topic bank has no fire in it. If a
   second light appears in output, regenerate; it cannot be fixed after.
5. **Warm is permitted ONLY inside the shaft**, as the amber of light through dust. There is no
   golden-hour wash, no warm ambient, no orange grade on the room. The LIGHT block states both
   halves in one breath so they cannot be confused, and `negative.txt` category 10 scopes the warm
   ban to the *global grade* for the same reason.
6. **The volumetric beam is wanted.** The negative list deliberately does not contain bare `glow`,
   `haze`, `smoke` or `god rays`: those would suppress the format's own signature. It bans `haze
   outside the shaft`, `fog filling the room` and `bloom around the highlights` instead.

---

## 4. GRADE, LENS, CAMERA, GRAIN

### 4.1 Colour grade

- **Palette: bone-white light · amber inside the shaft · neutral black shadow.** Three values, no
  fourth.
- **Not one blue pixel.** No cyan, no teal, no neon, no hologram glow, no "digital" light. This is
  an AI channel that refuses the entire visual vocabulary of AI channels; that refusal is most of
  the brand.
- Blacks are **neutral and true** — not lifted, not milky, not tinted, not crushed to banding.
- No teal-orange grade, no colour separation between highlight and shadow, no LUT look.
- Saturation is low overall: the only saturated things in the frame are the amber of the shaft and
  whatever colour the object of the day carries.

*Resolved conflict, recorded so it does not get "fixed" later:* the ONNO house UGC workflow bans
`cinematic grade`, `shallow depth of field` and `film grain` outright. Those bans are correct **for
UGC/creator register** and wrong here. This format is not UGC; it is a deadpan studio object film,
and the reference repo's cinematic discipline governs the look. The one UGC ban this format keeps is
the anti-slop half: no beauty-filter smoothing, no waxy skin, no HDR glow/bloom/halos, no
oversharpening.

### 4.2 Lens and depth

- **50 mm in portrait orientation.** Natural perspective, no wide-angle distortion, no fisheye, no
  telephoto compression.
- **Moderately shallow depth of field.** Focus sits on the object and is fixed for the whole take —
  **no rack focus, no focus hunt, no breathing.** He is 1.6 m behind the object and reads softer
  than it, but his face must never be unreadably soft; the back wall goes to nothing. This is not an
  extreme shallow-focus look.

### 4.3 Camera behaviour — the load-bearing decision of the whole format

**The camera never moves. Not for one frame. Not in one video out of 365.**

Three reasons this is locked and not a preference:

1. **Scale and weight read by parallax inside a fixed frame.** A push-in destroys exactly the effect
   it appears to add. This was measured in the reference analysis, not guessed: on the shot that
   works, subject height held within ±5% across ten seconds.
2. **Unmotivated camera movement is the number-one first-second catastrophe in generated video.**
   Removing the camera as a variable removes the failure.
3. **Enumerate the forbidden moves individually, then name the closed list of what may move.**
   "Static camera" alone does not hold; the positive closed list (*only the object, the dust and his
   right hand move*) does more work than all the prohibitions combined.

**The lock is deliberately not motivated by a camera object.** v1.0 of this file said "LOCKED on a
tripod" and v1.0 of the template said the camera "stands on the oak table" — and `negative.txt`
banned both `tripod` and `a camera visible in frame`, while the OBJECT block insisted nothing else
was on the table. Naming the viewpoint device as a noun that exists in the scene is the single
best-documented way to make the model draw it. `TEMPLATE.md` §2 now says there is no camera object
in the room at all, and keeps the enumerated prohibitions and the closed list, which are the parts
that work.

**No cuts inside the generation.** Every cut is a fresh re-entry point for identity drift, and
single-take coherence is precisely what this model is being paid for. This is the one place the
format deliberately departs from the reference repo's three-clip stitch, which was a workaround for
an older model's duration ceiling.

**The hard cut to black at 10.0 is an edit, not a prompt instruction.** Inside a 10.000 s generation
"cut to black at 10.0" has no in-frame referent and the model's available reading is *bake black
tail frames* — which fails the no-fade acceptance test. The prompt says the shot is still live on
the last frame; the cut lives in `RUNBOOK.md` §11.

### 4.4 Grain

**Fine natural grain, present, subtle, film-like.** Deliberate and required: a perfectly clean
near-black frame bands and plastics out, and grain is what makes deep shadow read as photographed
rather than rendered. Directly coupled to the bitrate decision in §6.

**No vignette.** The frame is already dark at the edges by lighting; an added vignette on top reads
as a filter and flattens the shaft's authority.

---

## 5. AUDIO IDENTITY

`generate_audio: true`, always. The model renders the sound bed and the foley; there is never any
post-added score.

### 5.1 Speech — there is none, ever

**No dialogue. No voice-over. No narration. No whisper. No lip movement at any point, in any video,
in any language.** Permanent and non-negotiable, for four reasons, the first two decisive:

1. At 04:00 nobody is awake to catch broken Russian articulation. Russian is one of this model's
   weaker speech languages ("weak, often English-accented") and its voice casting is unpredictable —
   unrequested accents have appeared unprompted. A botched Russian line is worse for the brand than
   no video at all, and it is the only failure that damages the brand directly.
2. Feeds are watched muted. A silent visual demonstration is natively muted-friendly.
3. The film becomes language-independent: Russian caption today, Uzbek or English tomorrow, same
   negative.
4. Nobody learns anything from ten seconds of talking. Everybody remembers an image.

The words live in the post caption, in perfect editable indexable Cyrillic, outside the frame. The
caption is a required daily output and its structure is in `RUNBOOK.md` §10.

### 5.2 The sound bed — fixed shape, one variable

| Window | Sound |
|---|---|
| 00.0–02.6 | Room tone of a large empty stone room. One quiet low sustained drone. A thin glassy overtone from the hovering object, drifting slightly with its rotation. |
| 02.6–04.2 | Cloth and skin as the hand rises. The drone thickens slightly. The object's overtone creeps upward in pitch. |
| **04.2–04.6** | **EVERYTHING OUT. ABSOLUTE SILENCE for 0.40 s. A cut, not a fade.** |
| 04.6–08.9 | **Transformation foley only.** Dry, close, no music underneath. This is the one sound that changes from day to day. |
| 08.9–10.0 | Room tone returns. The drone returns an octave lower and wider. Dust settling. Still running at 10.0. |

**The 0.40 s of absolute silence before the transformation is one of the three things in this
document that may never change.** It is the direct fix for the diagnosed failure of the reference
video, whose loudness rose monotonically for twenty seconds so that its climax landed on an
already-full shelf and did not hit. Silence is the punch.

It is written into the prompt as **plain prose outside any sound-effect bracket**. An absence placed
inside a `<…>` tag invites the model to render it as an event — a swell, a sub drop, a filtered
cut-off. The gap has to be described as nothing playing, not as a sound of nothing.

The room tone of a large stone room is *wanted*, so `negative.txt` category 13 bans only excess:
`cathedral reverb`, `long echo tail`, `reverb tail after the cut`.

### 5.3 Music policy

**No music with a beat, ever. No trending audio, ever.** Owned sound design is an asset; a rented
track is an expense that timestamps the video. The low drone is the only tonal element and it is
part of the room, not a score. If a platform demands a trend, it is layered at publish time
(`tiktok_music_tune`) and is never generated into the file.

---

## 6. TECHNICAL PARAMETERS — the reasons only

**The values live in `TEMPLATE.md` §7 and nowhere else.** This section gives the reason for each and
deliberately prints no copyable block; v1.0 printed one, and printed `use_unlim` as the placeholder
`<explicit true|false>`, which is a type error a runner cannot pass to an API.

| Parameter | Reason |
|---|---|
| **Model** | `seedance_2_5` is the only model on this account that does 10 s in one pass with native audio and an inline element reference. |
| **Mode** | `omni_reference`, because the element is a character reference. **No fallback.** Whether the element token binds in `t2v` is unverified, and the failure mode is publishing a video of a stranger under the founder's brand. A rejection aborts the run. |
| **Aspect ratio** | `9:16`, passed explicitly, never `auto`. Vertical feed is the only delivery surface, and `auto` hands a format decision to the model. Format is triple-locked: parameter + header text + negative. |
| **Resolution** | `1080p`. **Measured 2026-08-15 with `get_cost:true`:** 10 s at 1080p = 90 credits, at 720p = 65. 1080×1920 is the delivery standard and 720p gets visibly re-compressed by the feeds, so the 25-credit premium buys delivery conformance. 720p is the documented austerity lever, not the default. |
| **Duration** | Exactly **10.00 s**. Shortest length that carries anomaly + gesture + payoff, comfortably inside every identity-drift threshold for a real recognisable face, and cost is linear in duration (9 credits/second at 1080p) so it is also the runway decision. |
| **FPS** | Not a parameter — ONNO exposes none for this model. It is a QC constant: whatever the first accepted video returns becomes the library lock. Never re-time, never interpolate, never mix two frame rates across the library. |
| **Bitrate** | `high`. The frame is dark, grainy and full of dust in a beam — exactly the content `standard` destroys with banding. **Measured 2026-08-15: credit-neutral**, 90 credits either way. Settled; do not re-check. |
| **Audio** | `generate_audio: true`. The drone, the foley and — critically — the 0.40 s silence are all generated in-pass; there is no post audio stage. |
| **`use_unlim`** | `false`, unconditionally, on every call, with no runtime branch. Omitting it makes the server return an interactive `unlim_choice` question instead of generating, which is instantly fatal at 04:00. `seedance_2_5` carries no unlim support and the account allowance is `{available:false}`, so `true` has no upside and only adds a branch that can stall. |
| **`get_cost: true`** | Preflight before every submission, against the numeric ceiling in `RUNBOOK.md` §6. |
| **`medias`** | **Absent.** The element is never a media. The daily `start_image` QC gate described in v1.0 was removed: its compatibility with `omni_reference` plus an inline element token is unverified, it doubles the number of generations that can fail unattended, and its pass criteria were vision judgements no unattended run can make. Room consistency is carried by byte-identical locked blocks instead. Reinstating it needs a daylight test and a written spec. |

---

## 7. NEVER — the look

Absolute, permanent, applies to every video.

**Never in frame**

1. **A screen of any kind** — no laptop, phone, monitor, tablet, TV, keyboard, projector, UI panel,
   dashboard, or interface. In an AI channel. Three reasons: screens are where generative video
   breaks worst; a 2026 UI looks dated in 2027 and this is a 365-video library; and the metaphor
   beats the screenshot every time.
2. **Any text** — no titles, no captions, no subtitles, no watermark, no logo, no lower third, no
   numbers, no lettering on any object, no Cyrillic anywhere. If a brand mark is ever mandatory it
   is a fixed PNG glued on in ffmpeg afterwards — never generated.
3. **Sci-fi signifiers** — no hologram, no blue glow, no neon, no circuit board, no matrix code, no
   glowing lines, no robot, no android, no futuristic anything.
4. **A second thing arriving in the shaft.** Whatever is there at 00.0 is all there ever is; anything
   more has to come *out of* it.
5. **A second person, a hand that is not his right hand, or a hand entering from above or the side.**
6. **A window, a door, furniture, decoration, a plant, a chair, a rug, a wall hanging.**
7. **Jewellery, a watch, glasses, a logo, a print, a pattern on the sweater.**
8. **Damage to the set.** The tabletop is never pierced, cut, notched, burned or stained, and the
   table never moves.

**Never in the treatment**

9. **A camera move.** Any. Including a "subtle" one.
10. **A cut, transition, fade, flash, black frame, split screen, aspect-ratio change, letterbox or
    black bars** inside the generation — including a fade or darkening in the final frames.
11. **Slow motion or a speed ramp.** The model editorialises tempo unless forbidden.
12. **A smile.** Or a laugh, grin, nod, eyebrow raise, wink, shrug, or any reaction shot.
13. **Speech, mouthing, lip movement, singing, or a voice of any kind.**
14. **Eye contact outside the two scheduled looks** (01.4–02.6 and 08.9–10.0). No other lens
    address, no posing, no performing to camera.
15. **Bright, flat, evenly lit, overcast, softbox, ring-light or studio lighting.** No second light
    source, no flame, no lens flare, no visible sun.
16. **Blue.** Any blue, any cyan, any teal in the grade.
17. **Golden-hour / warm-amber wash over the room.** Amber lives inside the shaft and nowhere else.
18. **A vignette, a LUT look, oversaturation, HDR glow, bloom, halos, oversharpening.**
19. **Beauty-filter smoothing, waxy skin, plastic skin, CGI sheen, cartoon, anime, illustration, 3D
    render.**
20. **A facial description in the prompt.** See §1.2. This is the one that costs you the shot.
21. **Music with a beat, a trending track, or any post-added score.**

---

## 8. The negative list

**It is not stored here.** It lives in `prompts/negative.txt`, one source of truth, flattened into
the prompt at assembly time by the transform in `TEMPLATE.md` §5. v1.0 of this file carried a
second, shorter, materially different hand-typed copy under the heading "THE PERMANENT NEGATIVE —
locked, appended to every prompt". That copy is deleted. Two negative lists is the exact
stale-duplicate failure the change-control rule at the top of this file exists to prevent.

The doctrine behind that file — threat ordering, paraphrase clusters, wrong-outcome entries, and the
rule that a token protecting nothing gets deleted — is stated in its own header and is not repeated
here either.

---

## 9. Acceptance tests

**They are not stored here.** The single test table lives in `RUNBOOK.md` §9, with one threshold per
test. v1.0 of this file and v1.0 of `TEMPLATE.md` both carried test tables and they disagreed on
four thresholds out of ten, which means an unattended run could not tell whether it had passed.

Two principles that govern that table and belong in this file:

- **Thresholds that were guessed are calibrated on the first accepted render, not asserted from
  theory.** An absolute whole-frame luminance band invented before anyone had seen a frame is a
  paid regeneration waiting to happen.
- **A test must be runnable by `ffmpeg`/`ffprobe` at 04:00.** "Looks like the same person" is not a
  test in an unattended pipeline; it is a morning-review item, and the runbook treats it as one.

---

## 10. The three things that may never change

Everything above is locked for 365 days. Three of them are locked beyond that, and no argument,
trend, metric or client note reopens them:

1. **The camera never moves.**
2. **0.40 s of absolute silence before the transformation.**
3. **No speech and no text inside the frame — ever.**

The format is a sonnet, not a joke. The constraint is fixed and public; the content inside it is
infinite. Repetition does not kill a sonnet — repetition is what makes the next one recognisable as
one.
