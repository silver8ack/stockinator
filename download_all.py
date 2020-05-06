import pandas as pd
import requests
import csv
import stockinator as st

if __name__ == '__main__':
    urls = {
        'nasdaq': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
        'nyse': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
    }

    tickers = []
    for exchange, url in urls.items():
        resp = requests.get(url)
        lines = resp.text.split(',\r\n')
        lines.pop(0)

        for line in lines:
            l = line.replace('"', '').split(',')
            tickers.append(l[0].strip())

    periods = ['1d']
    for p in periods:
        data = st.get_stock_data(tickers + ['SPX', 'VIX'], period='2y', interval=p)
        data.to_pickle(f"stocks/all_{p}.pkl")
