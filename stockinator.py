import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import json
import requests
import csv
import os
from collections import OrderedDict

def unique_list(l):
    list_set = set(l) 
    return list(list_set)
        
def get_sp_companies():
    data = pd.read_csv('sp500.csv')
    return data
    
# get stock data from yahoo finance
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

def get_period_performance(data, periods=[360], stat='Close', offset=0, weight=1):
    tickers = unique_list([x[0] for x in data.columns.values])
    columns = periods
    if offset > 0:
        columns += [f"Next_{offset}"]
    df = pd.DataFrame(columns=columns, index=tickers)

    for ticker in tickers:
        period_pctchanges = []
        for i, period in enumerate(periods):
            if offset > 0:
                chunk = data.iloc[-(period+offset):-offset]
            else:
                chunk = data.iloc[-(period+offset):]
            
            first_close = chunk[ticker].iloc[0]['Close']
            last_close = chunk[ticker].iloc[-1]['Close']
            period_pctchanges.append(((last_close - first_close) / first_close) * 100)
         
        df.loc[ticker] = period_pctchanges
        display(df)
            
    
# calculate performance data from dataframes
# using the periods and offset
def get_performance(data, periods=[360], stat='Close', offset=0):
    perf_data = {}
    for i, period in enumerate(periods):
        for t, d in data.iteritems():
            if t[1] == stat:
                chunk = None
                if offset > 0:
                    chunk = d[-(period+offset):-offset]
                else:
                    chunk = d[-(period+offset):]

                if not t[0] in perf_data:
                    perf_data[t[0]] = OrderedDict()

                perf_data[t[0]][period] = \
                    {'raw': (chunk[-1] - chunk[0]) / chunk[0] * 100}            
        
                #check if offset is used and we're at the last data period
                if offset > 0 and i == len(periods)-1:
                    new_chunk = d[-(offset):]
                    perf_data[t[0]][offset]['next_period'] = \
                        (new_chunk[-1] - new_chunk[0]) / new_chunk[0] * 100

    return perf_data

# weight the performance data based on the periods used
def get_weighted_performance(d, weight=1):
    for ticker, period in d.items():
        for period_key, perf_data in d[ticker].items():
            d[ticker][period_key]['weighted'] = \
                (weight / int(period_key)) * perf_data['raw']

    return d

# rank investements and calculate performance of next period
def get_new_investments(d):
    weighted_totals = []
    for ticker, perf_data in d.items():
        ticker_total = 0
        next_period = 0
        for period, data in perf_data.items():
            ticker_total += data['weighted']
            if 'next_period' in data:
                next_period = data['next_period']
        
        weighted_totals.append((ticker, \
            np.around(ticker_total, decimals=2), np.around(next_period, decimals=2,)))

    return weighted_totals

# sort tuples
def sort_list_of_tuples(l, reverse=True):  
    return(sorted(l, key = lambda x: x[1], reverse=reverse))


if __name__ == '__main__':
    #tickers = [
    #    'SPY', #'VBR', 'VBK', 'VUG', 'VTV',
    #    'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU'
    #]
    #tickers = ['SPY', 'VHT']

    data_set_intervals = [
        #[144, 89, 34],
        #[144, 34, 8],
        #[34, 21, 13, 8, 5],
        #[89, 34, 13, 5],
        #[144, 55, 21, 8],
        [89, 21, 5],
    ]
    sp500 = get_sp_companies()
    #data = get_stock_data(tickers, period='2y', interval='1d')
    
    data = None
    data_file = 'sp500_data.pkl'
    if os.path.exists(data_file):
        data = pd.read_pickle(data_file)
    else:
        data = get_stock_data(list(sp500['Symbol'].values) + ['SPY'], period='2y', interval='1d')
        data.to_pickle(data_file)

    print("Sector strength according to STOCKINATOR")
    print(f"Date of report: {datetime.datetime.now()}")

    for days_back in data_set_intervals:
        print()
        print(f"Intervals and weighting used: {days_back}")
        
        offset = 0
        #offset = days_back[-1]
        #offset = days_back[len(days_back)-2]
        raw_perf_data = get_performance(data, periods=days_back, offset=offset)
        weighted_perf_data = get_weighted_performance(raw_perf_data, weight=days_back[-1])
        new_stocks = get_new_investments(weighted_perf_data)
        
        print(f"Ticker, Rank, Performance Next {offset}")
        sorted_stocks = sort_list_of_tuples(new_stocks)
        for stock in sorted_stocks:
            print(f"{stock[0]}, {stock[1]}, {stock[2]}")


