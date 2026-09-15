# --- SYNTHETIC DATASET: ZOMATO & SWIGGY RESTAURANT DATA ---
# Self-generated so this file runs identically on any machine with zero
# external file dependencies -- copy this block verbatim into the week's
# setup chunk (each .Rmd must stay self-contained; do not source() this
# file from posit.cloud).
set.seed(42)

n_restaurants <- 200

restaurant_data <- data.frame(
  restaurant_id = 1:n_restaurants,
  platform = sample(c("Zomato", "Swiggy"), n_restaurants, replace = TRUE),
  average_cost_two = round(runif(n_restaurants, min = 150, max = 2500)),
  distance_center_km = round(runif(n_restaurants, min = 0.5, max = 15), 1),
  rating = round(runif(n_restaurants, min = 1.5, max = 4.9), 1),
  votes = round(runif(n_restaurants, min = 10, max = 1500))
)

# More votes + higher cost => higher estimated revenue (linear relationship)
restaurant_data$estimated_revenue <- round(
  (restaurant_data$votes * 1.5) + (restaurant_data$average_cost_two * 0.4) -
    (restaurant_data$distance_center_km * 50) + rnorm(n_restaurants, mean = 500, sd = 100)
)
restaurant_data$estimated_revenue[restaurant_data$estimated_revenue < 100] <- 100

# Expensive restaurants are more likely to offer online delivery (binary relationship)
prob_delivery <- 1 / (1 + exp(-(-1 + 0.0015 * restaurant_data$average_cost_two)))
restaurant_data$has_online_delivery <- rbinom(n_restaurants, 1, prob_delivery)

# Price tier from cost (non-linear rule relationship)
restaurant_data$price_range <- factor(cut(restaurant_data$average_cost_two,
                                   breaks = c(0, 400, 800, 1500, Inf),
                                   labels = c("Budget", "Moderate", "Premium", "Luxury")))
