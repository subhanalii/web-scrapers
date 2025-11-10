from flask import Flask, render_template, request
from scraper.scraper import get_market_data, get_tagged_new_listings
from scraper.utils import format_volume, format_market_cap, save_to_csv, save_to_sqlite
from flask import send_file
import os

app = Flask(__name__)
app.jinja_env.filters['format_volume'] = format_volume
app.jinja_env.filters['format_market_cap'] = format_market_cap

@app.route("/")
def dashboard():
    quote = request.args.get("quote", "USDT").upper()
    sort_by = request.args.get("sort", "marketCap")
    order = request.args.get("order", "desc")
    page = int(request.args.get("page", 1))
    per_page = 20

    all_coins = get_market_data(quote)
    reverse = order == "desc"

    if sort_by == "base":
        all_coins = sorted(all_coins, key=lambda x: x.get("base", ""), reverse=reverse)
    else:
        all_coins = sorted(all_coins, key=lambda x: float(x.get(sort_by, 0) or 0), reverse=reverse)

    total_pages = (len(all_coins) + per_page - 1) // per_page
    visible_coins = all_coins[(page - 1) * per_page : page * per_page]

    visible_symbols = [coin["symbol"] for coin in visible_coins]
    coins = get_market_data(quote, visible_symbols)

    top_gainers = sorted(all_coins, key=lambda x: float(x["priceChangePercent"]), reverse=True)[:3]
    top_volume = sorted(all_coins, key=lambda x: float(x["quoteVolume"]), reverse=True)[:3]
    hot_coins = sorted(all_coins, key=lambda x: float(x.get("marketCap", 0)), reverse=True)[:3]
    new_listings = get_tagged_new_listings()[:3]

    save_to_csv(all_coins)
    save_to_sqlite(all_coins)

    return render_template("dashboard.html",
        coins=coins,
        top_gainers=top_gainers,
        top_volume=top_volume,
        hot_coins=hot_coins,
        new_listings=new_listings,
        quote=quote,
        sort_by=sort_by,
        order=order,
        page=page,
        total_pages=total_pages
    )

@app.route("/more/<category>")
def view_more(category):
    quote = request.args.get("quote", "USDT").upper()
    page = int(request.args.get("page", 1))
    per_page = 40

    if category == "new":
        data = get_tagged_new_listings()
        title = "New Listings"
    else:
        coins = get_market_data(quote)
        if category == "gainers":
            data = sorted(coins, key=lambda x: float(x["priceChangePercent"]), reverse=True)
            title = "Top Gainers"
        elif category == "volume":
            data = sorted(coins, key=lambda x: float(x["quoteVolume"]), reverse=True)
            title = "Top Volume"
        elif category == "hot":
            data = sorted(coins, key=lambda x: float(x.get("marketCap", 0)), reverse=True)
            title = "Hot Coins"
        else:
            return "Invalid category", 404

    total_pages = (len(data) + per_page - 1) // per_page
    paginated_data = data[(page - 1) * per_page : page * per_page]
    return render_template("more.html", coins=paginated_data, title=title, quote=quote, page=page, total_pages=total_pages)

@app.route("/download/csv")
def download_csv():
    path = "exports/market_scraper.csv"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "CSV file not found", 404

@app.route("/download/sqlite")
def download_sqlite():
    path = "db/market.db"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "SQLite DB not found", 404

if __name__ == "__main__":
    app.run(debug=True)
