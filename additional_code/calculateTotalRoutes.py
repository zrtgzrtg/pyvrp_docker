#!/usr/bin/env python3
"""
Batch-solve Network Analyst Route layers for a directory of stop shapefiles,
with the ability to resume from a specific filename token (e.g. ID166).

- Files are read in lexicographic order (Python's default .sort()).
- Processing begins once the first filename containing START_TOKEN is met.
- If the solved layer already exists, the file is skipped.
- A CSV is updated/appended with Simulation_Name + Total_Route_Length.
"""

import arcpy
import csv
import glob
import os
from pathlib import Path

START_TOKEN = "ID0"          # first filename token to process

# PATHS & ENVIRONMENT
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True

arcpy.env.workspace = (
#enter the current ArcGIS project you are working as the Workspace
)

network_ds = os.path.join(
    arcpy.env.workspace,
#enter the road network dataset you built in ArcGIS
)
if not arcpy.Exists(network_ds):
    raise RuntimeError(f"Network dataset not found: {network_ds}")

stops_dir  = (
#enter your entire points dataset from which you create the VRP stops
)

output_dir = (
#enter output directory for the stops shp files you are creating from VRP solution, to be able to visualize routes in ArcGIS
)
os.makedirs(output_dir, exist_ok=True)

csv_dir  = (
#enter the csv file where you want to output total route lengths for each run
)
os.makedirs(csv_dir, exist_ok=True)
csv_path = os.path.join(csv_dir, "Total_Route_Lengths_Munich_200x200.csv")
write_header = not os.path.isfile(csv_path)

# NETWORK ANALYST INITIALISATION
arcpy.CheckOutExtension("Network")

# COLLECT TARGET SHAPEFILES
shp_paths = glob.glob(os.path.join(stops_dir, "*.shp"))
if not shp_paths:
    raise RuntimeError(f"No *.shp files found in {stops_dir}")
shp_paths.sort()                           # keeps lexicographic order

# MAIN LOOP
reached_start = False
processed = 0
skipped   = 0

with open(csv_path, "a", newline="", encoding="utf-8") as f_csv:
    writer = csv.writer(f_csv)
    if write_header:
        writer.writerow(["Simulation_Name", "Total_Route_Length"])

    for stops_shp in shp_paths:
        sim_name = os.path.basename(stops_shp)

        # wait until we hit the resume token
        if not reached_start:
            if START_TOKEN in sim_name:
                reached_start = True
                print(f"\n=== Resuming at {sim_name} ===")
            else:
                continue

        # skip if solved layer already exists
        layer_file = os.path.join(
            output_dir, f"{os.path.splitext(sim_name)[0]}.lyrx"
        )
        if os.path.exists(layer_file):
            skipped += 1
            print(f"⏩ {sim_name}   (layer exists, skipped)")
            continue

        processed += 1
        print(f"▶ Processing {sim_name}")

        # 1. Create fresh Route layer
        result = arcpy.na.MakeRouteLayer(
            in_network_dataset=network_ds,
            out_network_analysis_layer="Route",
            impedance_attribute="Length",
            find_best_order="USE_INPUT_ORDER",
        )
        route_layer = result.getOutput(0)

        # 2. Get NA sublayer names
        na_classes       = arcpy.na.GetNAClassNames(route_layer)
        stops_layer_name = na_classes["Stops"]

        # 3. Field mappings
        field_map = arcpy.na.NAClassFieldMappings(route_layer, stops_layer_name)
        field_map["RouteName"].mappedFieldName = "RouteID"
        field_map["Sequence"].mappedFieldName  = "SeqID"

        # 4. Load stops
        arcpy.na.AddLocations(
            in_network_analysis_layer = route_layer,
            sub_layer                 = stops_layer_name,
            in_table                  = stops_shp,
            field_mappings            = field_map,
            sort_field                = "SeqID",
            append                    = "CLEAR",
            snap_to_position_along_network = "SNAP",
        )

        # 5. Solve
        arcpy.na.Solve(route_layer)

        # 6. Add / populate RouteID field
        routes_layer_name = na_classes["Routes"]
        routes_sublayer   = route_layer.listLayers(routes_layer_name)[0]

        if "RouteID" not in [f.name for f in arcpy.ListFields(routes_sublayer)]:
            arcpy.AddField_management(routes_sublayer, "RouteID", "TEXT", field_length=50)

        with arcpy.da.UpdateCursor(routes_sublayer, ["RouteID", "Name"]) as cur:
            for row in cur:
                row[0] = row[1]
                cur.updateRow(row)

        # 7. Sum total length
        total_len = sum(
            (length or 0)
            for (length,) in arcpy.da.SearchCursor(routes_sublayer, ["Total_Length"])
        )

        # 8. CSV entry
        writer.writerow([sim_name, total_len])

        # 9. Save solved layer
        arcpy.management.SaveToLayerFile(route_layer, layer_file)
        print(f"   ✓ Total length: {total_len:.2f}  → {layer_file}")

print(f"\nRun complete.  Processed {processed}, skipped {skipped}.")
print(f"CSV updated: {csv_path}")






