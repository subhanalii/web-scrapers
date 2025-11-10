from flask import Flask, render_template, request, jsonify, send_file
from scraper import scrape_google_maps 
import io
import pandas as pd

app = Flask(__name__)


LAST_SCRAPED_DATA = []

@app.route("/", methods=["GET", "POST"])
def index():
    global LAST_SCRAPED_DATA
    
    if request.method == "POST":
        try:
            query = request.form.get("query", "")
            max_results = int(request.form.get("max_results", 10))
            max_pages = int(request.form.get("max_pages", 1)) 

            print(f"Starting scrape for: '{query}' (Max Results: {max_results})")

            scraped_data_list = scrape_google_maps(query, max_results, max_pages)

            LAST_SCRAPED_DATA = scraped_data_list

            if scraped_data_list:
                print(f"Scrape successful. Returning {len(scraped_data_list)} results.")
                return jsonify(scraped_data_list)
            else:
                print("Scrape completed, but returned 0 results.")
                return jsonify([])

        except Exception as e:
            print(f"Flask Error processing POST request: {e}")
            return jsonify({"error": str(e), "message": "Scraper failed or internal server error."}), 500

    # For GET requests, render the HTML template
    return render_template("index.html")

@app.route("/download/<filetype>", methods=["GET"])
def download_data(filetype):
    global LAST_SCRAPED_DATA
    
    if not LAST_SCRAPED_DATA:
        return "No data to download. Please run a scrape first.", 404
        
    df = pd.DataFrame(LAST_SCRAPED_DATA)
    
    if filetype == 'csv':
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(
            io.BytesIO(buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='google_maps_scrape.csv'
        )
    
    elif filetype == 'xlsx':
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='google_maps_scrape.xlsx'
        )
        
    return "Invalid file type.", 400

if __name__ == "__main__":
    app.run(debug=True)