import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import cfscrape
import temp
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject

app = Flask("__name__")

scraper = cfscrape.create_scraper()
client = Client(temp.coinbase_API_key, temp.coinbase_API_secret)


def _get_soup(url):
    return BeautifulSoup(
        scraper.get(
            url
        ).text,
        "lxml"
    )


class News_Scraper:
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
    s = News_Scraper([
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

    news_text_list = []
    news_links_list = []
    s.parse()
    for x in s.news_links:
        news_text_list.append(x.text)
        news_links_list.append("https://economictimes.indiatimes.com"+x['href'])
    news = list(zip(news_text_list,news_links_list))
    return render_template("index.html",news=list(set(news)))


@app.route('/table')
def table_creator():
    return render_template("table.html")


@app.route('/chart')
def chart_creator():
    return render_template("chart.html")   

@app.route('/api/table')
def get_cryptos_table():

    base_url = "https://finance.yahoo.com/cryptocurrencies"
    soup = _get_soup(base_url)
    currency_rows = soup.select("table tbody tr")

    table_currency = [{
        "symbol":td.select("td")[0].select("img")[0]['src'],
        "name":td.select("td")[1].text,
        "price":td.select("td")[2].text,
        "chg":td.select("td")[3].text,
        "chg_per":td.select("td")[4].text,
        "market_cap":td.select("td")[5].text
    } for td in currency_rows]

    return jsonify(table_currency)

@app.route('/api/chart')
def get_crypto_prices():

    base_url = "https://www.investing.com/crypto/currencies"

    soup = _get_soup(base_url)
    currency_rows = soup.select(".genTbl.openTbl.js-all-crypto-table.mostActiveStockTbl.crossRatesTbl.allCryptoTlb.wideTbl.elpTbl.elp15")[0].select("tbody")[0].select("tr")

    crypto_list = {}

    for crypto in currency_rows[:30]:
        crypto_name = crypto.select(".left.bold.elp.name.cryptoName.first.js-currency-name")[0].text
        crypto_symbol = crypto.select(".left.noWrap.elp.symb.js-currency-symbol")[0].text
        crypto_price = crypto.select(".price.js-currency-price")[0].text
        crypto_list[crypto_symbol]=crypto_price


    return jsonify(crypto_list)


@app.route('/api/chart-symbols1')
def get_crypto_symbols1():

    base_url = "https://www.investing.com/crypto/currencies"

    soup = _get_soup(base_url)
    currency_rows = soup.select(".genTbl.openTbl.js-all-crypto-table.mostActiveStockTbl.crossRatesTbl.allCryptoTlb.wideTbl.elpTbl.elp15")[0].select("tbody")[0].select("tr")

    crypto_list = {}

    for crypto in currency_rows[:30]:
        crypto_name = crypto.select(".left.bold.elp.name.cryptoName.first.js-currency-name")[0].text
        crypto_symbol = crypto.select(".left.noWrap.elp.symb.js-currency-symbol")[0].text
        crypto_list[crypto_symbol]=crypto_name


    return jsonify(crypto_list)

@app.route('/api/chart-symbols2')
def get_crypto_symbols2():

    base_url = "https://finance.yahoo.com/cryptocurrencies"
    soup = _get_soup(base_url)
    currency_rows = soup.select("table tbody tr")

    crypto_list = {}

    for td in currency_rows:
        short_name = td.select('td')[0].select("a")[0].text.split('-')[0]
        name = td.select("td")[1].text

        crypto_list[short_name]=name

    return jsonify(crypto_list)

@app.route('/api/chart-data1')
def get_crypto_data1():

    base_url = "https://finance.yahoo.com/cryptocurrencies"
    soup = _get_soup(base_url)
    currency_rows = soup.select("table tbody tr")

    crypto_list = {}

    for td in currency_rows:
        symbol = td.select("td")[0].select("img")[0]['src']
        short_name = td.select('td')[0].select("a")[0].text.split('-')[0]
        name = td.select("td")[1].text
        price = td.select("td")[2].text
        chg = td.select("td")[3].text
        chg_per = td.select("td")[4].text
        market_cap = td.select("td")[5].text
        
        items = {
        "name":name,
        "price":price
        }

        crypto_list[short_name]=items

    return jsonify(crypto_list)



@app.route("/api/chart-data2")
def get_historic_data():
    input_code = request.args['crypto_name']
    data = client._make_api_object(client._get('v2', 'prices', f'{input_code}-USD', 'historic'), APIObject)

    return jsonify(data)

if __name__=='__main__':
    app.run(debug=True)

