join_numClients <- function(data_df, input_df) {
  # Join nur mit den benötigten Spalten
  input_subset <- input_df[, c("vrp.file", "numClients")]
  
  # Merge basierend auf vrp.file und X_setUsedName
  merged <- merge(data_df, input_subset,
                  by.x = "X_setUsedName",
                  by.y = "vrp.file",
                  all.x = TRUE)
  
  return(merged)
}

inputs_data_combined_1 <- join_numClients(data1, inputs_html)
inputs_data_combined_2 <- join_numClients(data2, inputs_htmk_n106_chicago)

