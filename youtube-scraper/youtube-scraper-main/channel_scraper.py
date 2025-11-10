import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_channel_info(channel_or_video_url):
    print(f"\n Starting channel scrape: {channel_or_video_url}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(channel_or_video_url)
    wait = WebDriverWait(driver, 15)

    if "watch?v=" in channel_or_video_url:
        try:
            print(" Navigating to channel page from video...")
            channel_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-channel-name a')))
            channel_url = channel_element.get_attribute("href")
            driver.get(channel_url + "/about")
            time.sleep(3)
        except:
            print(" Failed to find channel link on video")
            driver.quit()
            return
    else:
        driver.get(channel_or_video_url + "/about")
        time.sleep(3)

    def safe_text(by, value, label):
        try:
            print(f" {label}...")
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element.text.strip()
        except:
            print(f" {label} not found")
            return ""

    try:
        channel_name = driver.find_element(By.CSS_SELECTOR, ".dynamic-text-view-model-wiz__h1 span").text.strip()
        print(f" Channel Name: {channel_name}")
    except:
        channel_name = ""

    try:
        handle = driver.find_element(By.XPATH, '//span[contains(text(),"@")]').text.strip()
        print(f" Handle: {handle}")
    except:
        handle = ""

    try:
        meta = driver.find_elements(By.CSS_SELECTOR, '.yt-content-metadata-view-model-wiz__metadata-row span')
        subscribers = ""
        videos = ""
        for span in meta:
            txt = span.text.lower()
            if "subscriber" in txt:
                subscribers = span.text.strip()
            elif "video" in txt:
                videos = span.text.strip()
        print(f"Subscribers: {subscribers}, 🎞️ Videos: {videos}")
    except:
        subscribers = videos = ""

    try:
        print("Extracting Join Date...")
        join_rows = driver.find_elements(By.CSS_SELECTOR, 'ytd-about-channel-renderer yt-attributed-string span')
        join_date = ""
        for row in join_rows:
            text = row.text.strip()
            if text.startswith("Joined"):
                join_date = text.replace("Joined", "").strip()
                break
        print(f" Join Date: {join_date}")
    except:
        print(" Failed to get Join Date")
        join_date = ""

    current_url = driver.current_url
    driver.quit()

    os.makedirs("output", exist_ok=True)
    output_file = "output/channel_data.csv"
    write_header = not os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8", errors='replace') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Channel Name", "Handle", "Subscribers", "Videos", "Join Date", "URL"])
        writer.writerow([channel_name, handle, subscribers, videos, join_date, current_url])

    print(f" Done scraping channel: {channel_name or 'Unknown'}")
