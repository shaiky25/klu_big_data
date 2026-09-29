#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Bucket topics.yaml's latest entry into pending / changed / current against build-state.json.

Mirrors the dated-entry parsing in bda-weekly-deliverables' current_topic.py (a top-level
`sessions` list, each entry a `date` (YAML date, YYYY-MM-DD), a `status` (pending/completed),
and a `topics` list; sessionN folders are named by 1-indexed position) -- the only entry a
weekly Pulse should ever act on is the latest one. An older entry with no sessionN folder is
a class that already happened without one, not a build candidate; pass --all to audit every
entry instead of just the latest.

A session is:
  - "pending"  -- topics.yaml has status: pending for that date
  - "changed"  -- status: completed, but build-state.json's recorded topic_text for that
                  date no longer matches what topics.yaml says now (someone edited the
                  topic after it was marked completed)
  - "current"  -- status: completed and topics.yaml is unchanged since the recorded build

Usage:
    check-pending-sessions.py <project-root> [--all] [--topics-file PATH] [--state-file PATH]

Prints one JSON object to stdout: {"pending": [...], "changed": [...], "current": [...]}.
Each entry: {date, session_number, output_dir, topic_text}. Default scope is the latest
dated entry only; --all buckets every entry in topics.yaml (audit use, never auto-build).
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

import yaml


def parse_entries(text: str) -> list[dict]:
    data = yaml.safe_load(text) or {}
    entries = []
    for session in data.get("sessions", []):
        raw_date = session["date"]
        d = raw_date if isinstance(raw_date, date) else datetime.strptime(raw_date, "%Y-%m-%d").date()
        topics = session.get("topics", [])
        entries.append({
            "date": d.strftime("%m/%d/%Y"),
            "status": session.get("status", "pending"),
            "topic_text": "\n".join(f"* {t}" for t in topics),
        })
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_root")
    ap.add_argument("--all", action="store_true",
                     help="bucket every dated entry, not just the latest (audit only -- never auto-build the results)")
    ap.add_argument("--topics-file", default=None, help="default: {project-root}/topics.yaml")
    ap.add_argument("--state-file", default=None,
                     help="default: {project-root}/_bmad/memory/bda-session-autopilot/build-state.json")
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    topics_path = Path(args.topics_file) if args.topics_file else project_root / "topics.yaml"
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
        if entry["status"] == "pending":
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
