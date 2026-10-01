#!/usr/bin/env python3
"""
scripts/review_classification_log.py

Turns the raw, append-only classification review log into something a human
can act on. The log itself never changes runtime behavior -- this script is
the "review" half of the learning loop: run it periodically, look for
columns that keep showing up across multiple uncertain classifications, and
use that to deliberately expand INDUSTRY_KEYWORDS in main.py.

This does NOT auto-edit any code. It only recommends. You stay the one
deciding what's a real signal vs coincidence -- same discipline used for
every keyword added to this project so far.

Usage:
    python scripts/review_classification_log.py
"""

import json
import os
import sys
from collections import Counter, defaultdict

LOG_PATH = "data/outputs/logs/classification_review_log.jsonl"


def load_entries():
    if not os.path.exists(LOG_PATH):
        print(f"No log found at {LOG_PATH} yet -- nothing to review.")
        sys.exit(0)
    entries = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def main():
    entries = load_entries()
    if not entries:
        print("Log exists but is empty -- nothing to review.")
        return

    print(f"Reviewing {len(entries)} low-confidence classification event(s)\n")

    by_reason = defaultdict(list)
    for e in entries:
        by_reason[(e["reason"], e["landed_on"])].append(e)

    for (reason, landed_on), group in sorted(by_reason.items(), key=lambda x: -len(x[1])):
        print(f"=== {reason} -> landed on [{landed_on.upper()}]  ({len(group)} occurrence(s)) ===")

        col_counter = Counter()
        for e in group:
            for col in e["columns"]:
                col_counter[str(col).lower().strip()] += 1

        recurring = [(col, n) for col, n in col_counter.items() if n > 1]
        if recurring:
            print("  Columns recurring across multiple files in this group (candidates worth reviewing):")
            for col, n in sorted(recurring, key=lambda x: -x[1])[:15]:
                print(f"    {n}x  {col}")
        else:
            print("  (no column recurred more than once in this group yet -- likely still one-off files)")

        print("  Files:")
        for e in group[:5]:
            print(f"    {e['timestamp'][:10]}  {e['file_name']}")
        if len(group) > 5:
            print(f"    ... and {len(group) - 5} more")
        print()

    print("-" * 60)
    print("Reminder: a column appearing once is coincidence. A column recurring")
    print("across several unrelated real files in the same group is a genuine")
    print("signal worth adding to INDUSTRY_KEYWORDS in main.py -- then re-run")
    print("`make test` to confirm the addition doesn't introduce a new")
    print("cross-industry collision (see the collision-scanner pattern used")
    print("throughout this project's development).")


if __name__ == "__main__":
    main()
