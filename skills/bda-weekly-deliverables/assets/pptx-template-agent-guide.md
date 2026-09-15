# Agent Guide: Apple-Style Session Template

File: `session-template-apple-style.pptx` (16:9, dark theme)

## How to use this template

1. **Open the .pptx** in your slide tooling (or with python-pptx).
2. **Do NOT design slides from scratch.** For each slide you need, **duplicate the
   closest LAYOUT slide** (slides are named `LAYOUT 01 — Cover`, etc.).
3. **Replace every `[BRACKETED]` placeholder** with real content. Delete any
   placeholder you don't need — never leave brackets visible.
4. **Read the speaker notes of each layout** before using it — they carry
   per-layout rules.
5. **Never restyle**: keep the near-black background, Helvetica Neue type,
   Apple-blue (`#0071E3`) accents, and generous whitespace. The design *is* the template.

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
- **Images full-bleed or not at all.** A small image floating on black looks broken.
- **Code is real and short.** ≤12 lines, and narrate the 1–2 lines that matter.
- **Accent color is rationed.** Blue marks the *one* thing to look at per slide.
- **End sections with a Statement slide**, not a summary bullet list. Summaries are
  for handouts; the last thing on screen should be the idea you want remembered.

## Deck structure for a 75-min session

Cover → Section → (Statement → Key Points / Diagram / Steps / Stat / Code…) →
Section → … → Statement (the takeaway) → Closing.
Aim for ~1 slide per 2 minutes. A 75-min session ≈ 30–35 slides.
