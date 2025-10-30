
# Yelp Scraper — Lead Generation Automation

[![Demo Video](https://img.youtube.com/vi/O8ur10GAEv4/0.jpg)](https://www.youtube.com/watch?v=O8ur10GAEv4)

A Python + Playwright web scraping tool to automatically extract business leads from Yelp. This script collects verified business details such as name, phone, website, address, rating, and more. It can be customized to scrape any type of business, including restaurants, gyms, coffee shops, salons, and local services.

## 📹 Demo

Watch the demo video here: [Yelp Lead Generation Automation Demo](https://www.youtube.com/watch?v=O8ur10GAEv4)

In this demo, a few sample businesses were scraped for demonstration purposes. In practice, this script has been used to collect **1200+ verified leads** for small coffee shops in Los Angeles and Buffalo.

## ⚙️ Key Features

- Scrapes verified business listings from Yelp
- Extracts details like phone, website, address, rating, and reviews
- Detects independent small businesses (1–10 employees)
- Exports results directly into Excel
- Human-like safe browsing to avoid CAPTCHA blocks
- Configurable areas, cities, and number of pages to scrape

## 💼 Use Cases

- Lead generation for local businesses  
- Market research & B2B targeting  
- Data extraction for analytics  
- Automating manual data collection  

## 🛠️ Requirements

- Python 3.9+
- Playwright (`pip install playwright`)
- Pandas (`pip install pandas`)
- Requests (`pip install requests`)
- BeautifulSoup4 (`pip install beautifulsoup4`)

> Make sure to install Playwright browsers before running:
> playwright install

## ⚡ How to Run

1. Clone this repository:

git clone https://github.com/yourusername/yelp-scraper.git
cd yelp-scraper
Update configuration paths in the script:

BASE_FOLDER = r"E:\folder"
PROFILE_PATH = r"E:\folder\chrome_yelp_temp"

Run the scraper:

python yelp_scraper.py

The script first collects candidate Yelp links.
Then it visits each business page, verifies details, and exports results to Excel.
Failed entries are saved separately for review.

Output

final_verified_coffee_shops.xlsx → Verified business leads with details and flags for manual checks

collected_links_full.csv → All candidate Yelp links collected

failed_links_full.xlsx → Failed pages during verification

💬 Need Custom Scraping?

If you want a tailored solution for Yelp or any other website, feel free to contact me for automation and data collection projects.
 #YelpScraper #PythonAutomation #LeadGeneration #Playwright #WebScraping #BusinessLeads #DataExtraction #YelpData #SubhanAli #FreelanceDeveloper #LocalLeads #PythonProject #AutomationDemo
