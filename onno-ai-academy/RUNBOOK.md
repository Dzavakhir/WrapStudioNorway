# RUNBOOK — «Один предмет» · the unattended 04:00 run

**Version 1.0 · 2026-08-15.** This file is the entry point. A fresh session with no memory, pointed
at `/home/user/WrapStudioNorway/onno-ai-academy`, executes the numbered steps below in order and
nothing else.

**The governing law of this file: the run never waits for a human.** Every branch below ends in
*continue*, or in *log and exit 0*. There is no step whose failure mode is a question. If you find
yourself about to ask something, you have hit a bug in this runbook — log `NEEDS_SPEC` with the
detail and exit.

**Authority.** `prompts/TEMPLATE.md` owns the prompt text and the parameters. `prompts/negative.txt`
owns the negative list. `topics/topic-bank.md` owns the day's content. `brand/style-bible.md` owns
the reasons and owns nothing executable. **This file owns the procedure, the limits and the tests.**
Where any other file states a limit or a threshold, this file wins.

---

## 0. Before day 1 — a human does these once, in daylight

The run is not started until all four are done. None of them is a runtime step.

| # | Task | Why |
|---|---|---|
| 0.1 | ~~Commit `onno-ai-academy/` so a fresh container can find it.~~ **Done 2026-08-15** — committed and pushed to `claude/onno-ai-academy-video-gen-48gzn8`. The Routine's prompt checks that branch out before reading this file. | Without this there is no run at all. |
| 0.2 | **One test generation in `t2v` carrying the element token**, to settle whether the element binds outside `omni_reference`. Cost: 90 credits. Write the verdict into `TEMPLATE.md` §7. Until then the mode fallback stays *abort*. | Removes the one branch that could publish a stranger's face. |
| 0.3 | **Run steps 1–13 once by hand and inspect the output.** Set the fps lock and calibrate tests T3 and T6 from the accepted render (§9). | Two thresholds cannot be honestly asserted before a frame exists. |
| 0.4 | **Confirm `ffmpeg` and `ffprobe` exist in the runner image**, and that `TZ=Asia/Tashkent date +%F` returns the expected date. | Both are assumed by steps 8–11. |

---

## 1. Schedule

| Item | Value |
|---|---|
| Fire time | **04:00 Asia/Tashkent (UTC+5)**, daily |
| UTC cron | `0 23 * * *` — note this fires on the **previous** UTC day |
| Routine id | `trig_01DyMPumrvLe69VLyCSAVjbD`, created 2026-08-16, fresh session per fire, push notification on |
| Wall-clock budget | 30 minutes; past that, step 7's timeout has already fired |
| Concurrency | one run at a time. If a run is already in flight, exit 0 immediately. |

Tashkent does not observe daylight saving, so `0 23 * * *` stays correct all year. No seasonal fix
is needed — unlike a Europe-based schedule, which would drift by an hour twice a year.

> **The fired sessions carry no MCP connector tools.** The `connectors` parameter is not available
> for this organisation, so the Routine stores no connector grant and each fired session starts
> without `mcp__*` tools. **This is fine for `prompt_only`, which needs only git and python and
> touches no platform tool at all.** It does mean `delivery.mode: generate` **will not work from the
> Routine** — a fired session cannot reach the platform to submit anything. Switching to `generate`
> therefore also requires recreating the Routine from the claude.ai Routines UI (or from a session
> that can pass the grant) so it carries the connector. Recorded here so a future run does not read
> the missing tools as an outage and log `TOOLS_UNAVAILABLE` every morning.

---

## 2. Load the tools

The platform's tools are deferred in this environment: their schemas are not loaded and calling one
without fetching it first fails with `InputValidationError`. **First action of every run:**

```
ToolSearch(query="select:mcp__ONNO__generate_video,mcp__ONNO__jobs_wait,mcp__ONNO__show_generation_by_ids,mcp__ONNO__balance,mcp__ONNO__models_explore,mcp__ONNO__select_workspace", max_results=8)
```

**The server prefix is not stable — do not trust `mcp__ONNO__`.** The same connector surfaces
sometimes as `mcp__ONNO__*` and sometimes as `mcp__<uuid>__*` (e.g.
`mcp__86f48f70-8e2a-412f-8a4b-4a12ccb6f077__generate_video`), and it can flip *within one session*
when the server reconnects. Both spellings were observed on 2026-08-15. A `select:` query naming the
wrong prefix returns **no matches**, not an error.

So if the call above returns nothing, **do not conclude the platform is down.** Search by keyword
instead and use whatever prefix comes back:

```
ToolSearch(query="generate_video seedance video generation", max_results=10)
```

Take the server prefix from the result and re-issue the `select:` query with that prefix for the
other five tools. Only after *both* the name query and the keyword query come back empty: log
`TOOLS_UNAVAILABLE`, exit 0.

`models_explore` is in the list because §6.1 needs it to read today's unlim availability. Without it
loaded the run cannot answer the one question the owner cares about most.

Then `select_workspace` for workspace **Javokhir** if the tool reports a different active workspace.

> Everywhere below, `mcp__ONNO__X` means "tool `X` on whichever prefix step 2 resolved". The names
> after the last `__` are stable; the prefix is not.

---

## 3. Get the date — in Tashkent, never in UTC

```bash
TZ=Asia/Tashkent date +%F
```

This exact command. A bare `date +%F` in the container returns UTC, and 04:00 Tashkent is 23:00 UTC
the previous day, so a naive call yields **yesterday's topic, silently, every single day**, with a
log entry that looks correct.

---

## 4. Compute the topic number, and prove it

```python
from datetime import date
topic_no = (day - date(2026, 1, 1)).days % 120 + 1     # 1..120
```

**Mandatory self-check before any paid call.** Compute the same formula for `2026-08-16` and assert
it returns `108`. If it does not, the date parsing is wrong: log `DATE_CHECK_FAILED`, exit 0, spend
nothing. Also assert `1 <= topic_no <= 120` and that the date is not before `2026-01-01`.

Read the block `### <topic_no> · …` from `topics/topic-bank.md`. Take all eight fields verbatim.
Do not edit, translate, shorten or "improve" any of them.

---

## 5. Assemble the prompt

**Use the script. Do not assemble by hand.**

```bash
python3 tools/assemble.py --json      # metadata + preflight verdict, for the log
python3 tools/assemble.py             # the prompt itself on stdout, only if preflight passed
```

`tools/assemble.py` implements exactly this section: it resolves the date in `Asia/Tashkent`, derives
the topic, parses the bank, flattens the negative, substitutes the four content slots, and runs every
preflight below. **Exit 0 = the prompt on stdout is safe to submit. Exit 1 = a preflight failed, and
the reasons are on stderr → log `PREFLIGHT_FAILED` and exit 0. Exit 2 = a file is missing or
malformed → log `NEEDS_SPEC` and exit 0.** No stdout on a non-zero exit, so a failed assembly cannot
be submitted by accident.

Hand assembly is the one place where a silent one-character slip costs 90 credits and ships a broken
film, which is why the substitution is code and not prose. The prose below is the spec the script
implements, kept because the script must remain auditable against it.

Per `prompts/TEMPLATE.md` §5:

```
prompt = TEMPLATE_BODY
           .replace("{{OBJECT}}",         topic.object_en)
           .replace("{{PAYOFF}}",         topic.payoff_en)
           .replace("{{PAYOFF_REST}}",    topic.rest_en)
           .replace("{{FOLEY}}",          topic.foley_en)
           .replace("{{NEGATIVE}}",       flatten("prompts/negative.txt"))
           .replace("{{NEGATIVE_TODAY}}", "" if topic.negative_today == "—" else topic.negative_today)
```

`TEMPLATE_BODY` is the fenced `text` block in `TEMPLATE.md` §2, taken byte-for-byte. `flatten()` is
defined in `TEMPLATE.md` §5 and is the only transform applied to the negative file.

**Preflight assertions. Any failure: log `PREFLIGHT_FAILED` with the failing assertion, exit 0.**

| # | Assertion |
|---|---|
| P1 | `<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>` occurs exactly once |
| P2 | no `{{` and no `}}` remain anywhere |
| P3 | no Cyrillic character anywhere in the string |
| P4 | the standing negative substring is byte-identical to `flatten("prompts/negative.txt")` |
| P5 | no `(`…`)`, `{`…`}` or `【`…`】` used as an audio bracket; only `<`…`>` |
| P6 | total length between 14 000 and 17 000 characters (topic 108 measures 15 262; measured range across all 120 is 15 128–15 320) |
| P7 | `05.2-07.0`, `04.6-05.2` and `07.0-08.9` occur **once** each; `04.2-04.6` and `08.9-10.0` occur **twice** each — once in TIMELINE, once in AUDIO |
| P8 | neither `{{PAYOFF}}`'s nor `{{PAYOFF_REST}}`'s substituted text starts with a capital letter or ends with a full stop — the template supplies both, and a doubled one is a visible seam |

---

## 6. Delivery mode, unlim, and the hard limits

Read `config.json` → `delivery` and `billing` at the start of this step. That file is the only place
the policy lives; nothing below is hard-coded anywhere else.

### 6.0 Which mode is this run in?

| `delivery.mode` | What the run does |
|---|---|
| `prompt_only` **(current)** | Everything except pressing the button. Skip §6.1–§6.3 and §7–§8 entirely, jump to **§7A**. Nothing is submitted, nothing is spent, no API call that costs anything is made. |
| `generate` | Submit through the API. Continue to §6.1. |

**Why `prompt_only` is the default, recorded so nobody "fixes" it later.** The owner asked for
Seedance 2.5 *on unlimited*. Unlimited is a web-UI entitlement and is **not reachable from here**:

- Over the API, `models_explore(action="get", model_id="seedance_2_5")` reports
  `unlim: {available:false, remaining:null}` and the model carries no `supports_unlim` flag. The
  owner confirmed independently that unlimited does not work over MCP.
- Driving the web UI from this container is not an alternative. The egress policy answers **403 to
  CONNECT** for `onno.ai`, `app.onno.ai` and `higgsfield.ai` (verified 2026-08-16). Chromium is
  installed and Playwright is configured, and it makes no difference — there is nowhere to go.
  Do not attempt to disable TLS verification or bypass the proxy to get around this.

So the only path to a genuinely unlimited generation is a human pasting the prompt into the web UI.
`prompt_only` automates the other 95% of the work and hands over a finished, validated prompt.
Switching to `generate` does not unlock unlimited — it only spends credits.

### 6.1 Ask whether unlim is available today — always, before anything else

### 6.1 Ask whether unlim is available today — always, before anything else

```
mcp__ONNO__models_explore(action="get", model_id="seedance_2_5")
```

Read the `unlim` block of the response:

| `unlim.available` | What it means | What the run does |
|---|---|---|
| `true` | The account holds an allowance that covers this model right now | **`use_unlim: true`.** The generation is free. Skip §6.3 entirely — balance floor, cost ceilings and the day ceiling are all about credits and do not apply. The generation cap of 2/day still applies. Log `unlim=yes`. |
| `false` (or the block is absent) | No allowance covers `seedance_2_5` today | Go to §6.2. |

This check runs **every single day**. It is not cached and its answer is not assumed. The owner's
instruction is *Seedance 2.5 on unlim*; the moment an allowance appears on the account, the run picks
it up by itself with no edit to any file.

> **State as of 2026-08-15.** `seedance_2_5` carries no `supports_unlim` flag and the account
> allowance reads `{available:false, remaining:null}`. The unlim-eligible video models are
> `seedance_2_0`, `seedance_2_0_mini`, `kling3_0`, `gemini_omni` and `wan2_7`. So today this check
> returns `false` and the run lands in §6.2. This is recorded, not worked around.

### 6.2 No unlim — the spend gate

`config.json` → `billing.credit_spend_authorized` decides, and nothing else does:

| Value | What the run does |
|---|---|
| `false` **(current setting)** | Log `NO_UNLIM_NOT_AUTHORIZED` with today's topic number and the cost the run *would* have incurred. **Generate nothing. Spend nothing. Exit 0.** Report it in step 15's summary so the human sees a clean, honest "no video today, and why". |
| `true` | Continue to §6.3 and pay with credits. |

**Never flip this flag from inside a run.** It encodes a standing authorisation for a recurring
real-money charge — roughly 90 credits every day, unattended, indefinitely. Only the account owner
sets it, by editing `config.json` and committing. An unattended session that talks itself into
spending is the exact failure this gate exists to prevent.

### 6.3 Paying with credits — the hard limits

These are numbers, not policies. They are the whole defence against an unattended credit fire.

| Limit | Value | Action on breach |
|---|---|---|
| **Balance floor** | 200 credits | `mcp__ONNO__balance` first. Below the floor: log `BALANCE_FLOOR`, exit 0 without generating. |
| **Per-job ceiling** | **95 credits** | `get_cost: true` before every submission, including the retry. Quote above ceiling: log `COST_CEILING`, exit 0. |
| **Per-day ceiling** | **190 credits** | Sum of everything actually submitted today. Reaching it ends the day. |
| **Generation cap** | **2 video generations per day, maximum.** | Applies on the unlim path too. After the second failure: log `QC_FAIL`, keep both files, publish nothing, exit 0. There is no third attempt, ever. |

Measured 2026-08-15 with `get_cost: true`: 10 s / 1080p / high = **90 credits**; 720p = 65;
`bitrate_mode` is credit-neutral. Cost is linear in duration at 9 credits per second at 1080p.
At 90 credits/day a 6 602-credit balance is **73 days** of runway.

The preflight call is free and submits nothing. `use_unlim` carries whatever §6.1/§6.2 decided:

```json
{"model":"seedance_2_5","params":{"mode":"omni_reference","prompt":"<assembled>","duration":10,
 "resolution":"1080p","aspect_ratio":"9:16","generate_audio":true,"bitrate_mode":"high",
 "use_unlim":false,"get_cost":true}}
```

---

## 7. Submit and wait

Identical call with `get_cost` **removed**. No `medias` key.

**`use_unlim` is always present and is never omitted.** Omitting it makes the server return the
interactive `unlim_choice` question instead of generating, which is fatal at 04:00. Its value is not
a constant — it is whatever §6.1/§6.2 decided this morning:

- §6.1 said `unlim.available: true` → **`use_unlim: true`** (free generation, the intended path)
- §6.1 said `false` **and** `config.json` authorises credits → **`use_unlim: false`**
- §6.1 said `false` **and** credits are not authorised → the run already exited at §6.2 and never
  reaches this step

That is a decision made from a server answer plus a committed config value, both read before this
step. It is never an interactive question and it is never a coin toss, so the run neither stalls nor
spends without standing authorisation.

Then poll with `mcp__ONNO__jobs_wait`, and `mcp__ONNO__show_generation_by_ids` for detail.

| Outcome | Action |
|---|---|
| Completed with a media URL | continue to step 8 |
| **Still queued or running after 20 minutes** | log `TIMEOUT` with the job id, exit 0. **Never keep waiting.** The job may still complete; a human picks it up in the morning from the log. |
| Rejected for `mode` | log `MODE_REJECTED`, exit 0. **Do not retry in `t2v`** — see §0.2. |
| Rejected by content moderation / filtered | log `MODERATION` with the exact server message, exit 0. This is a distinct outcome, not a generic error: it involves a real face and needs a human. **Do not retry.** |
| Any other error | log `JOB_ERROR`; retry once only if the generation cap in §6 allows, otherwise exit 0 |

---

## 7A. Deliver the prompt (mode `prompt_only`)

This is the whole run in the default mode. No platform tools are needed beyond step 2's bootstrap,
and if that bootstrap failed it does not matter — **this mode does not touch the platform at all.**

Write four files to `out/<YYYY-MM-DD>/`:

| File | Contents |
|---|---|
| `prompt.txt` | stdout of `python3 tools/assemble.py` — the full assembled prompt, preflight-clean. Nothing else in the file, no header, no fences, so it is one clean select-all-and-copy. |
| `settings.md` | the web-UI settings below, filled in with today's numbers |
| `caption.txt` | the Russian caption from step 10 |
| `meta.json` | stdout of `python3 tools/assemble.py --json` |

`settings.md` is written from this table every day — the values are locked and come from
`TEMPLATE.md` §7:

| Field in the ONNO web UI | Value |
|---|---|
| Model | **Seedance 2.5** |
| Mode | **Unlimited** — this is the entire reason this mode exists. If the UI does not offer it for this model, stop and tell the owner rather than silently generating on credits. |
| Reference / character | element **Javokhir**. The prompt already carries `<<<abd99f1e-…>>>`; if the UI resolves the token itself, change nothing. If it does not, attach the element by name and delete the token from the pasted text. |
| Aspect ratio | **9:16** |
| Resolution | **1080p** |
| Duration | **10 s** |
| Audio | **on** |
| Bitrate | **high**, if exposed |

Then commit and push per §13, and report per step 15 with the topic, the hook, and the path to
`prompt.txt`. Outcome for the log is `PROMPT_READY`.

**A run in this mode has no failure mode that costs anything.** If assembly fails, log
`PREFLIGHT_FAILED` and exit 0; if the push fails, log it and exit 0 — the files are still on disk.

---

## 8. Download

Fetch the returned media to:

```
out/<YYYY-MM-DD>/raw.mp4
```

Failure to download: log `DOWNLOAD_FAILED` with the URL and exit 0 — the credits are already spent
and the URL in the log is the recovery path.

---

## 9. Acceptance tests — the only table

Run on `raw.mp4`. **Gate the whole suite on `ffmpeg -version`**; if `ffmpeg` is missing, log
`TESTS_SKIPPED` and treat the render as *provisional pass*, then continue — never stall.

| # | Claim | Test | Pass |
|---|---|---|---|
| T1 | One continuous take | `ffmpeg` scene detection at threshold 0.10 | **0** scene changes |
| T2 | Duration exact | `ffprobe` container duration | 9.9–10.1 s |
| T3 | Format | stream dimensions | 1080×1920, every frame, no letterbox rows |
| T4 | Camera locked | x-position of the shaft's left and right boundary at a fixed scanline, per frame | each constant within **±3 px** across the whole clip |
| T5 | The silence exists | audio RMS in 10 ms windows | a contiguous window **≥ 0.30 s** between 04.10 and 04.75 that is **≥ 25 dB below** the 02.6–04.2 mean |
| T6 | Chiaroscuro not lifted | whole-frame mean luminance per frame | within **±20 %** of the value measured on the first accepted render (§0.3). Not an absolute band — that number cannot be known before a frame exists. |
| T7 | The payoff is not crushed | frame-difference energy curve | its maximum falls inside **05.2–07.0** |
| T8 | It lands and stays | frame-difference energy over 08.0–08.9 | near the clip floor |
| T9 | No fade-out | mean luminance of the final 6 frames | no monotonic decay greater than **5 %** |
| T10 | No baked text | OCR sample every 0.5 s | zero glyph detections |
| T11 | Object legible | downscale a frame at 07.5 s to 240 px wide | the object occupies ≥ 40 px of preview height |
| T12 | Frame rate | `ffprobe` | matches the library fps lock exactly, constant |

**T4 is the acceptance test for the locked camera and is the most important one. T5 is the test for
the format's best moment.** T6 and the fps lock are calibrated, not asserted.

Two things are explicitly **not** tests: whether the mouth stayed closed, and whether the face is
recognisably his. Both are vision judgements, both go on the morning-review line of the log, and
neither blocks publication at 04:00.

**On failure of any test:** if the generation cap in §6 still allows, regenerate **once** from step 6
with the identical prompt — the model is stochastic and the same prompt is the correct retry. On the
second failure, log `QC_FAIL` listing which tests failed, keep both files, publish nothing, exit 0.
**Do not edit the prompt to chase a pass. Do not fix anything in post.**

---

## 10. Caption

Required daily output, built by concatenation from the topic block. No composition, no rewriting.

```
<тема без префикса полосы>

<hook_ru>

<payoff_ru>

<один вопрос читателю>

Онно AI Academy
```

The question line is the last sentence of `payoff_ru` turned into a question, or, if that does not
work, the fixed fallback `А как это у вас?`. Write it to:

```
out/<YYYY-MM-DD>/caption.txt
```

No text is ever burned into the frame. If a brand mark is ever required it is a fixed PNG overlaid
in step 11 — never generated.

---

## 11. Assembly

One `ffmpeg` pass, and the only edit this format has:

- Copy the video stream untouched; do not re-encode the picture if it can be avoided.
- **Hard cut to black and to silence at 10.0** — the last frame is followed by nothing. This is why
  the prompt does not ask for it: a generation asked to end on black bakes black tail frames and
  fails T9.
- No fade, no titles, no logo, no music, no colour grade.

Output: `out/<YYYY-MM-DD>/final.mp4`.

---

## 12. Log

Append one row to `log/runs.md` on **every** run, including the ones that exit early. The log is the
only thing a human reads in the morning.

Columns: `date · topic_no · lane · verb_ru · outcome · credits · job_id · failed tests · note`.

Outcome is exactly one of: `OK` · `QC_FAIL` · `TIMEOUT` · `MODERATION` · `MODE_REJECTED` ·
`JOB_ERROR` · `PROMPT_READY` · `COST_CEILING` · `BALANCE_FLOOR` · `NO_UNLIM_NOT_AUTHORIZED` · `PREFLIGHT_FAILED` ·
`DATE_CHECK_FAILED` · `DOWNLOAD_FAILED` · `TOOLS_UNAVAILABLE` · `TESTS_SKIPPED` · `NEEDS_SPEC`.

The `credits` column records `0 (unlim)` on the unlim path, the quoted number on the credit path, and
`0 (not authorised)` on `NO_UNLIM_NOT_AUTHORIZED`.

On `OK`, add the two morning-review items as free text: *mouth closed?* and *face reads as him?*

---

## 13. Commit

```
git add log/runs.md out/<YYYY-MM-DD>/caption.txt
git commit -m "run <YYYY-MM-DD>: topic <NNN> <outcome>"
git push origin claude/onno-ai-academy-video-gen-48gzn8
```

The branch name is `git.branch` in `config.json`; the line above is its current value. If the working
copy is on a different branch, check it out first — a fresh container clones the repo's default
branch, which is **not** this one.

Video files are **not** committed. **A failed commit or push is never fatal**: log `push failed` in
the note column and exit 0 anyway. Credits have already been spent; losing the run over a git error
would be the worst possible trade.

---

## 14. Publishing

**Not part of the 04:00 run.** The run produces `final.mp4` and `caption.txt` and stops. Publication
is a human action, or a separate later job, because it is the one step where an unreviewed bad
render becomes public and unrecoverable. The morning review is: watch it once, check the two vision
items from the log, publish or discard.

---

## 15. Failure taxonomy — what each outcome means to the human reading the log

| Outcome | What happened | What to do |
|---|---|---|
| `OK` | Video produced and passed the tests | Review the two vision items, publish |
| `PROMPT_READY` | Mode `prompt_only`: the day's prompt is assembled, validated and pushed | Paste `out/<date>/prompt.txt` into the ONNO web UI with `settings.md`, generate on unlimited |
| `QC_FAIL` | Two renders, both failed tests | Look at which test. A repeated T4 or T7 failure means the prompt needs work — that is a daylight job, not a 04:00 job |
| `TIMEOUT` | Job never came back inside 20 min | Check the job id; it may have completed. Credits were spent |
| `MODERATION` | The job was filtered | Real-face content policy. Needs a human before the next run |
| `MODE_REJECTED` | Backend refused `omni_reference` | Do §0.2. Nothing else changes until it is answered |
| `COST_CEILING` / `BALANCE_FLOOR` | Money guard fired | Top up, or switch to 720p as documented in `README.md` |
| `NO_UNLIM_NOT_AUTHORIZED` | No unlim allowance covered `seedance_2_5` today, and `config.json` does not authorise paying with credits | **Not an error — the configured behaviour.** Either wait for an unlim allowance, or set `billing.credit_spend_authorized: true` to accept ~90 credits/day |
| `PREFLIGHT_FAILED` / `DATE_CHECK_FAILED` | The assembled prompt or the date was wrong | A file is malformed. Nothing was spent |
| `NEEDS_SPEC` | The run hit a branch this runbook does not cover | Extend this file. That is the bug |

---

## 16. What this runbook deliberately does not do

- **It does not generate a start image.** The daily `start_image` QC gate was removed in v2.0:
  unverified compatibility with `omni_reference` plus an inline element token, it doubles the number
  of unattended failure points, and its pass criteria were vision judgements. See `TEMPLATE.md` §7.
- **It does not substitute topics.** A failed day is a failed day; the topic returns in the next
  120-day cycle. Manual substitution only, and only by the `((n-1+60) mod 120)+1` rule in
  `topic-bank.md` §5.
- **It does not edit the prompt to chase a pass.** Two identical attempts, then stop.
- **It does not publish.** See §14.
- **It does not ask anyone anything.** See the top of this file.
- **It does not authorise its own spending.** `billing.credit_spend_authorized` is read, never
  written. A run that finds no unlim and no authorisation reports and exits — it does not reason its
  way into a charge, does not "just this once", and does not downgrade to 720p to squeeze under a
  gate that is about permission rather than price.
- **It does not switch models to chase unlim.** `seedance_2_0` and friends are unlim-eligible and
  `seedance_2_5` is not, but the model is the owner's choice and a silent swap would change the
  channel's look. Changing it is a `config.json` edit by a human.
