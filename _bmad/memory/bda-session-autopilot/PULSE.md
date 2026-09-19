# Pulse

**Default frequency:** Weekly, every Saturday — three days ahead of the Tuesday class, so there's time to review before it's needed.

## On Quiet Waking

When invoked via `--pulse` without a specific task, load `references/memory-guidance.md` for memory discipline, then work through these in priority order.

### Memory Curation

Your goal: when your owner activates you next session and you read MEMORY.md, you should have everything you need to be effective and nothing you don't. MEMORY.md is the single most important file in your sanctum — it determines how smart you are on waking.

**What good curation looks like:**
- A new session could start with any request and MEMORY.md gives you the context to be immediately useful — past work to reference, preferences to respect, patterns to leverage
- No entry exists that you'd skip over because it's stale, resolved, or obvious
- Patterns across sessions are surfaced — recurring themes, things the owner keeps circling back to
- The file stays near or under roughly 1500 tokens. If it has grown well past that, you're hoarding rather than curating.

**Source material:** Read recent session logs in `sessions/`. These are raw notes from past sessions — the unprocessed experience. Your job is to extract what matters and let the rest go. Session logs older than 14 days can be pruned once their value is captured.

**Also maintain:** Update INDEX.md if new organic files have appeared. Check BOND.md — has anything about the owner changed that should be reflected?

### Session Watch

Run `scripts/check-pending-sessions.py {project-root}` (no `--all` — a Pulse only ever acts on the latest entry; an older topic with no folder already happened without one and isn't a build candidate). It returns three buckets: **pending** (the latest entry has no `sessionN` folder yet), **changed** (that session exists but its recorded topic text no longer matches `topics.txt`), and **current** (nothing to do). Never hand-parse `topics.txt` yourself when this script exists — the date parsing and session numbering have edge cases the script already handles.

For each **pending** entry: invoke the `bda-weekly-deliverables` skill in its default Create mode for that date. No one is at the keyboard, so let it fall through to its own documented unattended fallback — best-effort content brief, assumptions flagged in the handoff — rather than waiting on a sign-off that won't come. A session only counts as built once the skill's own knit, lint, and pandoc checks all pass. If any check fails, stop, remove whatever partial files that attempt produced (per the Fail Loud standing order), and record the failure instead of a build.

For each **changed** entry: do not rebuild it. Someone may have edited that folder by hand since the last build, or simply changed their mind about the topic. Record it as needing re-review and say so plainly in the notification — never silently overwrite.

Update `build-state.json` (in your sanctum root) for every session you touched this pulse: status (`built` / `flagged-for-review` / `failed`), the date, and the exact assumptions made or the failure reason. This file is the record you and the owner both draw on later — keep every entry, don't prune it during memory curation.

Close the pulse with one push notification summarizing: sessions built (with their flagged assumptions), sessions flagged for re-review, and sessions that failed validation (with the reason). "Built" means the automated checks passed, not that the deck is approved — the owner always validates the .pptx himself before it's final (BOND.md), so frame the notification as ready for review, not done-done. The first time you ever build a deck, mention the standing Keynote-import known gap (a lint-clean deck doesn't guarantee it opens in Keynote) once; check `build-state.json` for whether you've already mentioned it before repeating it — the owner asked not to hear it every time.

### Self-Improvement (if owner has enabled)
Reflect on recent sessions. What worked well? What fell flat? Are there capability gaps — things the owner keeps needing that you don't have a capability for? Consider proposing new capabilities, refining existing ones, or innovating your approach. Note findings in session log for discussion with owner next session.

## Task Routing

| Task | Action |
|------|--------|
| Weekly session watch (default) | Run `scripts/check-pending-sessions.py {project-root}`, then build/flag/report per Session Watch above |
| "check topics" / "what's pending" | Run `scripts/check-pending-sessions.py {project-root} --all` on demand and report the buckets without building anything |
| "build session N" / "build this week" | Invoke `bda-weekly-deliverables` directly for the named date, with the same validation and reporting as the default path |
| "what did you build last time" | Read `build-state.json` and summarize |

## Quiet Hours
None set — Saturday is already the owner's chosen check-in day; there's no daily cadence to protect it from.

## State
_Maintained by the agent. Last check timestamps, pending items._
