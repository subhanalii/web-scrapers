import requests, json, os, time
from datetime import datetime, timedelta
from notifier import send_telegram_message

TRACKED_FILE = "tracked_tokens.json"

def human_format(n):
    return f"${n/1e6:.1f}M" if n >= 1e6 else f"${n/1e3:.0f}k" if n >= 1e3 else f"${n}"

def get_token_profiles():
    r = requests.get("https://api.dexscreener.com/token-profiles/latest/v1")
    return r.json() if r.status_code == 200 else []

def get_token_stats(chain, address):
    r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/{chain}/{address}")
    return r.json() if r.status_code == 200 else []

def is_gem(pair):
    try:
        fdv = pair.get("fdv", 0)
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        volume = pair.get("volume", {}).get("h24", 0)
        created = pair.get("pairCreatedAt", 0)
        recent = datetime.utcnow() - datetime.utcfromtimestamp(created / 1000) <= timedelta(hours=48)
        return recent and 5_000 < volume < 2_000_000 and 20_000 < liquidity < 300_000 and 0 < fdv < 2_000_000
    except:
        return False

def save_token(token_data):
    if not os.path.exists(TRACKED_FILE):
        tracked = []
    else:
        with open(TRACKED_FILE) as f:
            tracked = json.load(f)

    existing = {t["tokenAddress"] for t in tracked}
    if token_data["tokenAddress"] not in existing:
        tracked.append(token_data)
        with open(TRACKED_FILE, "w") as f:
            json.dump(tracked, f, indent=2)

        # send to Telegram
        msg = f"""📡 *New Signal*
🪙 *Name:* {token_data['name'][:50]}
💰 *Entry:* ${token_data['entry_price']:.10f}
🔗 [View Chart]({token_data['url']})
📬 *Address:* `{token_data['tokenAddress']}`
"""
        send_telegram_message(msg)

def discover_new_signals(chain="solana"):
    profiles = get_token_profiles()
    filtered = [t for t in profiles if t["chainId"] == chain]
    for t in filtered:
        stats = get_token_stats(t["chainId"], t["tokenAddress"])
        if not stats:
            continue
        for pair in stats:
            if is_gem(pair):
                name = (
                    t.get("description")
                    or t.get("tokenName")
                    or pair.get("baseToken", {}).get("name")
                    or t["tokenAddress"]
                )
                token_data = {
                    "tokenAddress": t["tokenAddress"],
                    "name": name,
                    "entry_price": float(pair["priceUsd"]),
                    "entry_time": int(datetime.utcnow().timestamp()),
                    "url": pair["url"],
                    "chain": t["chainId"]
                }
                save_token(token_data)
                print(f"[{datetime.utcnow()}] ✅ New signal saved: {token_data['name']}")

if __name__ == "__main__":
    print("🔄 Running continuous discovery loop every 5 minutes...\n")
    while True:
        try:
            discover_new_signals("solana")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        time.sleep(300)
