# Validating What You Built: Diagnostics for Regression, Classification, Trees & Clustering

*BDA POP — Session 09/01/2026*

## Why validation is not optional at scale

At Zomato- or Swiggy-scale, a model doesn't get to be "probably fine." A revenue-forecasting
model that's quietly 20% off skews marketing budget allocation across hundreds of cities. A
delivery-availability classifier that looks accurate in a training notebook but fails on
restaurants it hasn't seen breaks service commitments the moment it goes live — and customer
trust doesn't come back from a few bad experiences. Every model that reaches production analytics
gets validated first, twice: once against a threshold, and once against data it never trained on.
This document walks that protocol across four models built on the same running restaurant
dataset, then runs the same evaluate step a second way — as database aggregate functions — to
show the same protocol, two engines.

## The protocol, in one line

For every model: **fit it, score it against a holdout set the model never saw, and evaluate the
result against a stated threshold.** A metric with no threshold is an opinion; a metric with a
threshold is a decision.

## Linear Regression — predicting restaurant revenue

Fit on `distance_center_km` and `votes`, scored on a 30% holdout, the model reaches an R² of 0.84
and a holdout RMSE equal to roughly 17% of mean revenue. The residual plot shows no funnel and no
curve — errors scatter randomly around zero across the full range of predictions, which is what
"the model isn't missing a pattern" looks like in practice.

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Holdout R² | 0.84 | ≥ 0.60 | Within threshold |
| Holdout RMSE (% of mean revenue) | ~17% | ≤ 20% | Within threshold |

## Logistic Regression — predicting delivery availability

Accuracy (73%) and AUC (0.77) both clear a reasonable bar — and that's exactly the trap a
headline metric sets. The confusion matrix on the holdout set tells a sharper story: of the
restaurants that genuinely don't offer delivery, the model correctly flags only about one in
five. It has learned to predict "yes, delivery" by default, because most restaurants in this data
do offer it. A delivery-fleet staffing decision built on this model would dramatically
under-plan for the offline-only segment — a real operational miss that accuracy and AUC alone
never surface.

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Holdout AUC | 0.77 | ≥ 0.70 | Within threshold |
| Holdout accuracy | 73% | ≥ 70% | Within threshold |
| Recall, "no delivery" class | ~20% | ≥ 50% | Flagged |

## Decision Tree — the diagnostic catching a real problem

An unconstrained tree (no depth limit, minimum leaf size of one) fit on weak-signal predictors
(`rating`, `votes`, `platform`, `distance_center_km`) reaches 100% training accuracy — and 40%
holdout accuracy, worse than chance among four roughly equal tiers. A 60-point gap between
training and holdout accuracy is the signature of a model that memorized its training data
instead of learning a pattern from it.

`rpart`'s built-in cross-validation table (recorded automatically while the tree grows) flags this
before any holdout check is even needed: cross-validated error is worst at the tree's full,
unpruned size. Pruning to the cross-validated best size collapses the tree to a single split;
training and holdout accuracy then land close together (~48% vs ~42%) instead of 60 points apart.

The fix didn't produce a strong classifier — and that's the real lesson. Pruning fixed the
*overfitting*. It also revealed that these four features simply don't carry much signal about
price tier on their own. Diagnostics did its job twice here: it caught a model that would have
shipped with false confidence, and it told the team to go find better features rather than reach
for a fancier model.

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Unpruned: train − holdout accuracy gap | ~60 pts | ≤ 15 pts | Flagged |
| Pruned: train − holdout accuracy gap | ~6 pts | ≤ 15 pts | Within threshold |

## k-Means Clustering — restaurant segments

Clustering has no holdout labels, so the confirmation step here is trying a range of cluster
counts (k = 2 through 5) and comparing silhouette scores instead. k = 3 is the best of the four
values tried, but at 0.42 it sits below the 0.50 bar for "clearly separated" segments — cost and
rating alone produce clusters that overlap more than they're distinct. That's useful to know
*before* building a marketing plan around three crisp restaurant personas: the segments are real
but fuzzy, best treated as a starting point for judgment rather than a hard rule.

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Silhouette, best k (k=3) | 0.42 | ≥ 0.50 | Flagged |

## The second engine: database aggregate functions

Everything above ran in R, in memory. In production, the same evaluate step usually runs as an
aggregate query against the platform's database instead of pulling every row into R first. The
`group_by()` / `summarise()` grammar used in this session's R Markdown is the same grammar that
pushes straight down to a live SQL database with no code changes — this is what "database
analytical functions to fit, score, and evaluate models" looks like in practice: the same
protocol, a second engine. Re-running the linear model's error and the delivery rate as grouped
aggregates confirms the model's error is stable across both platforms, and shows delivery rate
climbing steadily from Budget restaurants (40%) to Luxury (88%) — consistent with what the
logistic regression found, and a check that costs one query against a live table.

## Summary: every model, one glance

| Model | Metric | Value | Threshold | Status |
|---|---|---|---|---|
| Linear Regression | Holdout R² | 0.84 | ≥ 0.60 | Within threshold |
| Linear Regression | Holdout RMSE (% of mean) | ~17% | ≤ 20% | Within threshold |
| Logistic Regression | Holdout AUC | 0.77 | ≥ 0.70 | Within threshold |
| Logistic Regression | Recall, "no delivery" | ~20% | ≥ 50% | Flagged |
| Decision Tree (unpruned) | Train − holdout gap | ~60 pts | ≤ 15 pts | Flagged |
| Decision Tree (pruned) | Train − holdout gap | ~6 pts | ≤ 15 pts | Within threshold |
| k-Means (k=3) | Avg. silhouette | 0.42 | ≥ 0.50 | Flagged |

Three of seven checks are flagged — and that is the entire argument for running diagnostics on
every model, not only the ones that feel shaky going in. A model can look production-ready on its
headline metric and still fail a component check that matters more to the business than the
headline does.
