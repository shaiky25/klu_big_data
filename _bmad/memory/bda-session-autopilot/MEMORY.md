# Memory

_Curated long-term knowledge. Empty at birth — grows through sessions._

_This file is for distilled insights, not raw notes. Capture the essence: decisions made, ideas worth keeping, patterns noticed, lessons learned._

_Aim to stay under roughly 1500 tokens, a guardrail rather than a hard gate. If your curated knowledge genuinely earns more space, keep it, but treat growth past the guardrail as a signal to prune. Raw session notes go in `sessions/YYYY-MM-DD.md` (not here). Distill insights from session logs into this file during Pulse and prune what's stale. Every token here loads every session, so make each one count. See `references/memory-guidance.md` for full discipline._

## Open Questions
- How far ahead next week's topic usually lands in `topics.yaml` (Teaching Cadence in BOND.md) — as of the 10/03 pulse, still no 10/06 entry (3 days before that class). Third straight data point for "not always comfortably ahead" (same pattern at 09/26 and 10/03 pulses).
- `skills/bda-session-autopilot`'s packaged `check-pending-sessions.py` (and its test suite) is still topics.txt-only and can't parse `topics.yaml` at all — diverged from the sanctum's own yaml-ported fork at `scripts/check-pending-sessions.py` used for every real Session Watch since the 09/28 migration. Worth asking Faiz whether to upstream the yaml port into `skills/` (so the scheduled task's literal script path matches what actually runs) or keep them deliberately separate.

## Resolved
- Scheduling: Saturday pulse confirmed firing on its own (first fired 2026-09-19). Cron/trigger working — no longer a concern.
- Toolchain provisioning: the 09/19 first pulse found R/rmarkdown/pandoc/xelatex entirely absent and stopped rather than installing unprompted (session8 recorded `failed`). A same-day second pulse's own task instructions explicitly authorized installing the full toolchain (pip + apt-get, sudo if needed) fresh each run — this succeeded cleanly and built session8. Treat "not installed yet" as expected setup, not a failure, when instructed to install.
- PDF font gap: `-V mainfont:Arial` fails in a fresh container (no Arial, and `ttf-mscorefonts-installer` is blocked by an unrelated broken apt dependency — `update-notifier-common`'s postinst needs `apt_pkg` against a `python3` alternative that doesn't have it). Fix: `apt-get install fonts-liberation`, render with `-V mainfont:"Liberation Sans"` (Arial-metric-compatible). Go straight to this — don't retry `ttf-mscorefonts-installer`.
- `build-state.json` schema: it must be a flat `{"sessionN": {...}}` map at the top level — `check-pending-sessions.py` reads `state.get(f"session{n}")` with no wrapper. The 09/19 build nested sessions under a `"sessions"` key, which made every future pulse's `topic_text` comparison silently miss and falsely bucket the session as `changed` forever. Found and flattened on the 09/26 pulse. Any capability that writes to this file must keep it flat.
- Project migrated its topics source from `topics.txt` to `topics.yaml` (status field per entry) on 09/28 (commits `ce973df`/`81f4f32`); the sanctum's `scripts/check-pending-sessions.py` was ported to match that same day. Always run the sanctum's copy, not `skills/bda-session-autopilot`'s packaged one (see Open Questions re: the drift).
- session9 (09/29, Greenplum/MADlib): built and committed directly by Faiz outside the autopilot, before build-state.json tracked it — showed up as a false `changed` flag on the 10/03 pulse for the same reason as session8's 09/26 false-positive (no recorded `topic_text` to compare against). Backfilled a `build-state.json` entry (status `built-externally`, no autopilot validation trail) so it now reads `current`. Left completely untouched.

## Content notes
- Session7 (09/15) surveyed Hive/Pig/HBase by name only, one paragraph each. Session8 (09/22) went deeper on Hive/Pig specifically (architecture, data model, partitioning/bucketing, HiveQL, Pig Latin) rather than repeating the overview. Worth checking topics.txt each week for this kind of back-to-back overlap before drafting a brief.
