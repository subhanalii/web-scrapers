import os
import csv
import time
import re
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def format_duration(iso_duration):
    match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if match:
        minutes = match.group(1) or "0"
        seconds = match.group(2) or "0"
        if minutes != "0":
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    return iso_duration

def is_duplicate(url, path):
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        return url in f.read()


def scrape_video_info(url):
    print(f"\n🎬 Scraping video: {url}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    def safe_text(by, value, label):
        try:
            print(f" Extracting {label}...")
            element = wait.until(EC.presence_of_element_located((by, value)))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return element.text.strip()
        except:
            print(f" Failed to get {label}")
            return ""

    # Force scrolling to load lazy-loaded content
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 1200);")
    time.sleep(2)

    try:
        print(" Extracting Title...")
        title = driver.find_element(By.CSS_SELECTOR, 'h1.title yt-formatted-string').text.strip()
        if not title:
            title = driver.title.strip()
        print(f" Title: {title}")
    except:
        print(" Failed to get Title")
        title = ""

    views = safe_text(By.XPATH, '//yt-formatted-string[@id="info"]/span[1]', "Views")

    try:
        print(" Extracting Upload Date...")
        info_text = driver.find_element(By.CSS_SELECTOR, 'yt-formatted-string#info').text
        lines = info_text.splitlines()
        upload_date = ""
        for part in lines:
            if "ago" in part or "202" in part:
                upload_date = part.strip()
                break
        print(f"Upload Date: {upload_date}")
    except:
        print(" Failed to get Upload Date")
        upload_date = ""

    likes = safe_text(By.CSS_SELECTOR, 'button[aria-label*="like this video"] .yt-spec-button-shape-next__button-text-content', "Likes")
    comments = safe_text(By.CSS_SELECTOR, 'ytd-comments-header-renderer yt-formatted-string.count-text span:nth-child(1)', "Comments")

    try:
        print(" Extracting description...")
        description = driver.find_element(By.CSS_SELECTOR, '#description-inline-expander span').text.strip()
        description = unicodedata.normalize("NFKD", description)
        print(" Description extracted.")
    except:
        print(" Failed to get Description")
        description = ""

    try:
        raw_duration = driver.find_element(By.XPATH, '//meta[@itemprop="duration"]').get_attribute("content")
        duration = format_duration(raw_duration)
        print(f" Duration: {duration}")
    except:
        duration = ""

    driver.quit()

    os.makedirs("output", exist_ok=True)
    output_file = "output/video_data.csv"
    write_header = not os.path.exists(output_file)

    if is_duplicate(url, output_file):
        print(" Skipping duplicate video")
        return

    with open(output_file, "a", newline="", encoding="utf-8", errors='replace') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["URL", "Title", "Views", "Likes", "Comments", "Upload Date", "Duration", "Description"])
        writer.writerow([url, title, views, likes, comments, upload_date, duration, description])

    print(f" Done: {title[:60]}...")
