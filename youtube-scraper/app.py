from flask import Flask, render_template, request, jsonify, redirect, url_for
from youtube_search_scraper import search_videos
from video_scraper import scrape_video_info
from channel_scraper import scrape_channel_info
import pandas as pd
import os, threading, time

app = Flask(__name__)
scrape_status = {"status": "idle", "progress": 0, "total": 0, "type": "video"}

@app.route('/home')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video', methods=['GET', 'POST'])
def video_scrape():
    if request.method == 'POST':
        mode = request.form.get('mode')
        input_data = request.form.get('input_data').strip()
        limit = int(request.form.get('limit') or 5)

        if not input_data:
            return render_template("video_scrape.html", error="Input cannot be empty.")

        urls = []
        if mode == 'search':
            urls = search_videos(input_data, limit)
        elif mode == 'url':
            urls = [u.strip() for u in input_data.split(',') if u.strip() and u.startswith("http")]

        if not urls:
            return render_template("video_scrape.html", error="No valid video URLs found.")

        def video_scrape_thread(urls):
            scrape_status.update({"status": "scraping", "progress": 0, "total": len(urls), "type": "video"})
            for idx, url in enumerate(urls):
                scrape_video_info(url)
                scrape_status["progress"] = idx + 1
                time.sleep(1)
            scrape_status["status"] = "done"

        threading.Thread(target=video_scrape_thread, args=(urls,)).start()
        return redirect(url_for('progress_page'))

    return render_template('video_scrape.html')

@app.route('/channel', methods=['GET', 'POST'])
def channel_scrape():
    if request.method == 'POST':
        raw_input = request.form.get('channel_urls').strip()
        urls = [u.strip() for u in raw_input.split(',') if u.strip() and u.startswith("http")]

        if not urls:
            return render_template("channel_scrape.html", error="Only valid channel or video URLs are allowed.")

        def channel_scrape_thread(urls):
            scrape_status.update({"status": "scraping", "progress": 0, "total": len(urls), "type": "channel"})
            for idx, url in enumerate(urls):
                scrape_channel_info(url)
                scrape_status["progress"] = idx + 1
                time.sleep(1)
            scrape_status["status"] = "done"

        threading.Thread(target=channel_scrape_thread, args=(urls,)).start()
        return redirect(url_for('progress_page'))

    return render_template('channel_scrape.html')

@app.route('/progress')
def progress_page():
    return render_template("progress.html")

@app.route('/get_progress')
def get_progress():
    return jsonify(scrape_status)

@app.route('/results/<result_type>')
def results(result_type):
    file_map = {
        'video': 'output/video_data.csv',
        'channel': 'output/channel_data.csv'
    }

    file_path = file_map.get(result_type)
    if not os.path.exists(file_path):
        return f"No data found for {result_type}."

    df = pd.read_csv(file_path)
    return render_template('results.html', data=df.to_dict(orient='records'), headers=df.columns)

if __name__ == '__main__':
    app.run(debug=True)
