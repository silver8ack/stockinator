import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import json
from collections import OrderedDict

def get_stock_data(tickers, start=None, end=None, interval='1d', period=None):
    return yf.download(
        tickers=' '.join(tickers),
        start=start,
        end=end,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=True,
        threads=True
    )

def get_performance(data, periods=[360], stat='Close'):
    perf_data = {}
    for period in periods:
        for t, d in data.iteritems():
            if t[1] == stat:
                chunk = d[-period:]
                if not t[0] in perf_data:
                    perf_data[t[0]] = OrderedDict()

                perf_data[t[0]][period] = {'raw': (chunk[-1] - chunk[0]) / chunk[0] * 100}
    
    return perf_data

def get_weighted_performance(d, weight=1):
    for ticker, period in d.items():
        for period_key, perf_data in d[ticker].items():
            d[ticker][period_key]['weighted'] = (weight / int(period_key)) * perf_data['raw']

    return d

def get_new_investments(d):
    weighted_totals = []
    for ticker, perf_data in d.items():
        ticker_total = 0
        for period, data in perf_data.items():
            ticker_total += data['weighted']
        
        weighted_totals.append((ticker, ticker_total))

    return weighted_totals

def sort_list_of_tuples(l, reverse=True):  
    return(sorted(l, key = lambda x: x[1], reverse=reverse))


if __name__ == '__main__':
    tickers = ['SPY', 'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU']
    data = get_stock_data(tickers, period='2y', interval='1d')
    
    raw_perf_data = get_performance(data, periods=[144, 89, 55, 34, 21, 8, 5])
    weighed_perf_data = get_weighted_performance(raw_perf_data, weight=5)
    new_stocks = get_new_investments(weighed_perf_data)

    print(f"Sector strength according to STOCKINATOR as of {datetime.datetime.now()}")
    for stock in sort_list_of_tuples(new_stocks):
        print(stock[0], stock[1])


