from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def search_videos(query, limit=5):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    driver.get(search_url)
    video_links = []
    seen_links = set()

    scroll_pause = 2
    scroll_attempts = 0
    max_attempts = 20  # to avoid infinite loops

    try:
        while len(video_links) < limit and scroll_attempts < max_attempts:
            videos = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
            for video in videos:
                href = video.get_attribute("href")
                if href and "watch" in href and href not in seen_links:
                    video_links.append(href)
                    seen_links.add(href)
                    if len(video_links) >= limit:
                        break

            # Scroll down to load more videos
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(scroll_pause)
            scroll_attempts += 1

    except Exception as e:
        print(f" Error while scrolling or scraping: {e}")
    finally:
        driver.quit()

    return video_links
