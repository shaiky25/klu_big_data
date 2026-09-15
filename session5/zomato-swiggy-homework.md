# Homework Assignment: Demystifying ML Algorithms using Zomato & Swiggy Data

**Course:** Introduction to Machine Learning & Deep Learning  
**Language:** R  
**Dataset:** Simulated Zomato & Swiggy Restaurant Profiles  

---

## Objective
This homework is designed to help you bridge the gap between machine learning theory and practical R coding. Using the simulated Swiggy and Zomato restaurant dataset you ran in `zomato-swiggy-ml-intro.R`, you will analyze model outputs, interpret key statistical metrics, and explain how different algorithms solve distinct business problems.

---

## Deliverables
Please submit a single document (either a compiled R Markdown PDF/HTML or a written report) containing your R code outputs, plots, and written answers to the questions below.

---

## Part 1: Linear Regression (Predicting a Continuous Number)
In the lecture, we discussed **Linear Regression** as a way to draw a "best-fit line" to predict a continuous numeric outcome. In our R script, we run the following code:

```R
linear_model <- lm(estimated_revenue ~ distance_center_km + votes, data = restaurant_data)
summary(linear_model)
```

### Questions:
1. **Coefficient Interpretation**: Look at the `Estimate` column in your `summary(linear_model)` output.
   * What is the coefficient for `distance_center_km`? 
   * Explain what this number means in plain English regarding how a restaurant's distance from the city center affects its monthly revenue.
2. **Making Predictions**: Suppose a restaurant on Zomato has **500 votes** and is located **3.0 kilometers** from the city center. Using the intercept and coefficients from your model's output, write down the linear equation and calculate its predicted `estimated_revenue`.
3. **Goodness of Fit**: Locate the **Multiple R-squared** value in the summary. In your own words, explain what this value tells us about how well our features (distance and votes) explain the variation in restaurant revenue.

---

## Part 2: Logistic Regression (Predicting Yes/No Classifications)
We used **Logistic Regression** to predict whether a restaurant offers online delivery (`has_online_delivery`), which is a binary outcome (1 for Yes, 0 for No).

```R
logistic_model <- glm(has_online_delivery ~ average_cost_two + rating, 
                      data = restaurant_data, 
                      family = binomial)
summary(logistic_model)
```

### Questions:
1. **Linear vs. Logistic**: Why must we use Logistic Regression instead of standard Linear Regression to predict `has_online_delivery`? What would happen to our predictions if we tried to fit a standard linear regression line to 0 and 1 data points?
2. **The Role of the Sigmoid**: The R output shows coefficients, but these are in "log-odds" terms which can be hard to read. 
   * What mathematical function does Logistic Regression use to convert these log-odds values into a clean probability between 0% and 100%?
   * If a restaurant's calculated probability of having online delivery is `0.74`, what is the model's final classification (Yes or No) if we use the standard threshold of `0.50`?

---

## Part 3: Decision Trees (Flowchart-Based Logic)
We built a **Decision Tree** to classify restaurants into one of four price range categories (`Budget`, `Moderate`, `Premium`, or `Luxury`) based on their characteristics.

```R
tree_model <- rpart(price_range ~ average_cost_two + rating + platform, 
                    data = restaurant_data, 
                    method = "class")
rpart.plot(tree_model)
```

### Questions:
1. **Reading the Tree**: Look at the plotted decision tree flowchart generated in RStudio.
   * What is the very first feature (known as the "Root Node") that the tree splits on?
   * Why do you think the algorithm chose this specific feature to make its first split instead of `platform` or `rating`? (Hint: Think about what "Gini Impurity" or "Entropy" measures).
2. **Trace the Path**: Imagine a new restaurant joins Swiggy. It has an `average_cost_two` of **1,200 INR** and a customer `rating` of **4.2**. 
   * Walk through your plotted decision tree step-by-step and write down the path you take.
   * What is the final predicted `price_range` tier for this restaurant?

---

## Part 4: K-Means Clustering (Unsupervised Grouping)
Unlike our first three models, **K-Means Clustering** is an unsupervised learning algorithm. We ran K-Means to find 3 natural restaurant profiles based on their average cost and customer rating.

```R
cluster_features <- scale(restaurant_data[, c("average_cost_two", "rating")])
kmeans_result <- kmeans(cluster_features, centers = 3, nstart = 20)
```

### Questions:
1. **Supervised vs. Unsupervised**: Explain the fundamental difference between the K-Means clustering model we built here and the Decision Tree model we built in Part 3. Why does K-Means not require a "label" (like `price_range`) to group the data?
2. **Why Scale?**: In the first line of the code, we applied the `scale()` function to our features. 
   * Why is scaling or standardizing variables critically important before running a K-Means clustering algorithm? 
   * What would happen to our clusters if we clustered raw `average_cost_two` (values from 150 to 2500) and raw `rating` (values from 1.5 to 4.9) without scaling?
3. **Analyzing the Clusters**: Look at the ggplot visualization of your 3 clusters. Write a brief 1-sentence marketing profile/label for each of the three clusters discovered by the model (e.g., "Cluster 1 represents cheap, highly-rated hidden gems...").

---

## Part 5: Elevating to Deep Learning
Now that you have worked with standard machine learning algorithms, let's explore where **Deep Learning (DL)** enters the picture.

### Case Scenario:
Imagine Zomato wants to build a feature that automatically reads hundreds of thousands of unstructured, written customer reviews (e.g., *"The butter chicken was incredibly rich, but the delivery took ages and arrived cold."*) to automatically determine whether a restaurant has high-quality food or poor service.

### Questions:
1. **The Feature Engineering Bottleneck**: Why would standard machine learning algorithms (like Linear Regression or Decision Trees) struggle to process this raw text data directly? What manual effort (feature engineering) would a human have to perform to make it work in standard ML?
2. **The Deep Learning Advantage**: Explain how a Deep Learning approach (such as a Recurrent Neural Network or a Transformer model) handles this unstructured review text differently than standard ML. 
3. **Computer Vision Expansion**: If Zomato also wanted to analyze user-uploaded photos of dishes to verify if they match the cuisine tags (e.g., identifying a pizza vs. a burger), why is Deep Learning (specifically Convolutional Neural Networks) essential for this task instead of classic tabular ML?
