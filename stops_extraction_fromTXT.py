#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script:        visualize_vrp_stops_geopandas.py

Description:   For each VRP solution TXT file in TXT_DIR:
                 1. Read the routes ("Route #X: ..." lines).
                 2. Map each internal VRP ID (1-100) back to its ORIGINAL ID via MAPPING_JSON.
                 3. For each route:
                      - Automatically prepend and append the depot (original ID = "1") 
                        as sequence=1 and sequence=(N+2).
                      - Assign route_id = X; assign sequence numbers in order.
                      - Build a GeoDataFrame (in the FGDBs native CRS), then reproject to TARGET_CRS.
                      - Write a shapefile named "[txtname]_route_X.shp" into a subfolder named after the TXT.
                 4. After writing all individual routes, concatenate them (all in TARGET_CRS) 
                    into one GeoDataFrame and write "[txtname]_allRoutes.shp" into that same subfolder.

Usage:        Make sure you have GeoPandas (with Fiona/GDAL “OpenFileGDB” support).
              Then run:
                  python visualize_vrp_stops_geopandas.py
"""

import json
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

# ——— BASE DIRECTORY ———
BASE_DIR = Path(__file__).parent.resolve()

# ——— CONFIGURATION ———
# Folder containing all solution TXT files (each file has “Route #X: …” lines)
TXT_DIR      = BASE_DIR / "VRP_stops_txt"

# Where to write each route‐stop shapefile (will be created if missing)
OUTPUT_DIR   = BASE_DIR / "vrp_stops_visualization" / "Munich_DHL_Samples_100_stops_1"

# JSON that maps ORIGINAL IDs (strings) → VRP‐IDs (ints in 1–100)
MAPPING_JSON = BASE_DIR / "data" / "distance_matrices" / "Munich_Sample_100_RoadData_MapToOriginal.json"

# Path to the file geodatabase and the name of the point layer inside it
POINTS_GDB   = r""
POINTS_LAYER = "DHL_Warehouse_and_PostBoxes"

# Field in the layer that holds the original ID (must match keys in MAPPING_JSON)
ID_FIELD     = "ID"

# CRS for the output shapefile
TARGET_CRS    = "EPSG:4326"  # WGS84


def main():
    # 1) Load and INVERT the JSON mapping so we get: vrp_id (int) → original_id (string)
    if not MAPPING_JSON.exists():
        raise FileNotFoundError(f"Cannot find mapping JSON at: {MAPPING_JSON}")
    with open(MAPPING_JSON, "r") as f:
        raw_map = json.load(f)

    # raw_map maps original_id_str → vrp_id_int
    vrp_to_orig = {}
    for orig_str, vrp_val in raw_map.items():
        try:
            vrp_int = int(vrp_val)
        except (ValueError, TypeError):
            raise ValueError(
                f"Expected integer VRP‐ID in JSON, but got '{vrp_val}' for original ID '{orig_str}'"
            )
        vrp_to_orig[vrp_int] = orig_str

    # 2) Ensure OUTPUT_DIR exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 3) Read the entire point layer from the File Geodatabase into a GeoDataFrame
    try:
        points_gdf = gpd.read_file(str(POINTS_GDB), layer=POINTS_LAYER)
    except Exception as e:
        raise RuntimeError(f"Failed to read layer '{POINTS_LAYER}' from '{POINTS_GDB}': {e}")

    if ID_FIELD not in points_gdf.columns:
        raise KeyError(
            f"Field '{ID_FIELD}' not found in layer '{POINTS_LAYER}'. "
            f"Available fields: {list(points_gdf.columns)}"
        )

    # Convert the ID_FIELD to string so it matches the JSON keys (which are strings)
    points_gdf[ID_FIELD] = points_gdf[ID_FIELD].astype(str)

    # 3a) Extract the “depot” row(s) (original ID = "1")
    depot_gdf = points_gdf[points_gdf[ID_FIELD] == "1"]
    if depot_gdf.empty:
        raise KeyError("Depot with original ID = '1' not found in the point layer.")
    # We'll copy from depot_gdf each time we need a depot row.

    # 4) Loop over every TXT file in TXT_DIR
    if not TXT_DIR.exists():
        raise FileNotFoundError(f"TXT_DIR does not exist: {TXT_DIR}")

    for txt_file in sorted(TXT_DIR.glob("*.txt")):
        if not txt_file.is_file():
            continue

        txt_name = txt_file.stem  # filename without .txt
        print(f"Processing '{txt_file.name}' ...")

        # Create a subdirectory under OUTPUT_DIR named after the txt filename
        subdir = OUTPUT_DIR / txt_name
        os.makedirs(subdir, exist_ok=True)

        # Read all lines and strip whitespace
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines()]

        # Parse out any line that begins with "Route #"
        routes = {}  # route_num (int) → list of VRP‐IDs (ints)
        for ln in lines:
            if ln.startswith("Route #"):
                parts = ln.split(":", maxsplit=1)
                if len(parts) != 2:
                    continue
                header = parts[0].strip()   # e.g. "Route #3"
                payload = parts[1].strip()  # e.g. "45 95 24 23 46 32"
                try:
                    rnum = int(header.replace("Route #", "").strip())
                except ValueError:
                    continue

                if payload == "":
                    vrp_list = []
                else:
                    try:
                        vrp_list = [int(tok) for tok in payload.split()]
                    except ValueError:
                        raise ValueError(f"Non‐integer token in route line: '{payload}'")

                routes[rnum] = vrp_list

        if not routes:
            print(f"  → No 'Route #' lines found in '{txt_file.name}'. Skipping.")
            continue

        # Collect each route's GeoDataFrame (in TARGET_CRS) for later concatenation
        all_route_gdfs = []

        # 5) Process each route
        for rnum, vrp_ids in routes.items():
            # Build an ordered list of original IDs, including depot at start and end
            sequence_list = []
            # 5a) Depot at start
            sequence_list.append("1")  # original ID of depot is "1"
            # 5b) Translate VRP‐IDs → original IDs
            for vid in vrp_ids:
                if vid not in vrp_to_orig:
                    raise KeyError(f"VRP ID '{vid}' not found in mapping JSON.")
                sequence_list.append(vrp_to_orig[vid])
            # 5c) Depot at end
            sequence_list.append("1")

            # Now build a GeoDataFrame for this route (still in the original CRS)
            route_rows = []
            for seq_idx, orig_id in enumerate(sequence_list, start=1):
                # Select the row(s) for this original ID
                stop_gdf = points_gdf[points_gdf[ID_FIELD] == orig_id]
                if stop_gdf.empty:
                    # This shouldn’t happen (we know depot and sampled IDs are in points_gdf)
                    print(f"    Warning: original ID '{orig_id}' not found in points_gdf.")
                    continue

                # There should normally be exactly 1 row. If multiple, we include all but assign same sequence.
                for _, row in stop_gdf.iterrows():
                    # Build a dict of attributes + geometry + new fields
                    attrs = row.drop(labels="geometry").to_dict()
                    attrs["route_id"] = rnum
                    attrs["sequence"] = seq_idx
                    geom = row.geometry
                    route_rows.append({**attrs, "geometry": geom})

            if not route_rows:
                print(f"  → Route {rnum} produced no output rows. Skipping.")
                continue

            # Convert list of dicts into a GeoDataFrame
            route_gdf = gpd.GeoDataFrame(route_rows, crs=points_gdf.crs)

            # Reproject to TARGET_CRS
            try:
                route_gdf = route_gdf.to_crs(TARGET_CRS)
            except Exception as e:
                raise RuntimeError(f"Failed to reproject route {rnum} to {TARGET_CRS}: {e}")

            # Save this route’s shapefile: "[txt_name]_route_<rnum>.shp"
            route_filename = f"{txt_name}_route_{rnum}.shp"
            out_path = subdir / route_filename
            try:
                route_gdf.to_file(str(out_path), driver="ESRI Shapefile")
            except Exception as e:
                raise RuntimeError(f"Failed to write shapefile for route {rnum} to '{out_path}': {e}")

            print(f"  → Route {rnum}: wrote '{route_filename}' ({len(route_gdf)} points including depot).")

            # Keep for concatenation
            all_route_gdfs.append(route_gdf)

        # 6) After all individual routes, create a combined GeoDataFrame and save "[txt_name]_allRoutes.shp"
        if all_route_gdfs:
            combined_gdf = gpd.GeoDataFrame(
                pd.concat(all_route_gdfs, ignore_index=True),
                crs=all_route_gdfs[0].crs
            )
            all_filename = f"{txt_name}_allRoutes.shp"
            all_out_path = subdir / all_filename
            try:
                combined_gdf.to_file(str(all_out_path), driver="ESRI Shapefile")
            except Exception as e:
                raise RuntimeError(f"Failed to write combined shapefile '{all_out_path}': {e}")

            print(f"  → All routes combined: wrote '{all_filename}' ({len(combined_gdf)} total rows).")
        else:
            print(f"  → No valid routes found for '{txt_name}', skipping combined shapefile.")

    print("All TXT files processed. Output folders and shapefiles are under:")
    print(f"  {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
