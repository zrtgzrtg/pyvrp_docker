import os
import json
import geopandas as gpd
from shapely.geometry import Point

# Fill in your own locations before running
RES_JSON  = r""  # Path to the resDict.json file that contains the VRP results
GDB_PATH  = r""  # Path to the File Geodatabase (.gdb) holding the point layer
GDB_LAYER = "Utah_GroceryStores_1161_Fixed"  # Name of the feature class inside the GDB
OUT_DIR   = r""  # Folder where the new shapefiles will be saved
BASENAME  = "Utah_1161x1161_VRP_stops_Data_{}.shp"  # {} will be replaced by 1..8
CRS       = "EPSG:4326"  # Coordinate reference system
ID_FIELD  = "ID"  # Field in the GDB layer that stores each store’s integer ID

os.makedirs(OUT_DIR, exist_ok=True)

# 1) Read the VRP results
with open(RES_JSON, "r", encoding="utf-8") as f:
    res = json.load(f)

# 2) Load the point layer from the GDB
stops_gdf = gpd.read_file(GDB_PATH, layer=GDB_LAYER)

# Build a quick lookup table: original ID → (x, y) coordinates
stop_coords = {
    int(row[ID_FIELD]): (row.geometry.x, row.geometry.y)
    for _, row in stops_gdf.iterrows()
}

# 3) Create a shapefile for each of the first eight VRP solutions
for i, entry in enumerate(res[:8], start=1):
    records = []
    for rid, route in enumerate(entry["routes"], start=1):
        # The JSON route omits the depot, so we add depot ID 1 before and after
        seq_original_ids = [1] + [sid + 1 for sid in route] + [1]

        for seq_idx, orig_id in enumerate(seq_original_ids, start=1):
            if orig_id not in stop_coords:
                raise KeyError(f"ID {orig_id} not found in the GDB layer")

            x, y = stop_coords[orig_id]
            records.append(
                {
                    "ID": orig_id,
                    "routeID": rid,
                    "seqID": seq_idx,
                    "geometry": Point(x, y),
                }
            )

    gdf = gpd.GeoDataFrame(records, crs=CRS)
    out_path = os.path.join(OUT_DIR, BASENAME.format(i))
    gdf.to_file(out_path)
    print(f"Saved {len(records)} points to {out_path}")

