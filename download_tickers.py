import pandas as pd
from yahoo_fin import stock_info as si
import requests
import csv
import stockinator as st

if __name__ == '__main__':
    tickers = []
    for ex in ['dow', 'sp500', 'nasdaq', 'other']:
        tickers += (getattr(si, f"tickers_{ex}")())

        periods = ['1d']
        for p in periods:
            data = st.get_stock_data(tickers, period='5y', interval=p)
            data.to_pickle(f"stocks/{ex}_{p}.pkl")
