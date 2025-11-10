from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import pandas as pd
import time

# === Step 1: Setup Driver ===
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Uncomment to run without opening a browser
driver = webdriver.Chrome(options=options)

# === Step 2: Instagram Login ===
try:
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys("hopec_hainn")
    password_input.send_keys("Nyctophile")
    password_input.send_keys(Keys.ENTER)

    time.sleep(10)  # Let login complete
except Exception as e:
    print("Login failed:", e)
    driver.quit()
    exit()

# === Step 3: Bing Search ===
query = 'site:instagram.com "fitness coach" "email"'
search_url = f"https://www.bing.com/search?q={query}"
driver.get(search_url)
time.sleep(5)

results = set()
page = 1
last_page_num = None

while True:
    print(f"\n Scanning Bing Page {page}...")
    time.sleep(3)

    # Collect Instagram links
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "div.b_tpcn a.tilk")
        for link in links:
            href = link.get_attribute("href")
            if href and "instagram.com" in href and "/p/" not in href and "/reel/" not in href:
                results.add(href.split("?")[0])
    except Exception as e:
        print("Error collecting links:", e)

    # Detect pagination stuck
    try:
        current_page = int(driver.find_element(By.CSS_SELECTOR, "a.sb_pagS").text)
    except:
        current_page = page

    if last_page_num == current_page:
        print(" Pagination stuck. Ending.")
        break
    last_page_num = current_page

    # Try clicking "Next"
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.sb_pagN")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", next_button)
        page += 1
    except (NoSuchElementException, ElementClickInterceptedException):
        print(" No more pages.")
        break

# === Step 4: Scrape Instagram Profiles ===
print(f"\n Found {len(results)} Instagram profile links.")
profile_data = []

for idx, url in enumerate(results, start=1):
    print(f"\n[{idx}] Visiting: {url}")
    try:
        driver.get(url)
        time.sleep(10)

        # Try name
        try:
            name = driver.find_element(By.XPATH, '//header//h2').text
        except NoSuchElementException:
            try:
                name = driver.find_element(By.XPATH, '//h1').text
            except:
                name = ""

        # Try bio
        try:
            bio = driver.find_element(By.XPATH, '//section//div/span').text
        except NoSuchElementException:
            bio = ""

        # Try stats
        try:
            stats = driver.find_elements(By.XPATH, '//ul/li//span')
            posts = stats[0].text if len(stats) > 0 else ""
            followers = stats[1].get_attribute("title") or stats[1].text if len(stats) > 1 else ""
            following = stats[2].text if len(stats) > 2 else ""
        except:
            posts = followers = following = ""

        print(f"  Name: {name}")
        print(f"  Bio: {bio}")
        print(f"  Posts: {posts}")
        print(f"  Followers: {followers}")
        print(f"  Following: {following}")

        profile_data.append({
            "URL": url,
            "Name": name,
            "Bio": bio,
            "Posts": posts,
            "Followers": followers,
            "Following": following
        })

    except Exception as e:
        print(f"  Failed to scrape {url}: {e}")
        continue

# === Step 5: Save to CSV ===
driver.quit()
pd.DataFrame(profile_data).to_csv("instagram_profiles.csv", index=False)
print("\nSaved to instagram_profiles.csv")
