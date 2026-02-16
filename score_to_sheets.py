import sys
import pandas as pd

if len(sys.argv) < 2:
    print("Usage: python score_to_sheets.py <csv_file>")
    sys.exit()

input_file = sys.argv[1]
df = pd.read_csv(input_file)

# ---- metrics ----
total_variants = len(df)
unique_products = df["product_name"].nunique()
avg_variants_per_product = total_variants / max(unique_products, 1)

# ---- scores ----
def score_sku_volume(n: int) -> int:
    if n < 40: return 0
    if n < 80: return 1
    if n < 150: return 2
    return 3

def score_variant_density(x: float) -> int:
    if x < 2: return 0
    if x < 4: return 1
    if x < 6: return 2
    return 3

def score_availability(unavailable_ratio: float) -> int:
    if unavailable_ratio < 0.05: return 0
    if unavailable_ratio < 0.15: return 1
    return 2

# normalize available column
avail = df["available"].astype(str).str.strip().str.lower().map({"true": True, "false": False})
unavailable_ratio = (avail == False).mean()

s1 = score_sku_volume(total_variants)
s2 = score_variant_density(avg_variants_per_product)
s3 = score_availability(unavailable_ratio)

final_score = s1 + s2 + s3

tier = "HIGH" if final_score >= 6 else ("MEDIUM" if final_score >= 4 else "LOW")

# ---- sheets-ready table ----
summary = pd.DataFrame([{
 "brand": "BIOSTEEL",

    "total_variants": total_variants,
    "unique_products": unique_products,
    "avg_variants_per_product": round(avg_variants_per_product, 2),
    "unavailable_ratio": round(float(unavailable_ratio), 4),

    "score_sku_volume_0_3": s1,
    "score_variant_density_0_3": s2,
    "score_availability_0_2": s3,

    "final_score": final_score,
    "tier": tier,
}])

output_file = input_file.replace(".csv", "_complexity_scores.csv")
summary.to_csv(output_file, index=False)
print(f"Done! Created {output_file}")
