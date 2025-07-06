import re
import pandas as pd

# Fill in your own file locations below
INPUT_NORM_CSV = r""  # CSV that holds the “input” normalized differences
ROUTES_CSV     = r""  # CSV with total route lengths from your VRP runs
OUT_CSV        = r""  # Where the merged results should be written

# 1) load the input-side normalized differences
df_in = pd.read_csv(INPUT_NORM_CSV)          # expects columns: ID, NormDifference
df_in = df_in.rename(columns={"NormDifference": "InputNormalizedDifference"})

# 2) load the total route lengths produced by the solver
df = pd.read_csv(ROUTES_CSV)                 # expects columns: Simulation_Name, Total_Route_Length

# 3) pull the sample ID and data type (RoadData or EuclideanData) out of the name
def parse_name(name):
    m = re.search(r"ID(\d+)_(RoadData|EuclideanData)", name)
    if not m:
        return pd.NA, pd.NA
    return int(m.group(1)), m.group(2)

df[["ID", "Type"]] = df["Simulation_Name"].apply(lambda x: pd.Series(parse_name(x)))

# 4) for each sample ID, compute the output-side normalized difference
records = []
for sample_id, grp in df.groupby("ID"):
    grp = grp.dropna(subset=["Type"])
    min_road = grp.loc[grp["Type"] == "RoadData",      "Total_Route_Length"].min()
    min_euc  = grp.loc[grp["Type"] == "EuclideanData", "Total_Route_Length"].min()

    if pd.isna(min_road) or pd.isna(min_euc) or min_euc == 0:
        out_norm = float("nan")
    else:
        out_norm = abs(min_road - min_euc) / min_euc

    records.append({"ID": sample_id, "OutputNormalizedDifference": out_norm})

df_out_norm = pd.DataFrame(records)

# 5) merge the input- and output-side metrics and save
df_final = (
    pd.merge(df_in, df_out_norm, on="ID", how="outer")
      .sort_values("ID")
)

df_final.to_csv(OUT_CSV, index=False)
print(f"Wrote {len(df_final)} rows to {OUT_CSV}")


