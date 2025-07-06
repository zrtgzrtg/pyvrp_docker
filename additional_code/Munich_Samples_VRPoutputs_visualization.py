#!/usr/bin/env python3
import arcpy
import json
import os
import re
from pathlib import Path

# Update the paths below with your own directories and geodatabase
RESULTS_ROOT = Path(
    # Folder that contains the VRP result JSON files
)
MAPPINGS_ROOT = Path(
    # Folder that holds the partner-ID mapping sub-folders
)
OUTPUT_DIR = Path(
    # Folder where the script will write the shapefiles
)
POINTS_GDB = Path(
    # Path to the geodatabase that stores your point feature class
)
POINTS_LAYER = "DHL_Warehouse_and_PostBoxes"  # Name of the feature class inside the GDB
ORIG_ID_FIELD = "ID"                          # Field that stores the original ID
DEPOT_ORIG_ID = 1                             # ID value of the depot feature

arcpy.env.overwriteOutput = True
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Get spatial reference and depot geometry from the points layer
orig_fc = str(POINTS_GDB / POINTS_LAYER)
sp_ref = arcpy.Describe(orig_fc).spatialReference
with arcpy.da.SearchCursor(
        orig_fc,
        ["SHAPE@"],
        where_clause=f"{ORIG_ID_FIELD} = {DEPOT_ORIG_ID}"
) as cursor:
    depot_geom = next(cursor)[0]

# Cache partner-to-original mappings so each mapping file is loaded only once
_partner_cache = {}

def load_partner_dict(id_token: str):
    """Return a dict that maps partner indices to original IDs."""
    if id_token in _partner_cache:
        return _partner_cache[id_token]

    map_path = MAPPINGS_ROOT / f"500MunichSampleDMS_{id_token}" / "partnerIDS.json"
    if not map_path.is_file():
        raise FileNotFoundError(f"Missing partnerIDS.json at {map_path}")

    with map_path.open() as f:
        orig2partner = json.load(f)

    partner2orig = {int(v): int(k) for k, v in orig2partner.items()}
    _partner_cache[id_token] = partner2orig
    return partner2orig

processed_ct = 0
skipped_ct = 0

# Walk through every result folder, read each resDict file, and build a shapefile
for sample_folder in RESULTS_ROOT.iterdir():
    for res_name, cat_map in [
        ("0_resDict.json", [("RoadData", 0, 6), ("EuclideanData", 6, 2)]),
        ("1_resDict.json", [("CombinedData", 0, 8)]),
    ]:
        res_path = sample_folder / res_name
        if not res_path.is_file():
            continue

        with res_path.open() as f:
            runs = json.load(f)

        for run_idx, run in enumerate(runs):
            # Find the “ID##” token in DMUsedName
            m = re.search(r"ID(\d+)", run["DMUsedName"])
            if not m:
                raise ValueError(f"No ID token in {run['DMUsedName']}")
            id_token = f"ID{m.group(1)}"

            partner2orig = load_partner_dict(id_token)

            # Work out which category this run belongs to
            for cat, start, count in cat_map:
                if start <= run_idx < start + count:
                    cat_seq = f"{cat}{run_idx - start + 1}"
                    break

            # Use the X_setUsedName in the output filename
            xset = run["X_setUsedName"].replace("/", "_")

            shp_name = f"Munich_500Samples_{id_token}_{cat_seq}_{xset}.shp"
            out_shp = OUTPUT_DIR / shp_name

            if out_shp.exists():
                skipped_ct += 1
                print(f"Skipping {shp_name} (already exists — processed {processed_ct}, skipped {skipped_ct})")
                continue

            processed_ct += 1
            print(f"Creating {shp_name} (processed {processed_ct}, skipped {skipped_ct})")

            arcpy.CreateFeatureclass_management(
                str(OUTPUT_DIR), shp_name, "POINT", spatial_reference=sp_ref
            )

            for fld, typ in [
                ("OriginalID", "LONG"),
                ("SimID", "TEXT"),
                ("RouteID", "LONG"),
                ("SeqID", "LONG"),
            ]:
                arcpy.AddField_management(str(out_shp), fld, typ, field_length=50)

            with arcpy.da.InsertCursor(
                str(out_shp),
                ["SHAPE@", "OriginalID", "SimID", "RouteID", "SeqID"]
            ) as cur:
                for r_id, route in enumerate(run["routes"], start=1):
                    # Depot as the first stop
                    cur.insertRow((depot_geom, DEPOT_ORIG_ID, cat_seq, r_id, 1))

                    # Customer stops
                    for seq, sample_pt in enumerate(route, start=2):
                        partner_idx = sample_pt + 1   # partner mapping is 1-based
                        orig_id = partner2orig[partner_idx]
                        geom = next(
                            arcpy.da.SearchCursor(
                                orig_fc,
                                ["SHAPE@"],
                                where_clause=f"{ORIG_ID_FIELD} = {orig_id}"
                            )
                        )[0]
                        cur.insertRow((geom, orig_id, cat_seq, r_id, seq))

                    # Depot again at the end of the route
                    cur.insertRow(
                        (depot_geom, DEPOT_ORIG_ID, cat_seq, r_id, len(route) + 2)
                    )

print(f"Done. Processed {processed_ct} shapefile(s); skipped {skipped_ct}.")
print(f"Shapefiles are saved to {OUTPUT_DIR}")


