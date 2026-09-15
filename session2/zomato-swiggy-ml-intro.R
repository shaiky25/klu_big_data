# ==============================================================================
# INTRO TO MACHINE LEARNING FOR BEGINNERS: ZOMATO & SWIGGY CASE STUDY
# Language: R
#
# This script is designed for students with no prior ML experience.
# It uses a self-generated dataset mimicking Zomato & Swiggy features 
# so you can run this script instantly without needing external files!
# ==============================================================================

# --- STEP 0: PREPARE LIBRARIES ---
# R packages used for modeling and visualization.
# If you don't have these, uncomment and run the lines below:
# install.packages("rpart")      # For Decision Trees
# install.packages("rpart.plot") # For plotting Decision Trees
# install.packages("ggplot2")    # For beautiful charts

library(rpart)
library(rpart.plot)
library(ggplot2)

# Set seed for reproducibility (so everyone gets the same "random" data)
set.seed(42)

# --- STEP 1: CREATE SYNTHETIC DATA ---
# Since raw data files can be hard to configure on different machines, 
# we will programmatically generate a dataset resembling our restaurant sources!
n_restaurants <- 200

restaurant_data <- data.frame(
  restaurant_id = 1:n_restaurants,
  platform = sample(c("Zomato", "Swiggy"), n_restaurants, replace = TRUE),
  average_cost_two = round(runif(n_restaurants, min = 150, max = 2500)),
  distance_center_km = round(runif(n_restaurants, min = 0.5, max = 15), 1),
  rating = round(runif(n_restaurants, min = 1.5, max = 4.9), 1),
  votes = round(runif(n_restaurants, min = 10, max = 1500))
)

# Create logical relationships for our models to discover:
# 1. More votes + higher cost = higher estimated revenue (Linear Relationship)
restaurant_data$estimated_revenue <- round(
  (restaurant_data$votes * 1.5) + (restaurant_data$average_cost_two * 0.4) - (restaurant_data$distance_center_km * 50) + rnorm(n_restaurants, mean = 500, sd = 100)
)
# Ensure revenue isn't negative
restaurant_data$estimated_revenue[restaurant_data$estimated_revenue < 100] <- 100

# 2. Expensive restaurants are more likely to offer Online Delivery (Binary Relationship)
prob_delivery <- 1 / (1 + exp(-(-1 + 0.0015 * restaurant_data$average_cost_two)))
restaurant_data$has_online_delivery <- rbinom(n_restaurants, 1, prob_delivery)

# 3. Categorize price range (1 to 4) based on cost (Non-linear Rule Relationship)
restaurant_data$price_range <- factor(cut(restaurant_data$average_cost_two, 
                                   breaks = c(0, 400, 800, 1500, Inf), 
                                   labels = c("Budget", "Moderate", "Premium", "Luxury")))

# Let's inspect the generated dataset
print("--- PREVIEW OF THE DATASET ---")
print(head(restaurant_data))


# ==============================================================================
# ALGORITHM 1: LINEAR REGRESSION (Predicting a Continuous Number)
# Goal: Predict 'estimated_revenue' using distance from city center and votes.
# ==============================================================================
print("--- RUNNING LINEAR REGRESSION ---")

# R uses the formula syntax: y ~ x1 + x2 (Predict y using x1 and x2)
linear_model <- lm(estimated_revenue ~ distance_center_km + votes, data = restaurant_data)

# Print the model results
print(summary(linear_model))

# Visualization of Linear Regression
ggplot(restaurant_data, aes(x = votes, y = estimated_revenue, color = distance_center_km)) +
  geom_point() +
  geom_smooth(method = "lm", col = "red", se = FALSE) +
  labs(title = "Linear Regression: Revenue vs. Votes",
       x = "Number of Votes (Popularity)",
       y = "Estimated Monthly Revenue (INR)",
       color = "Distance (KM)") +
  theme_minimal()


# ==============================================================================
# ALGORITHM 2: LOGISTIC REGRESSION (Predicting Yes/No)
# Goal: Predict 'has_online_delivery' (1/0) based on average cost and rating.
# ==============================================================================
print("--- RUNNING LOGISTIC REGRESSION ---")

# We use glm() with family = binomial to tell R this is a logistic model
logistic_model <- glm(has_online_delivery ~ average_cost_two + rating, 
                      data = restaurant_data, 
                      family = binomial)

# Print summary
print(summary(logistic_model))


# ==============================================================================
# ALGORITHM 3: DECISION TREES (Flowchart-Based Rules)
# Goal: Predict 'price_range' (Budget, Moderate, Premium, Luxury) based on ratings & votes.
# ==============================================================================
print("--- RUNNING DECISION TREE ---")

# Build the tree using rpart
tree_model <- rpart(price_range ~ average_cost_two + rating + platform, 
                    data = restaurant_data, 
                    method = "class")

# Plot the beautiful flowchart for the students to see!
rpart.plot(tree_model, 
           type = 2, 
           extra = 104, 
           under = TRUE, 
           fallen.leaves = TRUE, 
           main = "Decision Tree: Classifying Price Range Tier")


# ==============================================================================
# ALGORITHM 4: K-MEANS CLUSTERING (Unsupervised Grouping)
# Goal: Group restaurants into 3 distinct marketing clusters based on cost & rating.
# ==============================================================================
print("--- RUNNING K-MEANS CLUSTERING ---")

# Scale the variables first since K-means is sensitive to different ranges
cluster_features <- scale(restaurant_data[, c("average_cost_two", "rating")])

# Run K-means with k = 3
kmeans_result <- kmeans(cluster_features, centers = 3, nstart = 20)

# Add the cluster labels back to our original dataset
restaurant_data$cluster <- factor(kmeans_result$cluster)

# Plot the clusters
ggplot(restaurant_data, aes(x = average_cost_two, y = rating, color = cluster)) +
  geom_point(size = 3, alpha = 0.8) +
  labs(title = "K-Means Clustering: Finding 3 Restaurant Profiles",
       x = "Average Cost for Two",
       y = "Aggregate Customer Rating",
       color = "Discovered Cluster") +
  theme_minimal()

print("Script complete! Feel free to run this in RStudio and look at the plots.")
