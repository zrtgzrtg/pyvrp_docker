road_min_grouped <- group_road %>%
  group_by(route_id) %>%
  summarise(min_cost_road = min(feas_best_cost, na.rm = TRUE))

euclidean_min_grouped <- group_euclidean %>%
  group_by(route_id) %>%
  summarise(min_cost_euclidean = min(feas_best_cost, na.rm = TRUE))

euclidean_mean <- mean(euclidean_min_grouped$min_cost_euclidean)
road_mean <- mean(road_min_grouped$min_cost_road)
euclidean_min <- min(euclidean_min_grouped$min_cost_euclidean)
road_min <- min(road_min_grouped$min_cost_road)


