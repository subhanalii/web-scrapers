import requests
from datetime import datetime

def get_tagged_new_listings():
    url = "https://www.binance.com/bapi/asset/v1/public/asset-service/product/get-products"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        new_listings = []
        for p in data.get("data", []):
            tags = p.get("tags", [])
            if "newListing" in tags:
                new_listings.append({
                    "symbol": p["s"],
                    "base": p["b"],
                    "quote": p["q"],
                    "listedDate": p.get("listedDate", 0),
                    "tags": tags
                })

        return new_listings

    except Exception as e:
        print("❌ Error fetching data:", e)
        return []

# Run
tokens = get_tagged_new_listings()

if not tokens:
    print("⚠️ No new listings found based on tag filters.")
else:
    print(f"✅ {len(tokens)} new listings found:\n")
    for t in tokens:
        date_str = "N/A"
        if t["listedDate"]:
            date_str = datetime.utcfromtimestamp(t["listedDate"] / 1000).strftime('%Y-%m-%d')
        print(f"🆕 {t['symbol']} ({t['base']}/{t['quote']}) - Listed on: {date_str} | Tags: {t['tags']}")
