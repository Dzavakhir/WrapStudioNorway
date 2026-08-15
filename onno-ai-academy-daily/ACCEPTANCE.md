# Приёмка ролика

Проверки из проектной сессии, в исходном виде. Класс проверки указан в самом тексте:
`RE-ROLL class` — провал уходит в бюджет перегенерации, `LOG-ONLY` — записывается в журнал
и ролик всё равно уходит.

## 1

PRE-SUBMIT PROMPT ASSERT — no credit is spent until this passes; it is the only check that runs before billing and the only one that can save a generation. (1) STRING: the assembled prompt must NOT contain '{{', '}}', 'FILL RULES', 'DELETE THIS BLOCK' or '———'; it MUST contain the literal '<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>' exactly once, begin with 'HORIZONTAL 16:9', and contain each of 'CHARACTER —', 'HAIR —', 'WARDROBE —', 'THE ROOM —', 'CAMERA —', 'STAGING —', 'THE APPARATUS —', 'TIMELINE —', 'LIGHT —', 'STYLE —', 'AUDIO —', 'NEGATIVE —'. (2) SLOTS: all ten strings came from TOPICS.md verbatim; this session authored none of them. If any is missing or empty, do not invent it and do not advance to another topic — substituting one desynchronises the thirty-day rotation from the day-of-year index and makes two later days render the same film; log status: blocked, reason: topic_incomplete, notify, generate nothing. (3) CONTINUITY: diff today's prompt against yesterday's; one character of drift outside the ten slots is broken continuity — abort and log. (4) PARAMS: exactly the eight keys in params and no others. extension_mode, use_unlim and count are NOT on the seedance_2_5 model card; extension_mode is a documented hard rejection when mode is not video_extension and the other two are untested against this model — an unattended run rejected on an unrecognised key produces nothing, silently, every day. A batch count, if the tool needs one, is a tool-level argument outside the model parameter block. aspect_ratio is the literal '16:9', never 'auto'. (5) MEDIAS: non-empty on every call from the first attempt. Before submitting, call show_reference_elements on abd99f1e-d482-4cf5-92a4-2ce3aea26018 — free and read-only — and append every image media id it returns as a further {role: 'image_references'} entry after the one already in params, skipping duplicates; if it errors or returns no images, submit params exactly as written and log elements_lookup: unavailable. Any failure aborts the run and submits nothing.

## 2

RE-ROLL BUDGET — HARD. Two generations per day, total, including the first. Confirm cost with generate_video get_cost:true before the first call and abort with status: blocked if credits < 2x cost. Run every check on attempt 1 and log every result. Re-roll ONCE only if a check in the RE-ROLL class fails: ASSET EXISTS (b), DURATION, AUDIO PRESENT, NO SPEECH, SINGLE CONTINUOUS TAKE, THE DELTA HAPPENED. Every other check is LOG-ONLY: record pass/fail with its measured number in runs/YYYY-MM-DD.md and ship regardless — there is no seed, so a re-roll is a fresh lottery ticket, never a correction. If attempt 2 also fails a RE-ROLL-class check, ship it as status: shipped-with-defects, list the failed checks in the journal and the notification, and stop. Under no circumstance a third generation.

## 3

ASSET EXISTS, run before every other post-generation check. Read the job with show_generation_by_ids. (a) status failed / error / rejected, or any error message on the job: log status: failed with the verbatim error string, notify, generate nothing further today, stop — a failed job is NOT a re-roll trigger. (b) status completed but zero result assets or no video URL: log status: failed, reason empty_result, notify, stop. (c) still running after two jobs_wait cycles totalling 20 minutes: log status: failed, reason timeout, notify, stop. (d) URL present: download it, then confirm ffprobe opens the file and reports exactly one video stream; if ffprobe errors or the file is under 200 KB, retry the download twice at 5 s and 15 s, then log status: failed, reason unfetchable, notify, stop.

## 4

IDENTITY ECHO (LOG-ONLY), first of the content checks: show_generation_by_ids on the returned job id. If the echoed prompt still contains the literal '<<<abd99f1e', placeholder injection is unsupported on seedance_2_5 and the identity came from the medias array alone — this is EXPECTED, it is NOT a failure, log injection: media-only and continue. If it contains '@Javokhir', log injection: both and continue. There is no resubmit on this check: the medias array carries the face on every call, so no call can lose the identity. Never issue a second generation for identity reasons, and never repair the CHARACTER line by writing a description of him — description on top of a reference photo only fights it.

## 5

DURATION (RE-ROLL class): ffprobe container duration is 15.0 s plus or minus 0.2 s. Under 14.8 s means a beat was dropped. Fail — counts against the RE-ROLL BUDGET.

## 6

AUDIO PRESENT AND NON-SILENT (RE-ROLL class): an audio stream exists, its duration is within 0.2 s of the video duration, and full-file RMS is above -50 dBFS. Per-window: RMS must exceed -50 dBFS in at least 60% of one-second windows, EXCLUDING from the count the four windows the audio sheet designs as near-silent — 00.0-01.0, 06.0-07.0, 08.0-10.5 and 14.0-15.0. A missing stream, or a file whose full-file RMS is below -60 dBFS, is the only automatic failure. The two designed silences at 06.3 and 08.4 are the format; a gate that counts them as defects re-rolls correct films.

## 7

NO SPEECH (RE-ROLL class): run a speech-to-text pass, NOT a bare voice-activity detector, over the full track. Fail only if the transcript returns two or more distinct word tokens of three or more characters, at confidence above 0.5, inside any single 2-second window. A bare VAD must not be used: the audio sheet mandates a sustained 120-300 Hz tone across 02.6-06.3 which sits in the male F0 band and which energy-gated detectors report as voiced — that tone is the format, not a defect. Transcribed words are a fail; tone and room noise are a pass. Log the full transcript, even when empty.

## 8

SINGLE CONTINUOUS TAKE (RE-ROLL class): ffmpeg scene-change detection at threshold 0.10 finds ZERO scene changes between 0.30 s and 14.70 s. Any internal cut is a fail — counts against the RE-ROLL BUDGET.

## 9

THE DELTA HAPPENED (RE-ROLL class): compare the frame at t = 6.6 s (end of the COST beat, wrong state final, both hands at rest on the bench) with the frame at t = 14.7 s (state B, hands out of frame). Sample ONLY the apparatus band, x = 55-72% of frame width and y = 40-66% of frame height — the volume above the bench surface where nothing but the object stands, so hands resting flat on the bench cannot contribute. Mean absolute pixel difference must exceed 12/255. Additionally the frame at 14.7 s must differ from the frame at 2.0 s in that same band by more than 12/255. Both conditions must hold. A single fixed threshold measured over the whole bench passes on a film where the apparatus never changed state at all, because the hand leaves frame and the wreckage arrives; this band is the only region that answers the question.

## 10

BEAT COMPRESSION (LOG-ONLY): mean absolute frame-to-frame difference over the bench region, x = 50-80%, y = 55-100%, computed per 0.5 s window across the file. No window between 10.5 s and 13.8 s may fall below 30% of the file's median window value. A dead final third means the payoff finished early and the model stretched everything before it — the failure the house README measured when a 1.2 s payoff was delivered in 0.3 s, and one no other check can see. Log the minimum window value in that span as a number.

## 11

FRAME, CAMERA LOCK AND BRAND MARK (LOG-ONLY, three measurements, none re-rolls). (a) FRAME: every frame is exactly 1920x1080 with no resolution change mid-file; sample the top and bottom 24 pixel rows and the left and right 24 pixel columns at 15 evenly spaced timestamps and require mean luma above 16/255 in all of them, proving no letterbox, no pillarbox and no portrait frame padded into a landscape container. (b) CAMERA LOCK: sample 60 evenly spaced frame pairs and measure global translation using the bench edge line and the lamp centroid — both high-contrast features. NEVER the bare plaster wall: THE ROOM specifies it as unbroken matte plaster with no trackable texture, STYLE adds fine 35 mm grain on top, and flow over an untextured region is undefined and returns noise. The 95th-percentile frame-to-frame translation must stay below 3.0 px and no single pair may exceed 12 px; log the 95th percentile and the max. (c) AMBER LAMP: in the region x = 12-38% of frame width, y = 5-40% of frame height, at least 0.05% of pixels have HSV value above 0.66, HSV saturation above 0.25 and hue in the 15-55 degree band, at a minimum of 12 of the 15 sampled timestamps. Measure the glow and the lit plaster around the shade, not a clipped core — clipped pixels desaturate and carry no usable hue, which is why THE ROOM and LIGHT both specify a lamp that glows rather than clips. Log the count of passing timestamps.

## 12

SUBJECT AND SURFACE (LOG-ONLY, three measurements, none re-rolls). (a) ONE FACE ONLY: face detection on 30 evenly spaced frames. The failure this catches is a SECOND PERSON, not a missed detection — the staging has him working head-down through parts of the first third, where frontal detectors correctly return nothing. Fail condition: two or more faces in a single frame, on two or more of the 30 frames. A frame with zero faces is not a fail and is not counted against the total. Separately, at least 8 of the 30 frames must contain exactly one face, proving a person is present at all; log the per-frame counts. (b) HEAD SIZE FLOOR: in every frame where a face is detected, the face bounding-box height is at least 9% of frame height. STAGING pins the HEAD at one quarter of frame height and a face box measures roughly 55-70% of head height, so 9% is the correct derived floor; 12% fails staging that is in fact compliant. Below 9% the model went wide or pushed him back. (c) NO BURNED-IN TEXT: OCR over 15 evenly spaced frames. Fail only if a text region of three or more characters is returned at confidence above 0.75 on two or more of the 15 frames, or if any single region of three or more characters occupies more than 2% of frame area. Single-character and single-frame hits are wood grain and plaster texture, not baked text: log them with string, confidence and frame index, do not fail on them.

