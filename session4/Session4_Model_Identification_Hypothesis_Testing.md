---
marp: true
theme: gaia
paginate: true
size: 16:9
style: |
  section { font-size: 24px; }
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.2rem;
  }
  .columns h4 { margin-top: 0; }
  code { font-size: 0.85em; }
---

<!-- _class: lead -->

# Big Data Analytics Lifecycle
## Model Identification, Hypothesis Testing & Technique Selection

**Session date:** 08/18/2026 · **Language:** R (tidyverse) · **Dataset:** Telco Customer Churn

### Session Learning Objectives
By the end of this session, we can:
1. **Identify** a candidate model/test for a business question and justify the choice
2. **State** a precise, falsifiable null (H0) and alternative (H1) hypothesis *before* touching test output
3. **Run** exploratory hypothesis tests in R (t-test, chi-square) as a bridge from EDA into formal modeling
4. **Differentiate** analytic technique families (descriptive → predictive) and select one based on business objective, not habit

---

## Theoretical Concept & Motivation (1/3)

**Where this sits in the lifecycle:** between *Model Planning* (Phase 2) and committing engineering effort to *Model Building* (Phase 3). Skipping it is the #1 cause of wasted modeling cycles.

<style scoped>
table { font-size: 0.92em; }
</style>

| Business Objective | Dependent Variable (Y) | Recommended Technique | Model Example |
|---|---|---|---|
| Quantify Impact / Forecast (e.g., ad spend on sales) | Continuous (numerical) | Multiple Linear Regression | Y = β0 + β1X1 + β2X2 + ε |
| Predict Binary Choice (e.g., customer churn vs. retain) | Categorical (binary: 0/1) | Logistic Regression | ln(p / (1−p)) = β0 + β1X1 |
| Compare Group Performance (e.g., A/B test pricing pages) | Continuous across 2+ groups | Two-Sample t-Test / ANOVA | Compare μ(Control) vs. μ(Variant) |
| Segment Customer Base (e.g., high vs. low engagement) | Unlabeled / multi-feature | k-Means Clustering | Distance minimization |

---

## Theoretical Concept & Motivation (2/3)

- A business question does **not** automatically imply a model. It implies a *statistical question*, which then constrains the model family.
- "Which customers will churn?" → prediction on a binary outcome → classification
- "Are churned customers different in tenure?" → comparison of two distributions → hypothesis test first, model second
- Picking the model before framing the question leads to answering the wrong thing precisely.

> **Rule of thumb:** if you can't write the null hypothesis in one sentence, you're not ready to write code.

---

## Theoretical Concept & Motivation (3/3)

**Anchoring to our churn case study** (building on the `churn_clean` dataset from Phase 1):

| Business question | Statistical framing |
|---|---|
| Do longer-tenure customers churn less? | Compare mean `tenure` across `Churn` groups (2-sample test) |
| Is contract type related to churn? | Association between two categorical variables (chi-square test) |
| Can we predict *which* customers will churn? | Binary classification model (next session — logistic regression) |

- Hypothesis tests answer **"is there a real effect?"**
- Predictive models answer **"can we act on it for a new customer?"**
- Today we do the *first*, and use it to justify *which* model belongs in the second.

---

<!-- _class: columns-slide -->

## Step 1 — Formulate & Test H0/H1 on a Continuous Variable

<div class="columns">
<div>

**Business question:** Do customers who churn have shorter tenure than those who stay?

- **H0:** μ(tenure | Churn = Yes) = μ(tenure | Churn = No)
- **H1:** μ(tenure | Churn = Yes) ≠ μ(tenure | Churn = No)
- **α = 0.05**, two-sample Welch t-test (unequal variances assumed by default in R)

```r
# ---- Step 1: Test tenure difference by churn ----
t_result <- t.test(
  tenure ~ Churn,
  data = churn_clean,
  var.equal = FALSE
)

t_result
```

</div>
<div>

**Representative console output**

```
    Welch Two Sample t-test

data:  tenure by Churn
t = 33.0, df = 2400, p-value < 2.2e-16
alternative hypothesis:
true difference in means is not equal to 0
95 percent confidence interval:
 16.9  19.2
sample estimates:
mean in group No  mean in group Yes
            37.6               18.0
```

**Interpretation:** p ≪ 0.05 → reject H0. Retained customers average ~37.6 months tenure vs. ~18.0 for churned — a large, practically meaningful gap.

</div>
</div>

---

<!-- _class: columns-slide -->

## Step 2 — Test H0/H1 on Two Categorical Variables

<div class="columns">
<div>

**Business question:** Is churn associated with contract type?

- **H0:** `Churn` and `Contract` are independent
- **H1:** `Churn` and `Contract` are *not* independent
- Chi-square test of independence (both variables categorical)

```r
# ---- Step 2: Chi-square test of independence ----
contract_tbl <- table(
  churn_clean$Contract,
  churn_clean$Churn
)

contract_tbl
chisq.test(contract_tbl)
```

</div>
<div>

**Representative console output**

```
              No   Yes
Month-to-month 2220 1655
One year        1307  166
Two year        1647   48

	Pearson's Chi-squared test

data:  contract_tbl
X-squared = 1184, df = 2,
p-value < 2.2e-16
```

**Interpretation:** p ≪ 0.05 → reject H0. Month-to-month customers churn at a far higher rate (~43%) than one-year (~11%) or two-year (~3%) customers.

</div>
</div>

---

<!-- _class: columns-slide -->

## Step 3 — Visual Experimentation (Sanity-Check Before Modeling)

<div class="columns">
<div>

**Why:** a p-value alone can hide *shape*. Always pair a test with a plot before trusting it.

```r
# ---- Step 3: Visual checks ----
churn_clean %>%
  ggplot(aes(x = Churn, y = tenure, fill = Churn)) +
  geom_boxplot() +
  labs(title = "Tenure by Churn Status")

churn_clean %>%
  count(Contract, Churn) %>%
  ggplot(aes(x = Contract, y = n, fill = Churn)) +
  geom_col(position = "fill") +
  labs(title = "Churn Rate by Contract Type",
       y = "Proportion")
```

</div>
<div>

**Expected visual**

- **Boxplot:** "No" group's box sits noticeably higher (median ~38 mo.) than "Yes" group (median ~10 mo.), with the "Yes" box right-skewed toward low tenure — confirms the t-test result isn't driven by a few outliers.
- **Stacked bar:** Month-to-month bar is roughly half red ("Yes"); one-year and two-year bars are almost entirely blue ("No") — visually confirms the chi-square association.

*Takeaway: both tests are visually corroborated — safe to proceed to modeling.*

</div>
</div>

---

<!-- _class: columns-slide -->

## Step 4 — Selecting the Right Analytic Technique

<div class="columns">
<div>

**Decision framework** — match technique to business objective, not to what's trendy:

| Business objective | Technique family | Example here |
|---|---|---|
| "What happened?" | Descriptive | Churn rate by segment (Step 3) |
| "Why did it happen?" | Diagnostic | t-test / chi-square (Steps 1–2) |
| "What will happen?" | Predictive | Classification model |
| "What should we do?" | Prescriptive | Retention offer optimization |

```r
# ---- Step 4: Translate hypothesis -> model choice ----
# Outcome is binary (Churn: Yes/No) and we've confirmed
# real association with tenure + contract -> supports a
# predictive classification model as the next step.
outcome_type <- class(churn_clean$Churn)
n_levels     <- nlevels(churn_clean$Churn)
cat("Outcome type:", outcome_type,
    "| Levels:", n_levels, "\n")
```

</div>
<div>

**Representative console output**

```
Outcome type: factor | Levels: 2
```

**Justification for churn case:**
- Business objective = *predict which customers will churn* → **predictive**, not just diagnostic
- Outcome is binary factor → **classification**, not regression
- Confirmed drivers (`tenure`, `Contract`) become candidate predictors
- → Baseline model: **logistic regression** (interpretable, fast, sets the benchmark before trying Random Forest — see next session)

</div>
</div>

---

## Common Pitfalls & Best Practices

**Pitfalls**
- Writing H0/H1 *after* peeking at results ("p-hacking") — decide the hypothesis and α before running the test
- Treating statistical significance as business significance — with n = 7,043, even a 0.5% difference can be "significant" (see 08/11 session: *Sound vs. Significant*)
- Running a chi-square/t-test without checking assumptions (independence of observations, adequate cell counts)
- Jumping straight to a complex model when a simple descriptive/diagnostic check already answers the business question

**Best practices**
- Always pair a test statistic with a visualization
- Report effect size (mean difference, odds ratio) alongside the p-value
- Pre-register the hypothesis and α in a comment block at the top of the analysis script

---

## Quick In-Class Checkpoint

**Discussion question:**

> Marketing wants to know if customers on **Fiber optic** internet churn more than customers on **DSL**.
>
> 1. Write the null and alternative hypothesis.
> 2. Which R test would you run, and why?
> 3. Suppose the test returns p < 0.05, but the actual churn-rate gap is only 1 percentage point across 7,000 customers. Do you recommend a retention campaign? Justify using the sound-vs-significant distinction from the last session.

*(2–3 min pair discussion, then cold-call two groups.)*

---

## Summary & Next Steps

**Today we covered:**
- Framing a business question as a testable H0/H1 *before* modeling
- Running and interpreting a t-test and chi-square test in R on the churn dataset
- A decision framework for choosing descriptive → prescriptive technique based on business objective

**Next session:** Full **Model Building** — fitting and comparing Logistic Regression vs. Random Forest on `churn_clean` (already scaffolded in the lifecycle workshop notebook, Phase 3).

**Lab exercise (before next class):**
- Pick one more variable pair from `churn_clean` (e.g. `PaymentMethod` vs `Churn`, or `MonthlyCharges` vs `Churn`)
- Write H0/H1, run the appropriate test in R, and bring a one-slide summary of your finding + recommended technique
