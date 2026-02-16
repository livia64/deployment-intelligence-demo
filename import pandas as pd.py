import pandas as pd

# Load scraped data
df = pd.read_csv("olipop_products.csv")

# Basic metrics
total_variants = len(df)
unique_products = df["product_name"].nunique()
avg_variants_per_product = total_variants / unique_products

# SKU Volume Score
if total_variants < 40:
    score_sku_volume = 0
elif total_variants < 80:
    score_sku_volume = 1
elif total_variants < 150:
    score_sku_volume = 2
else:
    score_sku_volume = 3

# Variant Density Score
if avg_variants_per_product < 2:
    score_variant_density = 0
elif avg_variants_per_product < 4:
    score_variant_density = 1
elif avg_variants_per_product < 6:
    score_variant_density = 2
else:
    score_variant_density = 3

# Availability Volatility
unavailable_ratio = (df["available"] == False).mean()

if unavailable_ratio < 0.05:
    score_availability = 0
elif unavailable_ratio < 0.15:
    score_availability = 1
else:
    score_availability = 2

# Simple total score (partial model)
final_score = score_sku_volume + score_variant_density + score_availability

# Create Google Sheets ready table
summary = pd.DataFrame([{
    "brand": "OLIPOP",
    "total_variants": total_variants,
    "unique_products": unique_products,
    "avg_variants_per_product": round(avg_variants_per_product, 2),
    "score_sku_volume_0_3": score_sku_volume,
    "score_variant_density_0_3": score_variant_density,
    "score_availability_0_2": score_availability,
    "final_score": final_score
}])

summary.to_csv("olipop_complexity_scores.csv", index=False)

print("Done! Created olipop_complexity_scores.csv")
