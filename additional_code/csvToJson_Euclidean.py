import pandas as pd
import json
from pathlib import Path

# Tell the script where to find your data
CSV_IN   = Path(r"")  # e.g. r"C:\Data\distance_matrix.csv"
JSON_OUT = Path(r"")  # e.g. r"C:\Data\distance_matrix.json"

# Read the CSV.  If your file uses regular commas for both separators and decimals,
# change sep=";" to "," and decimal="," to "."
df = pd.read_csv(
    CSV_IN,
    sep=";",           # field separator
    decimal=",",       # decimal symbol
    dtype={"IN_FID": int, "NEAR_FID": int}
)

# Rename columns so they’re easier to work with
df = df.rename(columns={
    "IN_FID":   "OriginID",
    "NEAR_FID": "DestinationID",
    "NEAR_DIST": "Total_Length"
})

# Make sure the distance column is stored as a float
df["Total_Length"] = df["Total_Length"].astype(float)

# Export to a nicely formatted JSON file
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
with JSON_OUT.open("w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, indent=2)

print(f"Saved {len(df):,} records to {JSON_OUT}")

