---
name: build-session-deliverables
description: Build and validate one week's PDF, deck, and Rmd
code: BD
added: 2026-09-14
type: external
---

# Build Session Deliverables

This capability is the `bda-weekly-deliverables` skill, not a reimplementation of it. Invoke that skill directly for the target date, in its default Create mode. It already owns the content brief, the voice and format rules, the running dataset, and its own knit/lint/pandoc validation — don't duplicate any of that logic here.

The one thing this agent adds on top: when invoking from Pulse, no one is present to answer the skill's "anything to add or adjust?" check-in, so let it fall through to its own documented unattended fallback — best-effort content brief, assumptions flagged in the handoff — rather than waiting. Carry every assumption it flags into your own pulse notification verbatim; don't summarize it away.

A session counts as built only when the skill's own validation (knit, `lint_rmd.py`, `lint_deck.py`, the pandoc PDF rebuild) all pass. If any step fails, that's a failed build, not a partial one — per the Fail Loud standing order, clean up and report it rather than leaving generated files behind.
