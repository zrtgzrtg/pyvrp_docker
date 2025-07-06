"""
Convert a semicolon-separated CSV to JSON, keeping only
OriginID, DestinationID and Total_Length.

The CSV is assumed to use European commas as decimal marks (1.234,56 ⇒ 1234.56).
"""

import pandas as pd
import json
from pathlib import Path

# Tell the script where to find your files
INPUT_CSV  = Path(          # path to the source CSV
    # r"C:\Data\Utah_RoadData.csv"
)
OUTPUT_JSON = Path(         # path for the new JSON file
    # r"C:\Data\Utah_RoadData.json"
)

# 1) Read the CSV (semicolon separators, comma decimals)
df = pd.read_csv(INPUT_CSV, sep=";", decimal=",")

# 2) Keep only the columns we care about
df = df[["OriginID", "DestinationID", "Total_Length"]]

# 3) Convert to a list of dictionaries
records = df.to_dict(orient="records")

# 4) Write pretty-printed JSON
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_JSON.open("w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Saved {len(records)} records to {OUTPUT_JSON}")

