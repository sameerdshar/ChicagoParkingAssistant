from flask import Flask, render_template, request
import requests
from get_Cleaning_Schedule import get_cleaning_schedule, get_cleaning_schedule_from_api
import logging
from get_Zone import get_zone
from datetime import date
from datetime import datetime as dt
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    coords = None
    if request.method == "POST":
        address = request.form["address"]
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {
            "User-Agent": "MyGeocodingApp/1.0 (your.email@example.com)"  # Set a real email if deploying
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data:
            coords = {"lat": data[0]["lat"], "lng": data[0]["lon"]}
        else:
            coords = {"error": "Could not geocode address"}

        # Get the zone based on GPS location
        zone = get_zone(float(coords["lat"]), float(coords["lng"]))

        if not isinstance(zone, dict):
            logging.error("Failed to retrieve zone information.")
            logging.error(zone)
            coords = {"error": "Address not in Chicago."}
            return render_template("index.html", coords=coords)
        # Print the results
        logging.info(f"Coordinates: {coords}")
        logging.info(f"Zone Details: {zone}")
        logging.info(f"Ward: {zone['ward']}, Section: {zone['section']}")

        cleaning_schedule = get_cleaning_schedule(zone["ward"], zone["section"])
        schedule = []
        if cleaning_schedule:
            for i in cleaning_schedule:
                if i.date() == date.today() and dt.now().hour < 14:
                    schedule.append(i.date().strftime("%Y-%m-%d"))
                elif i.date() > date.today():
                    schedule.append(i.date().strftime("%Y-%m-%d"))

        else:
            coords = {"error": "No cleaning Schedule for the zone."}
            return render_template("index.html", coords=coords)

        if schedule is not None:
            logging.info(
                f"Cleaning schedule for Ward in the next 30 days: {zone['ward']}, Section: {zone['section']}:\n{schedule}"
            )
            coords = schedule
        else:
            logging.warning(
                f"No cleaning schedule found for Ward: {zone['ward']}, Section: {zone['precinct']}."
            )

    return render_template("index.html", coords=coords)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
