import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Load environment variables for security
KOBO_TOKEN = os.getenv("KOBO_TOKEN")
FORM_UID = os.getenv("FORM_UID")

if not KOBO_TOKEN or not FORM_UID:
    raise Exception("KOBO_TOKEN and FORM_UID must be set in environment variables")

KOBO_API_URL = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"

HEADERS = {
    "Authorization": f"Token {KOBO_TOKEN}"
}

def fetch_kobo_data():
    # Request Kobo submissions JSON
    try:
        response = requests.get(KOBO_API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        # Extract relevant fields per submission
        results = []
        for item in data.get('results', []):
            # Adjust these keys based on your Kobo form field names:
            # Example assumes fields 'sector', 'collector_name', and 'location' with lat/lon
            sector = item.get('sector', 'Others')
            collector = item.get('collector_name', 'Unknown')
            # Location might be a list like [lat, lon] or dict, adapt accordingly
            location = item.get('location', None)
            latitude, longitude = None, None
            if location:
                if isinstance(location, list) and len(location) == 2:
                    latitude, longitude = location
                elif isinstance(location, dict):
                    latitude = location.get('latitude')
                    longitude = location.get('longitude')

            submission_date = item.get('_submission_time', None)

            results.append({
                "sector": sector,
                "collector": collector,
                "latitude": latitude,
                "longitude": longitude,
                "submission_date": submission_date
            })
        return results
    except Exception as e:
        print(f"Error fetching Kobo data: {e}")
        return []

@app.route("/data")
def data():
    submissions = fetch_kobo_data()
    return jsonify(submissions)

@app.route("/")
def index():
    return "RASME+ API is live. Use /data endpoint to get submissions."

if __name__ == "__main__":
    app.run(debug=True)
