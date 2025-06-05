#!/usr/bin/env python3
import re
from pathlib import Path
import geopandas as gpd

# ——— CONFIGURATION ———
# Folder where your solution txts now live (with headers + “Route #i:” lines)
TXT_DIR      = Path(r"")
# Where to dump the point‐stop shapefiles
OUTPUT_DIR   = Path(r"")
POINTS_GDB   = r""
POINTS_LAYER = "UtahStores_Small_WGS84"
ID_FIELD     = "ID"
CRS          = "EPSG:4326"

DEPOT_ID     = 1    # shapefile ID of your depot point
ID_OFFSET    = 1    # how much to add to each client ID

def read_routes_from_txt(txt_fp: Path):
    """
    Ignores the header, picks up lines like:
      Route #1: 2 9 81 ...
    and returns [[2,9,81,...], ...].
    """
    pattern = re.compile(r"^Route\s+#\d+:\s+(.*)$")
    routes = []
    for line in txt_fp.read_text().splitlines():
        m = pattern.match(line.strip())
        if m:
            routes.append([int(tok) for tok in m.group(1).split()])
    if not routes:
        raise RuntimeError(f"No routes found in {txt_fp.name}")
    return routes

def export_stops(routes, out_fp: Path):
    # load all points once
    pts = gpd.read_file(POINTS_GDB, layer=POINTS_LAYER)
    pts = pts.set_index(ID_FIELD)

    print(f"→ Applying a constant ID_OFFSET = {ID_OFFSET}")

    records = []
    for ridx, route in enumerate(routes, start=1):
        # always start+end at depot
        seq_ids = [DEPOT_ID] + route + [DEPOT_ID]
        for seq, nid in enumerate(seq_ids, start=1):
            # shift only client IDs
            shp_id = DEPOT_ID if nid == DEPOT_ID else nid + ID_OFFSET

            try:
                geom = pts.loc[shp_id].geometry
            except KeyError:
                raise KeyError(
                    f"Could not find shapefile ID {shp_id} "
                    f"(from TXT id {nid} + offset {ID_OFFSET})"
                )

            records.append({
                "route_id": ridx,
                "seq":       seq,
                ID_FIELD:    shp_id,   # ← add: keep the original point’s ID
                "geometry":  geom
            })

    out_gdf = gpd.GeoDataFrame(records, geometry="geometry", crs=CRS)
    if out_fp.exists():
        out_fp.unlink()
    out_gdf.to_file(out_fp)
    print(f"→ Exported {len(out_gdf)} stops to {out_fp.name}")

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for txt in sorted(TXT_DIR.glob("*.txt")):
        try:
            routes = read_routes_from_txt(txt)
        except RuntimeError as e:
            print(f"⚠️  {e} — skipping {txt.name}")
            continue

        shp_name = OUTPUT_DIR / f"{txt.stem}_stops.shp"
        export_stops(routes, shp_name)
