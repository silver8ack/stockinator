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

def get_performance(data, periods=[360], stat='Close', offset=0):
    perf_data = {}
    for i, period in enumerate(periods):
        for t, d in data.iteritems():
            if t[1] == stat:
                chunk = d[-(period+offset):]
                if not t[0] in perf_data:
                    perf_data[t[0]] = OrderedDict()

                perf_data[t[0]][period] = \
                    {'raw': (chunk[-1] - chunk[0]) / chunk[0] * 100}            
        
                #check if offset is used and we're at the last data period
                if offset > 0 and i == len(periods)-1:
                    new_chunk = d[-period:]
                    perf_data[t[0]][period]['next_period'] = \
                        (new_chunk[-1] - new_chunk[0]) / new_chunk[0] * 100

    return perf_data

def get_weighted_performance(d, weight=1):
    for ticker, period in d.items():
        for period_key, perf_data in d[ticker].items():
            d[ticker][period_key]['weighted'] = \
                (weight / int(period_key)) * perf_data['raw']

    return d

def get_new_investments(d):
    weighted_totals = []
    next_period_title = ''
    for ticker, perf_data in d.items():
        ticker_total = 0
        for period, data in perf_data.items():
            ticker_total += data['weighted']
            next_period = data.get('next_period', None)
            if not next_period is None:
                next_period_title = period
        
        weighted_totals.append((ticker, ticker_total, next_period))

    return ('Ticker', 'Rank', f"Performance Next {next_period_title}"), weighted_totals

def sort_list_of_tuples(l, reverse=True):  
    return(sorted(l, key = lambda x: x[1], reverse=reverse))


if __name__ == '__main__':
    tickers = [
        'SPY', 'AAPL', 'AMZN', 'MSFT', 'FB', 'GOOG', 'NFLX',
        'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU'
    ]

    data_set_intervals = [
        [144, 89, 34],
        [144, 89, 34, 13],
        [144, 89, 55, 34, 21, 13, 8]
    ]
    
    data = get_stock_data(tickers, period='5y', interval='1d')
    
    print("Sector strength according to STOCKINATOR")
    print(f"Date of report: {datetime.datetime.now()}")

    for days_back in data_set_intervals:
        print()
        print(f"Intervals and weighting used: {days_back}")
        
        raw_perf_data = get_performance(data, periods=days_back, offset=days_back[-1])
        #raw_perf_data = get_performance(data, periods=days_back, offset=0)
        weighed_perf_data = get_weighted_performance(raw_perf_data, weight=days_back[-1])
        header, new_stocks = get_new_investments(weighed_perf_data)
        sorted_stocks = sort_list_of_tuples(new_stocks)
        
        print(', '.join(header))
        for stock in sort_list_of_tuples(new_stocks):
            print(f"{stock[0]}, {stock[1]}, {stock[2]}")


