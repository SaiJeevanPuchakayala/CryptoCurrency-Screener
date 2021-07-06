import requests
import json
import time
from datetime import datetime
from flask import Flask, render_template, Response

app = Flask("__name__")

API_URL = "https://yahoo-crypto-api.herokuapp.com/chart"


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/table')
def table_creator():
    return render_template("table.html")   


@app.route("/<crypto>")
def index(crypto):
    supported_cryptos = requests.get(API_URL).json().keys()
    if crypto in supported_cryptos:
        return render_template("chart.html",crypto=crypto)
    return "This Cryptocurrency is not yet supported!"



def generate_random_data(crypto_code):
    while True:
        price = float(requests.get(API_URL).json()[crypto_code]['price'].replace(",",''))
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "value": price,
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(15)


@app.route("/chart-data/<crypto>")
def chart_data(crypto):
    return Response(generate_random_data(crypto), mimetype="text/event-stream")


if __name__=='__main__':
    app.run(debug=True)

