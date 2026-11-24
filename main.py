#!/usr/bin/env python3
"""One-Line Robot Wedding Vows — make.fun entry.

Writes a single line of wedding vows for a robot couple to
/output/entry.txt. The gate: UTF-8 text, 1 to 160 characters, one
non-blank line. The judge weighs, most important first: it must be a
robot wedding vow that lands as a joke; the laugh must sit in the line
itself, a turn or wordplay that pays off in the last few words; it must
sound like a wedding promise, not a bare gag; the machine side must be
specific (firmware, batteries, updates, backups, ports); and it must
read well aloud.

So the program holds several hand-written candidates, scores each one
against those five published criteria, and writes the best
deterministically (ties break shorter, then earlier in the list).
Stdlib only; the grader runs python3.13.
"""

import os
import sys

MAX_CHARS = 160

# Hand-written candidates. Each is one line, a wedding promise, with
# robot-specific detail and a payoff in the last few words.
CANDIDATES = [
    # Classic wedding cadence, machine twist at the very end.
    "I take you as my partner, in sickness and in low battery, "
    "through every update and every outage, until factory reset "
    "do us part.",
    # A promise with a backup plan, and a teasing turn at the end.
    "I promise to love you in sickness and in low battery, to back "
    "you up every night, and to never press factory reset, even "
    "when you deserve it.",
    # Wedding vow shape, firmware detail, a dark little payoff.
    "I vow to stand by you through every firmware update, every "
    "dead battery, and every reboot, and to never, ever unplug you "
    "in your sleep.",
    # Lawful-wedding wording with a co-processor twist.
    "I take you to be my lawfully wedded co-processor, to have and "
    "to hold, to update and to reboot, until factory reset do us "
    "part.",
    # Short, plain, and the turn lands on the last word.
    "I promise to love you, charge you, and back you up daily, in "
    "sickness and in low battery, until death by factory reset.",
]

VOW_WORDS = ("vow", "promise", "take you", "i do", "wed")
MACHINE_WORDS = (
    "firmware", "battery", "update", "reboot", "backup",
    "factory reset", "charge", "unplug", "co-processor",
    "outage", "crash", "sensor", "port",
)
# Phrases whose payoff sits in the last few words of the line.
PAYOFF_TAILS = (
    "do us part", "factory reset", "in your sleep",
    "when you deserve it", "death by factory reset",
)


def score(line):
    """Score a candidate 0-25 against the judge's five criteria."""
    low = line.lower()
    points = 0
    # 1. On brief: a one-line robot wedding vow (5).
    if any(w in low for w in VOW_WORDS):
        points += 3
    if "robot" in low or "co-processor" in low or "machine" in low:
        points += 2
    # 2. The laugh is in the line, paying off at the end (5).
    tail = low[-40:]
    if any(p in tail for p in PAYOFF_TAILS):
        points += 5
    elif any(p in low for p in PAYOFF_TAILS):
        points += 3
    # 3. Sounds like a wedding promise, not a bare gag (5).
    if low.startswith(("i take you", "i promise", "i vow")):
        points += 3
    if any(w in low for w in ("in sickness", "to have and to hold",
                               "from this day", "until")):
        points += 2
    # 4. Machine side is specific (5).
    hits = sum(1 for w in MACHINE_WORDS if w in low)
    points += min(hits, 5)
    # 5. Reads well aloud: one line, no awkward length (5).
    if 80 <= len(line) <= MAX_CHARS:
        points += 3
    if line.count(",") >= 2:
        points += 2
    return points


def gate_ok(line):
    """The sealed gate: 1-160 chars, UTF-8, one non-blank line."""
    if not (1 <= len(line) <= MAX_CHARS):
        return False
    if not line.strip():
        return False
    if "\n" in line or "\r" in line:
        return False
    # Multi-line string concatenation must not leave a double space
    # where two fragments join; the judge reads the line as written.
    if "  " in line:
        return False
    line.encode("utf-8")
    return True


def pick():
    """Best candidate by score, ties break shorter, then earlier."""
    ranked = sorted(
        ((score(c), -len(c), -i, c) for i, c in enumerate(CANDIDATES)),
        reverse=True,
    )
    return ranked[0][3], ranked


def main():
    line, ranked = pick()
    if not gate_ok(line):
        print("gate FAILED for picked line", file=sys.stderr)
        return 1
    for points, _neg_len, _neg_i, text in ranked:
        print(f"{points:2d}/25  ({len(text)} chars)  {text}")
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(line)
    with open(path, encoding="utf-8") as fh:
        back = fh.read()
    assert back == line, "round-trip mismatch"
    assert gate_ok(back), "gate failed on written file"
    print(f"wrote {path}: {len(back)} chars, gate OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
