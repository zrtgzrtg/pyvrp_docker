
# library(jsonlite)
# 
# inputs_html <- as.data.frame(fromJSON("inputsHTML.json"))
# inputs_htmk_n106_chicago <- as.data.frame(fromJSON("inputsHTML_n106_chicago.json"))
# 
# # Function to read and clean a JSON file
# clean_json_import <- function(file_path) {
#   json_text <- readLines(file_path, warn = FALSE)
#   json_text <- paste(json_text, collapse = "\n")
#   json_text <- gsub("\\bNaN\\b", "null", json_text)
#   json_text <- gsub("\\bInfinity\\b", "null", json_text)
#   json_text <- gsub("\\-Infinity\\b", "null", json_text)
#   as.data.frame(fromJSON(json_text))
# }
# 
# # Import both files
# data1 <- clean_json_import("resDict.json")
# data2 <- clean_json_import("resDict_n106_chicago.json")
# 
# # Optional: View structure
# str(c(data1, data2))
# 

# New
# Finde alle passenden Dateien
#files <- list.files(path = ".", pattern = "allXSets.*Updated\\.csv$", full.names = TRUE)

files <- list.files(
  path = ".", 
  pattern = "Total_Route_Lengths_Munich_(1000x100|200x200)_.*(8Euclidean|32Threads)_allXSets\\.csv$",
  full.names = TRUE
)


# Lese jede Datei ein und speichere sie in einer benannten Liste
data_list <- setNames(lapply(files, read.csv), basename(files))



data_list <- lapply(data_list, function(df) {
  df$XSet <- sub(".*(X-[^_\\.]+).*", "\\1", df$Simulation_Name)
  return(df)
})

sort_by_n <- function(df) {
  # Extrahiere n-Wert als Zahl (z. B. aus "X-n101-k25" → 101)
  df$n_val <- as.numeric(sub("X-n(\\d+)-k\\d+", "\\1", df$XSet))
  
  # Sortiere nach n_val
  df <- df[order(df$n_val), ]
  
  # Optional: n_val-Spalte wieder entfernen
  df$n_val <- NULL
  
  return(df)
}

# Auf alle DataFrames in data_list anwenden
data_list <- lapply(data_list, sort_by_n)


# Funktion für ein einzelnes DataFrame
add_min_columns <- function(df) {
  df <- df |> 
    dplyr::mutate(
      DataType = dplyr::case_when(
        grepl("CombinedData", Simulation_Name) ~ "Combined",
        grepl("EuclideanData", Simulation_Name) ~ "Euclidean",
        grepl("RoadData", Simulation_Name) ~ "Road",
        TRUE ~ NA_character_
      )
    )
  
  # Berechne die Minima je XSet und Typ
  min_values <- df |> 
    dplyr::group_by(XSet, DataType) |> 
    dplyr::summarise(MinVal = min(Total_Route_Length), .groups = "drop") |> 
    tidyr::pivot_wider(names_from = DataType, values_from = MinVal, names_prefix = "Min_")
  
  # Füge die Werte wieder an df an
  df <- dplyr::left_join(df, min_values, by = "XSet")
  
  return(df)
}

# Auf alle DataFrames in data_list anwenden
library(dplyr)
library(tidyr)

data_list <- lapply(data_list, add_min_columns)

library(stringr)

data_list <- lapply(data_list, function(df) {
  df$SampleSize <- str_extract(df$Simulation_Name, "(?<=Munich_)\\d+(?=Samples)")
  df$SampleSize <- as.integer(df$SampleSize)  # optional als Zahl
  return(df)
})


library(dplyr)
library(tidyr)
library(ggplot2)
library(ggthemes)

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

make_combined_only_plot <- function(df) {
  sample_size <- unique(df$SampleSize)
  
  plot_data <- df %>%
    select(XSet, Min_Combined, Min_Euclidean) %>%
    distinct() %>%
    mutate(
      Improvement_Combined = (Min_Euclidean - Min_Combined) / Min_Euclidean * 100,
      n_val = as.numeric(sub("X-n(\\d+)-k\\d+", "\\1", XSet))
    ) %>%
    arrange(n_val)
  
  ggplot(plot_data, aes(x = n_val, y = Improvement_Combined)) +
    geom_line(size = 0.5, color = "steelblue") +
    geom_point(size = 3, color = "steelblue") +
    geom_hline(yintercept = 0, linetype = "dashed", color = "black", size = 1.5) +
    labs(
      title = paste("Improvement to Euclidean –", sample_size, "samples"),
      x = "XSet",
      y = "Improvement (%)"
    ) +
    theme_minimal(base_size = 12) +
    scale_y_continuous(breaks = seq(-4, 5, by = 0.5)) +
    theme.main +
    theme.adjusted +
    theme(
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank()
    )
}


plot2 <- make_combined_only_plot(data_list[[2]])
plot3 <- make_combined_only_plot(data_list[[3]])

