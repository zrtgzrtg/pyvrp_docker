adjust_demands_column_static <- function(df) {
  # Extrahiere numClients einmal
  num_clients <- df$numClients[1]
  
  adjust_single_demands <- function(demands_string) {
    # demandsUsed ist ein String wie 'c("0", "81", "64", ...)', also bereinigen
    demands_vec <- gsub('[c()" ]', "", demands_string)
    demands_vec <- unlist(strsplit(demands_vec, ","))
    
    # Index 0 (erstes Element) entfernen
    demands_core <- demands_vec[-1]
    
    # Wenn genug Werte da sind: einfach abschneiden
    if (length(demands_core) >= num_clients) {
      return(demands_core[1:num_clients])
    } else {
      # Ansonsten: recyceln
      recycled <- rep(demands_core, length.out = num_clients)
      return(recycled)
    }
  }
  
  df$adjusted_demands <- lapply(df$demandsUsed, adjust_single_demands)
  return(df)
}

# res_1 <- adjust_demands_column_static(long_combined_data1) keine demands noch verfügbar
res_2 <- adjust_demands_column_static(long_combined_data2)

mean(as.numeric(res_2$adjusted_demands[[1]]))