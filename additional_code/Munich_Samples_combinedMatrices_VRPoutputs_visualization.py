#!/usr/bin/env python3
import arcpy
import json
import re
from pathlib import Path

# User parameters: replace the placeholders below with your own paths
RESULTS_ROOT = Path(
    # Folder that holds the VRP result JSON files
)
MAPPINGS_ROOT = Path(
    # Folder that contains the partner-ID mapping sub-folders
)
OUTPUT_DIR = Path(
    # Folder where the script will write the new shapefiles
)
POINTS_GDB = Path(
    # Path to the geodatabase that stores your point feature class
)
POINTS_LAYER = "Munich_DHL_Locations2"  # Name of the feature class inside the GDB
ORIG_ID_FIELD = "ID"                    # Field that stores the original ID
DEPOT_ORIG_ID = 1                       # ID value of the depot feature

arcpy.env.overwriteOutput = True
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Get the spatial reference from the points layer and fetch the depot geometry
orig_fc = str(POINTS_GDB / POINTS_LAYER)
sp_ref = arcpy.Describe(orig_fc).spatialReference
with arcpy.da.SearchCursor(
    orig_fc,
    ["SHAPE@"],
    where_clause=f"{ORIG_ID_FIELD} = {DEPOT_ORIG_ID}"
) as cursor:
    depot_geom = next(cursor)[0]

# Cache partner-to-original lookups so each mapping file is read only once
_partner_cache = {}


def load_partner_dict(id_token: str):
    """Return a dict that maps partner indexes to original IDs for this sample."""
    if id_token in _partner_cache:
        return _partner_cache[id_token]

    # Find the folder under MAPPINGS_ROOT whose name ends with the ID token
    mapping_dir = None
    for d in MAPPINGS_ROOT.iterdir():
        if d.is_dir() and d.name.endswith(id_token):
            mapping_dir = d
            break
    if mapping_dir is None:
        raise FileNotFoundError(
            f"Could not find a mapping folder ending in {id_token} under {MAPPINGS_ROOT}"
        )

    map_path = mapping_dir / "partnerIDS.json"
    if not map_path.is_file():
        raise FileNotFoundError(f"Missing partnerIDS.json at {map_path}")

    with map_path.open() as f:
        orig2partner = json.load(f)

    partner2orig = {int(v): int(k) for k, v in orig2partner.items()}
    _partner_cache[id_token] = partner2orig
    return partner2orig


# Walk through every result set and create the corresponding shapefile
for sample_folder in RESULTS_ROOT.iterdir():
    if not sample_folder.is_dir():
        continue

    for res_path in sample_folder.glob("*_resDict.json"):
        with res_path.open() as f:
            runs = json.load(f)

        for j, run in enumerate(runs, start=1):
            # Extract the ID## token from DMUsedName
            m = re.search(r"/ID(\d+)/", run["DMUsedName"])
            if not m:
                raise ValueError(f"No ID## in DMUsedName: {run['DMUsedName']}")
            id_token = f"ID{m.group(1)}"

            # Matrix type is the last segment before ".json"
            matrix_type = Path(run["DMUsedName"]).stem

            partner2orig = load_partner_dict(id_token)

            shp_name = (
                f"Munich_100Samples_combinedMatrices_"
                f"{id_token}_{matrix_type}_varyingDemand_{j}.shp"
            )
            out_shp = OUTPUT_DIR / shp_name

            if out_shp.exists():
                print(f"Skipping existing {shp_name}")
                continue

            print(f"Creating {shp_name}")
            arcpy.CreateFeatureclass_management(
                str(OUTPUT_DIR), shp_name, "POINT", spatial_reference=sp_ref
            )

            # Add the required fields
            for fld, typ in [
                ("OriginalID", "LONG"),
                ("SimID", "TEXT"),
                ("RouteID", "LONG"),
                ("SeqID", "LONG"),
            ]:
                arcpy.AddField_management(str(out_shp), fld, typ, field_length=50)

            # Insert depot and customer points
            with arcpy.da.InsertCursor(
                str(out_shp),
                ["SHAPE@", "OriginalID", "SimID", "RouteID", "SeqID"]
            ) as cur:
                for r_id, route in enumerate(run["routes"], start=1):
                    # Depot at the start of the route
                    cur.insertRow((depot_geom, DEPOT_ORIG_ID, matrix_type, r_id, 1))

                    # Customer stops
                    for seq, sample_pt in enumerate(route, start=2):
                        orig_id = partner2orig[sample_pt + 1]  # partner indices are 1-based
                        geom = next(
                            arcpy.da.SearchCursor(
                                orig_fc,
                                ["SHAPE@"],
                                where_clause=f"{ORIG_ID_FIELD} = {orig_id}"
                            )
                        )[0]
                        cur.insertRow((geom, orig_id, matrix_type, r_id, seq))

                    # Depot again at the end of the route
                    cur.insertRow(
                        (depot_geom, DEPOT_ORIG_ID, matrix_type, r_id, len(route) + 2)
                    )

print("All done!")

