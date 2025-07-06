#!/usr/bin/env python3
"""
Compute total route lengths for every VRP stop-file using its
corresponding distance matrix, then append the results to a CSV.

Shapefile schema:
    OriginalID  (0 = depot, other integers = customer IDs)
    RouteID
    SeqID       (1, 2, 3 … ; depot appears twice per route)
"""

import arcpy
import csv
import glob
import json
import os
import re
from collections import defaultdict
from pathlib import Path

# ------------------- paths: replace these with your own -------------------
STOPS_DIR = Path(
    # Folder that contains the stop shapefiles (*.shp)
)

MATRIX_ROOT = Path(
    # Folder that holds the distance-matrix subfolders (one per sample ID)
)

CSV_PATH = Path(
    # CSV file where the results will be saved (created if it doesn’t exist)
)
# -------------------------------------------------------------------------

CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
arcpy.env.overwriteOutput = True

# Cache distance matrices so each sample’s matrix is loaded only once
_matrix_cache: dict[int, dict[tuple[int, int], float]] = {}


def load_matrix(sample_id: int) -> dict[tuple[int, int], float]:
    """
    Return a dict keyed by (origin, dest) → total_length for the given ID##.
    """
    if sample_id in _matrix_cache:
        return _matrix_cache[sample_id]

    matrix_path = (
        MATRIX_ROOT
        / f"100MunichSampleDMS_ID{sample_id}"
        / "OrgEntries1.json"
    )
    if not matrix_path.is_file():
        raise FileNotFoundError(f"Matrix not found: {matrix_path}")

    with open(matrix_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    dist = {(e["OriginID"], e["DestinationID"]): e["Total_Length"]
            for e in entries}
    _matrix_cache[sample_id] = dist
    return dist


def total_route_length(route_ids: list[int], matrix: dict[tuple[int, int], float]) -> float:
    """
    Sum the leg lengths for an ordered list of node IDs.
    Uses (o,d) if present, otherwise falls back to (d,o) for symmetric matrices.
    """
    total = 0.0
    for o, d in zip(route_ids[:-1], route_ids[1:]):
        if (o, d) in matrix:
            total += matrix[(o, d)]
        elif (d, o) in matrix:
            total += matrix[(d, o)]
        else:
            raise KeyError(f"Distance ({o} → {d}) missing in matrix.")
    return total


def process_shapefile(shp: Path) -> float:
    """
    Read one stop shapefile and return the combined length of all its routes.
    """
    # Grab the numeric ID## token from the filename
    m = re.search(r"ID(\d+)", shp.name)
    if not m:
        raise ValueError(f"No ID token in filename: {shp.name}")
    sample_id = int(m.group(1))

    # 1) Load (or fetch cached) distance matrix
    matrix = load_matrix(sample_id)

    # 2) Collect points per route, ordered by SeqID
    routes: dict[int, list[tuple[int, int]]] = defaultdict(list)
    fields = ["RouteID", "SeqID", "OriginalID"]
    with arcpy.da.SearchCursor(str(shp), fields) as cur:
        for r_id, seq, orig in cur:
            routes[r_id].append((seq, orig))

    # 3) Compute total route lengths
    grand_total = 0.0
    for seq_list in routes.values():
        ordered = [1 if oid == 0 else oid
                   for _, oid in sorted(seq_list, key=lambda x: x[0])]
        grand_total += total_route_length(ordered, matrix)

    return grand_total


def main():
    # Open (or create) the CSV and add a header row if it’s new
    csv_exists = CSV_PATH.is_file()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not csv_exists:
            writer.writerow(["Simulation_Name", "Total_Route_Length"])

        # Process shapefiles in lexical order
        for shp_path in sorted(STOPS_DIR.glob("*.shp")):
            print(f"▶ Processing {shp_path.name} ...", end=" ", flush=True)
            try:
                total_len = process_shapefile(shp_path)
            except Exception as exc:
                print(f"ERROR: {exc}")
                continue

            writer.writerow([shp_path.name, total_len])
            print(f"✓ total = {total_len:.4f}")

    print(f"\nFinished. Results written to:\n  {CSV_PATH}")


if __name__ == "__main__":
    main()

