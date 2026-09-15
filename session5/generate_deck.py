"""
generate_deck.py
Builds the 08/25/2026 ML & DL masterclass deck (16:9, light theme) with python-pptx.
Introductory-level content for an undergraduate audience with no ML background.
Run: python generate_deck.py  ->  Session5_ML_DL_Masterclass_20260825.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---- palette -----------------------------------------------------------
BG = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xF1, 0xF5, 0xF9)
FORMULA_BG = RGBColor(0xEF, 0xF6, 0xFF)
TEXT = RGBColor(0x0F, 0x17, 0x2A)
MUTED = RGBColor(0x47, 0x55, 0x69)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)
CYAN = RGBColor(0x0E, 0x74, 0x90)
BORDER = RGBColor(0xCB, 0xD5, 0xE1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
# "Segoe UI" is Windows-only; PowerPoint silently substitutes a fallback but
# Keynote's importer rejects the whole file as invalid when it hits that
# typeface name. Arial is installed on macOS, Windows, and covered by Google
# Slides/Keynote's web-font substitution, so it round-trips everywhere.
FONT = "Arial"

# ---- helpers -------------------------------------------------------------

def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    return slide


def add_title(slide, title, kicker=None):
    top = Inches(0.35)
    if kicker:
        box = slide.shapes.add_textbox(Inches(0.6), top, Inches(11.5), Inches(0.35))
        p = box.text_frame.paragraphs[0]
        p.text = kicker.upper()
        p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(13), True, CYAN, FONT
        top = Inches(0.68)
    box = slide.shapes.add_textbox(Inches(0.6), top, Inches(12.1), Inches(0.8))
    p = box.text_frame.paragraphs[0]
    p.text = title
    p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(30), True, TEXT, FONT
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), top + Inches(0.75), Inches(1.1), Pt(4))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()


def add_card(slide, x, y, w, h, header, body_lines, body_size=13.5, header_color=CYAN):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = BORDER; shape.line.width = Pt(0.75)
    shape.adjustments[0] = 0.05
    tf = shape.text_frame
    tf.word_wrap = True
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.14))
    p0 = tf.paragraphs[0]
    p0.text = header
    p0.font.bold, p0.font.size, p0.font.color.rgb, p0.font.name = True, Pt(15), header_color, FONT
    for line in body_lines:
        p = tf.add_paragraph()
        p.text = "• " + line
        p.font.size, p.font.color.rgb, p.font.name = Pt(body_size), TEXT, FONT
        p.space_after = Pt(4)
    return shape


def add_formula(slide, x, y, w, h, formula, label=None, size=20):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = FORMULA_BG
    shape.line.color.rgb = BLUE; shape.line.width = Pt(1)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = formula
    p.alignment = PP_ALIGN.CENTER
    p.font.size, p.font.italic, p.font.color.rgb, p.font.name = Pt(size), True, CYAN, FONT
    if label:
        p2 = tf.add_paragraph()
        p2.text = label
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size, p2.font.color.rgb, p2.font.name = Pt(11), MUTED, FONT
    return shape


def add_table(slide, x, y, w, h, data):
    rows, cols = len(data), len(data[0])
    tbl = slide.shapes.add_table(rows, cols, x, y, w, h).table
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.text = str(data[r][c])
            cell.fill.solid()
            cell.fill.fore_color.rgb = BLUE if r == 0 else CARD
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(12.5)
            para.font.bold = (r == 0)
            para.font.color.rgb = WHITE if r == 0 else TEXT
            para.font.name = FONT
    return tbl


def add_bullets(slide, x, y, w, h, items, size=15):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + item
        p.font.size, p.font.color.rgb, p.font.name = Pt(size), TEXT, FONT
        p.space_after = Pt(8)
    return box


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ---- deck build ------------------------------------------------------------

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
# python-pptx doesn't update sldSz@type when you set custom dimensions, so it
# stays "screen4x3" — PowerPoint tolerates the mismatch but Keynote rejects
# the file as an invalid import. Fix it to match the actual 16:9 ratio.
prs.part._element.find(qn("p:sldSz")).set("type", "screen16x9")

# 1. Title & Roadmap ----------------------------------------------------
s = new_slide(prs)
box = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(11.9), Inches(1.3))
p = box.text_frame.paragraphs[0]
p.text = "Machine Learning & Deep Learning: An Introduction"
p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(40), True, TEXT, FONT
box2 = s.shapes.add_textbox(Inches(0.7), Inches(2.55), Inches(11.9), Inches(0.6))
p2 = box2.text_frame.paragraphs[0]
p2.text = "A Beginner-Friendly Tour of the Algorithms Behind Modern AI — Session 08/25/2026"
p2.font.size, p2.font.color.rgb, p2.font.name = Pt(18), CYAN, FONT
roadmap = ["What is machine learning, really?", "Predicting numbers: Linear Regression", "Keeping models simple: Regularization",
           "Predicting yes/no: Logistic Regression", "Learning from neighbors, margins & trees: k-NN, SVM, Decision Trees",
           "Teamwork models: Random Forests & Boosting", "Bonus tools: spotting cause vs. coincidence, forecasting, catching outliers",
           "How neural networks actually learn", "Attention & Transformers — the idea behind ChatGPT",
           "How do we know if a model is any good?"]
add_bullets(s, Inches(0.7), Inches(3.4), Inches(11.9), Inches(3.5), roadmap, size=16)
notes(s, "Welcome slide, pitched at beginners — no assumed background beyond basic algebra. This session "
         "(08/25/2026) introduces the ML/DL algorithm toolbox at an intuitive level: what each method does, "
         "why it works, and when you'd reach for it. Walk through the roadmap in plain language before "
         "diving into any formulas so the class has a mental map of where we're headed.")

# 2. What Is Machine Learning? ----------------------------------------------------
s = new_slide(prs)
add_title(s, "What Is Machine Learning, Really?", "From Hand-Written Rules to Learned Rules")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(2.5), "Traditional Programming vs. ML",
         ["Traditional programming: you write the Rules, feed in Data, get Answers",
          "Machine learning flips it: you feed in Data + known Answers, the computer works out the Rules",
          "Example: instead of hand-coding 'if income > X and debt < Y, approve loan', show the model "
          "thousands of past loan outcomes and let it find the pattern"])
add_card(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(2.5), "Every Model We'll See Has 3 Parts",
         ["Representation — how the model turns inputs into a prediction (a line, a tree, a network...)",
          "Evaluation — a loss function that scores how wrong a prediction was",
          "Optimization — a way to adjust the model to make that loss smaller (e.g. Gradient Descent)"])
add_card(s, Inches(0.6), Inches(4.3), Inches(12.1), Inches(2.6), "The Analytics Maturity Ladder",
         ["Descriptive: What happened? (dashboards, simple aggregations)",
          "Diagnostic: Why did it happen? (root-cause, correlation studies)",
          "Predictive: What will happen next? — this is where most of today's algorithms live",
          "Prescriptive: What should we do about it? (optimization, decision engines)"])
notes(s, "Ground the whole session before any formulas: traditional software is rules-in, answers-out; ML "
         "is examples-in, rules-out. Every algorithm we cover today — no matter how different it looks — "
         "is just a different choice of Representation + Evaluation + Optimization. The analytics maturity "
         "ladder also helps place today's material: most of what follows is 'predictive' analytics, "
         "building on the descriptive/diagnostic techniques from earlier sessions.")

# 3. Linear Regression ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Linear Regression", "Predicting a Number")
add_formula(s, Inches(0.6), Inches(1.7), Inches(5.9), Inches(1.3),
            "θ = (XᵀX)⁻¹Xᵀy", "The formula that finds the best-fit line directly")
add_formula(s, Inches(6.7), Inches(1.7), Inches(6.0), Inches(1.3),
            "Error = average of (actual − predicted)²", "How we measure how 'wrong' a line is")
add_card(s, Inches(0.6), Inches(3.2), Inches(5.9), Inches(3.6), "What Linear Regression Does",
         ["Draws the straight line that best fits a scatter of points",
          "'Best fit' means the line that minimizes total squared distance to every point",
          "Can be solved exactly in one step using the Normal Equation formula",
          "Works best when the relationship really is roughly a straight line"])
add_card(s, Inches(6.7), Inches(3.2), Inches(6.0), Inches(3.6), "Gradient Descent (the other way to fit it)",
         ["Like a hiker lost in thick fog, feeling for the steepest downhill slope underfoot at each step",
          "Useful when the exact formula is too slow (huge datasets, many features)",
          "The step size (learning rate) controls how big each downhill step is",
          "Too big a step overshoots; too small takes forever to reach the bottom"])
notes(s, "Running example for this slide: predicting house price from square footage. Two ways to fit "
         "the same line: solve for it directly with the Normal Equation, or walk toward it step by step "
         "with Gradient Descent — like a hiker in the fog feeling out the steepest downhill direction at "
         "every step until they reach the valley floor. The direct formula gets expensive with lots of "
         "features, which is when gradient descent — and the regularization we cover next — become useful.")

# 4. Regularization ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Keeping Models Simple: Regularization", "Ridge vs. Lasso vs. ElasticNet")
add_formula(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(1.1),
            "Error + a penalty for large coefficients", "Ridge — shrinks every coefficient a little", size=17)
add_formula(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(1.1),
            "Error + a penalty for non-zero coefficients", "Lasso — can shrink some coefficients to zero", size=17)
add_table(s, Inches(0.6), Inches(2.9), Inches(12.1), Inches(3.9), [
    ["Method", "In Plain Words", "Effect on Coefficients", "Best Use Case"],
    ["Ridge", "Discourages any coefficient from getting too big", "Shrinks all coefficients, none reach zero", "Many features that overlap/correlate"],
    ["Lasso", "Also discourages using unnecessary features at all", "Can drive weak coefficients to exactly zero", "Automatically drop useless features"],
    ["ElasticNet", "A blend of both ideas at once", "Shrinks and can zero out coefficients", "Lots of correlated features, want some sparsity"],
])
notes(s, "The problem: a model that fits the training data too perfectly often fits its noise too "
         "(overfitting). Regularization fixes this by penalizing the model for using large coefficients — "
         "it's a 'keep it simple' rule. Ridge shrinks everything a bit; Lasso can shrink some features "
         "all the way to zero, effectively deciding they're not needed at all.")

# 5. Logistic Regression ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Logistic Regression", "Predicting Yes/No (or one of several classes)")
add_formula(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(1.4),
            "σ(z) = 1 / (1 + e⁻ᶻ)", "The Sigmoid — squashes any number into a 0–1 probability")
add_formula(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(1.4),
            "softmax → picks probabilities across classes", "Same idea, extended to more than 2 categories")
add_card(s, Inches(0.6), Inches(3.3), Inches(11.9), Inches(1.3), "How It's Trained",
         ["Loss = how far the predicted probability was from the true 0 or 1 label (cross-entropy)",
          "The model adjusts its weights to make confident, correct predictions and shrink that loss"])
add_card(s, Inches(0.6), Inches(4.8), Inches(11.9), Inches(2.0), "Reading the Model",
         ["Despite the name, it's a classification method, not a regression one",
          "It draws a straight decision boundary that separates the two classes as well as possible",
          "Each coefficient tells you how that feature pushes the prediction toward 'yes' or 'no'",
          "Extends naturally to multiple classes (e.g. cat / dog / bird) via softmax"])
notes(s, "Running example: predicting whether a loan applicant will default, using income and debt as "
         "features. Logistic regression takes a weighted sum of the inputs (just like linear regression) "
         "but then runs it through the sigmoid function so the output is always a valid probability "
         "between 0 and 1. Training nudges the weights so predicted probabilities line up with the true "
         "yes/no labels. Softmax is the same trick generalized to picking among several categories at once.")

# 6. k-NN ----------------------------------------------------
s = new_slide(prs)
add_title(s, "k-Nearest Neighbors (k-NN)", "\"You Are the Average of Your Neighbors\"")
add_card(s, Inches(0.6), Inches(1.6), Inches(6.0), Inches(2.7), "How It Works",
         ["To predict a new point, find its k closest points in the training data",
          "Classification: let those neighbors vote on the label",
          "Regression: average their values",
          "There's no real 'training' — it just remembers all the data"])
add_table(s, Inches(6.9), Inches(1.6), Inches(5.8), Inches(2.7), [
    ["Distance Used to Find Neighbors", "Idea"],
    ["Euclidean", "Straight-line distance (as the crow flies)"],
    ["Manhattan", "Distance moving only along grid lines (city blocks)"],
    ["Minkowski", "A general formula that includes both above"],
])
add_card(s, Inches(0.6), Inches(4.5), Inches(6.0), Inches(2.3), "Choosing k",
         ["Small k (like 1): follows the data very closely — can be noisy",
          "Large k: smooths things out — can miss real patterns",
          "Pick k by trying a few values and checking what predicts best"])
add_card(s, Inches(6.9), Inches(4.5), Inches(5.8), Inches(2.3), "Where It Struggles",
         ["Slow to predict on huge datasets — checks distance to every point",
          "Features on different scales (e.g. age vs. income) can distort distance",
          "With too many features, everything starts looking equally 'far away'"])
notes(s, "k-NN is the most intuitive algorithm in the deck: just look at what's nearby and go with that. "
         "The two design choices that matter are the distance metric (how do we measure 'nearby') and k "
         "(how many neighbors to consult). Emphasize that it needs scaled features and struggles as the "
         "number of features grows — a gentle first mention of the 'curse of dimensionality'.")

# 7. SVM ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Support Vector Machines (SVM)", "Draw the Widest Possible Street Between Classes")
add_formula(s, Inches(0.6), Inches(1.6), Inches(11.9), Inches(1.2),
            "Find the boundary line that maximizes the gap to the nearest points on each side",
            "The 'margin' — SVM's core idea")
add_card(s, Inches(0.6), Inches(3.1), Inches(5.9), Inches(3.7), "Margins & Support Vectors",
         ["Support vectors: the handful of closest points that actually define the boundary",
          "Every other point could move around freely without changing the line at all",
          "C is a dial: low C allows a few points inside the margin for a wider, more tolerant street",
          "High C insists on zero mistakes, giving a narrower, stricter boundary"])
add_card(s, Inches(6.7), Inches(3.1), Inches(6.0), Inches(3.7), "The Kernel Trick",
         ["Sometimes classes can't be separated by a straight line — think two circles, one inside another",
          "Kernels let SVM draw curvy boundaries without ever explicitly computing the curve",
          "Linear kernel: straight boundary",
          "RBF kernel: flexible, curved boundary — a common default choice"])
notes(s, "SVM's guiding idea is simple: don't just separate the classes, separate them by as wide a gap "
         "as possible, since a wider gap tends to generalize better to new points. The kernel trick is "
         "the more advanced idea — it lets the same method handle non-straight boundaries by measuring "
         "similarity in a cleverer way, without the computational cost of actually reshaping the data.")

# 8. Decision Trees ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Decision Trees", "Like Playing 20 Questions With Your Data")
add_card(s, Inches(0.6), Inches(1.6), Inches(11.9), Inches(1.4), "The Basic Idea",
         ["Repeatedly ask yes/no questions about the features (\"Is age > 30?\") to split the data",
          "Each split tries to make the resulting groups as 'pure' as possible (mostly one class)",
          "Keep splitting until groups are pure enough or a stopping rule kicks in"])
add_table(s, Inches(0.6), Inches(3.2), Inches(12.1), Inches(1.6), [
    ["How We Score a Split", "In Plain Words"],
    ["Gini Impurity", "How often you'd mislabel a random point if you guessed randomly from the group"],
    ["Entropy / Information Gain", "How much 'surprise' or disorder is left in the group after splitting"],
])
add_card(s, Inches(0.6), Inches(5.0), Inches(12.1), Inches(1.8), "The Overfitting Trap",
         ["A tree grown all the way down can perfectly memorize the training data — and generalize badly",
          "Pruning (limiting depth, requiring a minimum group size) keeps the tree from memorizing noise",
          "A single tree is easy to read and explain, but a bit unstable on its own"])
notes(s, "A decision tree is literally a flowchart of yes/no questions learned from the data. Gini and "
         "entropy are just two different ways of scoring 'how mixed is this group of labels' — lower is "
         "better. The key risk is overfitting: an unpruned tree can carve out a rule for every single "
         "training example, which is why we usually limit its depth, and why ensembles (next slides) help.")

# 9. Random Forests ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Random Forests", "Wisdom of the Crowd, Applied to Trees")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(2.5), "The Core Idea",
         ["A single decision tree is easily fooled by noise in its training data",
          "So instead, train hundreds of trees, each on a random, slightly different sample of the data",
          "Let every tree vote, and go with the majority (or average, for numbers)",
          "One tree's mistakes tend to get outvoted by the rest"])
add_card(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(2.5), "One Extra Trick",
         ["Each tree is also only shown a random subset of the features at every split",
          "This keeps the trees from all making the exact same mistakes",
          "More variety among the trees makes the group vote more reliable"])
add_card(s, Inches(0.6), Inches(4.3), Inches(5.9), Inches(2.5), "A Built-In Report Card",
         ["Since each tree only sees part of the data, the leftover part can quietly test it",
          "This gives a free, ready-made estimate of how well the forest generalizes",
          "No separate test set required to get this estimate"])
add_card(s, Inches(6.7), Inches(4.3), Inches(6.0), Inches(2.5), "Which Features Mattered?",
         ["Random Forests can rank features by how much they helped reduce mistakes",
          "Useful for understanding what's actually driving the predictions"])
notes(s, "Random Forest is the 'wisdom of the crowd' idea applied to trees: many imperfect, slightly "
         "different trees, averaged together, tend to outperform any single one. The two sources of "
         "randomness — random data samples and random feature subsets per split — are what make the "
         "trees different enough from each other for averaging to actually help.")

# 10. Boosting / XGBoost ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Boosting & XGBoost", "Each New Tree Fixes the Last One's Mistakes")
add_formula(s, Inches(0.6), Inches(1.6), Inches(11.9), Inches(1.2),
            "New prediction = old prediction + (a small tree trained on the leftover errors)",
            "The boosting loop, repeated many times")
add_table(s, Inches(0.6), Inches(3.0), Inches(12.1), Inches(1.9), [
    ["", "Random Forest (Bagging)", "XGBoost (Boosting)"],
    ["How trees are built", "All at once, independently", "One at a time, each learning from the last one's errors"],
    ["Good analogy", "A panel of independent experts voting", "A student redoing a draft based on feedback"],
])
add_card(s, Inches(0.6), Inches(5.1), Inches(12.1), Inches(1.7), "Why XGBoost Is So Popular",
         ["Usually squeezes out very high accuracy on structured/tabular data",
          "Has built-in safeguards against overfitting (it penalizes overly complex trees)",
          "A 'learning rate' controls how much each new tree is allowed to change the prediction"])
notes(s, "Boosting builds trees sequentially instead of in parallel: each new tree is trained specifically "
         "to correct the mistakes the ensemble has made so far. This tends to produce very accurate models "
         "but needs care to avoid overfitting, since it will happily keep chasing residual errors. XGBoost "
         "and LightGBM are fast, well-regularized implementations of this idea.")

# 11. Applied Analytics ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Three More Useful Tools", "Cause vs. Coincidence, Forecasting, Outliers")
add_card(s, Inches(0.6), Inches(1.6), Inches(3.9), Inches(4.9), "Causal Inference",
         ["Just because two things move together doesn't mean one causes the other",
          "These methods try to isolate the actual effect of one change on an outcome",
          "Answers 'what would happen if we did X?' — not just 'what happened when X occurred?'",
          "Important for decisions, not just predictions"])
add_card(s, Inches(4.7), Inches(1.6), Inches(3.9), Inches(4.9), "Time-Series Forecasting",
         ["Predicting future values from a sequence of past values (sales, traffic, temperature...)",
          "Look for a trend (long-term direction) and seasonality (repeating patterns)",
          "Always test by predicting the future from the past — never shuffle time-ordered data"])
add_card(s, Inches(8.7), Inches(1.6), Inches(3.9), Inches(4.9), "Anomaly Detection",
         ["Finding the unusual data points — fraud, defects, sensor glitches",
          "Isolation Forest: odd points are easier to 'isolate' with just a few random splits",
          "Works without needing any labeled examples of what an anomaly looks like"])
notes(s, "This slide broadens the toolbox beyond plain prediction. Causal inference asks a different "
         "question than the rest of the deck ('what if we intervened?' rather than 'what will happen?'). "
         "Time-series forecasting reuses regression ideas but respects the order of time. Anomaly "
         "detection flips the usual approach — instead of learning what's normal, it looks for what's "
         "easy to tell apart from everything else.")

# 12. Deep Learning Mechanics ----------------------------------------------------
s = new_slide(prs)
add_title(s, "How Neural Networks Learn", "Layers of Simple Math, Stacked Together")
add_card(s, Inches(0.6), Inches(1.6), Inches(11.9), Inches(1.5), "The Structure",
         ["A neural network is layers of simple units ('neurons') stacked one after another",
          "Each neuron takes a weighted sum of its inputs, then passes it through a small non-linear "
          "function so the network can learn curves, not just straight lines"])
add_table(s, Inches(0.6), Inches(3.3), Inches(12.1), Inches(1.4), [
    ["Activation Function", "What It Does"],
    ["ReLU", "Passes positive values through, zeroes out negative ones — simple and fast"],
    ["GELU", "A smoother version of ReLU, common in today's large models"],
])
add_card(s, Inches(0.6), Inches(4.9), Inches(12.1), Inches(1.9), "How Training Works: Backpropagation",
         ["Make a prediction, compare it to the true answer, measure the error",
          "Backpropagation traces that error backward through the network to find out how much each "
          "weight contributed to the mistake",
          "The optimizer (e.g. Adam) then nudges every weight slightly to reduce that error, and repeat"])
notes(s, "Keep the mental model simple: a neural net is a big stack of weighted sums plus small nonlinear "
         "'bends', and training is just repeated trial-and-error — predict, measure the error, and adjust "
         "every weight a little in the direction that reduces it. Backpropagation is just an efficient way "
         "to compute 'which weights caused how much of the error' using the chain rule; no need to derive "
         "it by hand for an intro audience.")

# 13. Attention & Transformers ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Attention & Transformers", "The Idea Behind ChatGPT")
add_formula(s, Inches(0.6), Inches(1.7), Inches(11.9), Inches(1.4),
            "Attention(Q,K,V) = softmax(QKᵀ/√dₖ) V",
            "Formal version — every word looks at every other word and decides how relevant it is")
add_card(s, Inches(0.6), Inches(3.3), Inches(5.9), Inches(3.5), "In Plain Words",
         ["Every word in a sentence 'looks around' at all the other words",
          "It decides which other words are most relevant to understanding it right now",
          "Example: in \"the animal didn't cross the street because it was tired\", "
          "attention helps the model figure out 'it' means the animal, not the street",
          "The model then blends information from the relevant words to build understanding"])
add_card(s, Inches(6.7), Inches(3.3), Inches(6.0), Inches(3.5), "Why This Was a Big Deal",
         ["Older models read text one word at a time, in order — slow, and easy to 'forget' earlier words",
          "Attention lets a model look at the whole sentence at once, in parallel — much faster to train",
          "This is the core building block inside GPT, BERT, and most modern language models"])
notes(s, "This is the mechanism behind today's large language models, so it's worth spending real time "
         "on the intuition before showing the formula. The core idea: for every word, compute how much "
         "it should 'pay attention to' every other word, then combine information accordingly. The "
         "formula is just the precise, matrix version of that same idea — show it, but don't dwell on "
         "the linear algebra with a beginner audience.")

# 14. Model Evaluation ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Is the Model Actually Good?", "Bias-Variance, Precision & Recall")
add_card(s, Inches(0.6), Inches(1.6), Inches(5.9), Inches(2.6), "Too Simple vs. Too Complicated",
         ["Underfitting (high bias): e.g. fitting a straight line to data that actually curves like a parabola",
          "Overfitting (high variance): the model memorized noise instead of the real pattern",
          "The goal is the sweet spot in between — check this by testing on data the model never saw"])
add_table(s, Inches(6.7), Inches(1.6), Inches(6.0), Inches(2.6), [
    ["Metric", "The Question It Answers"],
    ["Precision", "Of everything I flagged as 'yes', how much was right?"],
    ["Recall", "Of everything that was actually 'yes', how much did I catch?"],
    ["F1", "A single score balancing precision and recall"],
])
add_card(s, Inches(0.6), Inches(4.5), Inches(12.1), Inches(2.4), "Picking the Right Metric",
         ["Example: spam filter — missing a spam email (low recall) is annoying but a false alarm "
          "blocking a real email (low precision) may be worse",
          "There's no universally 'best' metric — pick the one that matches what mistakes actually cost "
          "your business",
          "Accuracy alone can be misleading when one class is much rarer than the other"])
notes(s, "The two failure modes to teach clearly: underfitting (model too dumb) and overfitting (model "
         "too good at memorizing training data, bad at new data). For classification metrics, use a "
         "concrete relatable example (spam filter, medical test) to make precision vs. recall stick — "
         "the tradeoff between 'catching everything' and 'not crying wolf' is intuitive once grounded "
         "in a real scenario.")

# 15. Summary & Architecture Selection Guide ----------------------------------------------------
s = new_slide(prs)
add_title(s, "Putting It All Together", "Which Tool Do I Reach For?")
add_table(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(4.7), [
    ["If your problem looks like...", "A good starting point is..."],
    ["Small/medium data, need to explain the result", "Linear/Logistic Regression, a single Decision Tree"],
    ["Tabular data, want the best accuracy", "Random Forest or XGBoost"],
    ["Small dataset with a clear separation between groups", "SVM"],
    ["Quick baseline, small dataset", "k-NN"],
    ["Images or grid-like data", "Deep learning (CNNs)"],
    ["Text or sequences", "Transformers (attention-based)"],
    ["'What happens if we change X?' questions", "Causal inference"],
    ["Finding rare/unusual events", "Isolation Forest (anomaly detection)"],
])
notes(s, "Closing slide: there's no single 'best' algorithm — the right choice depends on your data size, "
         "whether you need to explain the model, and what kind of data you have (tabular, image, text). "
         "Encourage students to start simple (a regression or a single tree) and only reach for something "
         "more complex once a simple baseline stops being good enough.")

# python-pptx never updates docProps/app.xml's slide count / titles / format —
# they're left at the default template's stale values (0 slides, "4:3"). Keynote
# cross-checks these against the actual slide list and rejects the mismatch as
# "file format is invalid" (PowerPoint ignores the mismatch).
from lxml import etree

EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
app_part = next(p for p in prs.part.package.iter_parts() if p.partname == "/docProps/app.xml")
app_xml = etree.fromstring(app_part.blob)
ns = {"ep": EP_NS, "vt": VT_NS}

app_xml.find("ep:Slides", ns).text = str(len(prs.slides))
app_xml.find("ep:PresentationFormat", ns).text = "On-screen Show (16:9)"

heading_pairs = app_xml.find("ep:HeadingPairs/vt:vector", ns)
heading_pairs[3].find("vt:i4", ns).text = str(len(prs.slides))

titles_vector = app_xml.find("ep:TitlesOfParts/vt:vector", ns)
for _ in prs.slides:
    etree.SubElement(titles_vector, f"{{{VT_NS}}}lpstr")
titles_vector.set("size", str(int(titles_vector.get("size")) + len(prs.slides)))

app_part.blob = etree.tostring(app_xml, xml_declaration=True, encoding="UTF-8", standalone=True)

prs.save("Session5_ML_DL_Masterclass_20260825.pptx")
print(f"Saved Session5_ML_DL_Masterclass_20260825.pptx — {len(prs.slides)} slides")
