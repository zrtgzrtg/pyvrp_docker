#!/usr/bin/env python3
"""
Generic Origin–Destination (OD) Cost-Matrix calculator for ArcGIS.

What you supply
---------------
• A network dataset inside a file geodatabase.
• A feature class or shapefile containing origin points.
• A feature class or shapefile containing destination points.
• (Optional) one or more polygon-barrier layers that increase the chosen
  impedance attribute inside their footprint.

What you get
------------
A CSV listing OriginID, DestinationID and the total cost (time, distance,
or any other impedance attribute you choose).  Optionally you can add extra
exports or wrap the core calls in loops if you need to batch-process many
scenarios.
"""

import arcpy
import csv
import os
from pathlib import Path

try:
    # ── User settings – fill these in ──────────────────────────────────────
    NETWORK_DATASET  = r""   # e.g. r"C:\Data\Roads.gdb\Transportation\Road_ND"
    ORIGINS_FC       = r""   # feature class or .shp with origin points
    DESTINATIONS_FC  = r""   # feature class or .shp with destination points

    OUTPUT_CSV       = r""   # where the results CSV should be written
    IMPEDANCE_ATTR   = "TravelTime"   # name of the cost attribute in the network
    SEARCH_TOLERANCE = "500 Meters"
    ALLOW_UTURNS     = "ALLOW_UTURNS"  # or "NO_UTURNS", "ALLOW_DEAD_ENDS_ONLY"

    # Optional polygon barriers (leave the list empty if you have none)
    POLYGON_BARRIERS = [
        # r"C:\Data\Barriers\construction_zone.shp",
        # r"C:\Data\Barriers\flood_area.shp",
    ]
    # If you want to scale the impedance inside each barrier, set a number here;
    # set to None if you only want to block travel completely.
    BARRIER_COST_SCALE = 10
    # ───────────────────────────────────────────────────────────────────────

    # Make sure the output folder exists
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    # Use the geodatabase that holds the network as the workspace
    arcpy.env.workspace = os.path.dirname(os.path.dirname(NETWORK_DATASET))
    arcpy.env.overwriteOutput = True

    # Create the OD cost-matrix layer
    result = arcpy.na.MakeODCostMatrixLayer(
        in_network_dataset=NETWORK_DATASET,
        out_network_analysis_layer="OD_Matrix",
        impedance_attribute=IMPEDANCE_ATTR,
        default_cutoff=None,
        UTurn_policy=ALLOW_UTURNS
    )
    od_layer = result.getOutput(0)
    classes  = arcpy.na.GetNAClassNames(od_layer)

    # Add origins and destinations
    arcpy.na.AddLocations(
        od_layer, classes["Origins"], ORIGINS_FC,
        search_tolerance=SEARCH_TOLERANCE
    )
    arcpy.na.AddLocations(
        od_layer, classes["Destinations"], DESTINATIONS_FC,
        search_tolerance=SEARCH_TOLERANCE
    )

    # Add any polygon barriers
    if POLYGON_BARRIERS:
        fm = arcpy.na.NAClassFieldMappings(od_layer, classes["PolygonBarriers"])
        if BARRIER_COST_SCALE is not None:
            fm["BarrierType"].defaultValue = 1                         # scaled cost
            fm[f"Attr_{IMPEDANCE_ATTR}"].defaultValue = BARRIER_COST_SCALE
        for poly in POLYGON_BARRIERS:
            arcpy.na.AddLocations(
                od_layer, classes["PolygonBarriers"], poly,
                field_mappings=fm,
                search_tolerance=SEARCH_TOLERANCE
            )

    print("Solving OD cost matrix …")
    arcpy.na.Solve(od_layer)

    # Export OD lines to CSV
    cost_field = f"Total_{IMPEDANCE_ATTR}"
    lines_path = os.path.join("OD_Matrix", classes["ODLines"])

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["OriginID", "DestinationID", cost_field])
        with arcpy.da.SearchCursor(lines_path, ["OriginID", "DestinationID", cost_field]) as rows:
            for origin_id, dest_id, cost in rows:
                writer.writerow([origin_id, dest_id, cost])

    print(f"Finished!  Results saved to: {OUTPUT_CSV}")

except Exception as exc:
    arcpy.AddError(str(exc))
    raise
