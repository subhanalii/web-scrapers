import requests, json, time
from datetime import datetime
from notifier import send_telegram_message

TRACKED_FILE = "tracked_tokens.json"
thresholds = [2, 3, 5, 10, 20, 50, 100]

# track past sent gains
sent_gains = {}

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

def watch_tokens():
    tokens = load_tracked_tokens()
    for t in tokens:
        stats = get_token_stats(t["chain"], t["tokenAddress"])
        if not stats:
            continue
        current_price = float(stats[0].get("priceUsd", 0))
        gain = round(current_price / float(t["entry_price"]), 2)

        key = t["tokenAddress"]
        if key not in sent_gains:
            sent_gains[key] = []

        for thresh in thresholds:
            if gain >= thresh and thresh not in sent_gains[key]:
                sent_gains[key].append(thresh)
                msg = f"""🚀 *{t['name'][:50]} Reached {thresh}x*
🪙 *Entry:* ${t['entry_price']:.10f}
📈 *Now:* ${current_price:.10f}
💸 *Gain:* {gain}x
🔗 [Chart]({t['url']})
🔐 *Address:* `{t['tokenAddress']}`
"""
                send_telegram_message(msg)

if __name__ == "__main__":
    print("📡 Price watcher started. Scanning every 5 minutes...\n")
    while True:
        try:
            watch_tokens()
        except Exception as e:
            print(f"⚠️ Error: {e}")
        time.sleep(300)
