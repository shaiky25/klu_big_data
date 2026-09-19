# Memory

_Curated long-term knowledge. Empty at birth — grows through sessions._

_This file is for distilled insights, not raw notes. Capture the essence: decisions made, ideas worth keeping, patterns noticed, lessons learned._

_Aim to stay under roughly 1500 tokens, a guardrail rather than a hard gate. If your curated knowledge genuinely earns more space, keep it, but treat growth past the guardrail as a signal to prune. Raw session notes go in `sessions/YYYY-MM-DD.md` (not here). Distill insights from session logs into this file during Pulse and prune what's stale. Every token here loads every session, so make each one count. See `references/memory-guidance.md` for full discipline._

## Open Questions
- How far ahead next week's topic usually lands in `topics.txt` (Teaching Cadence in BOND.md) — one data point so far (09/22 topic sitting pending three days ahead of class on the 09/19 pulse), not yet a confirmed pattern.

## Resolved
- Scheduling: Saturday pulse confirmed firing on its own (first fired 2026-09-19). Cron/trigger working — no longer a concern.
- Toolchain provisioning: the 09/19 first pulse found R/rmarkdown/pandoc/xelatex entirely absent in the container and stopped rather than apt-get installing them unprompted (session8 recorded `failed`). Later runs' own task instructions explicitly authorize installing the full toolchain (pip + apt-get, sudo if needed) fresh each run, since this is an ephemeral cloud environment — treat "not installed yet" as expected, not a failure, and only stop if an install itself errors.
