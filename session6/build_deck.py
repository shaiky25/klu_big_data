"""Builds the 09/01/2026 model-diagnostics deck (16:9) with python-pptx,
via the reusable helper module. Run: python build_deck.py
"""
import sys
sys.path.insert(0, "../skills/bda-weekly-deliverables/scripts")
import pptx_helpers as h

prs = h.new_presentation()

# 1. Title -----------------------------------------------------------------
s = h.new_slide(prs)
box = s.shapes.add_textbox(h.Inches(0.7), h.Inches(1.7), h.Inches(11.9), h.Inches(1.3))
p = box.text_frame.paragraphs[0]
p.text = "Validating What You Built"
p.font.size, p.font.bold, p.font.color.rgb, p.font.name = h.Pt(40), True, h.TEXT, h.FONT
box2 = s.shapes.add_textbox(h.Inches(0.7), h.Inches(2.65), h.Inches(11.9), h.Inches(0.6))
p2 = box2.text_frame.paragraphs[0]
p2.text = "Diagnostics for Regression, Classification, Trees & Clustering — Session 09/01/2026"
p2.font.size, p2.font.color.rgb, p2.font.name = h.Pt(18), h.CYAN, h.FONT
h.add_bullets(s, h.Inches(0.7), h.Inches(3.5), h.Inches(11.9), h.Inches(3.2), [
    "Every model gets fit, scored on a holdout set, and evaluated against a threshold",
    "Four models from last session, one protocol, run twice — once in R, once as database aggregate functions",
    "One model breaks on purpose, so a diagnostic can catch it and we fix it live",
])
h.notes(s, "Set the stakes before any formulas: at Zomato/Swiggy scale, an unvalidated model is a "
           "business risk, not just a stats exercise. Roadmap: fit-score-evaluate on four models, "
           "confirm each with a holdout re-run, then the same evaluate step as DB aggregate functions.")

# 2. Why validation isn't optional -----------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Why This Isn't Optional at Scale", "The Cost of Skipping It")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(5.9), h.Inches(4.9), "What Breaks in Production",
           ["A revenue model quietly 20% off skews marketing spend across hundreds of cities",
            "A delivery-availability classifier that looks accurate in a notebook fails on restaurants it's never seen",
            "The cost shows up weeks later — in a P&L or a support queue — not in the training run"])
h.add_card(s, h.Inches(6.7), h.Inches(1.6), h.Inches(6.0), h.Inches(4.9), "The Protocol, One Line",
           ["Fit it, score it on a holdout set the model never trained on",
            "Evaluate the result against a stated threshold — a metric with no threshold is an opinion",
            "Run the same evaluate step a second way, as database aggregate functions"])
h.notes(s, "This is the framing slide. Ground each bullet in a business consequence a mixed exec/"
           "engineer audience recognizes, not a textbook definition.")

# 3. Dataset & methodology --------------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "One Dataset, One Holdout Split", "Methodology Used for Every Model Today")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(5.9), h.Inches(4.9), "The Running Dataset",
           ["Same self-generated Zomato/Swiggy restaurant dataset as last session (set.seed(42), 200 restaurants)",
            "platform, cost, distance, rating, votes — with revenue, delivery, and price tier derived from them",
            "Zero external files — runs identically on any machine"])
h.add_card(s, h.Inches(6.7), h.Inches(1.6), h.Inches(6.0), h.Inches(4.9), "The 70/30 Holdout Split",
           ["70% of restaurants train each model; the other 30% never touch training at all",
            "Every metric on the slides that follow is measured on that untouched 30%",
            "A model only gets credit for what it does on restaurants it has never seen"])
h.notes(s, "Establish the holdout methodology once here so every following slide can say 'holdout "
           "R²' or 'holdout accuracy' without re-explaining what that means.")

# 4. Linear regression: fit & metrics ---------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Linear Regression", "Predicting Restaurant Revenue")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.4), "Fit & Score",
           ["Fit on distance from city center and vote count against estimated revenue",
            "Scored on the 30% holdout set — restaurants the model never trained on"])
h.add_table(s, h.Inches(0.6), h.Inches(3.3), h.Inches(12.1), h.Inches(1.5), [
    ["Metric", "Value", "Threshold", "Status"],
    ["Holdout R²", "0.84", "≥ 0.60", "Within threshold"],
    ["Holdout RMSE (% of mean revenue)", "~17%", "≤ 20%", "Within threshold"],
])
h.notes(s, "Both checks pass comfortably here. Votes and distance genuinely explain most of the "
           "variation in this synthetic data — worth naming so students don't assume every model "
           "will look this clean.")

# 5. Linear regression: reading the panel ------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Linear Regression — Reading the Panel", "What the Residuals Tell You")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(4.9), "Beyond the Headline Number",
           ["Residual plot (actual − predicted, plotted against predicted) shows no funnel shape and no curve",
            "Errors scatter randomly around zero across the whole prediction range",
            "That randomness is what 'the model isn't missing a pattern' looks like — a curved or funnel-"
            "shaped residual plot would mean the model is systematically wrong somewhere specific",
            "R² alone can't tell you that; you have to look at the residuals"])
h.notes(s, "Show the actual residual plot from the Rmd here if presenting live. The point: R²=0.84 "
           "is necessary but not sufficient evidence the model is trustworthy — the residual shape "
           "is the second, independent check.")

# 6. Logistic regression: fit & metrics --------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Logistic Regression", "Predicting Delivery Availability")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.4), "Fit & Score",
           ["Fit on average cost and rating against has_online_delivery",
            "Scored on the same 30% holdout set"])
h.add_table(s, h.Inches(0.6), h.Inches(3.3), h.Inches(12.1), h.Inches(1.9), [
    ["Metric", "Value", "Threshold", "Status"],
    ["Holdout AUC", "0.77", "≥ 0.70", "Within threshold"],
    ["Holdout accuracy", "73%", "≥ 70%", "Within threshold"],
    ["Recall, \"no delivery\" class", "~20%", "≥ 50%", "Flagged"],
])
h.notes(s, "Both headline metrics pass. The third row is where it breaks — hold that for the next "
           "slide rather than explaining it here.")

# 7. Logistic regression: the headline-metric trap ---------------------------
s = h.new_slide(prs)
h.add_title(s, "The Headline-Metric Trap", "One Confusion Matrix Changes the Story")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(4.9), "What the Confusion Matrix Shows",
           ["Accuracy and AUC both clear a reasonable bar — that's exactly the trap a headline metric sets",
            "Of the restaurants that genuinely don't offer delivery, the model correctly flags only about 1 in 5",
            "It has learned to predict 'yes, delivery' by default, because most restaurants in this data do offer it",
            "A delivery-fleet staffing decision built on this model would badly under-plan for the offline-only "
            "segment — a real operational miss accuracy and AUC alone never surface"])
h.notes(s, "This is a naturally-occurring example, not fabricated — straight from the confusion "
           "matrix on this run. Emphasize: always look at the confusion matrix, not just the "
           "summary metrics derived from it.")

# 8. Detour: what "cross-validated" means -----------------------------------
s = h.new_slide(prs)
h.add_title(s, "A Quick Definition: \"Cross-Validated\" Error", "Needed Before the Decision Tree Section")
h.add_formula(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.3),
              "Split training data into k folds → train on k−1, validate on the 1 held out → rotate → average",
              "That average is the \"cross-validated error\" a tree reports — computed on training data alone")
h.add_card(s, h.Inches(0.6), h.Inches(3.2), h.Inches(12.1), h.Inches(3.6), "Not the Same Thing as the Holdout",
           ["k-fold cross-validation happens entirely inside the training 70% — the 30% holdout is never touched",
            "rpart repeats this automatically at every candidate tree size while it grows, recording the result "
            "as xerror in its cptable",
            "It's a second, independent overfitting check — done before the holdout evaluation on the next slide",
            "Two different words, two different slices of data: don't read 'cross-validated error' as 'holdout error'"])
h.notes(s, "Insert this before the Decision Tree section because the next two slides use 'cross-validated "
           "error' and xerror without defining them first. Whiteboard the k-fold rotation if the formula "
           "box alone doesn't land it — k=10 is rpart's default, worth naming explicitly.")

# 9. Decision Tree: overfit -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Decision Tree — Breaking It on Purpose", "No Size Limit, Weak Predictors")
h.add_formula(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.3),
              "Training accuracy: 100%   |   Holdout accuracy: 40%",
              "A 60-point gap is the signature of memorizing training data")
h.add_card(s, h.Inches(0.6), h.Inches(3.2), h.Inches(12.1), h.Inches(3.6), "What Happened",
           ["Tree grown with no depth limit (cp = 0, minsplit = 2) on rating, votes, platform, distance",
            "69 splits — rich enough to fit noise in the training restaurants perfectly",
            "rpart's own cross-validation table (built while the tree grows) already flags this: cross-validated "
            "error is worst at the tree's full, unpruned size"])
h.notes(s, "This is the deliberately broken example. Emphasize the tree didn't need a holdout set "
           "to be caught — the cptable's xerror column flags it during training, before any test-set peek.")

# 10. Decision Tree: fixed -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Decision Tree — The Fix", "Prune to the Cross-Validated Best Size")
h.add_table(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.3), [
    ["Metric", "Value", "Threshold", "Status"],
    ["Unpruned: train − holdout gap", "~60 pts", "≤ 15 pts", "Flagged"],
    ["Pruned: train − holdout gap", "~6 pts", "≤ 15 pts", "Within threshold"],
])
h.add_card(s, h.Inches(0.6), h.Inches(3.2), h.Inches(12.1), h.Inches(3.6), "The Honest Lesson",
           ["Pruned tree collapses to 1 split; train (~48%) and holdout (~42%) now land close together",
            "Absolute accuracy is still underwhelming — and that's the real finding, not a failure of pruning",
            "Pruning fixed the overfitting; it also revealed these features don't carry much price-tier signal",
            "Sometimes the fix isn't a fancier model — it's better features"])
h.notes(s, "Land the point: diagnostics did its job twice here — caught false confidence, then told "
           "the team where to actually spend effort next (features, not model complexity).")

# 11. k-Means: fit & silhouette -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "k-Means Clustering", "Restaurant Segments")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.4), "No Holdout Labels Here",
           ["Clustering has no 'correct' cluster to score against — the confirmation is trying a range of k",
            "Fit on scaled average cost and rating; k = 2 through 5 compared by silhouette score"])
h.add_table(s, h.Inches(0.6), h.Inches(3.3), h.Inches(12.1), h.Inches(1.0), [
    ["Metric", "Value", "Threshold", "Status"],
    ["Silhouette, best k (k=3)", "0.42", "≥ 0.50", "Flagged"],
])
h.notes(s, "Same protocol as every other model — fit, score, evaluate against a threshold — applied "
           "to a question with no labels: did we pick the right k?")

# 12. k-Means: reading the panel -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "k-Means — Reading the Panel", "Real Segments, Fuzzy Boundaries")
h.add_card(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(4.9), "What 0.42 Means Here",
           ["k = 3 is the best of the four values tried — but 0.42 sits below the 0.50 bar for 'clearly separated'",
            "Cost and rating alone produce segments that overlap more than they're distinct",
            "Useful to know before building a marketing plan around three crisp restaurant personas",
            "Treat the cluster boundaries as a starting point for judgment, not a hard rule"])
h.notes(s, "This is the third naturally-flagged result. Don't frame it as a failure of k-means — "
           "frame it as the diagnostic doing exactly its job: telling you how much to trust the "
           "segments before you build a plan on top of them.")

# 13. Second engine: concept -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "The Same Evaluate Step, a Second Engine", "Database Analytical Functions")
h.add_formula(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.2),
              "group_by() + summarise()  ==  the grammar dbplyr pushes straight to SQL",
              "Same protocol, no code changes to run it against a live table")
h.add_card(s, h.Inches(0.6), h.Inches(3.1), h.Inches(12.1), h.Inches(3.7), "Why This Matters in Production",
           ["Everything on the last 9 slides ran in R, in memory — every row pulled in first",
            "At platform scale, that evaluate step usually runs as an aggregate query against the database instead",
            "The grammar (group, then summarize) is identical either way — only where it executes changes"])
h.notes(s, "This is the second half of 'fit, score, evaluate' from the title slide — the same "
           "protocol, run through a different engine. Next slide shows the actual results.")

# 14. Second engine: the actual push-down ------------------------------------
s = h.new_slide(prs)
h.add_title(s, "The Actual Push-Down", "dbplyr → MySQL, Not Just a Diagram")
h.add_code(s, h.Inches(0.6), h.Inches(1.5), h.Inches(12.1), h.Inches(4.1), [
    'con <- DBI::dbConnect(RMySQL::MySQL(), dbname = "bda_pop", host = Sys.getenv("DB_HOST"))',
    'restaurants_db <- tbl(con, "restaurants")',
    "",
    "restaurants_db %>%",
    "  group_by(platform) %>%",
    "  summarise(avg_revenue = mean(estimated_revenue),",
    "            delivery_rate = mean(has_online_delivery)) %>%",
    "  show_query()   # prints the SELECT ... GROUP BY — nothing pulled into R yet",
    "  collect()      # only this line crosses the wire and returns rows",
], label="Credentials from an env var, per this environment's own no-hardcoded-secrets rule.")
h.add_card(s, h.Inches(0.6), h.Inches(5.8), h.Inches(12.1), h.Inches(1.3), "The Point of show_query()",
           ["Same group_by()/summarise() verbs from the last slide — dbplyr compiles them to real SQL, "
            "it doesn't run them row-by-row in R"])
h.notes(s, "Live-run this if a class MySQL instance is reachable (sql alias). Point at show_query()'s "
           "printed SQL first — that's the proof the grammar really does push down, not just a claim. "
           "The results table on the next slide is this query's actual output.")

# 15. Second engine: results -----------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Second Engine — The Results", "Same Numbers, Grouped by Platform and Tier")
h.add_table(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(1.5), [
    ["Platform", "Restaurants", "Avg. Revenue", "Avg. Abs. Error", "Delivery Rate"],
    ["Swiggy", "111", "1,642", "242", "71%"],
    ["Zomato", "89", "1,776", "277", "72%"],
])
h.add_table(s, h.Inches(0.6), h.Inches(3.5), h.Inches(12.1), h.Inches(2.0), [
    ["Price Tier", "Restaurants", "Delivery Rate", "Avg. Rating"],
    ["Budget", "25", "40%", "3.08"],
    ["Moderate", "31", "52%", "3.45"],
    ["Premium", "77", "75%", "3.06"],
    ["Luxury", "67", "88%", "3.36"],
])
h.notes(s, "Reading: linear model's error is stable across both platforms — no platform quietly "
           "dragging the average down. Delivery rate climbs steadily from Budget to Luxury, "
           "consistent with what logistic regression found. Both took one grouped query.")

# 16. Summary -----------------------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Every Model, One Glance", "Summary")
h.add_table(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(4.9), [
    ["Model", "Metric", "Value", "Threshold", "Status"],
    ["Linear Regression", "Holdout R²", "0.84", "≥ 0.60", "Within threshold"],
    ["Linear Regression", "Holdout RMSE (% of mean)", "~17%", "≤ 20%", "Within threshold"],
    ["Logistic Regression", "Holdout AUC", "0.77", "≥ 0.70", "Within threshold"],
    ["Logistic Regression", "Recall, \"no delivery\"", "~20%", "≥ 50%", "Flagged"],
    ["Decision Tree (unpruned)", "Train − holdout gap", "~60 pts", "≤ 15 pts", "Flagged"],
    ["Decision Tree (pruned)", "Train − holdout gap", "~6 pts", "≤ 15 pts", "Within threshold"],
    ["k-Means (k=3)", "Avg. silhouette", "0.42", "≥ 0.50", "Flagged"],
])
h.notes(s, "Three of seven checks are flagged — that's the entire argument for running diagnostics "
           "on every model, not just the ones that feel shaky going in.")

# 17. Takeaways -----------------------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "What to Bring Back to Your Own Models", "Takeaways")
h.add_bullets(s, h.Inches(0.6), h.Inches(1.7), h.Inches(12.1), h.Inches(4.8), [
    "Never trust a metric with no threshold — decide the bar before you look at the number",
    "Always score on a holdout set, or on cross-validated error the model never optimized against directly",
    "Read the component metrics, not just the headline one — the confusion matrix caught what accuracy hid",
    "A flagged diagnostic isn't always a model problem — sometimes it's telling you to get better features",
    "Whatever you can compute in R, ask whether it could run as a database aggregate query instead",
], size=17)
h.notes(s, "Closing content slide before the sign-off. Keep this concrete and portable — these are "
           "rules a student can apply to a model they build next week, not a recap of today's numbers.")

# 18. Course capstone: six sessions, one lifecycle ---------------------------
s = h.new_slide(prs)
h.add_title(s, "Six Sessions, One Lifecycle", "Course Capstone — 09/01 Closes the Loop")
h.add_table(s, h.Inches(0.6), h.Inches(1.6), h.Inches(12.1), h.Inches(3.6), [
    ["Date", "Lifecycle Phase", "What We Built"],
    ["07/25", "All 5 phases, overview", "Telco churn workshop — prep through operationalizing, end to end"],
    ["08/01", "Data Prep + Initial EDA", "Distributions, initial exploration"],
    ["08/11", "Statistical foundations", "Summary tests, sound vs. significant"],
    ["08/18", "Model Planning", "H0/H1, technique selection by business objective"],
    ["08/25", "Model Building", "ML/DL algorithm survey, technical foundations"],
    ["09/01 (Today)", "Validation", "Diagnostics — R holdout checks, then database aggregate functions"],
])
h.add_card(s, h.Inches(0.6), h.Inches(5.4), h.Inches(12.1), h.Inches(1.7), "Where the Loop Closes",
           ["Validation is the gate: only a model that clears today's checks is fit to reach the "
            "Communicating and Operationalizing phases from 07/25 — that's why it comes last, not first"])
h.notes(s, "This is the course capstone, not just a session recap — 09/01 is the last date on the "
           "syllabus. Land the point explicitly: everything since 07/25 has been building toward the "
           "answer to one question — is this model allowed into production? Today answered it.")

# 19. Closing -----------------------------------------------------------
s = h.new_slide(prs)
h.add_title(s, "Next Up", "Where This Goes From Here")
h.add_card(s, h.Inches(0.6), h.Inches(1.8), h.Inches(12.1), h.Inches(4.6), "Questions & What's Next",
           ["Every model we validated today feeds directly into how results get communicated and operationalized",
            "Bring a model of your own next session — we'll run this same fit/score/evaluate protocol on it live",
            "Questions?"])
h.notes(s, "Sign-off slide. Leave 10-15 minutes for Q&A given the density of the diagnostics content.")

h.finalize_and_save(prs, "session6-model-diagnostics.pptx")
print(f"Saved session6-model-diagnostics.pptx — {len(prs.slides)} slides")
