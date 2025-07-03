# Set working directory to the Regression folder
setwd("/home/thomas4stank/project_studies/pyvrp_test_git/pyvrp_docker/Thomas Projekt/Percent")
library(ggplot2)
library(ggthemes)
library(stringr)
library(dplyr)

# List only CSV files in this folder (no subfolders)
files <- list.files(pattern = "\\.csv$", full.names = FALSE)

# Import all files into a named list
data_list <- lapply(files, read.csv)
names(data_list) <- tools::file_path_sans_ext(files)

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

data_list <- lapply(data_list, function(df) {
  # ID extrahieren, z.B. die Zahl nach _ID
  df$ID <- as.integer(str_extract(df$Simulation_Name, "(?<=_ID)\\d+"))
  # Nach ID sortieren
  df <- dplyr::arrange(df, ID)
  # Optional: Stelle sicher, dass ID die letzte Spalte ist
  df <- df[, c(setdiff(names(df), "ID"), "ID")]
  return(df)
})

idx <- (length(data_list)-1):length(data_list)

data_list[idx] <- lapply(data_list[idx], function(df) {
  df$BetweenIDandVarying <- sub(".*ID[0-9]+_(.*)_varyingDemand.*", "\\1", df$Simulation_Name)
  return(df)
})

# wende es für jedes DataFrame einzeln an:
data_list[idx] <- lapply(data_list[idx], function(df) {
  df %>%
    group_by(ID, BetweenIDandVarying) %>%
    mutate(Min_Route_Length = min(Total_Route_Length, na.rm = TRUE)) %>%
    ungroup()
})

make_improvement_plot <- function(df, baseline_name = "100Ec2dSampleMunichSpecial") {
  # Baseline: extract Min_Route_Length for each ID
  baseline <- df %>%
    filter(BetweenIDandVarying == baseline_name) %>%
    select(ID, Min_Route_Length) %>%
    rename(Min_Route_Length_Baseline = Min_Route_Length)
  
  # Calculate improvement for all other variants
  plot_data <- df %>%
    filter(BetweenIDandVarying != baseline_name) %>%
    left_join(baseline, by = "ID") %>%
    mutate(
      Improvement = (Min_Route_Length_Baseline - Min_Route_Length) / Min_Route_Length_Baseline * 100
    )
  
  # Plot
  ggplot(plot_data, aes(x = as.factor(ID), y = Improvement, color = BetweenIDandVarying, group = BetweenIDandVarying)) +
    geom_point() +
    geom_line() +
    geom_hline(yintercept = 0, linetype = "dashed", color = "black", size = 1.5) + 
    labs(
      title = paste("Improvement over Baseline X-n101-k25", sep = ""),
      y = "Improvement (%)",
      color = "Variant"
    ) +
    scale_x_discrete(breaks = NULL) +
    scale_y_continuous(breaks = seq(-2, 5, by = 0.5)) +
    theme.main + theme.adjusted
}

plots <- lapply(data_list, make_improvement_plot)


for (i in seq_along(plots)) {
  ggsave(
    filename = paste0("baseline_", i, ".png"),
    plot = plots[[i]],
    width = 18, height = 8.25, dpi = 300
  )
}

make_improvement_plot_facet <- function(df, baseline_name = "100Ec2dSampleMunichSpecial") {
  # Baseline: extract Min_Route_Length for each ID
  baseline <- df %>%
    filter(BetweenIDandVarying == baseline_name) %>%
    select(ID, Min_Route_Length) %>%
    rename(Min_Route_Length_Baseline = Min_Route_Length)
  
  # Calculate improvement for all other variants
  plot_data <- df %>%
    filter(BetweenIDandVarying != baseline_name) %>%
    left_join(baseline, by = "ID") %>%
    mutate(
      Improvement = (Min_Route_Length_Baseline - Min_Route_Length) / Min_Route_Length_Baseline * 100
    )
  
  # Plot
  ggplot(plot_data, aes(x = as.factor(ID), y = Improvement, color = BetweenIDandVarying, group = BetweenIDandVarying)) +
    geom_point() +
    geom_line() +
    geom_hline(yintercept = 0, linetype = "dashed", color = "black", size = 1.5) + 
    labs(
      title = paste("Improvement over Baseline X-n101-k25", sep = ""),
      x = "ID",
      y = "Improvement (%)",
      color = "Variant"
    ) +
    facet_wrap(~BetweenIDandVarying, ncol = 4, scales = "free_y") + 
    scale_x_discrete(breaks = NULL) +
    scale_y_continuous(limits = c(-2.5, 4), breaks = seq(-2.5, 4, by = 0.5)) +
    theme.main + theme.adjusted + theme(
      legend.position = "none",
      strip.text = element_text(size = 12, face = "bold"), 
      axis.text.y = element_text(size = 10, margin = margin(r = 6),)
    ) 
}

plots_facet <- lapply(data_list, make_improvement_plot_facet)

for (i in seq_along(plots_facet)) {
  ggsave(
    filename = paste0("baseline_facet_", i, ".png"),
    plot = plots_facet[[i]],
    width = 18, height = 8.25, dpi = 300
  )
}