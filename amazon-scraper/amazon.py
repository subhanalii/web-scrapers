import pandas as pd
import time
import re
from playwright.sync_api import sync_playwright

# ---------------- READ EXCEL ----------------
df = pd.read_excel("lists.xlsx")
product_codes = df.iloc[:2, 0].dropna().astype(str)
results = []

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080"
        ]
    )
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    for idx, code in enumerate(product_codes, start=1):
        url = f"https://www.amazon.in/dp/{code}"
        print(f"\n[{idx}] Scraping product: {code}")

        try:
            page.goto(url, timeout=120000, wait_until="domcontentloaded")
            print("   Page loaded")
        except:
            print("   Page load failed, skipping product")
            results.append({"Product Code": code, "URL": url})
            continue

        # ---------------- SMART SCROLL ----------------
        print("  Scrolling page dynamically...")
        scroll_pause = 1.0
        max_attempts = 30
        prev_height = 0

        for attempt in range(max_attempts):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            curr_height = page.evaluate("document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height
        print("   Scrolling completed")

        # ---------------- SAFE TEXT FUNCTION ----------------
        def safe_text(selector, label):
            try:
                text = page.locator(selector).first.inner_text().strip()
                print(f"   {label}: {text[:60]}...")
                return text
            except:
                print(f"   {label}: Not Found")
                return "Not Found"

        # ---------------- EXTRACTION ----------------
        title = safe_text("#productTitle", "Title")

        # Price
        try:
            symbol = page.locator("span.a-price-symbol").first.inner_text()
            whole = page.locator("span.a-price-whole").first.inner_text()
            price = f"{symbol}{whole}"
            print(f"   Price: {price}")
        except:
            price = "Not Found"
            print("  Price: Not Found")

        rating = safe_text("span.a-icon-alt", "Rating")
        raw_reviews = safe_text("#acrCustomerReviewText", "Review Count")
        reviews = re.sub(r"[^\d]", "", raw_reviews) if raw_reviews != "Not Found" else "Not Found"

        # Delivery date
        try:
            raw_delivery = page.locator("#deliveryBlockMessage").first.inner_text()
            match = re.search(r"\b\d{1,2}\s+[A-Za-z]+", raw_delivery)
            delivery_date = match.group() if match else "Not Found"
            print(f"  Delivery Date: {delivery_date}")
        except:
            delivery_date = "Not Found"
            print("  Delivery Date: Not Found")

        # Badge
        try:
            badge = page.locator(".dealBadgeTextColor span").first.inner_text().strip()
            print(f"  Badge: {badge}")
        except:
            badge = "Not Found"
            print("   Badge: Not Found")

        # Seller info
        seller_raw = safe_text("#merchant-info", "Seller Info")
        seller_info = seller_raw.split("|")[0].strip() if seller_raw != "Not Found" else "Not Found"

        # A+ Content
        try:
            a_plus_raw = page.locator("#aplus").first.inner_text().strip()
            a_plus_content = "Yes" if a_plus_raw else "No"
        except:
            a_plus_content = "No"

        # Images
        try:
            imgs = page.locator("img[data-a-dynamic-image]").all()
            image_urls = []
            for img in imgs:
                src_json = img.get_attribute("data-a-dynamic-image")
                matches = re.findall(r'"(https:[^"]+)"', src_json)
                image_urls.extend(matches)
            image_urls = list(set(image_urls))
            print(f"   Images found: {len(image_urls)}")
        except:
            image_urls = []
            print("   Images: Not Found")

        # Videos
        try:
            vids = page.locator("video source").all()
            video_urls = [v.get_attribute("src") for v in vids if v.get_attribute("src")]
            print(f"  Videos found: {len(video_urls)}")
        except:
            video_urls = []
            print("   Videos: Not Found")

        # Review Sentiment %
        sentiment = {"5 star": "0%", "4 star": "0%", "3 star": "0%", "2 star": "0%", "1 star": "0%"}
        try:
            lis = page.locator("ul#histogramTable li span.a-list-item").all()
            for li in lis:
                text = li.inner_text().strip()
                star_match = re.search(r"(\d) star", text)
                percent_match = re.search(r"(\d+)%", text)
                if star_match and percent_match:
                    sentiment[f"{star_match.group(1)} star"] = percent_match.group(1) + "%"
            print(f"   Review Sentiment: {sentiment}")
        except:
            print("   Review Sentiment: Not Found")

        # ---------------- STORE RESULT ----------------
        results.append({
            "Product Code": code,
            "URL": url,
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Review Count": reviews,
            "Review Sentiment %": "; ".join([f"{k}: {v}" for k, v in sentiment.items()]),
            "Expected Delivery": delivery_date,
            "Badge": badge,
            "Seller Info": seller_info,
            "A+ Content": a_plus_content,
            "Images": ", ".join(image_urls) if image_urls else "Not Found",
            "Videos": ", ".join(video_urls) if video_urls else "Not Found"
        })

        print(f"[{idx}] Product completed \n")
        time.sleep(2)  # short wait between products

    print("All products scraped. Closing browser...")
    browser.close()

# ---------------- SAVE ----------------
df_out = pd.DataFrame(results)
df_out.to_excel("amazon_output.xlsx", index=False)
print(" Data saved to amazon_output.xlsx")
