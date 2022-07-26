import requests
import json
import os
import time
import busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

API_KEY = os.environ.get("WEATHER_API_KEY")
LOCATIONS_FILE = "locations.json"
FORECAST_LOCATION = "forecasts"
LCD_COLUMNS = 20
LCD_ROWS = 4


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


def load_report(loc):
    report_path = os.path.join(FORECAST_LOCATION, f"{loc}.json")
    try:
        with open(report_path, "r") as f:
            return json.load(f)
    except:
        print(f"Failed to load report at path: {report_path}")
        raise


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


def generate_display_message(loc):
    """Generate the display message for a 20x4 LCD display."""
    forecast = load_report(loc)

    # First line: place (14 characters) + time (5 characters)
    # TODO: fix the time, value in json is incorrect
    localtime_full = forecast["location"]["localtime"]
    localtime = localtime_full[-5:len(localtime_full)].strip()

    place = forecast["location"]["name"]
    max_place_length = 20 - len(localtime) - 1
    if len(place) > max_place_length:
        place = place[0:max_place_length - 1]

    spaces = " " * (20 - len(localtime) - len(place))
    message = f"{place}{spaces}{localtime}\n"

    # Second line: temperature (5 characters) + UV (5 characters) + humidity (7 characters)
    temperature = round(forecast["current"]["temp_c"])
    uv = round(forecast["current"]["uv"])
    humidity = forecast["current"]["humidity"]
    message += f"T={temperature}C UVI={uv} RH={humidity}%\n"

    # Third line: wind (12 characters)
    wind = round(forecast["current"]["wind_kph"])
    direction = forecast["current"]["wind_dir"]
    message += f"W={wind}kph({direction})\n"

    # Fourth line: condition (variable length)
    condition = forecast["current"]["condition"]["text"]
    message += condition

    return message


if __name__ == "__main__":
    clear_reports()
    locations = load_locations()
    for location in locations:
        get_weather(location)

    i2c = busio.I2C(3, 2)
    lcd = character_lcd.Character_LCD_I2C(i2c, LCD_COLUMNS, LCD_ROWS)
    lcd.backlight = True
    lcd.message = generate_display_message(locations[0])
