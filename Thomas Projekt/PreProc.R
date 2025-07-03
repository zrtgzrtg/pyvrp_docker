library(dplyr)

# Step 1: Extract the last row from each stats data.frame
summarized_stats <- lapply(data$stats, function(df) tail(df, 1))

# Step 2: Combine all into a single data.frame
stats_df <- bind_rows(summarized_stats)

# Step 3: Bind with the rest of the data (excluding original stats column)
final_df <- bind_cols(data %>% select(-stats), stats_df)

# Optional: View the flattened result
View(final_df)




# Schritt 1: Long-Format mit route_id + runtime umbenennen
long_stats <- bind_rows(
  lapply(seq_along(data$stats), function(i) {
    data$stats[[i]] %>%
      rename(runtime_iteration = runtime) %>%
      mutate(route_id = i)
  })
)

# Schritt 2: Originaldaten mit route_id
data_with_id <- data %>% mutate(route_id = row_number())

# Schritt 3: Join
long_combined <- long_stats %>%
  left_join(data_with_id %>% select(-stats), by = "route_id")

# Schritt 4: Spaltenreihenfolge automatisch setzen
stat_cols <- names(long_stats)
meta_cols <- setdiff(names(data_with_id), "stats")

# Neue Reihenfolge: stats-Spalten zuerst, dann Metadaten
final_col_order <- c(stat_cols, setdiff(meta_cols, "route_id"))  # route_id ist schon drin

# Anwenden
long_combined <- long_combined[, c(
  "route_id", "routes",
  setdiff(names(long_stats), c(
    "route_id", "routes",
    "num_iterations", "runtime",
    "DMUsedName", "X_setUsedName", "seed", "isFeasible"
  )),
  "num_iterations", "runtime", "DMUsedName", "X_setUsedName", "seed", "isFeasible")]

# View
View(long_combined)

library(dplyr)

build_long_combined <- function(data) {
  # Schritt 1: Long-Format mit route_id + runtime umbenennen
  long_stats <- bind_rows(
    lapply(seq_along(data$stats), function(i) {
      data$stats[[i]] %>%
        rename(runtime_iteration = runtime) %>%
        mutate(route_id = i)
    })
  )
  
  # Schritt 2: Originaldaten mit route_id
  data_with_id <- data %>% mutate(route_id = row_number())
  
  # Schritt 3: Join
  long_combined <- long_stats %>%
    left_join(data_with_id %>% select(-stats), by = "route_id")
  
  # Schritt 4: Spaltenreihenfolge setzen
  long_combined <- long_combined %>%
    select(
      route_id, routes,
      -num_iterations, -runtime, -DMUsedName, -X_setUsedName, -seed, -isFeasible,
      everything(),
      num_iterations, runtime, DMUsedName, X_setUsedName, seed, isFeasible
    )
  
  return(long_combined)
}
long_combined_data1 <- build_long_combined(inputs_data_combined_1)
View(long_combined_data1)

long_combined_data2 <- build_long_combined(inputs_data_combined_2)
View(long_combined_data2)

group_road <- long_combined_func %>% 
  filter(DMUsedName == "Chicago_100x100_RoadData")

group_euclidean <- long_combined_func %>% 
  filter(DMUsedName == "Chicago_100x100_EuclideanData")
