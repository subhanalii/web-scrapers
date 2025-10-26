# YouTube Scraper

[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Scrape YouTube video and channel data **without using any API key!**  
This Python-based YouTube Scraper uses Selenium to extract:

✅ Video title, views, likes, comments, duration  
✅ Channel name, handle, subscribers, join date  
✅ Save data to CSV  
✅ Fully interactive CLI (no need to write commands)

---

## 📺 Demo
Watch the scraper in action:  
[YouTube Demo](https://www.youtube.com/watch?v=u4PV3uRqpR0)

---

## 🛠 Features
- Scrape videos from any YouTube channel or search query  
- Export results to CSV for analysis  
- Works for digital marketing, data analytics, and lead generation  
- Interactive CLI makes usage easy without coding

---

## ⚡ Installation

1. Clone the repo:
```bash
git clone https://github.com/subhanalii/youtube-scraper.git
cd youtube-scraper
Install dependencies:

pip install -r requirements.txt


Install ChromeDriver for Selenium:
https://developer.chrome.com/docs/chromedriver/downloads

**Usage**
Run the interactive CLI:

python app.py

**Or run scripts individually:
**
python main.py
python channel_scraper.py --channel "CHANNEL_URL"
python video_scraper.py --video "VIDEO_URL"

Output: CSV files will be saved in output/ folder.


Example (Python)

from video_scraper import scrape_video
from channel_scraper import scrape_channel

# Scrape single video
video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
video_data = scrape_video(video_url)
print("Video Data:", video_data)

# Scrape full channel
channel_url = "https://www.youtube.com/@CHANNEL_NAME"
channel_data = scrape_channel(channel_url)
print("Channel Data:", channel_data)

Who Can Use This

Digital marketers

Data analysts

Lead generators

Python developers

💼 Hire Me

Need a custom-built scraper or Python automation project?
📩 Hire me on Upwork: https://www.upwork.com/freelancers/~01b6c1b6819be875f2?mp_source=share
**
License**

This project is licensed under the MIT License - see the LICENSE file for details.
MIT License

Copyright (c) 2025 Subhan Ali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:



The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
