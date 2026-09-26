#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Parse topics.yaml and identify one week's class topic.

topics.yaml holds a top-level `sessions` list, each entry a `date`
(YAML date, i.e. YYYY-MM-DD), a `status` (`pending` or `completed`),
and a `topics` list of bullet strings, in chronological order. Session
folders (session2/, session3/, ...) are named by the 1-indexed position
of their date among all entries -- confirmed against session2=entry2
(08/01) through session5=entry5 (08/25).

Also globs for a brainstorm-intent.md whose text contains the target
date, since a hardened brief (when one exists) is the authoritative
content source over topics.yaml's terse bullets.

Usage:
    current_topic.py [--topics-file PATH] [--date MM/DD/YYYY]
        [--brainstorm-glob GLOB] [--mark-completed]

With no --date, targets the earliest entry with status: pending (falls
back to the latest entry if none are pending). Prints one JSON object
to stdout; exits 1 with a message on stderr if topics.yaml is missing
or --date isn't found in it.

--mark-completed flips the resolved entry's status to `completed` in
topics.yaml in place, after printing the (pre-update) JSON result --
run it once the week's three deliverables are generated and validated.
"""
import argparse
import glob
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ANY_DATE = re.compile(r"\d{2}/\d{2}/\d{4}")


def find_content_brief(target_date: str, pattern: str) -> str | None:
    for path in sorted(glob.glob(pattern)):
        text = Path(path).read_text(errors="ignore")
        m = ANY_DATE.search(text)
        if m and m.group(0) == target_date:
            return path
    return None


def parse_entries(text: str) -> list[dict]:
    data = yaml.safe_load(text) or {}
    entries = []
    for session in data.get("sessions", []):
        raw_date = session["date"]
        d = raw_date if isinstance(raw_date, date) else datetime.strptime(raw_date, "%Y-%m-%d").date()
        topics = session.get("topics", [])
        entries.append({
            "date": d.strftime("%m/%d/%Y"),
            "date_iso": d.isoformat(),
            "status": session.get("status", "pending"),
            "topics": topics,
            "topic_text": "\n".join(f"* {t}" for t in topics),
        })
    return entries


def mark_completed(path: Path, date_iso: str) -> None:
    text = path.read_text()
    block_pat = re.compile(
        rf"(?m)^(  - date:\s*{re.escape(date_iso)}\s*\n)((?:(?!^  - date:).*\n?)*)"
    )
    m = block_pat.search(text)
    if not m:
        raise ValueError(f"could not find session block for {date_iso} in {path}")
    header, body = m.group(1), m.group(2)
    if re.search(r"^\s*status:\s*\S+\s*$", body, re.MULTILINE):
        new_body = re.sub(r"(^\s*status:\s*)\S+(\s*$)", r"\g<1>completed\g<2>", body, count=1, flags=re.MULTILINE)
    else:
        new_body = "    status: completed\n" + body
    path.write_text(text[: m.start()] + header + new_body + text[m.end() :])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics-file", default="topics.yaml")
    ap.add_argument("--date", default=None, help="MM/DD/YYYY; default is the latest dated entry")
    ap.add_argument("--brainstorm-glob", default="_bmad-output/brainstorming/*/brainstorm-intent.md")
    ap.add_argument("--mark-completed", action="store_true", help="flip the resolved entry's status to completed")
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
        idx = next((i for i, e in enumerate(entries) if e["status"] == "pending"), len(entries) - 1)

    session_number = idx + 1
    result = {
        "date": entries[idx]["date"],
        "status": entries[idx]["status"],
        "topics": entries[idx]["topics"],
        "topic_text": entries[idx]["topic_text"],
        "session_number": session_number,
        "output_dir": f"session{session_number}",
        "output_dir_exists": Path(f"session{session_number}").exists(),
        "content_brief_path": find_content_brief(entries[idx]["date"], args.brainstorm_glob),
    }
    print(json.dumps(result, indent=2))

    if args.mark_completed:
        mark_completed(path, entries[idx]["date_iso"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
