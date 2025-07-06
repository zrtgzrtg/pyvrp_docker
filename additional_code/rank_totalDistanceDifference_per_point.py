#!/usr/bin/env python
"""
Compare Euclidean vs. road-network distances for every origin point
and rank points by percentage change.

Output: Munich_DHL_1747_RankedDiffs.json
"""

import json
from collections import defaultdict
from pathlib import Path

# FILE PATHS – adjust if necessary
euc_file  = Path(r"")
road_file = Path(r"")
out_file  = euc_file.with_name("Munich_DHL_1747_TotalDistanceDifRanked.json")

# 1. LOAD EUCLIDEAN DISTANCES INTO A LOOK-UP DICT
with euc_file.open("r", encoding="utf-8") as f:
    euc_matrix = json.load(f)

# key: (origin, destination)  ➜  value: euclidean length
euc_lookup = {(rec["OriginID"], rec["DestinationID"]): rec["Total_Length"]
              for rec in euc_matrix}

# 2. SCAN ROAD MATRIX AND ACCUMULATE TOTALS PER ORIGIN
sum_road = defaultdict(float)
sum_euc  = defaultdict(float)

with road_file.open("r", encoding="utf-8") as f:
    for rec in json.load(f):
        i, j   = rec["OriginID"], rec["DestinationID"]
        d_road = rec["Total_Length"]
        d_euc  = euc_lookup.get((i, j))

        # Skip if Euclidean entry missing
        if d_euc is None:
            continue

        sum_road[i] += d_road
        sum_euc[i]  += d_euc

# 3. BUILD RESULT LIST (one record per origin)
results = []
for i in sum_road.keys():                      # every origin seen
    diff_abs = sum_road[i] - sum_euc[i]
    diff_pct = (diff_abs / sum_euc[i]) * 100 if sum_euc[i] else 0.0

    results.append({
        "id": i,
        "real_distance_difference": diff_abs,
        "relative_distance_difference": diff_pct
    })

# 4. SORT BY PERCENTAGE DIFFERENCE (descending)
results.sort(key=lambda r: r["relative_distance_difference"], reverse=True)

# 5. SAVE TO JSON
with out_file.open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Ranked list written to: {out_file}")
