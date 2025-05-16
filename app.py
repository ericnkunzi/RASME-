
from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

KOBO_TOKEN = os.getenv("KOBO_TOKEN")
FORM_UID = os.getenv("FORM_UID")
API_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{FORM_UID}/data.json"

HEADERS = {
    "Authorization": f"Token {KOBO_TOKEN}"
}

@app.route("/")
def home():
    return "RASME+ API is live. Use /data endpoint to get submissions."

@app.route("/data")
def get_data():
    if not KOBO_TOKEN or not FORM_UID:
        raise Exception("KOBO_TOKEN and FORM_UID must be set in environment variables")

    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        raw_data = response.json()

        cleaned_data = []
        for item in raw_data.get("results", []):
            geo = item.get("_geolocation", [None, None])
            lat = geo[0] if isinstance(geo, list) and len(geo) > 1 else None
            lon = geo[1] if isinstance(geo, list) and len(geo) > 1 else None
            sector = item.get("info_activity/group_description_act/sector_activity", "").strip().title()
            collector = item.get("group_enumerator_info/name_enum", "Unknown")
            submission_date = item.get("_submission_time", None)
            
            cleaned_data.append({
                "latitude": lat,
                "longitude": lon,
                "sector": sector,
                "collector": collector,
                "submission_date": submission_date,
                "score": None  # Optional
            })

        return jsonify(cleaned_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
