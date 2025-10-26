# dexscreener-signal-tracker

# 🚀 Dexscreener Signal Tracker

This Python-based tool tracks new Solana-based tokens using the **Dexscreener API**, filters potential gems based on key metrics, and displays everything in a **live auto-refreshing Flask dashboard**.

> ✅ **Telegram integration logic is already implemented**, but currently disabled due to restrictions in my country (Telegram is banned). You can enable it by configuring the `notifier.py`.

---

## 🌟 Features

- ✅ Real-time detection of new Solana-based tokens
- ✅ Filtering criteria:
  - Age < 48 hours
  - Volume: 5K – 2M USD
  - Liquidity: 20K – 300K USD
  - FDV: < 2M USD
- ✅ Tracks price growth milestones (e.g., 2x, 3x, 5x)
- ✅ Flask dashboard with auto-refresh (60 seconds)
- ✅ Responsive UI with Bootstrap + Tailwind CSS
- 🟡 **Telegram alerts ready (optional)**

---

## 🛠 Tech Stack

- Python (requests, json)
- Flask
- Dexscreener API
- HTML, Bootstrap, Tailwind CSS

---

## 🔧 Setup

```bash
git clone https://github.com/subhanalii/dexscreener-signal-tracker.git
cd dexscreener-signal-tracker
pip install -r requirements.txt


--- HOW TO RUN----
🚀 Usage
1. Run the signal tracker
python signal_tracker.py

2. Run the price watcher
python price_watcher.py

3. Start the Flask dashboard
python app.py
Open your browser at:
📍 http://localhost:5000/

📁 Project Structure

.
├── app.py                # Flask dashboard
├── dashboard.html        # UI template
├── signal_tracker.py     # New token discovery
├── price_watcher.py      # Monitors price gains
├── notifier.py           # (Telegram logic included, but currently disabled)
├── tracked_tokens.json   # JSON file storing tracked tokens
🔔 Telegram Alerts (Optional)
The code includes prewritten logic for Telegram notifications using notifier.py.

Just insert your bot token and chat ID in notifier.py to enable it.

🔒 Skipped by default due to Telegram restrictions in my country.

📜 License
MIT License – Free to use, modify, or build upon.

Let me know if you want me to:
- Add a clean version of `notifier.py` with the logic ready (but commented out)
- Help with a `requirements.txt` file
- Generate a sample preview image for GitHub

Just say the word.
