from flask import Flask, render_template
import json, requests
from datetime import datetime

app = Flask(__name__)
TRACKED_FILE = "tracked_tokens.json"

def human_format(n):
    return f"${n/1e6:.1f}M" if n >= 1e6 else f"${n/1e3:.0f}k" if n >= 1e3 else f"${n}"

def get_token_stats(chain, address):
    r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/{chain}/{address}")
    return r.json() if r.status_code == 200 else []

def load_tracked_tokens():
    try:
        with open(TRACKED_FILE) as f:
            return json.load(f)
    except:
        return []

@app.route("/")
def dashboard():
    tokens = load_tracked_tokens()
    enriched = []

    for t in tokens:
        stats = get_token_stats(t["chain"], t["tokenAddress"])
        if not stats:
            continue
        pair = stats[0]
        try:
            current_price = float(pair.get("priceUsd", 0))
            gain = round(current_price / float(t["entry_price"]), 2)

            enriched.append({
                "name": t["name"],
                "entry_price": t["entry_price"],
                "current_price": current_price,
                "gain": gain,
                "market_cap": human_format(pair.get("fdv", 0)),
                "liquidity": human_format(pair.get("liquidity", {}).get("usd", 0)),
                "volume": human_format(pair.get("volume", {}).get("h24", 0)),
                "url": t["url"],
                "token_address": t["tokenAddress"]
            })
        except Exception as e:
            print(f"Skipping a token due to error: {e}")
            continue

    return render_template("dashboard.html", tokens=enriched)

if __name__ == "__main__":
    app.run(debug=True)
