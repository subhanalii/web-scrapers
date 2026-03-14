# Amazon  Product Scraper 🕷️

A high-performance Python scraper built with **Playwright** to extract deep product data from Amazon.in. It automates browser interactions to capture everything from pricing and ratings to A+ content and sentiment analysis.

## 🚀 Key Features
* **Batch Processing:** Reads ASINs/Product codes directly from an Excel file (`lists.xlsx`).
* **Smart Dynamic Scroll:** Automatically scrolls to the bottom of the page to ensure all lazy-loaded content (like images and reviews) is captured.
* **Sentiment Analysis:** Parses the review histogram to extract the percentage of 1-5 star ratings.
* **Media Extraction:** Detects and captures both high-resolution image URLs and product video sources.
* **Robust Error Handling:** Uses a "Safe Text" function to prevent the script from crashing if a specific element (like a badge or seller info) is missing.

## 🛠️ Setup Instructions

1. **Install Dependencies:**
   pip install pandas openpyxl playwright

Setup Playwright Browsers:

playwright install chromium
Prepare your Input:
Create an Excel file named lists.xlsx with your Amazon product codes in the first column.

Data Extracted
The script exports an amazon_output.xlsx containing:

Product Basics: Title, Price, Rating, and Review Count.

Logistics: Expected Delivery Date and Seller Information.

Marketing: A+ Content status and Promotional Badges.

Media: Full lists of Image and Video URLs.

Analytics: 1-5 Star Sentiment percentages.

⚙️ How it Works
The script launches a Chromium instance with specific arguments to bypass basic automation detection (--disable-blink-features=AutomationControlled). It iterates through each product code, performs a dynamic scroll, and uses Regex to clean up raw text into usable data points.

Developed for research and data analysis purposes.

