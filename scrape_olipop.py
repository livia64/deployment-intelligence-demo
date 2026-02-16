import requests
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0"}

url = "https://drinkolipop.com/collections/all/products.json?limit=250"

r = requests.get(url, headers=HEADERS)
r.raise_for_status()

data = r.json()

rows = []

for product in data["products"]:
    for variant in product["variants"]:
        rows.append({
            "product_name": product["title"],
            "variant_title": variant["title"],
            "price": variant["price"],
            "sku": variant["sku"],
            "available": variant["available"],
        })

df = pd.DataFrame(rows)
df.to_csv("olipop_products.csv", index=False)

print("Done! olipop_products.csv created")
