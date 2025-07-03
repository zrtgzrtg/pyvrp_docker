# Set working directory to the Regression folder
setwd("/home/thomas4stank/project_studies/pyvrp_test_git/pyvrp_docker/Thomas Projekt/Regression")
# List only CSV files in this folder (no subfolderse
files <- list.files(pattern = "\\.csv$", full.names = FALSE)
print("Started Script")

library(ggplot2)
library(ggthemes)
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


# Overwrite the file before the loop starts (resets content)
cat("", file = "regression_summaries_thom.txt")

for (name in names(data_list)) {
  df <- data_list[[name]]
  
  y <-  "OutputNormalizedDifference" #Improvement
  x <-  "InputNormalizedDifference" #circuity factor
  
  #if (!all(c(x, y) %in% colnames(df))) next
  cat("Processing:", name, "\n")
  missing_cols <- setdiff(c(x, y), colnames(df))

  if (length(missing_cols) > 0) {
    cat("  ❌ Skipping file. Missing column(s):", paste(missing_cols, collapse = ", "), "\n")
    next
  } else {
    cat("  ✅ Columns found. Proceeding with regression and plot.\n")
  }
  
  # Werte in Prozent umrechnen
  df[[x]] <- df[[x]] +1
  df[[y]] <- df[[y]] * 100
  
  # Regression
  fit <- lm(as.formula(paste(y, "~", x)), data = df)
  
  # Capture summary output as text and append to file
  output <- capture.output({
    cat("\n======================\n")
    cat("File:", name, "\n")
    print(summary(fit))
  })
  cat(output, file = "regression_summaries_thom.txt", sep = "\n", append = TRUE)
  
  # Remove extension
  filename_base <- tools::file_path_sans_ext(name)
  title_parts <- strsplit(filename_base, "_")[[1]]
  plot_title_raw <- paste(title_parts[-length(title_parts)], collapse = "_")
  plot_title <- gsub("_", " ", plot_title_raw)
  cat("Plot title for", name, ":", plot_title, "\n")  # For debugging
  
  # Save plot
  p <- ggplot(df, aes_string(x = x, y = y)) +
    geom_point(alpha = 0.7) +
    geom_smooth(method = "lm", color = "steelblue") +
    ggtitle(plot_title) + labs(
      x = "Circuity Factor",
      y = "Improvement (%)"
    ) + 
    scale_y_continuous(breaks = seq(floor(min(df[[y]])), ceiling(max(df[[y]])), by = 0.5)) +
    scale_x_continuous(breaks = seq(floor(min(df[[x]]*40))/40, ceiling(max(df[[x]]*40))/40, by = 0.005)) +
    theme.main + theme.adjusted 
  
  ggsave(
    filename = paste0("regression_thom_plot_", name, ".png"),
    plot = p, width = 18, height = 8.25, dpi = 300
  )
}
print("Ended Script")
