import time
import requests
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0"}

BASE = "https://biosteel.ca"
COLLECTION_JSON = BASE + "/collections/all-products/products.json?limit=250&page={page}"

rows = []
page = 1

while True:
    url = COLLECTION_JSON.format(page=page)
    r = requests.get(url, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        print(f"Stopped at page {page}. HTTP {r.status_code}")
        break

    data = r.json()
    products = data.get("products", [])

    if not products:
        print(f"No more products at page {page}. Done.")
        break

    for p in products:
        product_name = p.get("title", "")
        handle = p.get("handle", "")
        vendor = p.get("vendor", "")
        product_type = p.get("product_type", "")

        for v in p.get("variants", []):
            rows.append({
                "product_name": product_name,
                "handle": handle,
                "vendor": vendor,
                "product_type": product_type,
                "variant_title": v.get("title", ""),
                "price": v.get("price", ""),
                "sku": v.get("sku", ""),
                "available": v.get("available", ""),
            })

    print(f"Fetched page {page} | products: {len(products)} | rows: {len(rows)}")
    page += 1
    time.sleep(1.5)

df = pd.DataFrame(rows)
df.to_csv("biosteel_products.csv", index=False)
print("Done! Created biosteel_products.csv")
