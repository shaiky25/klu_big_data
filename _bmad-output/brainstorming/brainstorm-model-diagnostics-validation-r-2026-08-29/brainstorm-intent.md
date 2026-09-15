# Brainstorm Intent — Model Diagnostics & Validation in R (Class 09/01/2026)

## Class metadata
- Topic source: `/Users/faiz/Downloads/__POP/BDA_POP/2026_Aug/topics.txt` — most recent dated entry = upcoming class.
- This class (09/01/2026): "Use appropriate diagnostic methods to validate the models created using R" and "Database analytical functions to fit, score and evaluate models."

## Audience & format constraints (hard)
- Undergraduate students, non-programmers, zero prior R experience.
- R code must be heavily commented, self-explanatory, no clever/terse idioms.
- Delivery: ~2 hour webinar.
- Three deliverables required, every week: PDF document, Presentation (slide deck), Markdown file for posit.cloud (students run it live).

## Voice & register
Write and present as a **Big Data industry expert delivering a conference keynote to a wide, mixed-background audience** — not a classroom lecture with cute analogies. Register: authoritative, grounded in real industry practice, accessible to non-specialists without dumbing down the substance (a conference audience ranges from execs to engineers — the same slide has to land for both).
- Ground diagnostics/validation in how it's actually done at scale in industry: why a food-delivery platform (Zomato/Swiggy-scale) can't ship a model without validation, what breaks in production when it skips this step, how "database analytical functions to fit/score/evaluate" reflects real in-database ML workflows (scoring at the data layer instead of pulling everything into R) used by data platforms today.
- Tie each diagnostic metric to a business consequence a wide audience recognizes (e.g. an unvalidated revenue model → bad forecasting decisions; a poorly validated delivery-time classifier → broken SLAs/customer trust) rather than only the statistical definition.
- This replaces the earlier "kid/illness" and "blood test" language as the register for the actual deliverables — those stay purely as the instructor's own optional spoken hook (see below), never the voice of the written materials.

## Chosen framing — SPOKEN ONLY, not written (do not put this text/wording into any deliverable)
The blood-test/doctor's-office analogy and the overfitting/underfitting "case file" illness language were the instructor's own mnemonic for talking points. They must **not** appear as literal text, headers, labels, or visual motifs (no lab-report styling, no "case file"/"℞"/red-green flag chrome) in the PDF, slides, or Markdown. Deliverables present the real metrics and results plainly. The instructor may narrate the analogy live; it stays out of the written/generated materials entirely.

The underlying structural pattern still applies to how the *content* (not its wording) is organized:
- **Pass/fail signal per metric**: each diagnostic metric shown with a clear pass/fail or good/concerning indicator against a stated threshold — plain labeling (e.g. "within range" / "flagged"), no medical framing.
- **Confirmation re-run**: cross-validation/holdout re-run shown as a distinct step that confirms (or contradicts) the first result.
- **Fit → score → evaluate shown twice**: once in R locally, once via a database analytical function — same protocol, two engines, plainly labeled as such (no "lab machine" language).
- Diagnostics walkthrough should span multiple common ML models, not just one.

## Dataset & code precedent (reuse this pattern)
- **Dataset**: Zomato/Swiggy (Indian food-delivery platforms) — students are already familiar with the industry.
- Prior-session precedent already exists at `session5/zomato-swiggy-ml-intro.R`: a self-generated synthetic restaurant dataset (`platform`, `average_cost_two`, `distance_center_km`, `rating`, `votes`, derived `estimated_revenue`, `has_online_delivery`, `price_range`) built with `set.seed(42)` so it runs identically on any machine with zero external file dependencies. It already demonstrates, heavily commented: linear regression (revenue), logistic regression (delivery yes/no), decision tree (price tier), k-means (restaurant clusters).
- **This week's script should extend that same dataset/style**, adding the diagnostic/validation layer on top of those same models: residual plots + R² + RMSE for the linear model, confusion matrix + ROC-AUC for the logistic model, cross-validation/pruning check for the tree, silhouette score for k-means — each presented plainly (metric name, value, pass/fail vs. threshold), no medical framing.
- **"Database analytical functions" beat**: re-run the same fit/score/evaluate protocol via a DB-style analytical function (e.g. R's `DBI`/`dplyr`/in-database aggregate or window functions) on the Zomato/Swiggy data, as a second, plainly-labeled engine pass.
- **Deck-build precedent**: `session5/generate_deck.py` (python-pptx) — reuse its palette/helper pattern. Must use **Arial**, not Segoe UI or other Windows-only fonts — Keynote's importer rejects the whole file on those.

## Core teaching content (this IS the deliverable content — plain, not analogy-themed)
- For **each** ML algorithm demonstrated (linear regression, logistic regression, decision tree, k-means, and others as time allows, per "span multiple common ML models" above), the walkthrough must:
  1. Fit the model on the Zomato/Swiggy dataset.
  2. Compute its relevant diagnostic metrics (R²/RMSE/residuals for regression, confusion matrix/ROC-AUC for classification, cross-validation/pruning check for trees, silhouette for clustering, etc).
  3. Go through the metrics one by one, narrating **what** each metric says and **why** the model is doing well or poorly on this specific dataset/feature choice — not generic textbook definitions, grounded in the actual numbers/plots produced.
- Where it strengthens the lesson, **deliberately construct a broken/flawed example** (e.g. an intentionally overfit deep tree, an underspecified regression, a poorly chosen feature) so students see a diagnostic actually flag a real problem — then walk through diagnosing it and fixing it live, before/after.
- Present each algorithm's metrics as a clean plain panel/table (metric, value, pass/fail vs threshold) — no lab-report/medical styling anywhere in the generated materials.

## Deliverable scope (MoSCoW)
- **Must**: presentation covering the topic in detail for the week; all framing ideas above included but light-touch (1-2 examples each); deck capped at 15-20 slides.
- **Should**: visualizations + code snapshots with results embedded directly in slides.
- **Could**: further-reading references for interested students.
- **Won't**: long/deep-dive deck — stay within 15-20 slides.

## Next Step
Hand this intent to a Claude Code skill-building process that reads `topics.txt` automatically (pulling the latest dated topic/class-date entry) and generates the PDF, Presentation, and Markdown deliverables each week following this pattern.
