from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException
)
import time
from urllib.parse import unquote 

# =========================================================================
# !!! CRITICAL: ENSURE THIS PATH POINTS TO YOUR CHROME.EXE !!!
CHROME_BINARY_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# =========================================================================

# Define a reliable wait time (in seconds)
WAIT_TIME = 20 

def _init_driver():
    """Initializes the Chrome WebDriver with necessary options."""
    options = Options()
    
    options.binary_location = CHROME_BINARY_PATH 
    
    # Run headless for better performance
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3") 
    options.add_argument("--disable-gpu") 
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    
    try:
        # Use a Service object (managed by Selenium 4+)
        driver = webdriver.Chrome(options=options) 
        return driver
    except Exception as e:
        print(f"FATAL: Error setting up WebDriver. Check CHROME_BINARY_PATH. Error: {e}")
        return None

def _scrape_detail_page(driver, wait):
    """
    Scrapes the address, phone, and website from the detail view page.
    Assumes the driver is already on the business's unique URL.
    """
    detail_data = {
        "full_address": "N/A",
        "phone": "N/A",
        "website": "N/A"
    }
    
    # Target elements that contain the key business details (address, phone, web)
    # These typically are buttons/links with data-item-id or specific aria-labels.
    DETAIL_LOCATOR = (By.XPATH, '//button[@data-item-id or @aria-label="Address" or @aria-label="Phone number" or @aria-label="Website"]')
    
    try:
        # Wait for at least one detail element to load
        wait.until(EC.presence_of_element_located(DETAIL_LOCATOR))
        
        detail_elements = driver.find_elements(*DETAIL_LOCATOR)
        
        for el in detail_elements:
            try:
                item_id = el.get_attribute('data-item-id')
                aria_label = el.get_attribute('aria-label')
                detail_text = el.text.strip()
                
                if not detail_text:
                    try:
                        # Fallback for text that might be in a child element
                        detail_text = el.find_element(By.XPATH, './/div[contains(@class, "fontBodyMedium")]').text.strip()
                    except:
                        pass
                
                
                if item_id and 'address' in item_id:
                    detail_data['full_address'] = detail_text
                elif item_id and 'phone' in item_id:
                    detail_data['phone'] = detail_text
                
                # Handling Website Link
                elif item_id and ('web' in item_id or 'website' in item_id):
                    href = el.get_attribute('href')
                    if href:
                        if 'url=' in href:
                            # Extract the clean URL and unquote URL encoding
                            href = href.split('url=')[1].split('&')[0]
                            detail_data['website'] = unquote(href).strip()
                        else:
                            detail_data['website'] = href.strip()
                    else:
                        detail_data['website'] = detail_text # Fallback to displayed text

                # Catch fallback labels
                elif aria_label and 'address' in aria_label:
                    detail_data['full_address'] = detail_text
                elif aria_label and 'phone' in aria_label:
                    detail_data['phone'] = detail_text

            except Exception:
                continue 
        
    except TimeoutException:
        print("Warning: Timed out waiting for detail elements on page.")
    except Exception as e:
        print(f"Error in detail scraping: {e}")
        
    return detail_data

def scrape_google_maps(query="restaurants near me", max_results=10, max_pages=1):
    driver = _init_driver()
    if not driver:
        return []

    print(f"Starting list scrape for: '{query}' (Max Results: {max_results})")
    
    # Start on the search URL
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    driver.get(search_url) 

    wait = WebDriverWait(driver, WAIT_TIME)
    
    # Locators
    RESULTS_PANEL_LOCATOR = (By.XPATH, '//*[@role="feed" or @aria-label="Results for {query}"]'.format(query=query))
    LISTING_LOCATOR = (By.XPATH, '//a[contains(@href, "/place/") and @aria-label]') 

    try:
        scroll_element = wait.until(EC.presence_of_element_located(RESULTS_PANEL_LOCATOR))
    except Exception:
        print("Error: Could not find the main results panel. Scrape aborted.")
        driver.quit()
        return []

    # --- 1. Scrolling and Stable URL Acquisition ---
    business_keys = {} 
    
    print("Beginning scroll to load results and acquire stable URLs...")
    for _ in range(max_pages):
        last_count = -1
        while True:
            # Scroll to load new results
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_element)
            time.sleep(3) 
            
            try:
                listings = driver.find_elements(*LISTING_LOCATOR)
            except WebDriverException:
                listings = []
            
            # Acquire stable keys (Name, URL, and list Address) during scroll
            for listing in listings:
                try:
                    name = listing.get_attribute('aria-label').strip()
                    url = listing.get_attribute('href')
                    
                    if name and url and url not in business_keys:
                        # Capture list address as a fallback
                        list_address = "Address not found in list view."
                        try:
                            address_el = listing.find_element(By.XPATH, './ancestor::div[@role="article"]//div[@class="fontBodyMedium"]')
                            list_address = address_el.text.strip().split('\n')[0]
                        except:
                            pass

                        business_keys[url] = {"name": name, "url": url, "list_address": list_address}
                        
                except Exception:
                    continue # Skip stale/broken elements
            
            current_count = len(business_keys) 
            
            if current_count == last_count or current_count >= max_results:
                print(f"End of list reached or scroll limit hit ({current_count} found).")
                break
            
            last_count = current_count
        
        if len(business_keys) >= max_results:
            break

    stable_list = list(business_keys.values())[:max_results]
    print(f"Starting **DIRECT** detail extraction for {len(stable_list)} listings...")

    # --- 2. Data Extraction Loop (Directly Navigate to URL) ---
    final_data = []
    
    for i, item_key in enumerate(stable_list):
        name = item_key['name']
        target_url = item_key['url']
        list_address = item_key['list_address'] 
        
        try:
            # CRITICAL FIX: Direct URL Navigation bypasses click/back button problems
            print(f"[{i+1}/{len(stable_list)}] Navigating to: {name}")
            driver.get(target_url)
            
            # Wait for the detail page to fully render
            time.sleep(5) 
            
            detail_data = _scrape_detail_page(driver, wait)
            
            # --- Compile Data ---
            # Prioritize detail address if available
            final_address = detail_data['full_address'] if (detail_data['full_address'] != "N/A" and len(detail_data['full_address']) > len(list_address)) else list_address
            
            final_data.append({
                "name": name,
                "address": final_address,
                "phone": detail_data['phone'],
                "website": detail_data['website']
            })
            
            print(f"  > Scraped: {name} | Phone: {detail_data['phone']} | Web: {detail_data['website']}")
                            
        except Exception as e:
            print(f"[{i+1}/{len(stable_list)}] Major error during processing item {name}: {e}. Skipping item.")
            
            # Append basic data if detail scrape failed
            final_data.append({
                "name": name,
                "address": list_address,
                "phone": "Detail Scrape Failed",
                "website": "Detail Scrape Failed"
            })
            continue
    
    driver.quit()
    return final_data 

if __name__ == "__main__":
    # Test execution
    results = scrape_google_maps(query="restaurants near me", max_results=5) 
    
    if results:
        print("\n--- FINAL RESULTS ---")
        for item in results:
            print(f"Name: {item['name']}")
            print(f"Address: {item['address']}")
            print(f"Phone: {item['phone']}")
            print(f"Website: {item['website']}")
            print("---")
    else:
        print("\nTEST FAILED: No results returned or scraper failed.")