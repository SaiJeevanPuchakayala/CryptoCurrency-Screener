import requests
import json
import time
from datetime import datetime
from flask import Flask, render_template, Response
from bs4 import BeautifulSoup

app = Flask("__name__")

API_URL = "https://yahoo-crypto-api.herokuapp.com/chart"


class Scraper:
    def __init__(self, keywords):
        self.markup = requests.get('https://economictimes.indiatimes.com/markets/cryptocurrency').text
        self.keywords = keywords

    def parse(self):
        soup = BeautifulSoup(self.markup, 'lxml')
        links = soup.findAll('a', limit=300)  
        self.news_links = []
        self.news_linksTexts = []
        for link in links:
            for keyword in self.keywords:
                if keyword in link.text and '?' not in link.text:
                    self.news_links.append(link)
        for link in self.news_links:
            self.news_linksTexts.append(link.text)



@app.route('/')
def home():
    s = Scraper([
    'cryptocurrency',
    'crypto',
    'bitcoin',
    'crash',
    'cryptocurrency prices',
    'government',
    'ranks',
    'towards',
    'crash',
    'market',
    'trends',
    'financials',
    'capitalist'
    ])

    news_list = []
    s.parse()
    for x in s.news_linksTexts:
        news_list.append(x)
    return render_template("index.html",news=list(set(news_list)))


@app.route('/table')
def table_creator():
    return render_template("table.html")


@app.route('/chart')
def chart_creator():
    return render_template("chart2.html")   


@app.route("/<crypto>")
def index(crypto):
    supported_cryptos = requests.get(API_URL).json().keys()
    crypt_values = requests.get(API_URL).json().values()
    print(list(crypt_values)[0])
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

