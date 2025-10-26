import csv
import sqlite3
from datetime import datetime

def format_volume(value):
    value = float(value)
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    return str(value)

def format_market_cap(value):
    return format_volume(value)

def ms_to_datetime(ms):
    return datetime.utcfromtimestamp(ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

def save_to_csv(data, filename="exports/market_scraper.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def save_to_sqlite(data, db_path="db/market.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS markets")
    c.execute("CREATE TABLE markets (symbol TEXT, base TEXT, lastPrice TEXT, priceChangePercent TEXT, quoteVolume TEXT, marketCap REAL)")
    for coin in data:
        c.execute("INSERT INTO markets VALUES (?, ?, ?, ?, ?, ?)", (
            coin["symbol"], coin["base"], coin.get("lastPrice", ""),
            coin.get("priceChangePercent", ""), coin.get("quoteVolume", ""),
            coin.get("marketCap", 0)
        ))
    conn.commit()
    conn.close()
