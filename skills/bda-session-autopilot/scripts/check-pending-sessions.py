#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bucket topics.txt's latest entry into pending / changed / current against build-state.json.

Mirrors the dated-entry parsing in bda-weekly-deliverables' current_topic.py (one entry
per class: a line that is only a date MM/DD/YYYY, followed by bullet lines, in
chronological order; sessionN folders are named by 1-indexed position) and its default
targeting (the latest dated entry) -- the only entry a weekly Pulse should ever act on.
An older entry with no sessionN folder is a class that already happened without one, not
a build candidate; pass --all to audit every entry instead of just the latest.

A session is:
  - "pending"  -- no {project-root}/sessionN/ folder exists yet
  - "changed"  -- sessionN/ exists, but build-state.json's recorded topic_text for that
                  date no longer matches what topics.txt says now (someone edited the
                  topic, or the folder may have been hand-edited since the last build)
  - "current"  -- sessionN/ exists and topics.txt is unchanged since the recorded build

Usage:
    check-pending-sessions.py <project-root> [--all] [--topics-file PATH] [--state-file PATH]

Prints one JSON object to stdout: {"pending": [...], "changed": [...], "current": [...]}.
Each entry: {date, session_number, output_dir, topic_text}. Default scope is the latest
dated entry only; --all buckets every entry in topics.txt (audit use, never auto-build).
"""
import argparse
import json
import re
import sys
from pathlib import Path

DATE_LINE = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})\s*$", re.MULTILINE)


def parse_entries(text: str) -> list[dict]:
    matches = list(DATE_LINE.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        entries.append({"date": m.group(1), "topic_text": text[start:end].strip()})
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_root")
    ap.add_argument("--all", action="store_true",
                     help="bucket every dated entry, not just the latest (audit only -- never auto-build the results)")
    ap.add_argument("--topics-file", default=None, help="default: {project-root}/topics.txt")
    ap.add_argument("--state-file", default=None,
                     help="default: {project-root}/_bmad/memory/bda-session-autopilot/build-state.json")
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    topics_path = Path(args.topics_file) if args.topics_file else project_root / "topics.txt"
    state_path = (Path(args.state_file) if args.state_file
                  else project_root / "_bmad" / "memory" / "bda-session-autopilot" / "build-state.json")

    if not topics_path.exists():
        print(f"topics file not found: {topics_path}", file=sys.stderr)
        return 2

    entries = parse_entries(topics_path.read_text())
    if not entries:
        print(f"no dated entries found in {topics_path}", file=sys.stderr)
        return 2

    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
        except json.JSONDecodeError as e:
            print(f"warning: {state_path} is not valid JSON ({e}); treating as empty", file=sys.stderr)

    scoped = entries if args.all else entries[-1:]

    buckets = {"pending": [], "changed": [], "current": []}
    for entry in scoped:
        session_number = entries.index(entry) + 1
        output_dir = project_root / f"session{session_number}"
        record = {
            "date": entry["date"],
            "session_number": session_number,
            "output_dir": str(output_dir),
            "topic_text": entry["topic_text"],
        }
        if not output_dir.exists():
            buckets["pending"].append(record)
            continue
        recorded = state.get(f"session{session_number}", {})
        if recorded.get("topic_text") != entry["topic_text"]:
            buckets["changed"].append(record)
        else:
            buckets["current"].append(record)

    print(json.dumps(buckets, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
