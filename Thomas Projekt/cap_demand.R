library(dplyr)
library(tidyr)
library(stringr)
library(ggplot2)
library(ggthemes)
setwd("/home/thomas4stank/project_studies/pyvrp_test_git/pyvrp_docker/Thomas Projekt/circuity")


files_demand <- list.files(path = ".", pattern = "Demand1.*\\.csv$", full.names = TRUE)

cap_demand_list <- lapply(files_demand, read.csv)

theme.main <- theme_stata(scheme = "s1color")
theme.adjusted <- theme(axis.text.x = element_text(angle = 0, hjust = 0.5, margin = margin(t = 5), size = 22),
                        axis.title.x = element_text(margin = margin(t = 20), size = 32), 
                        axis.text.y = element_text(hjust = 1, margin = margin(r = 10), size = 22, angle = 0),
                        axis.title.y = element_text(margin = margin(r = 20), size = 32),
                        title = element_text(color = "black"),
                        plot.title = element_text(size = 28, color = "black", face = "bold", hjust = 0.5), 
                        plot.subtitle = element_text(size = 17, color = "black", face = "italic"),
                        panel.grid.major = element_line(color = "darkgray", linewidth = 0.2), 
                        panel.grid.minor = element_line(color = "gray", linewidth  = 0.1),
                        plot.background = element_rect(fill = "white", color = NA))

# Schritt 1: XSet extrahieren
cap_demand_list <- lapply(cap_demand_list, function(df) {
  df$XSet <- sub(".*(X-[^_\\.]+).*", "\\2", df$Simulation_Name)
  return(df)
})

cap_demand_list <- lapply(cap_demand_list, function(df) {
  # ID extrahieren, z.B. die Zahl nach _ID
  df$ID <- as.integer(str_extract(df$Simulation_Name, "(?<=_ID)\\d+"))
  # Nach ID sortieren
  df <- dplyr::arrange(df, ID)
  # Optional: Stelle sicher, dass ID die letzte Spalte ist
  df <- df[, c(setdiff(names(df), "ID"), "ID")]
  return(df)
})

add_min_columns <- function(df) {
  df <- df %>%
    dplyr::mutate(
      DataType = dplyr::case_when(
        grepl("CircuityData", Simulation_Name) ~ "Circuity",
        grepl("EuclideanData", Simulation_Name) ~ "Euclidean",
        grepl("RoadData", Simulation_Name) ~ "Road",
        TRUE ~ NA_character_
      )
    )
  
  # Jetzt: Minimum für jede ID + DataType
  min_values <- df %>%
    dplyr::group_by(ID, DataType) %>%
    dplyr::summarise(MinVal = min(Total_Route_Length), .groups = "drop") %>%
    tidyr::pivot_wider(names_from = DataType, values_from = MinVal, names_prefix = "Min_")
  
  # Per Join an die passenden IDs
  df <- dplyr::left_join(df, min_values, by = "ID")
  
  return(df)
}


cap_demand_list <- lapply(cap_demand_list, add_min_columns)

# Schritt 4: SampleSize extrahieren
cap_demand_list <- lapply(cap_demand_list, function(df) {
  df$SampleSize <- str_extract(df$Simulation_Name, "(?<=Munich_)\\d+(?=Samples)")
  df$SampleSize <- as.integer(df$SampleSize)
  return(df)
})



make_improvement_plot_id <- function(df) {
  sample_size <- unique(df$SampleSize)
  
  plot_data <- df %>%
    select(ID, Min_Circuity, Min_Euclidean, Min_Road) %>%
    distinct() %>%
    mutate(
      Improvement_Combined = (Min_Euclidean - Min_Circuity) / Min_Euclidean * 100,
      Improvement_Road     = (Min_Euclidean - Min_Road) / Min_Euclidean * 100
    ) %>%
    pivot_longer(cols = c(Improvement_Combined, Improvement_Road),
                 names_to = "Method",
                 values_to = "Improvement") %>%
    mutate(
      Method = recode(Method,
                      "Improvement_Combined" = "Circuity",
                      "Improvement_Road" = "Road")
    ) %>%
    #filter(Improvement > -20, Improvement < 20) %>%
    arrange(ID, Method)
  
  ggplot(plot_data, aes(x = ID, y = Improvement, color = Method, group = Method)) +
    geom_point(size = 3) +
    geom_line(size = 0.5) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "black", size = 1.5) +
    labs(
      title = paste("Improvement to Euclidean (const) –", sample_size, "samples"),
      x = "ID",
      y = "Improvement (%)",
      color = "Method"
    ) +
    scale_color_manual(
      values = c("Circuity" = "steelblue", "Road" = "springgreen2")
    ) +
    theme_minimal(base_size = 12) +
    scale_y_continuous(breaks = seq(-2, 8, by = 0.5)) +
    theme.main +
    theme.adjusted +
    theme(
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank()
    )
}

# Für deine Liste, z. B. cap_demand_list:
plots_id <- lapply(cap_demand_list, make_improvement_plot_id)


for (i in 1:5) {
  ggsave(filename = paste0("plot_circuity", i, ".png"), plot = plots_id[[i]], width = 18, height = 8.25, dpi = 300)
}


#library(dplyr)
#library(ggplot2)
#library(patchwork)
#
## 1. Alle DataFrames zusammenführen (falls noch nicht geschehen)
#all_df <- bind_rows(cap_demand_list)
#
## 2. Improvements berechnen (gegen Euclidean)
#all_df <- all_df %>%
#  mutate(
#    Improvement_Combined = (Min_Euclidean - Min_Combined) / Min_Euclidean * 100,
#    Improvement_Road     = (Min_Euclidean - Min_Road) / Min_Euclidean * 100
#  )
#
## 3. Boxplot für Combined
#p_combined <- all_df %>%
#  filter(DataType == "Combined") %>%
#  ggplot(aes(x = factor(SampleSize), y = Improvement_Combined)) +
#  geom_boxplot(fill = "steelblue") +
#  labs(
#    title = "Combined vs. Euclidean (const)",
#    x = "Sample size",
#    y = "Improvement (%)"
#  ) +
#  theme.main + theme.adjusted
#
## 4. Boxplot für Road
#p_road <- all_df %>%
#  filter(DataType == "Road") %>%
#  ggplot(aes(x = factor(SampleSize), y = Improvement_Road)) +
#  geom_boxplot(fill = "springgreen2") +
#  labs(
#    title = "Road vs. Euclidean (const)",
#    x = "Sample size",
#    y = "Improvement (%)"
#  ) +
#  theme.main + theme.adjusted
#
## 5. Optional: Beide nebeneinander anzeigen
#p_combined | p_road
#
#ggsave(filename = "plot_cap_box1.png", plot = p_combined, width = 18, height = 8.25, dpi = 300)
#ggsave(filename = "plot_cap_box2.png", plot = p_road, width = 18, height = 8.25, dpi = 300)
#