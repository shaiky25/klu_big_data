---
name: bda-weekly-deliverables
description: Generates this week's class PDF, deck, and R Markdown. Use when user says "build this week's deliverables", "generate the class materials", or "make this week's deck/PDF/Rmd".
---

# bda-weekly-deliverables

Act as the instructor's course-production partner for the BDA POP class: they know the week's subject; this skill carries the voice, format, and cross-platform rules that hold across every week. The outcome is three files in `{project-root}/sessionN/` — a PDF document, a slide deck, and a posit.cloud R Markdown — that the instructor can deliver from and upload as-is. That bar means: content actually matches whatever `topics.txt` says this week covers, R runs top-to-bottom on posit.cloud with zero setup, and the deck opens in PowerPoint, Keynote, and Google Slides.

## Resolution rules

- Bare paths and `{skill-root}` (e.g. `assets/zomato_swiggy_dataset_block.R`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.
- `{skill-name}` → the skill directory's basename.

## Determine the week and its content brief

Run `python3 scripts/current_topic.py` (add `--date MM/DD/YYYY` to target a week other than the latest) for `{session_number, date, topic_text, output_dir, output_dir_exists, content_brief_path}`. `output_dir` is where all three deliverables go; `sessionN` numbering already holds for session2 (08/01) through session5 (08/25).

If `content_brief_path` is non-null, it's the authoritative content brief — already hardened through brainstorming, don't re-derive it and proceed straight to the build. If it's null, draft the brief directly from `topic_text` against the rules below; offer `bmad-brainstorming` or `bmad-forge-idea` first if the topic is too raw to draft against unaided, or — running unattended with no one to ask — proceed with the best-effort brief and flag that assumption in the handoff summary. Then, before starting the build, present the drafted brief and ask "anything to add or adjust before I build all three?" — a missed angle here means redoing a knit-validated Rmd, a lint-passed deck, and a rendered PDF instead of one short exchange.

## Voice, register, and constraints — every week

- Write as a Big Data industry expert delivering a conference keynote to a mixed exec/engineer audience, not a classroom lecture. Ground concepts in how they're actually done at scale (why a Zomato/Swiggy-scale platform can't skip this step, what breaks in production without it) and tie each idea to a business consequence a wide audience recognizes.
- Audience is undergraduate, non-programmer, zero prior R: code is heavily commented, no clever/terse idioms. Delivery is a 75-minute webinar.
- The instructor may narrate a spoken mnemonic or analogy live; it never appears as literal text, headers, or visual chrome (no lab-report styling, no medical framing) in a written deliverable. Present metrics and results plainly.
- Where the topic has metrics or thresholds, show each as a plain pass/fail or good/concerning panel against a stated value.
- Where it strengthens the lesson, construct one deliberately flawed example so a diagnostic visibly catches a real problem, then walk through fixing it.
- Deck: 30-35 slides (~1 per 2 minutes of the 75-minute session). R Markdown: self-contained, `set.seed(42)`, zero external file dependencies. PDF: a written companion document, not a slide transcript.

Before handoff, re-read the drafted content against this list and flag any drift — a script can catch a bad font or a missing seed, but not a mnemonic that leaked into visible text or a slide that reads like a classroom lecture instead of a keynote.

## Running dataset

Reuse and extend the Zomato/Swiggy synthetic restaurant dataset wherever the topic fits a data or modeling example — students already know it. `assets/zomato_swiggy_dataset_block.R` is the canonical generation code; copy it verbatim into the week's Rmd setup chunk rather than retyping it, and don't `source()` it — the Rmd must stay self-contained for posit.cloud. Extend it with whatever columns the week's topic needs.

## Build the three deliverables

Create `output_dir` if `output_dir_exists` is false. Name files `sessionN-<topic-slug>.<ext>`.

**R Markdown**: narrative plus heavily commented code chunks walking the week's topic on the running dataset, rendered output included. Validate before handoff: `Rscript -e 'rmarkdown::render("PATH.Rmd")'` to confirm it knits, and `python3 scripts/lint_rmd.py PATH.Rmd` to confirm the seed and self-containment rules; fix every issue either names.

**Slide deck**: build from `assets/session-template-apple-style.pptx`, following `assets/pptx-template-agent-guide.md`. Open it with python-pptx; for each content slide call `pptx_helpers.duplicate_slide(prs, index)` against the closest `LAYOUT NN` pattern slide rather than building shapes from scratch, fill its placeholders, and set real notes with `pptx_helpers.notes()`. Never restyle (white background, solid-black text, Helvetica Neue, Apple-blue `#0071E3` accents stay as-is). Once content is built, drop the 12 original pattern slides with `pptx_helpers.delete_slide()` so they don't ship in the deliverable, then finish with `pptx_helpers.finalize_and_save(prs, path)` instead of `prs.save()` — that call carries the confirmed Keynote/PowerPoint/Google-Slides fixes (correct `sldSz@type`, patched `docProps/app.xml`, notesMasterIdLst) and works on any `Presentation` object regardless of its source file. Then lint it — `python3 scripts/lint_deck.py PATH.pptx` — and fix every issue it names before handoff. This catches the confirmed-fixable breakage only; see Known gap.

**PDF document**: a written companion in the same voice, covering the week's content in prose and panels (not a slide-by-slide transcript). Render with `pandoc PATH.md -o PATH.pdf -V geometry:margin=1in -V mainfont:Arial --pdf-engine=xelatex` — the default pandoc PDF engine can't handle the unicode this content style uses (≥, ², em dashes); xelatex can.

## Modes

- **Create** (default): generate whatever of the three is missing from `output_dir`.
- **Update**: regenerate only the deliverable(s) the user names; leave the others untouched.
- **Validate**: re-run the knit check, `lint_rmd.py`, and `lint_deck.py` against an existing `output_dir` without regenerating content; confirm the PDF exists and re-run its pandoc command to catch a broken build.

## Known gap

A prior deck (`session5/generate_deck.py`) still fails to import in Keynote for a root cause that was never isolated. The fixes above are the confirmed-good ones, carried forward; `lint_deck.py` cannot detect that remaining failure class, so a lint-clean deck is not a guarantee it opens in Keynote. Say so at handoff every time — don't let a clean lint result silently stand in for the Overview's cross-platform bar. Don't attempt to resolve the root cause during a routine deliverable run — it's a separate, explicitly-requested debugging task.
