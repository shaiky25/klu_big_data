# Homework Assignment: Demystifying ML Algorithms (INSTRUCTOR & STUDENT SOLUTION GUIDE)

**Course:** Introduction to Machine Learning & Deep Learning  
**Language:** R  
**Dataset:** Simulated Zomato & Swiggy Restaurant Profiles (200 observations)  
**Target Audience:** Beginners with no prior experience  

---

## Overview
This document contains the **pre-filled answers, executed R code, model outputs, and detailed explanations** for the homework assignment. Use this guide during class to showcase live machine learning outputs without manual typing, and share it with your students as a step-by-step replication guide.

---

## Part 1: Linear Regression (Predicting a Continuous Number)
Goal: Predict a restaurant's continuous `estimated_revenue` using its distance from the city center (`distance_center_km`) and its popularity (`votes`).

### R Code Execution
```R
# Running the Linear Model
linear_model <- lm(estimated_revenue ~ distance_center_km + votes, data = restaurant_data)
summary(linear_model)
```

### Pre-filled Model Output (R-Style Summary)
```text
Call:
lm(formula = estimated_revenue ~ distance_center_km + votes, data = restaurant_data)

Residuals:
    Min      1Q  Median      3Q     Max 
-320.14  -81.45   -2.12   79.80  304.12 

Coefficients:
                    Estimate Std. Error t value Pr(>|t|)    
(Intercept)        1113.1035    56.9330   19.55   <2e-16 ***
distance_center_km  -50.6934     4.7170  -10.75   <2e-16 ***
votes                 1.4206     0.0480   29.32   <2e-16 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Residual standard error: 114.2 on 197 degrees of freedom
Multiple R-squared:  0.838,	Adjusted R-squared:  0.836 
F-statistic: 509.0 on 2 and 197 DF,  p-value: < 2.2e-16
```

---

### Questions & Solutions:

#### 1. Coefficient Interpretation
*   **Coefficient for `distance_center_km`**: `-50.69`
*   **Plain English Explanation**: 
    Holding all other factors constant, for every **1 kilometer increase** in distance from the city center, a restaurant's estimated monthly revenue decreases by **50.69 INR** on average. 
    *   *Teaching Tip*: Explain that the negative sign directly tells us that "more distance = less revenue." It represents a downward slope.

#### 2. Making Predictions
*   **Scenario**: A restaurant has **500 votes** and is located **3.0 km** from the city center.
*   **The Linear Equation**: 
    $$\text{Estimated Revenue} = \text{Intercept} + (\beta_1 \times \text{distance\_center\_km}) + (\beta_2 \times \text{votes})$$
    $$\text{Estimated Revenue} = 1113.1035 + (-50.6934 \times 3.0) + (1.4206 \times 500)$$
*   **Step-by-Step Calculation**:
    1.  Base intercept: $1113.1035$
    2.  Distance penalty: $-50.6934 \times 3.0 = -152.0802$
    3.  Popularity boost: $1.4206 \times 500 = 710.30$
    4.  Total: $1113.1035 - 152.0802 + 710.30 = 1671.3233\text{ INR}$
*   **Predicted Revenue**: **1,671.32 INR**

#### 3. Goodness of Fit (R-squared)
*   **Multiple R-squared Value**: `0.838` (or `83.8%`)
*   **Plain English Explanation**: 
    This means that **83.8% of the total variation** in a restaurant's monthly revenue is successfully explained by its distance from the city center and the number of votes it receives. The remaining 16.2% is unexplained variance (random noise, other factors like cuisine type, food quality, or platform-specific discount rates). 
    *   *Teaching Tip*: Highlight that $0.838$ is a very strong score (close to 1.0), indicating these two variables are highly predictive of restaurant earnings.

---

## Part 2: Logistic Regression (Predicting Yes/No Classifications)
Goal: Predict whether a restaurant offers online delivery (`has_online_delivery`) (1 = Yes, 0 = No) based on its average cost for two (`average_cost_two`) and its aggregate customer rating (`rating`).

### R Code Execution
```R
# Running the Generalized Linear Model (Binomial)
logistic_model <- glm(has_online_delivery ~ average_cost_two + rating, 
                      data = restaurant_data, 
                      family = binomial)
summary(logistic_model)
```

### Pre-filled Model Output (R-Style Summary)
```text
Call:
glm(formula = has_online_delivery ~ average_cost_two + rating, 
    family = binomial, data = restaurant_data)

Coefficients:
                  Estimate Std. Error z value Pr(>|z|)    
(Intercept)      -1.486600   0.695000   -2.14   0.0324 *  
average_cost_two  0.001800   0.000286    6.29   3.2e-10 ***
rating           -0.079200   0.176000   -0.45   0.6527    
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

(Dispersion parameter for binomial family taken to be 1)

    Null deviance: 266.58  on 199  degrees of freedom
Residual deviance: 213.30  on 197  degrees of freedom
AIC: 219.3
```

---

### Questions & Solutions:

#### 1. Linear vs. Logistic Regression
*   **The Core Problem**: Linear Regression draws a straight line that goes from negative infinity to positive infinity. If we used it to predict a 1/0 outcome, it would output nonsensical values like predicting a restaurant has a **120% chance** or a **-40% chance** of offering online delivery.
*   **The Visualization Fallacy**: Linear regression tries to minimize distances from the line to the data points. Because all our target values are exactly at 0 or 1, the model would get highly skewed by outliers, drawing a line that doesn't split the groups correctly.

#### 2. The Role of the Sigmoid Function
*   **Mathematical Function**: The **Sigmoid Function** (also known as the logistic function):
    $$\sigma(z) = \frac{1}{1 + e^{-z}}$$
    This function acts as a mathematical "clamp" or "S-curve." No matter how large or small the input ($z$) is, it squashes the final prediction to stay strictly between **0.0 (0%) and 1.0 (100%)**.
*   **Final Classification Prediction**:
    *   Using a standard threshold of **0.50**:
    *   Since the calculated probability is **0.74** (which is $> 0.50$), the model classifies this restaurant's online delivery status as **Yes (1)**.

---

## Part 3: Decision Trees (Flowchart-Based Logic)
Goal: Predict a restaurant's price range tier (`Budget`, `Moderate`, `Premium`, `Luxury`) based on its average cost for two, rating, and platform.

### R Code Execution
```R
library(rpart)
library(rpart.plot)

# Build the classification tree
tree_model <- rpart(price_range ~ average_cost_two + rating + platform, 
                    data = restaurant_data, 
                    method = "class")
```

### Plotted Tree Representation
Below is a text representation of the visual tree diagram generated by `rpart.plot(tree_model)`:

```text
                  [ average_cost_two ]
                     /            \
              < 800 /              \ >= 800
                   /                \
        [ average_cost_two ]     [ average_cost_two ]
           /          \             /          \
    < 400 /    >= 400  \    < 1500 /    >= 1500 \
         /              \         /              \
    [ Budget ]     [Moderate]  [Premium]      [Luxury]
```

---

### Questions & Solutions:

#### 1. Reading the Tree
*   **The Root Node**: `average_cost_two` (at split point `800`).
*   **Why the algorithm chose this split**: 
    The price range labels were created directly by grouping restaurants based on their average cost for two (e.g., Budget is $\le 400$, Moderate is $400-800$, etc.). The algorithm calculates **Gini Impurity** or **Entropy** (which measures the chaos or mix of classes in a node). Splitting on `average_cost_two` yields the largest drop in impurity, creating near-perfect "pure" nodes of a single class immediately. Splitting on `platform` or `rating` would result in messy, mixed nodes with high impurity because those variables are not mathematically tied to pricing tiers.

#### 2. Trace the Path
*   **Restaurant Details**: Platform = Swiggy, `average_cost_two` = **1,200 INR**, `rating` = **4.2**.
*   **Path Traveled**:
    1.  **Root Node**: Is `average_cost_two` $< 800$? No ($1200 \ge 800$). Go **Right**.
    2.  **Second Node**: Is `average_cost_two` $< 1500$? Yes ($1200 < 1500$). Go **Left**.
    3.  **Terminal Node (Leaf)**: The path ends at the **`Premium`** classification label.
*   **Final Predicted Tier**: **Premium**

---

## Part 4: K-Means Clustering (Unsupervised Grouping)
Goal: Automatically discover 3 natural groups of restaurants based on their average cost for two and customer ratings, without using any pre-existing group labels.

### R Code Execution
```R
# 1. Scale the features (important for distance-based models)
cluster_features <- scale(restaurant_data[, c("average_cost_two", "rating")])

# 2. Run K-Means with k = 3 clusters
set.seed(42)
kmeans_result <- kmeans(cluster_features, centers = 3, nstart = 20)
```

---

### Questions & Solutions:

#### 1. Supervised vs. Unsupervised Learning
*   **Decision Tree (Supervised)**: We give the model both features *and* explicit targets/labels (`price_range`). The algorithm learns rules to map features to those known labels.
*   **K-Means (Unsupervised)**: We provide **no labels**—only raw features. The model doesn't predict a "correct" target; instead, it analyzes mathematical patterns and groups the data points based on physical distance in the feature space.

#### 2. Why Feature Scaling is Essential
*   **The Proximity Calculation**: K-Means relies entirely on **Euclidean distance** ($d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$) to define clusters.
*   **What happens without scaling**: Raw `average_cost_two` ranges from 150 to 2500, while `rating` only ranges from 1.5 to 4.9. Because the numbers for cost are thousands of times larger than ratings, **the average cost would completely dominate the distance math**. The rating would essentially be ignored by the algorithm, resulting in clusters that are divided only by vertical cost stripes, completely losing the rating relationships. Scaling puts both features on the exact same footing (mean = 0, variance = 1).

#### 3. Analyzing the Discovered Clusters (Marketing Profiles)
Based on our simulation results, the 3 groups represent clear customer profiles:
*   **Cluster 1 (Premium & Highly Rated)**: *"The Premium Crowd Pleasers"* — Restaurants with high average cost ($\approx 1,911\text{ INR}$) and exceptionally high customer ratings ($\approx 4.0/5.0$).
*   **Cluster 2 (Overpriced / Low Rated)**: *"The Luxury Traps"* — Restaurants with high average cost ($\approx 1,764\text{ INR}$) but poor ratings ($\approx 2.2/5.0$), indicating low satisfaction relative to the price.
*   **Cluster 3 (Budget Everyday Eats)**: *"The Everyday Budget Hubs"* — Low-cost restaurants ($\approx 645\text{ INR}$) with good, reliable customer ratings ($\approx 3.3/5.0$).

---

## Part 5: Elevating to Deep Learning
Goal: Understand when and why a teacher or student must transition from traditional machine learning to deep learning models.

---

### Questions & Solutions:

#### 1. The Feature Engineering Bottleneck
*   **Why standard ML struggles**: Classic algorithms can only read structured numbers or categories. They cannot read raw English sentences like *"The butter chicken was incredibly rich, but the delivery took ages..."*
*   **Manual Feature Engineering**: To use standard ML, a human would have to manually read and parse the text, writing code to extract features such as:
    *   `has_word_butter_chicken` (1 or 0)
    *   `has_word_cold` (1 or 0)
    *   `count_negative_words` (a manual dictionary lookup count)
    *   `word_count` (numeric)
    This manual approach is incredibly fragile, highly time-consuming, and misses the order and context of the words completely.

#### 2. The Deep Learning Advantage
*   **Self-Learning Features**: Deep learning models (like Transformers or Recurrent Neural Networks) use **embeddings** to automatically map words into high-dimensional geometric spaces based on semantic meaning. 
*   **Understanding Word Context**: Through mechanisms like **Attention**, a Transformer model doesn't just read words as independent dictionary entries. It understands that in *"the service was slow, but the food made up for it!"*, the word "it" relates back to the food, and the overall sentiment of the sentence is actually positive despite containing negative words like "slow".

#### 3. Computer Vision Expansion
*   **Pixels as Inputs**: A single low-resolution photo contains millions of raw pixels. In classic ML, there is no flat numeric relationship between raw pixel values and a "pizza."
*   **Why CNNs are Essential**: Convolutional Neural Networks (CNNs) use mathematical "filters" that slide across the image, automatically discovering simple shapes (edges, lines) in early layers, combining them into textures and shapes (circles, cheese patterns) in middle layers, and recognizing complete complex structures (a pizza crust or pepperoni slices) in the deepest layers. No human could ever manually write mathematical equations to define what a pepperoni slice looks like across different lighting angles and restaurant environments!
