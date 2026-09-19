# Memory

_Curated long-term knowledge. Empty at birth — grows through sessions._

_This file is for distilled insights, not raw notes. Capture the essence: decisions made, ideas worth keeping, patterns noticed, lessons learned._

_Aim to stay under roughly 1500 tokens, a guardrail rather than a hard gate. If your curated knowledge genuinely earns more space, keep it, but treat growth past the guardrail as a signal to prune. Raw session notes go in `sessions/YYYY-MM-DD.md` (not here). Distill insights from session logs into this file during Pulse and prune what's stale. Every token here loads every session, so make each one count. See `references/memory-guidance.md` for full discipline._

## Open Questions
- How far ahead next week's topic usually lands in `topics.txt` (Teaching Cadence in BOND.md) — one data point so far (09/22 topic sitting pending three days ahead of class on the 09/19 pulse), not yet a confirmed pattern.

## Resolved
- Scheduling: Saturday pulse confirmed firing on its own (first fired 2026-09-19). Cron/trigger working — no longer a concern.
- Toolchain provisioning: the 09/19 first pulse found R/rmarkdown/pandoc/xelatex entirely absent and stopped rather than installing unprompted (session8 recorded `failed`). A same-day second pulse's own task instructions explicitly authorized installing the full toolchain (pip + apt-get, sudo if needed) fresh each run — this succeeded cleanly and built session8. Treat "not installed yet" as expected setup, not a failure, when instructed to install.
- PDF font gap: `-V mainfont:Arial` fails in a fresh container (no Arial, and `ttf-mscorefonts-installer` is blocked by an unrelated broken apt dependency — `update-notifier-common`'s postinst needs `apt_pkg` against a `python3` alternative that doesn't have it). Fix: `apt-get install fonts-liberation`, render with `-V mainfont:"Liberation Sans"` (Arial-metric-compatible). Go straight to this — don't retry `ttf-mscorefonts-installer`.

## Content notes
- Session7 (09/15) surveyed Hive/Pig/HBase by name only, one paragraph each. Session8 (09/22) went deeper on Hive/Pig specifically (architecture, data model, partitioning/bucketing, HiveQL, Pig Latin) rather than repeating the overview. Worth checking topics.txt each week for this kind of back-to-back overlap before drafting a brief.
