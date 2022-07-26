import requests
import json
import os

API_KEY = os.environ.get("WEATHER_API_KEY")
LOCATIONS_FILE = "locations.json"
FORECAST_LOCATION = "forecasts"


def clear_reports():
    if not os.path.exists(FORECAST_LOCATION):
        return

    contents = os.listdir(FORECAST_LOCATION)
    for file in contents:
        os.remove(os.path.join(FORECAST_LOCATION, file))


def save_report(file_name, data):
    if not os.path.exists(FORECAST_LOCATION):
        os.makedirs(FORECAST_LOCATION)

    with open(f"{FORECAST_LOCATION}/{file_name}.json", "w") as f:
        f.write(json.dumps(data, indent=4))


def get_weather(loc):
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={loc}&aqi=no")
    except:
        print("Failed to perform a request to the weather API.")
        raise
    if not response.ok:
        raise Exception(f"Error fetching the weather data. Status code: {response.status_code}")

    save_report(loc, response.json())


def load_locations():
    try:
        with open(LOCATIONS_FILE, "r") as f:
            return json.load(f)
    except:
        print(f"Locations json at path {LOCATIONS_FILE} is invalid. Must be a json list.")
        raise


if __name__ == "__main__":
    clear_reports()
    locations = load_locations()
    for location in locations:
        get_weather(location)
        print(f"Updated weather for location: {location}")
