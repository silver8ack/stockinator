import sys
import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor

def get_stocks(stock):
    sys.stdout.write("Getting Stock [{0}]   \r".format(stock))
    sys.stdout.flush()
    
    s = yf.Ticker(stock)
    i = s.info
    if (i['regularMarketPrice'] > 20 and 
            i['regularMarketPrice'] > i['fiftyDayAverage'] and 
            i['fiftyDayAverage'] > i['twoHundredDayAverage'] and
            (i['regularMarketPrice']/i['fiftyTwoWeekHigh'])*100 > 80):
        return i

if __name__ == "__main__":
    # URLs for Stock Ticker Download
    urls = {
        'nasdaq': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
        'nyse': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
    }

    # Get an array of stock tickers
    tickers = []
    for exchange, url in urls.items():
        resp = requests.get(url)
        lines = resp.text.split(',\r\n')
        lines.pop(0)

        for line in lines:
            l = line.replace('"', '').split(',')
            tickers.append(l[0].strip())

    # Number of threads to create for retrieving data
    stocks = []
    with ThreadPoolExecutor(32) as executor:
        results = executor.map(get_stocks, tickers)

    print("List processing complete.")
    for r in results:
        if not r is None:
            stocks.append(r)

    df = pd.DataFrame(stocks)
    print(df)

