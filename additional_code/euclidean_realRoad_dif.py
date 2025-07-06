import os
import json
import pandas as pd


BASE_DIR = r"" # base folder where all 100MunichSampleDMS_ID{ID} directories are in

output = []
total_ids = 1000
processed = 0

for sample_id in range(total_ids):
    print(f"[{processed}/{total_ids}] Processing ID {sample_id}…", flush=True)
    
    folder = os.path.join(BASE_DIR, f"100MunichSampleDMS_ID{sample_id}")
    file_euc  = os.path.join(folder, "OrgEntries0.json")
    file_road = os.path.join(folder, "OrgEntries1.json")
    
    if not (os.path.isfile(file_euc) and os.path.isfile(file_road)):
        print(f"  → Skipped ID {sample_id}: missing JSON", flush=True)
        processed += 1
        continue

    # load into DataFrames
    df_euc  = pd.DataFrame(json.load(open(file_euc,  'r')))
    df_road = pd.DataFrame(json.load(open(file_road, 'r')))
    
    # merge on OriginID & DestinationID
    df = pd.merge(
        df_euc, df_road,
        on=["OriginID", "DestinationID"],
        suffixes=("_euclid", "_road")
    )
    
    # sum up total distances
    total_euc  = df["Total_Length_euclid"].sum()
    total_road = df["Total_Length_road"].sum()
    
    # normalized difference
    norm_diff = (total_road - total_euc) / total_euc
    
    output.append({
        "ID": sample_id,
        "NormDifference": norm_diff
    })

    processed += 1
    print(f"  → Done ID {sample_id} (norm diff = {norm_diff:.4f})", flush=True)

# make DataFrame of results and save
df_out = pd.DataFrame(output)
out_path = "Euclidean_RealRoad_NormalizedDiff_Munich_1000x100.csv"
df_out.to_csv(out_path, index=False)

print(f"\nAll done — processed {processed}/{total_ids} IDs. Results written to {out_path}")
