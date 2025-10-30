
import os
import time
import random
import re
from pathlib import Path
import requests
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------- CONFIG ----------------
BASE_FOLDER = r"E:\folder"
PROFILE_PATH = r"E:\folder\chrome_yelp_temp"
OUTPUT_FILE = os.path.join(BASE_FOLDER, "final_verified_coffee_shops.xlsx")
TEMP_LINKS_FILE = os.path.join(BASE_FOLDER, "collected_links_full.csv")
FAILED_FILE = os.path.join(BASE_FOLDER, "failed_links_full.xlsx")

# Safe-mode timing
MIN_WAIT = 3.5
MAX_WAIT = 7.5
SCROLL_PAUSE_MIN = 0.6
SCROLL_PAUSE_MAX = 1.2

# Pagination / coverage
PAGES_PER_AREA = 10  # ~100 results per area (adjust if desired)

# Neighborhoods
LA_AREAS = [
    "Los Angeles, CA", "Downtown Los Angeles, CA", "Hollywood, Los Angeles, CA",
    "Koreatown, Los Angeles, CA", "Silver Lake, Los Angeles, CA", "Echo Park, Los Angeles, CA",
    "Santa Monica, CA", "Venice, Los Angeles, CA", "West Hollywood, CA", "Culver City, CA"
]
BUFFALO_AREAS = [
    "Buffalo, NY", "Allentown, Buffalo, NY", "Elmwood Village, Buffalo, NY",
    "North Buffalo, Buffalo, NY", "South Buffalo, Buffalo, NY", "Downtown Buffalo, NY",
    "Williamsville, NY", "University at Buffalo, Buffalo, NY"
]

CITIES = [
    ("Los Angeles", LA_AREAS),
    ("Buffalo", BUFFALO_AREAS)
]

FRANCHISE_BLACKLIST = [
    "starbucks", "dunkin", "peet", "coffee bean", "tim hortons", "caribou",
    "philz", "gloria jean", "second cup", "pret a manger", "mcdonald", "panera", "7-eleven"
]

OUTPUT_COLUMNS = [
    "Business Name", "City", "Address", "Phone", "Website", "Rating",
    "Yelp Link", "Employees (est.)", "Employee_flag", "Verification Date",
    "Verification Sources", "Notes"
]

# ---------------- Helpers ----------------
def human_wait(a=MIN_WAIT, b=MAX_WAIT):
    time.sleep(random.uniform(a, b))

def slow_scroll(page, pixels=3000):
    for _ in range(0, pixels, 300):
        try:
            page.mouse.wheel(0, 300)
        except Exception:
            pass
        time.sleep(random.uniform(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX))

def is_chain(text):
    if not text:
        return False
    lower = text.lower()
    return any(b in lower for b in FRANCHISE_BLACKLIST)

def normalize_link(href):
    if not href:
        return None
    href = href.split("?")[0]
    if href.startswith("/biz/"):
        return "https://www.yelp.com" + href
    if href.startswith("http"):
        return href
    return None

def parse_review_count_from_yelp_text(txt):
    if not txt:
        return None
    m = re.search(r"([\d,]+)\s*reviews?", txt)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except:
            return None
    nums = re.findall(r"[\d,]+", txt)
    if nums:
        try:
            return int(nums[0].replace(",", ""))
        except:
            return None
    return None

def fetch_website_head(url, timeout=8):
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None

def website_indicators(html_text):
    indicators = {"careers": False, "team": False, "about": False, "locations": False}
    if not html_text:
        return indicators
    lower = html_text.lower()
    indicators["careers"] = "careers" in lower or "join our team" in lower or "work with us" in lower
    indicators["team"] = "our team" in lower or "meet the team" in lower or "staff" in lower
    indicators["about"] = "about us" in lower or "our story" in lower
    indicators["locations"] = "locations" in lower or "find a location" in lower
    return indicators

# ---------------- Collect candidate links (only links; names NOT from anchors) ----------------
def collect_search_results(playwright):
    collected = []
    with playwright.chromium.launch_persistent_context(
        PROFILE_PATH, channel="chrome", headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    ) as browser:
        page = browser.new_page()
        page.set_default_timeout(60000)

        for city_tag, areas in CITIES:
            print(f"\n== Collecting for {city_tag} ==")
            for area in areas:
                for page_num in range(PAGES_PER_AREA):
                    start = page_num * 10
                    url = f"https://www.yelp.com/search?find_desc=Coffee+shops&find_loc={area.replace(' ', '+')}&start={start}"
                    print(f"→ {area} page {page_num+1} → {url}")
                    try:
                        page.goto(url, timeout=60000)
                    except PlaywrightTimeoutError:
                        print("  ⚠️ Timeout loading search page; skipping page.")
                        continue
                    human_wait()
                    slow_scroll(page, pixels=2800)
                    human_wait(0.8, 1.6)

                    anchors = page.locator('a[href^="/biz/"]')
                    seen = set()
                    for i in range(anchors.count()):
                        try:
                            href = anchors.nth(i).get_attribute("href")
                            link = normalize_link(href)
                            if not link:
                                continue
                            if link in seen:
                                continue
                            seen.add(link)
                            # we do NOT trust anchor inner_text (can be 'Order' or 'Menu')
                            # filter out obvious chain by href or short anchor text nearby
                            collected.append({"Yelp Link": link, "City": city_tag, "AreaSearched": area})
                        except Exception:
                            continue
                    human_wait(1.2, 2.6)
        browser.close()
    # dedupe
    unique = {r["Yelp Link"]: r for r in collected}
    return list(unique.values())

# ---------------- Verify by visiting business page and extracting proper name + fields ----------------
def verify_businesses(playwright, business_list):
    verified = []
    failed = []

    with playwright.chromium.launch_persistent_context(
        PROFILE_PATH, channel="chrome", headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    ) as browser:
        page = browser.new_page()
        page.set_default_timeout(60000)

        for idx, biz in enumerate(business_list, start=1):
            link = biz.get("Yelp Link")
            city = biz.get("City")
            area = biz.get("AreaSearched", "")
            print(f"[{idx}/{len(business_list)}] Visiting -> {link}")

            try:
                page.goto(link, timeout=60000)
                human_wait()
                slow_scroll(page, pixels=2500)
                human_wait(0.8, 1.8)

                # BUSINESS NAME: prefer <h1> on the business page
                name = None
                try:
                    h1 = page.locator("h1")
                    if h1.count() > 0:
                        name = h1.first.inner_text().strip()
                except Exception:
                    name = None
                # fallback: document.title trimming "- Yelp"
                if not name:
                    try:
                        dt = page.title()
                        if dt:
                            name = dt.replace(" - Yelp", "").strip()
                    except Exception:
                        name = None

                # rating
                rating = None
                try:
                    r_loc = page.locator('div[role="img"][aria-label*="star rating"]')
                    if r_loc.count() > 0:
                        rating = r_loc.first.get_attribute("aria-label").replace(" star rating", "")
                except Exception:
                    rating = None

                # phone
                phone = None
                try:
                    p_loc = page.locator('p:has-text("(")')
                    if p_loc.count() > 0:
                        phone = p_loc.first.inner_text().strip()
                    else:
                        # sometimes phone in a span
                        sp = page.locator('span:has-text("(")')
                        if sp.count() > 0:
                            phone = sp.first.inner_text().strip()
                except Exception:
                    phone = None

                # website
                website = None
                try:
                    w_loc = page.locator('a[href^="http"]:has-text("Business website")')
                    if w_loc.count() > 0:
                        website = w_loc.first.get_attribute("href")
                    else:
                        a_http = page.locator('a[href^="http"]')
                        for i in range(a_http.count()):
                            h = a_http.nth(i).get_attribute("href")
                            if h and "yelp.com/biz_redir" not in h and h.startswith("http"):
                                website = h
                                break
                except Exception:
                    website = None

                # address
                address = None
                try:
                    addr = page.locator("address")
                    if addr.count() > 0:
                        address = addr.first.inner_text().strip().replace("\n", ", ")
                    else:
                        p_addrs = page.locator('p:has-text(",")')
                        for i in range(p_addrs.count()):
                            t = p_addrs.nth(i).inner_text().strip()
                            if city.split()[0] in t or "CA" in t or "NY" in t:
                                address = t.replace("\n", ", ")
                                break
                except Exception:
                    address = None

                # reviews count (heuristic)
                rev_count = None
                try:
                    rev_loc = page.locator('span:has-text("reviews")')
                    if rev_loc.count() > 0:
                        rev_count = parse_review_count_from_yelp_text(rev_loc.first.inner_text())
                except Exception:
                    rev_count = None

                # website quick scan
                site_html = None
                indicators = {}
                if website:
                    # resolve Yelp redirect if present
                    if "yelp.com/biz_redir" in (website or ""):
                        m = re.search(r"url=(.+)$", website)
                        if m:
                            try:
                                website = requests.utils.unquote(m.group(1).split("&")[0])
                            except Exception:
                                pass
                    site_html = fetch_website_head(website) if website else None
                    indicators = website_indicators(site_html)

                # employee heuristic & flags
                employee_est = "1-10"
                employee_flag = ""
                notes = []
                verification_sources = [link]
                if website:
                    verification_sources.append(website)
                if rev_count:
                    notes.append(f"Yelp reviews: {rev_count}")
                if indicators.get("careers") or indicators.get("locations"):
                    employee_flag = "MANUAL_CHECK_POSSIBLE_>10"
                    notes.append("Website shows careers/locations.")
                if rev_count and rev_count > 800:
                    employee_flag = "MANUAL_CHECK_POSSIBLE_>10"
                    notes.append("High Yelp review count suggests larger business.")

                # final row
                verified.append({
                    "Business Name": name or "",
                    "City": city,
                    "Address": address,
                    "Phone": phone,
                    "Website": website,
                    "Rating": rating,
                    "Yelp Link": link,
                    "Employees (est.)": employee_est,
                    "Employee_flag": employee_flag,
                    "Verification Date": time.strftime("%Y-%m-%d"),
                    "Verification Sources": ";".join([s for s in verification_sources if s]),
                    "Notes": "; ".join(notes)
                })

                print(f"  ✔ {name} | Phone:{phone} | Website:{website} | Flag:{employee_flag}")
                human_wait()

            except Exception as e:
                print(f"  ✖ Error for {link}: {e}")
                failed.append({"Yelp Link": link, "City": city, "Error": str(e)})
                time.sleep(2.0)

        browser.close()
    return verified, failed

# ---------------- MAIN ----------------
def main():
    Path(BASE_FOLDER).mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        print("STEP 1: Collecting candidate Yelp links (expanded areas)...")
        collected = collect_search_results(playwright)
        print(f"Collected {len(collected)} unique candidate links.")
        try:
            pd.DataFrame(collected).to_csv(TEMP_LINKS_FILE, index=False)
            print(f"Saved candidates → {TEMP_LINKS_FILE}")
        except Exception:
            pass

        print("\nSTEP 2: Visiting business pages & verifying details...")
        verified_rows, failed_rows = verify_businesses(playwright, collected)

        if verified_rows:
            df_out = pd.DataFrame(verified_rows, columns=OUTPUT_COLUMNS)
            df_out.to_excel(OUTPUT_FILE, index=False)
            print(f"\n Final verified file saved → {OUTPUT_FILE} ({len(df_out)} rows)")
        else:
            print("\n No verified rows to save.")

        if failed_rows:
            pd.DataFrame(failed_rows).to_excel(FAILED_FILE, index=False)
            print(f" Failed rows saved → {FAILED_FILE} ({len(failed_rows)} rows)")

    print("\nDONE. Review 'Employee_flag' for manual headcount checks.")

if __name__ == "__main__":
    main()
