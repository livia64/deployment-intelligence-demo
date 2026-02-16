import glob
import os
import pandas as pd

INPUT_GLOB = "data/*_products.csv"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

def normalize_one(path: str) -> str:
    df = pd.read_csv(path)

    # required col
    if "product_name" not in df.columns:
        raise ValueError(f"{path} missing product_name")

    # ensure columns exist
    for col in ["variant_title", "price", "sku", "available"]:
        if col not in df.columns:
            df[col] = ""

    # normalize available to True/False
    df["available_norm"] = (
        df["available"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    )

    out_path = os.path.join(OUT_DIR, os.path.basename(path).replace(".csv", "_normalized.csv"))
    df.to_csv(out_path, index=False)
    return out_path

def main():
    files = sorted(glob.glob(INPUT_GLOB))
    if not files:
        print("No files found:", INPUT_GLOB)
        return

    for f in files:
        out = normalize_one(f)
        print("Normalized:", out)

if __name__ == "__main__":
    main()
