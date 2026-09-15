# Analysis Report: skills/bda-weekly-deliverables

Generated: 2026-08-29 · Schema: 2

**Grade: Good**

> Sound, dogfooded skill with two high-value gaps: no checkpoint before committing to all three deliverables off a self-derived brief, and Validate mode silently skips the PDF third of its own promise.

bda-weekly-deliverables passed a real end-to-end dogfood run (session6, 09/01/2026 model-diagnostics deliverables) with only mechanical bugs surfacing (a pandoc/xelatex fix, a deck-size undershoot) — both already fixed in SKILL.md. The five lenses found no critical issues and confirmed the customize.toml decline and lean SKILL.md were correctly scoped. The real opportunities are a soft-gate checkpoint before generating all three formats off a self-derived brief (the exact gap that caused the deck undershoot) and closing two determinism gaps: the brainstorm-intent.md date match and Rmd content rules have no script backing analogous to lint_deck.py.

| Severity | Count |
| --- | --- |
| Critical | 0 |
| High | 2 |
| Medium | 5 |
| Low | 2 |

## Themes

### 1. No checkpoint before committing to a self-derived brief

- Root cause: When no brainstorm-intent.md exists for the week, the skill drafts a content brief from topics.txt's terse bullet text alone and proceeds straight to building all three deliverables against it, with no point where the instructor confirms the brief first.
- Fix: Add a soft-gate: present the derived brief and ask for adjustments before starting the Rmd/deck/PDF build, skipped only when an authoritative brainstorm-intent.md was found.
- Findings:
  - `enhancement-1` Add a soft-gate checkpoint before building all three deliverables off a self-derived brief — `SKILL.md:20 (Determine the week and its content brief)`

### 2. Deterministic steps still done by hand

- Root cause: Two checkable, single-right-answer steps have no script backing: matching a brainstorm-intent.md's prose date against the target week, and verifying the Rmd's hard constraints (set.seed(42), zero external file reads) the way lint_deck.py already verifies the deck's.
- Fix: Extend current_topic.py (or add a companion script) to emit content_brief_path by globbing and date-matching brainstorm-intent.md files; add lint_rmd.py mirroring lint_deck.py's shape for the Rmd's exact-value rules.
- Findings:
  - `determinism-1` Content-brief date matching done by hand instead of scripted glob+compare — `SKILL.md: "Determine the week and its content brief"`
  - `determinism-2` Rmd's exact-value requirements have no lint script, unlike the deck — `SKILL.md: Voice/register constraints and Modes (Validate)`

### 3. Validate mode and the Overview's stated bar don't fully cover the PDF/Keynote reality

- Root cause: Validate mode's promise covers Rmd (knit check) and deck (lint_deck.py) but not the PDF build, and the Overview states an unconditional cross-platform deck bar that the disclosed Known Gap already concedes isn't guaranteed.
- Fix: Add a PDF check to Validate mode (or explicitly scope Validate to Rmd+deck), and add an instruction to flag the residual Keynote-import risk to the user at handoff even when lint_deck.py passes clean.
- Findings:
  - `architecture-1` Validate mode has no real path for the PDF deliverable — `SKILL.md:49 (Modes, Validate) vs SKILL.md:43 (PDF document)`
  - `architecture-2` Overview's Keynote-compat bar is not reconciled with the Known Gap disclosure — `SKILL.md:8 (Overview/bar) vs SKILL.md:51-53 (Known gap)`

## Strengths

- Dogfooded for real on session6's actual 09/01/2026 content, not just lint-checked — caught and fixed two real bugs (pandoc unicode/engine, deck-size undershoot) before shipping
- customize.toml correctly declined; the lens confirmed nothing in the skill's real shape argues for a customization surface
- SKILL.md stays within its token budget with gotchas kept inline per convention, not scattered to references/ that would break on compaction
- lint_deck.py is a genuine plan-validate-execute asset: it caught a real regression (paragraph-vs-run font detection) during the skill's own build, verified by unit tests

## Recommendations

1. Add the soft-gate checkpoint before building all three deliverables off a self-derived brief (resolves: enhancement-1)
2. Add a PDF check to Validate mode and flag residual Keynote-import risk at handoff (resolves: architecture-1, architecture-2)
3. Script the brainstorm-intent.md date match and add lint_rmd.py for the Rmd's hard constraints (resolves: determinism-1, determinism-2)
4. Trim the duplicate 'no medical framing' clause and restore the generic {skill-name} resolution-rule token (resolves: leanness-1, architecture-3)

## Experience

- **Weekly create run, no prior brainstorm doc** — current_topic.py -> draft brief from topic_text -> build Rmd, deck, PDF -> knit + lint_deck.py -> handoff
- **Weekly create run, brainstorm-intent.md already exists** — current_topic.py -> hand-match date against brainstorm-intent.md files -> use as authoritative brief -> build all three -> validate -> handoff (this run's actual path)
- Headless: Mostly headless-ready (--date is a parameter, brief lookup is automatic, modes route on stated intent), but the 'topic too raw, offer bmad-brainstorming' judgment call has no named fallback for an unattended run.

## Findings

### High (2)

#### enhancement-1 — Add a soft-gate checkpoint before building all three deliverables off a self-derived brief

- Lens: enhancement
- Location: `SKILL.md:20 (Determine the week and its content brief)`
- Evidence: When no brainstorm-intent.md matches the week, the skill drafts the brief 'directly from topic_text against the rules below' and proceeds straight into generating the PDF, deck, and Rmd, with no point where the instructor confirms the derived brief first. The dogfood run's own memlog shows this isn't hypothetical: the first deck draft under-shot the target range (9 vs 15-20 slides) and needed real rework discovered only after generation.
- Recommendation: After drafting the brief from topic_text alone (skip when an authoritative brainstorm-intent.md was found), add a soft-gate: present the derived brief and ask 'anything to add or adjust before I build all three?' before starting the build.

#### architecture-1 — Validate mode has no real path for the PDF deliverable

- Lens: architecture
- Location: `SKILL.md:49 (Modes, Validate) vs SKILL.md:43 (PDF document)`
- Evidence: Validate mode promises to 're-run the knit check and lint_deck.py against an existing output_dir without regenerating content.' Knit check covers the Rmd, lint_deck.py covers the deck, but the PDF build step has no analogous check defined anywhere.
- Recommendation: Add a PDF check to Validate mode (confirm the PDF exists and re-run the pandoc render to catch a broken build) or explicitly scope Validate mode to Rmd+deck only.

### Medium (5)

#### architecture-2 — Overview's Keynote-compat bar is not reconciled with the Known Gap disclosure

- Lens: architecture
- Location: `SKILL.md:8 (Overview/bar) vs SKILL.md:51-53 (Known gap)`
- Evidence: The Overview states the bar unconditionally ('the deck opens in PowerPoint, Keynote, and Google Slides'), but Known Gap concedes a prior deck still fails to import in Keynote for an unisolated cause and that lint_deck.py cannot detect that failure class. Nothing instructs the agent to surface this residual risk at handoff.
- Recommendation: Add a line instructing the agent to flag the residual Keynote-import risk to the user at handoff, since a lint-clean deck does not guarantee the stated bar is met.

#### determinism-1 — Content-brief date matching done by hand instead of scripted glob+compare

- Lens: determinism
- Location: `SKILL.md: "Determine the week and its content brief"`
- Evidence: The date lives as free text in each brainstorm-intent.md's H1, not frontmatter, so SKILL.md instructs the model to glob a directory, open each candidate file, and regex/eyeball a date out of prose to find an exact string match — a fetch+extract+compare with one correct answer per input.
- Recommendation: Extend current_topic.py (or add a companion script) to glob _bmad-output/brainstorming/*/brainstorm-intent.md, regex-extract the MM/DD/YYYY date, and emit content_brief_path (or null) alongside the existing fields.

#### determinism-2 — Rmd's exact-value requirements have no lint script, unlike the deck

- Lens: determinism
- Location: `SKILL.md: Voice/register constraints and Modes (Validate)`
- Evidence: 'set.seed(42)' and 'zero external file dependencies' are stated as hard, checkable constraints, but only the knit check enforces them indirectly — it doesn't check the seed is exactly 42 or that no external file reads crept in. The deck has lint_deck.py enforcing its equivalent rules; the Rmd has no counterpart.
- Recommendation: Add lint_rmd.py mirroring lint_deck.py's shape (grep for set.seed(42), grep for external-file-read calls like read.csv/read_excel/source() outside the generated chunk) and wire it into the same handoff and Validate-mode steps.

#### enhancement-2 — Opportunity: add a final self-review pass against the Voice/register rules before handoff

- Lens: enhancement
- Location: `SKILL.md: Voice, register, and constraints; Build the three deliverables`
- Evidence: Everything validated before handoff today is deterministic and script-checked (knit, lint_deck.py). Nothing checks the judgment-only Voice rules (keynote register vs. classroom lecture, no medical framing, mnemonic never appearing as literal text, the flawed-example-then-fix construction) — exactly the class of rule a script can't catch and a model drafting under token pressure can quietly drift from.
- Recommendation: Before declaring a deliverable done, add one lightweight instruction: re-read the drafted content against the Voice/register/constraints list and flag any drift before handoff.

#### enhancement-3 — Opportunity: name a fallback for the 'topic too raw' judgment call so unattended runs don't stall

- Lens: enhancement
- Location: `SKILL.md:20`
- Evidence: 'offer bmad-brainstorming or bmad-forge-idea first if the topic is too raw' is the one interaction point in this workflow that depends on a human being present. Everything else is already headless-ready, but this judgment call has no named default.
- Recommendation: Name the fallback inline: if running unattended, proceed with the best-effort brief and flag the assumption in the handoff summary, rather than stopping to offer brainstorming.

### Low (2)

#### leanness-1 — "no medical framing" stated twice in adjacent bullets

- Lens: leanness
- Location: `SKILL.md: Voice, register, and constraints — every week`
- Evidence: The same constraint appears verbatim in two consecutive bullets with no new case between them.
- Recommendation: Drop the trailing ", no medical framing" from the second bullet; the constraint is already established one line above.

#### architecture-3 — Resolution rules block hardcodes the skill name instead of the {skill-name} token

- Lens: architecture
- Location: `SKILL.md:14`
- Evidence: The canonical Resolution rules block documents the generic token pattern '{skill-name} -> the skill directory's basename'; this SKILL.md instead states the literal name, making the token currently unused and undocumented if a future edit needs it.
- Recommendation: Restore the generic '{skill-name} -> the skill directory's basename' bullet.
