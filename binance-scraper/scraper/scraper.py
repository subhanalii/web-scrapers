import requests
from datetime import datetime

def get_market_data(quote, symbols_to_include=None):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    res = requests.get(url)
    if res.status_code != 200:
        return []

    all_data = res.json()
    filtered = [coin for coin in all_data if coin["symbol"].endswith(quote)]

    for coin in filtered:
        coin["base"] = coin["symbol"].replace(quote, "")
        coin["marketCap"] = float(coin.get("lastPrice", 0)) * float(coin.get("quoteVolume", 0))

    if symbols_to_include:
        filtered = [coin for coin in filtered if coin["symbol"] in symbols_to_include]
        for coin in filtered:
            coin["sparkline"] = fetch_sparkline(coin["symbol"])

    return filtered

def fetch_sparkline(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=24"
        res = requests.get(url, timeout=5)
        data = res.json()
        return [float(entry[4]) for entry in data]
    except:
        return []

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
            if "newListing" in p.get("tags", []):
                new_listings.append({
                    "symbol": p["s"],
                    "base": p["b"],
                    "quote": p["q"],
                    "listedDate": p.get("listedDate", 0),
                    "tags": p["tags"]
                })

        return new_listings
    except:
        return []
