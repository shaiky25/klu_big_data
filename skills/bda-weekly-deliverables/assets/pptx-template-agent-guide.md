# Agent Guide: Apple-Style Session Template

File: `session-template-apple-style.pptx` (16:9, light theme — white background, solid black
primary text, mid-gray secondary text, Apple-blue accent). A second reference asset,
`bento-design-reference.pptx`, is available for additional bento-grid/accent-color
inspiration if a slide calls for it — not wired into the build pipeline, look but don't import
wholesale.

## How to use this template

1. **Open with python-pptx**: `prs = Presentation("assets/session-template-apple-style.pptx")`.
   The 12 LAYOUT slides are `prs.slides[0]` through `prs.slides[11]`, in the same
   order as the catalog below (index = catalog number − 1).
2. **Do NOT design slides from scratch.** For each content slide you need, call
   `pptx_helpers.duplicate_slide(prs, index)` against the closest LAYOUT slide's
   index — it returns a new slide with that layout's shapes copied in, ready to edit.
   Call it as many times as you need against the same index (e.g. Key Points
   for three different sections); the source pattern slide is untouched.
3. **Replace every `[BRACKETED]` placeholder** on the duplicate with real content
   (`shape.text_frame.text = "..."` or edit the relevant paragraph/run). Delete any
   placeholder shape you don't need — never leave brackets visible.
4. **Set real speaker notes** on the duplicate with `pptx_helpers.notes(slide, text)`.
   The template's own notes are authoring instructions for step 4 below, not content
   to carry into the delivered deck — duplication does not copy them.
5. **Read the speaker notes of each of the 12 original LAYOUT slides** before using
   it — they carry per-layout rules.
6. **Never restyle**: keep the white background, solid-black text, Helvetica Neue type,
   Apple-blue (`#0071E3`) accents, and generous whitespace. The design *is* the template.
7. **Once every content slide is built**, drop the 12 original LAYOUT pattern
   slides so they don't ship in the delivered deck: `for _ in range(12): pptx_helpers.delete_slide(prs, 0)`
   (they're always the first 12 at this point). Then call
   `pptx_helpers.finalize_and_save(prs, path)` — never `prs.save()` directly.

## Layout catalog

| # | Layout | Use for |
|---|--------|---------|
| 01 | Cover | Session title slide (use once) |
| 02 | Section | Opening a major part ("PART 2 — STORAGE") |
| 03 | Statement | One big idea, huge ("Bring the compute to the data.") |
| 04 | Key Points | ≤3 short phrases — never sentences |
| 05 | Two Column | Comparisons / pairs (HDFS vs YARN, Map vs Reduce) |
| 06 | Stat | A number that deserves a gasp ("3×", "128 MB") |
| 07 | Image | Full-bleed photo/diagram + short caption |
| 08 | Quote | One memorable line + source |
| 09 | Diagram | Architecture/flow visuals — label every box |
| 10 | Code | ≤12 lines, Menlo font, real runnable code |
| 11 | Steps | 3-stage processes (map → shuffle → reduce) |
| 12 | Closing | "Thank you." + next-week teaser |

## Apple-keynote content rules (non-negotiable)

- **One idea per slide.** If a slide needs "and also…", split it.
- **Headlines ≤ 8 words.** Big type does the persuading.
- **Phrases, not sentences.** The detail lives in spoken narration, not on screen.
- **Numbers get the Stat layout.** Never bury "3× replication" in a bullet.
- **No paragraphs. No clip art. No bullet walls.**
- **Images full-bleed or not at all.** A small image floating on white looks broken.
- **Code is real and short.** ≤12 lines, and narrate the 1–2 lines that matter.
- **Accent color is rationed.** Blue marks the *one* thing to look at per slide.
- **End sections with a Statement slide**, not a summary bullet list. Summaries are
  for handouts; the last thing on screen should be the idea you want remembered.

## Deck structure for a 75-min session

Cover → Section → (Statement → Key Points / Diagram / Steps / Stat / Code…) →
Section → … → Statement (the takeaway) → Closing.
Aim for ~1 slide per 2 minutes. A 75-min session ≈ 30–35 slides.
