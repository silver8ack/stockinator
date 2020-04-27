import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import json
import requests
import csv
import os
from collections import OrderedDict

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

def unique_list(l):
    list_set = set(l) 
    return list(list_set)

def get_sp_companies():
    data = pd.read_csv('stocks/sp500.csv')
    return data

def get_period_performance(data, periods=[360], offset=0, weight=1):
    tickers = unique_list([x[0] for x in data.columns.values])
    columns = periods.copy()
    if offset > 0:
        columns += [f"Next_{offset}"]
    df = pd.DataFrame(columns=columns, index=tickers)

    for i, period in enumerate(periods):
        if offset > 0:
            chunk = data.iloc[-(period + offset):-offset]
        else:
            chunk = data.iloc[-period:]

        for ticker in tickers:
            _first = chunk[ticker]['Open'].iloc[0]
            _last = chunk[ticker]['Close'].iloc[-1]
            
            pct_performance = ((_last - _first) / _first) * 100
            df.at[ticker, period] = pct_performance

            df.at[ticker, f"{period}_Weighted"] = pct_performance * (weight / period)
            #df.at[ticker, f"{period}_Weighted"] = pct_performance * (period / weight)
            #df.at[ticker, f"{period}_Weighted"] = pct_performance * (i + 1)

            #check if offset is used and we're at the last data period
            if offset > 0 and i == len(periods)-1:
                next_chunk = data.iloc[-(offset):]
                _next_first = next_chunk[ticker]['Open'].iloc[0]
                _next_last = next_chunk[ticker]['Close'].iloc[-1] 
                next_pct_performance = ((_next_last - _next_first) / _next_first) * 100
                df.at[ticker, f"Next_{offset}"] = np.around(next_pct_performance, decimals=4)

    period_columns = df.filter(regex='^[0-9]*$')
    df['TotalPerformance'] = np.around(period_columns.sum(axis=1), decimals=4)
    
    period_weights = df.filter(regex='_Weighted')
    df['TotalWeight'] = np.around(period_weights.sum(axis=1), decimals=4)
        
    return df

if __name__ == '__main__':
    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 150)
    #tickers = [
    #    'SPY', #'VBR', 'VBK', 'VUG', 'VTV',
    #    'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU'
    #]
    tickers = ['SPY', 'VHT']

    data_set_intervals = [
        #[144, 89, 34],
        #[144, 34, 8],
        #[34, 21, 13, 8, 5],
        #[89, 34, 13, 5],
        #[144, 55, 21, 8],
        #[89, 21, 5],
        [8, 5, 3, 2, 1]
    ]

    sp500 = get_sp_companies()
    #data = get_stock_data(tickers, period='2y', interval='1d')
    
    #data = None
    #data_file = 'sp500_data.pkl'
    #if os.path.exists(data_file):
    #    data = pd.read_pickle(data_file)
    #else:
    #    data = get_stock_data(list(sp500['Symbol'].values) + ['SPY'], period='2y', interval='1d')
    #    data.to_pickle(data_file)
    data = get_stock_data(tickers, period='2y', interval='1d')
    print("Sector strength according to STOCKINATOR")
    print(f"Date of report: {datetime.datetime.now()}")

    for days_back in data_set_intervals:
        print()
        print(f"Intervals and weighting used: {days_back}")
        
        offset = 0
        #offset = days_back[-1]
        #offset = days_back[len(days_back)-2]
        print(data.dropna())
        pf_data = get_period_performance(data.dropna(), data_set_intervals[-1], offset=offset, weight=days_back[-1])
        print(pf_data.sort_values('TotalWeight', ascending=False))  


