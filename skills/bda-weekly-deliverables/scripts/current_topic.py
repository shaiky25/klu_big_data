#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Parse topics.txt and identify one week's class topic.

topics.txt holds one entry per class: a line that is only a date
(MM/DD/YYYY), followed by bullet lines of topic text, in chronological
order. Session folders (session2/, session3/, ...) are named by the
1-indexed position of their date among all dated entries in the file --
confirmed against session2=entry2 (08/01) through session5=entry5 (08/25).

Also globs for a brainstorm-intent.md whose text contains the target
date, since a hardened brief (when one exists) is the authoritative
content source over topics.txt's terse bullets.

Usage:
    current_topic.py [--topics-file PATH] [--date MM/DD/YYYY]
        [--brainstorm-glob GLOB]

With no --date, targets the latest (last) dated entry. Prints one JSON
object to stdout; exits 1 with a message on stderr if topics.txt is
missing or --date isn't found in it.
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

DATE_LINE = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})\s*$", re.MULTILINE)
ANY_DATE = re.compile(r"\d{2}/\d{2}/\d{4}")


def find_content_brief(date: str, pattern: str) -> str | None:
    for path in sorted(glob.glob(pattern)):
        text = Path(path).read_text(errors="ignore")
        m = ANY_DATE.search(text)
        if m and m.group(0) == date:
            return path
    return None


def parse_entries(text: str) -> list[dict]:
    matches = list(DATE_LINE.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        entries.append({"date": m.group(1), "topic_text": text[start:end].strip()})
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics-file", default="topics.txt")
    ap.add_argument("--date", default=None, help="MM/DD/YYYY; default is the latest dated entry")
    ap.add_argument("--brainstorm-glob", default="_bmad-output/brainstorming/*/brainstorm-intent.md")
    args = ap.parse_args()

    path = Path(args.topics_file)
    if not path.exists():
        print(f"topics file not found: {path}", file=sys.stderr)
        return 1

    entries = parse_entries(path.read_text())
    if not entries:
        print(f"no dated entries found in {path}", file=sys.stderr)
        return 1

    if args.date:
        idx = next((i for i, e in enumerate(entries) if e["date"] == args.date), None)
        if idx is None:
            print(f"date {args.date} not found in {path}", file=sys.stderr)
            return 1
    else:
        idx = len(entries) - 1

    session_number = idx + 1
    result = {
        "date": entries[idx]["date"],
        "topic_text": entries[idx]["topic_text"],
        "session_number": session_number,
        "output_dir": f"session{session_number}",
        "output_dir_exists": Path(f"session{session_number}").exists(),
        "content_brief_path": find_content_brief(entries[idx]["date"], args.brainstorm_glob),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
