#!/usr/bin/env python3
"""
Assemble the day's Seedance 2.5 prompt for «Один предмет».

  python3 tools/assemble.py                 # today, in Asia/Tashkent
  python3 tools/assemble.py --date 2026-08-16
  python3 tools/assemble.py --topic 108
  python3 tools/assemble.py --check-all     # assemble all 120 and run every preflight

RUNBOOK.md §5 is the spec this implements. TEMPLATE.md §2 owns the prompt body, negative.txt owns
the negative list, topic-bank.md owns the day's content. This file owns none of them — it only
substitutes and asserts, which is exactly why the 04:00 run may use it and may not edit it.

Exit codes: 0 all preflights passed · 1 a preflight failed · 2 a file is missing or malformed.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_MD = os.path.join(ROOT, "prompts", "TEMPLATE.md")
NEGATIVE_TXT = os.path.join(ROOT, "prompts", "negative.txt")
TOPIC_BANK = os.path.join(ROOT, "topics", "topic-bank.md")

EPOCH = dt.date(2026, 1, 1)          # day 0 == topic 001
CYCLE = 120
ELEMENT = "<<<abd99f1e-d482-4cf5-92a4-2ce3aea26018>>>"

CONTENT_FIELDS = ("object_en", "payoff_en", "rest_en", "foley_en")
ALL_FIELDS = CONTENT_FIELDS + ("verb_ru", "negative_today", "hook_ru", "payoff_ru")


class Malformed(Exception):
    pass


# ---------------------------------------------------------------- loading


def topic_of(day: dt.date) -> int:
    delta = (day - EPOCH).days
    if delta < 0:
        raise Malformed(
            f"{day} is before the epoch {EPOCH}; the modulo would silently pick a wrong topic"
        )
    return delta % CYCLE + 1


def load_template() -> str:
    """The prompt body is the first ```text fence in TEMPLATE.md §2."""
    md = open(TEMPLATE_MD, encoding="utf-8").read()
    m = re.search(r"```text\n(.*?)```", md, re.S)
    if not m:
        raise Malformed(f"no ```text fence found in {TEMPLATE_MD}")
    return m.group(1).strip()


def flatten_negative() -> str:
    """RUNBOOK §5 / TEMPLATE §5: drop # comments and blank lines, join with one space."""
    out = []
    for line in open(NEGATIVE_TXT, encoding="utf-8"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def load_topics() -> dict:
    """Parse `### NNN · LANE · Title` blocks with `- \\`field:\\` value` lines."""
    topics, cur = {}, None
    head = re.compile(r"^###\s+(\d{3})\s+·\s+([^·]+?)\s+·\s+(.+?)\s*$")
    field = re.compile(r"^-\s+`([a-z_]+):`\s*(.*?)\s*$")
    for raw in open(TOPIC_BANK, encoding="utf-8"):
        m = head.match(raw)
        if m:
            cur = int(m.group(1))
            topics[cur] = {"no": cur, "lane": m.group(2).strip(), "title": m.group(3).strip()}
            continue
        if cur is None:
            continue
        f = field.match(raw)
        if f:
            key, val = f.group(1), f.group(2)
            topics[cur][key] = "" if val in ("—", "-", "") else val
    return topics


# ---------------------------------------------------------------- assembly


def assemble(topic: dict, template: str, negative: str) -> str:
    for f in CONTENT_FIELDS:
        if not topic.get(f):
            raise Malformed(f"topic {topic['no']:03d} is missing `{f}`")
    return (
        template.replace("{{OBJECT}}", topic["object_en"])
        .replace("{{PAYOFF}}", topic["payoff_en"])
        .replace("{{PAYOFF_REST}}", topic["rest_en"])
        .replace("{{FOLEY}}", topic["foley_en"])
        .replace("{{NEGATIVE}}", negative)
        .replace("{{NEGATIVE_TODAY}}", topic.get("negative_today", ""))
    )


def preflight(prompt: str, topic: dict) -> list:
    """TEMPLATE.md §5 / RUNBOOK.md §5. Returns a list of failure strings; empty means pass."""
    bad = []

    if prompt.count(ELEMENT) != 1:
        bad.append(f"P1 element token appears {prompt.count(ELEMENT)}x, expected exactly 1")

    if "{{" in prompt or "}}" in prompt:
        leftover = set(re.findall(r"\{\{[A-Z_]+\}\}", prompt))
        bad.append(f"P2 unsubstituted slot(s) remain: {sorted(leftover) or 'stray braces'}")

    cyr = {c for c in prompt if "CYRILLIC" in unicodedata.name(c, "")}
    if cyr:
        bad.append(f"P3 Cyrillic in the prompt: {sorted(cyr)[:8]}")

    if "【" in prompt or "】" in prompt:
        bad.append("P5 subtitle bracket 【】 present — it renders as burned-in text")

    n = len(prompt)
    if not 14_000 <= n <= 17_000:
        bad.append(f"P6 assembled length {n} outside the 14000-17000 band")

    for code, want in (("05.2-07.0", 1), ("04.6-05.2", 1), ("07.0-08.9", 1),
                       ("04.2-04.6", 2), ("08.9-10.0", 2)):
        got = prompt.count(code)
        if got != want:
            bad.append(f"P7 timecode {code} appears {got}x, expected {want}")

    for f in ("payoff_en", "rest_en"):
        v = topic[f]
        if v[:1].isupper():
            bad.append(f"P8 `{f}` starts with a capital — the template supplies the sentence start")
        if v.endswith("."):
            bad.append(f"P8 `{f}` ends with a full stop — the template supplies it")

    nt = topic.get("negative_today", "")
    if nt and not nt.endswith(";"):
        bad.append("P9 `negative_today` is not terminated with ';'")

    return bad


# ---------------------------------------------------------------- entry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD; default = today in Asia/Tashkent")
    ap.add_argument("--topic", type=int, help="force a topic number, 1-120")
    ap.add_argument("--check-all", action="store_true", help="assemble all 120 and report")
    ap.add_argument("--json", action="store_true", help="emit metadata as JSON, not the prompt")
    args = ap.parse_args()

    try:
        template, negative, topics = load_template(), flatten_negative(), load_topics()
    except (OSError, Malformed) as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if len(topics) != CYCLE:
        print(f"FATAL: parsed {len(topics)} topics, expected {CYCLE}", file=sys.stderr)
        return 2

    if args.check_all:
        failures = 0
        for n in range(1, CYCLE + 1):
            t = topics.get(n)
            if t is None:
                print(f"{n:03d}  MISSING")
                failures += 1
                continue
            missing = [f for f in ALL_FIELDS if f not in t]
            if missing:
                print(f"{n:03d}  MISSING FIELDS {missing}")
                failures += 1
                continue
            try:
                bad = preflight(assemble(t, template, negative), t)
            except Malformed as e:
                print(f"{n:03d}  {e}")
                failures += 1
                continue
            if bad:
                failures += 1
                print(f"{n:03d}  FAIL")
                for b in bad:
                    print(f"       {b}")
        verbs = [topics[n].get("verb_ru", "") for n in range(1, CYCLE + 1)]
        for i in range(CYCLE):
            window = [verbs[(i + k) % CYCLE] for k in range(1, 21)]
            if verbs[i] and verbs[i] in window:
                print(f"{i+1:03d}  verb '{verbs[i]}' repeats inside the 21-row window")
                failures += 1
        print(f"\n{CYCLE - failures}/{CYCLE} topics assemble clean.")
        return 1 if failures else 0

    if args.topic:
        n = args.topic
        day = None
    else:
        if args.date:
            day = dt.date.fromisoformat(args.date)
        else:
            os.environ["TZ"] = "Asia/Tashkent"
            try:
                import time
                time.tzset()
            except AttributeError:
                pass
            day = dt.date.today()
        try:
            n = topic_of(day)
        except Malformed as e:
            print(f"FATAL: {e}", file=sys.stderr)
            return 2

    t = topics.get(n)
    if t is None:
        print(f"FATAL: topic {n} not in the bank", file=sys.stderr)
        return 2

    try:
        prompt = assemble(t, template, negative)
    except Malformed as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    bad = preflight(prompt, t)

    if args.json:
        print(json.dumps({
            "date": day.isoformat() if day else None,
            "topic_no": n,
            "lane": t.get("lane"),
            "title": t.get("title"),
            "verb_ru": t.get("verb_ru"),
            "hook_ru": t.get("hook_ru"),
            "payoff_ru": t.get("payoff_ru"),
            "prompt_chars": len(prompt),
            "preflight": "pass" if not bad else bad,
        }, ensure_ascii=False, indent=2))
    else:
        if bad:
            for b in bad:
                print(f"PREFLIGHT FAIL: {b}", file=sys.stderr)
            return 1
        print(prompt)

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
