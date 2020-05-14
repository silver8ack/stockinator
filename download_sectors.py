import pandas as pd
from yahoo_fin import stock_info as si
import requests
import csv
import stockinator as st

if __name__ == '__main__':
    tickers = [
        'SPY', 'VBR', 'VBK', 'VUG', 'VTV',
        'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU'
    ]

    periods = ['1d', '1wk', '1mo']
    for p in periods:
        data = st.get_stock_data(tickers, period='20y', interval=p)
        data.to_pickle(f"stocks/sectors_{p}.pkl")
