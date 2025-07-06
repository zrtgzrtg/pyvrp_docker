import re
import pandas as pd
from pathlib import Path
import shutil

# Update these paths before running the script
csv_path   = Path(
    # Path to the CSV with total route lengths
)
shp_dir    = Path(
    # Folder that holds the stop shapefiles (*.shp, .dbf, .shx, .prj)
)
output_dir = Path(
    # Folder where the selected shapefiles will be copied
)

# Show floats with two-decimal formatting when printing DataFrames
pd.set_option("display.float_format", "{:,.2f}".format)

# 1) Read the CSV produced by the total-route-lengths script
df = pd.read_csv(csv_path)

# 2) Remove “.shp” so we can parse the base names more easily
df["BaseName"] = df["Simulation_Name"].str.replace(r"\.shp$", "", regex=True)

# 3) Extract the case ID, matrix method, and run number from the base name
def parse_name(base):
    parts = base.split("_")
    for i, part in enumerate(parts):
        if part.startswith("ID") and part[2:].isdigit():
            case_id = int(part[2:])
            if i + 1 < len(parts):
                m = re.match(
                    r"(?P<Method>EuclideanData|RoadData|CombinedData)(?P<Run>\d+)$",
                    parts[i + 1],
                )
                if m:
                    return case_id, m.group("Method"), int(m.group("Run"))
    return None, None, None

parsed = df["BaseName"].apply(parse_name)
df[["ID", "Method", "Run"]] = pd.DataFrame(parsed.tolist(), index=df.index)

# 4) Drop rows that didn’t match the expected pattern
mask = df["ID"].notna()
if not mask.all():
    print("Skipping unparsable rows:", df.loc[~mask, "BaseName"].tolist())
df = df.loc[mask].copy()

# 5) Ensure correct data types
df["ID"]  = df["ID"].astype(int)
df["Run"] = df["Run"].astype(int)
df["Length"] = df["Total_Route_Length"].astype(float)

# 6) For each (ID, Method), keep only the run with the smallest route length
idx    = df.groupby(["ID", "Method"])["Length"].idxmin()
minima = df.loc[idx, ["ID", "Method", "Run", "Length"]]

# 7) Pivot so each row is an ID and columns show Run and Length per Method
pivot = minima.pivot(index="ID", columns="Method", values=["Run", "Length"])
pivot.columns.set_names(["What", "Method"], inplace=True)
pivot = pivot.sort_index(axis=1, level="Method")

# 8) Absolute difference between EuclideanData and RoadData lengths
pivot[("Length", "diff")] = (
    pivot[("Length", "EuclideanData")] - pivot[("Length", "RoadData")]
).abs()

# 9) Identify the IDs with the smallest and largest differences
min_diff_id = pivot[("Length", "diff")].idxmin()
max_diff_id = pivot[("Length", "diff")].idxmax()

print(f"ID with MIN difference: {min_diff_id}")
print(pivot.loc[min_diff_id, ("Length", slice(None))].to_string())
print()
print(f"ID with MAX difference: {max_diff_id}")
print(pivot.loc[max_diff_id, ("Length", slice(None))].to_string())

# 10) Copy the shapefiles for the two extreme cases into a new folder
output_dir.mkdir(parents=True, exist_ok=True)

# Determine the common filename prefix (e.g. “Munich_300Samples”)
prefix = df["BaseName"].iloc[0].split("_ID", 1)[0]
suffix = "_varyingDemand"  # Keep this suffix if it matches your filenames

def copy_case(case_id, label):
    info = pivot.loc[case_id]
    print(f"--- {label} (ID {case_id}) ---")
    for method in ["EuclideanData", "RoadData", "CombinedData"]:
        run  = int(info[("Run", method)])
        base = f"{prefix}_ID{case_id}_{method}{run}{suffix}"
        for ext in [".shp", ".dbf", ".shx", ".prj"]:
            src = shp_dir / (base + ext)
            if src.exists():
                dst = output_dir / (base + ext)
                shutil.copy(src, dst)
                print(f"  Copied {base + ext}")

copy_case(min_diff_id, "MIN-DIFF")
copy_case(max_diff_id, "MAX-DIFF")

print(f"\nDone! Selected files are in:\n  {output_dir.resolve()}")







