# Weather Web App using AJAX and Flask

# Import statements
import requests
import re
import pprint
import datetime
import json
from flask import Flask, render_template, request


# Constants
DEBUG = True
API_KEY = open("APIKEY.txt", "r").readline()
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

# Flask Setup
app = Flask(__name__)


# Functions
def make_request(postcode):
    postcode_to_lat_lng_url = "http://uk-postcodes.com/postcode/{}.json" \
        .format(postcode)
    print(postcode_to_lat_lng_url)
    postcode_request = requests.get(postcode_to_lat_lng_url)
    postcode_data = postcode_request.json()

    geo_data = postcode_data["geo"]
    lat = geo_data["lat"]
    lng = geo_data["lng"]

    forecast_url = "https://api.forecast.io/forecast/{}/{},{}?units=uk" \
        .format(API_KEY, lat, lng)
    print(forecast_url)
    forecast_request = requests.get(forecast_url)
    forecast_data = forecast_request.json()
    return forecast_data


def warnings(forecast_data):
    try:
        alert_data = forecast_data[0]["alerts"]
        warning_data = []
        if len(alert_data) != 0:
            for item in alert_data:
                title = item["title"]
                expires = item["expires"]
                url = item["uri"]
                warning_data.append([title, expires, url])
    except:
        warning_data = [["No Warnings", "N/A", "N/A"]]
    return warning_data


# Routes
@app.route("/")
def weather():
    return render_template("weather.html")


@app.route("/contact")
def contact():
    return "contact"


@app.route("/get_weekly_summary", methods=("POST", "GET"))
def get_weekly_summary():
    postcode = request.form["postcode"]
    space_less_postcode = re.sub(" ", "", postcode)
    if space_less_postcode != "":
        forecast_data = make_request(space_less_postcode)
        daily_data = forecast_data["daily"]["data"]
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(daily_data)
        output_data = []
        for data_block in daily_data:
            unix_time = data_block["time"]
            unix_time_int = int(unix_time)
            date = datetime.datetime.fromtimestamp(unix_time_int)
            summary = data_block["summary"]
            output_data.append([DAYS_OF_WEEK[date.weekday()], summary])

        warning_data = warnings(forecast_data)

        return json.dumps([output_data, warning_data])
    return json.dumps("No Postcode")


@app.route("/get_today_summary", methods=("POST", "GET"))
def get_today_summary():
    postcode = request.form["postcode"]
    space_less_postcode = re.sub(" ", "", postcode)
    if space_less_postcode != "":
        forecast_data = make_request(space_less_postcode)
        daily_data = forecast_data["hourly"]["data"]

        c = 1
        output_data = []
        for data_block in daily_data:
            if c == 25:
                break
            unix_time = data_block["time"]
            unix_time_int = int(unix_time)
            date = datetime.datetime.fromtimestamp(unix_time_int)
            summary = data_block["summary"]
            output_data.append([date.strftime("%H:%M %d-%m-%Y"), summary])
            c += 1

        new_output_data = []
        first = True
        for item in output_data:
            if first is True:
                first = False
                new_output_data.append(item)
            else:
                if new_output_data[-1][1] == item[1]:
                    new_output_data[-1][0] = "{} to {}".format(
                        new_output_data[-1][0][:15], item[0]
                    )
                else:
                    new_output_data.append(item)

        warning_data = warnings(make_request(space_less_postcode))

        return json.dumps([new_output_data, warning_data])
    return json.dumps("No Postcode")


@app.route("/get_detailed_summary", methods=["POST", "GET"])
def get_detailed_summary():
    postcode = request.form["postcode"]
    space_less_postcode = re.sub(" ", "", postcode)
    if space_less_postcode != "":
        forecast_data = make_request(space_less_postcode)
        daily_data = forecast_data["hourly"]["data"]

        c = 1
        output_data = []
        for data_block in daily_data:
            if c == 25:
                break
            unix_time = data_block["time"]
            unix_time_int = int(unix_time)
            date = datetime.datetime.fromtimestamp(unix_time_int)
            summary = data_block["summary"]
            temperature = data_block["temperature"]
            apparent_temperature = data_block["apparentTemperature"]
            precip_probability = data_block["precipProbability"]
            if precip_probability != 0:
                precip_type = data_block["precipType"]
            else:
                precip_type = "none"
            output_data.append(
                [
                    date.strftime("%H:%M %d-%m-%Y"),
                    summary,
                    temperature,
                    apparent_temperature,
                    precip_probability,
                    precip_type
                ]
            )
            c += 1

        warning_data = warnings(forecast_data)

        return json.dumps([output_data, warning_data])
    return json.dumps("No Postcode")

# Run
if __name__ == "__main__":
    app.run(debug=DEBUG)
