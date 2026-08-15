#!/usr/bin/env python3
"""Собирает промпт дня и прогоняет PRE-SUBMIT PROMPT ASSERT.

    python3 assemble.py                 # тема на сегодня по местной дате Ташкента
    python3 assemble.py --date 2026-08-16
    python3 assemble.py --json          # готовый params для generate_video

Ничего не генерирует и не тратит кредитов. Ненулевой код возврата означает, что
собранный промпт отправлять нельзя.
"""

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EPOCH = dt.date(2026, 1, 1)
TASHKENT = dt.timezone(dt.timedelta(hours=5))
ELEMENT = "abd99f1e-d482-4cf5-92a4-2ce3aea26018"

SLOT_KEYS = [
    "APPARATUS", "TOOL", "WRONG_ACTION", "DEGRADATION", "COST_EVENT",
    "REVERSAL_ACT", "STATE_B", "WRECKAGE", "PROOF_ACTION", "TOPIC_NEGATIVES",
]

REQUIRED_BLOCKS = [
    "CHARACTER —", "HAIR —", "WARDROBE —", "THE ROOM —", "CAMERA —", "STAGING —",
    "THE APPARATUS —", "TIMELINE —", "LIGHT —", "STYLE —", "AUDIO —", "NEGATIVE —",
]

FORBIDDEN = ["{{", "}}", "FILL RULES", "DELETE THIS BLOCK", "———"]


def topic_index(date):
    return (date - EPOCH).days % 30 + 1


def load_topics():
    """TOPICS.md -> {day: {"title": str, "slots": {...}}}"""
    text = (HERE / "TOPICS.md").read_text(encoding="utf-8")
    topics = {}
    for m in re.finditer(r"^## (\d+)\. (.+?)\n(.*?)(?=^## \d+\.|\Z)", text, re.M | re.S):
        day, title, body = int(m.group(1)), m.group(2).strip(), m.group(3)
        block = re.search(r"```text\n(.*?)```", body, re.S)
        if not block:
            continue
        slots = {}
        for line in block.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                if k.strip() in SLOT_KEYS:
                    slots[k.strip()] = v.strip()
        topics[day] = {"title": title, "slots": slots}
    return topics


def assemble(day, topics):
    master = (HERE / "PROMPT-MASTER.txt").read_text(encoding="utf-8")
    # Отрезаем блок FILL RULES вместе с разделителем. Искать по 'HORIZONTAL 16:9'
    # нельзя: эта строка цитируется внутри самого блока FILL RULES.
    sep = master.rfind("———")
    if sep == -1:
        raise SystemExit("PROMPT-MASTER.txt: не найден разделитель '———' после блока FILL RULES")
    prompt = master[sep + len("———"):].lstrip("\n").rstrip() + "\n"
    if not prompt.startswith("HORIZONTAL 16:9"):
        raise SystemExit("PROMPT-MASTER.txt: после разделителя промпт не начинается с 'HORIZONTAL 16:9'")

    entry = topics.get(day)
    if entry is None:
        raise SystemExit(f"TOPICS.md: нет темы {day}")

    missing = [k for k in SLOT_KEYS if not entry["slots"].get(k)]
    if missing:
        raise SystemExit(
            "status: blocked, reason: topic_incomplete — "
            f"тема {day} без слотов: {', '.join(missing)}. "
            "Тему не подменять, день пропустить, уведомить владельца."
        )

    for k in SLOT_KEYS:
        prompt = prompt.replace("{{%s}}" % k, entry["slots"][k])
    return prompt, entry


def assert_prompt(prompt):
    problems = []
    for bad in FORBIDDEN:
        if bad in prompt:
            problems.append(f"в промпте осталось {bad!r}")
    token = "<<<%s>>>" % ELEMENT
    if prompt.count(token) != 1:
        problems.append(f"плейсхолдер элемента встречается {prompt.count(token)} раз, нужен ровно 1")
    if not prompt.startswith("HORIZONTAL 16:9"):
        problems.append("промпт не начинается с 'HORIZONTAL 16:9'")
    for block in REQUIRED_BLOCKS:
        if block not in prompt:
            problems.append(f"нет блока {block!r}")
    return problems


def params_for(prompt):
    base = json.loads((HERE / "PARAMS.json").read_text(encoding="utf-8"))
    base["prompt"] = prompt
    if not base.get("medias"):
        raise SystemExit("PARAMS.json: medias пуст — identity-lock потерян, запуск отменён")
    allowed = {"model", "mode", "prompt", "duration", "resolution",
               "aspect_ratio", "generate_audio", "bitrate_mode", "medias"}
    extra = set(base) - allowed
    if extra:
        raise SystemExit(f"PARAMS.json: лишние ключи {sorted(extra)} — отказ API, запуск отменён")
    if base.get("aspect_ratio") != "16:9":
        raise SystemExit("PARAMS.json: aspect_ratio должен быть литералом '16:9'")
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD, по умолчанию сегодня в Ташкенте")
    ap.add_argument("--json", action="store_true", help="напечатать params одним JSON")
    args = ap.parse_args()

    date = (dt.date.fromisoformat(args.date) if args.date
            else dt.datetime.now(TASHKENT).date())
    day = topic_index(date)
    topics = load_topics()
    prompt, entry = assemble(day, topics)
    problems = assert_prompt(prompt)
    params = params_for(prompt)

    if args.json:
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return 0 if not problems else 1

    print(f"дата           {date}  (Asia/Tashkent)")
    print(f"тема           {day}. {entry['title']}")
    print(f"длина промпта  {len(prompt)} символов")
    print(f"референсов     {len(params['medias'])}")
    if problems:
        print("\nPRE-SUBMIT PROMPT ASSERT: ПРОВАЛ")
        for p in problems:
            print("  -", p)
        return 1
    print("\nPRE-SUBMIT PROMPT ASSERT: пройден. Промпт можно отправлять.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
