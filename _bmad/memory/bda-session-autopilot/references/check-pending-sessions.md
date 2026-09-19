---
name: check-pending-sessions
description: Find which topics.txt entries need building or re-review
code: WS
added: 2026-09-14
type: script
---

# Check Pending Sessions

Run `scripts/check-pending-sessions.py {project-root}`. By default it evaluates only the latest dated entry in `topics.txt` — an older entry with no `sessionN` folder is a class that already happened without one, not something to build now. It returns three buckets as JSON: `pending` (no `sessionN` folder yet), `changed` (a built session whose topic text no longer matches what `topics.txt` now says, per `build-state.json`), and `current` (already built, unchanged since). Pass `--all` only when the owner explicitly asks to audit every session ever listed — never use `--all`'s results to drive an automatic build.

Use the default (latest-only) at the start of every Pulse, and any time the owner asks what's pending or what changed. Never hand-parse `topics.txt` yourself when this script exists — the date parsing and session numbering have edge cases (multi-line bullets, blank entries, trailing dates with no body) that are exactly why this is a script and not a judgment call.
