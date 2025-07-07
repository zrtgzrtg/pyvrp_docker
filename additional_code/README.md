# Real-World VRP Analysis and Visualization (ArcGIS & Python)

This directory contains scripts for analyzing and visualizing Vehicle Routing Problem (VRP) solutions using both real road networks and Euclidean distances. The workflow is designed for batch processing, comparison, and visualization of VRP results, primarily using ArcGIS and Python.

---

## Workflow Overview

### OD Cost Matrix Calculation

The OD-costMatrix_calculation.py script is used to generate Origin–Destination (OD) cost matrices, which are essential for VRP analysis. This script leverages ArcGIS Network Analyst's OD Cost Matrix tool to compute the shortest path distances (or travel times) between all pairs of points in your study area.

How to use:
- Prepare your input point layers (e.g., depots, delivery locations) in an ArcGIS File Geodatabase.
- Open ArcGIS Pro and ensure the Network Analyst extension is enabled.
- Run the OD Cost Matrix tool from ArcGIS Pro, or automate it using the provided script.
- The tool will export the results as a CSV file, listing OriginID, DestinationID, and Total_Length (distance or time).

Note:  
The OD Cost Matrix tool only exports distance matrices as CSV files. These CSVs must be converted to JSON format for use in the Python VRP solver scripts. Use the provided data conversion scripts for this purpose.

Euclidean distance matrices can be generated using any tool of your preference, or by using the "Generate Near Table" function in ArcGIS.

### Data Conversion

- csvToJson_Road.py  
  Converts semicolon-separated CSVs (with European decimal marks) to JSON, keeping only relevant fields for road distances.
- csvToJson_Euclidean.py  
  Converts Euclidean distance CSVs to JSON, renaming columns for consistency.

### Exporting and Visualization

- export_Utah_stops.py  
  Exports VRP solution stops to shapefiles for visualization in ArcGIS, matching solution IDs to spatial coordinates.
- Munich_Samples_VRPoutputs_visualization.py  
  Converts VRP JSON results for Munich samples into shapefiles, mapping partner IDs to original IDs and including depot locations.
- Munich_Samples_combinedMatrices_VRPoutputs_visualization.py  
  Similar to above, but for combined matrix VRP results.
- Munich_Samples_allXSets_VRPoutputs_visualization.py  
  Batch-creates shapefiles for all result sets and X sets, handling multiple categories and partner mappings.

### Batch Route Solving and Statistics

- calculateTotalRoutes.py  
  Batch-solves ArcGIS Route layers for a directory of stop shapefiles, skipping already-processed files, and logs total route lengths to a CSV.
- totalRouteLengths_fromDistanceMatrices.py  
  Computes total route lengths for each VRP stop-file using its corresponding distance matrix, appending results to a CSV.

### Analysis and Comparison

- rank_totalDistanceDifference_per_point.py  
  Compares Euclidean vs. road-network distances for each origin, ranking points by percentage change and saving results as JSON.
- euclidean_realRoad_dif.py  
  Computes normalized differences between total Euclidean and road distances for all samples, outputting a summary CSV.
- visualizationCasesFinder.py  
  Finds and copies shapefiles for cases with the smallest and largest differences between Euclidean and road solutions, for focused visualization.
- inputDif_vs_outputDif.py  
  Merges input-side and output-side normalized differences for each sample, producing a CSV for further analysis.

---

## Usage Notes

- ArcGIS Pro and the arcpy Python package are required for scripts that interact with geodatabases, shapefiles, or perform network analysis.
- GeoPandas and Shapely are used for spatial data manipulation and exporting.
- Many scripts require you to fill in your own file paths and directory locations before running. Due to memory limitations we can't upload the full datasets and instances we generated.
- Batch scripts are designed to resume from a specific point or skip already-processed files for robustness.

---

## Typical Workflow

1. Calculate OD matrices for your study area using ArcGIS (see OD-costMatrix_calculation.py).
2. Convert matrices to JSON for use in Python scripts (see csvToJson_Road.py and csvToJson_Euclidean.py).
3. Solve VRPs using the provided Python scripts (see solve_vrp.py).
4. Export and visualize results as shapefiles in ArcGIS.
5. Analyze and compare the results using the analysis scripts.

---

Tip:  
Read the comments at the top of each script for specific instructions and required parameters.