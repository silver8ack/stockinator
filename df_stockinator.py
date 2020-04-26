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

def get_period_performance(data, periods=[360], stat='Close', offset=0, weight=1):
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
            first_close = chunk[ticker]['Close'].iloc[0]
            last_close = chunk[ticker]['Close'].iloc[-1]
            pct_performance = ((last_close - first_close) / first_close) * 100
            df.at[ticker, period] = pct_performance

            df.at[ticker, f"{period}_Weighted"] = pct_performance * (weight / period)

            #check if offset is used and we're at the last data period
            if offset > 0 and i == len(periods)-1:
                next_chunk = data.iloc[-(offset):]
                next_first_close = next_chunk[ticker]['Close'].iloc[0]
                next_last_close = next_chunk[ticker]['Close'].iloc[-1] 
                next_pct_performance = ((next_last_close - next_first_close) / next_first_close) * 100
                df.at[ticker, f"Next_{offset}"] = next_pct_performance

    period_weights = df.filter(regex='_Weighted')
    df['TotalWeight'] = period_weights.sum(axis=1)
        
    return df

tickers = [
    'SPY', #'VBR', 'VBK', 'VUG', 'VTV',
    'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU'
]

data_set_intervals = [
    #[144, 89, 34],
    #[144, 34, 8],
    #[34, 21, 13, 8, 5],
    #[89, 34, 13, 5],
    #[144, 55, 21, 8],
    [89, 21, 5],
]


data = get_stock_data(tickers, period='2y', interval='1d')  
pf_data = get_period_performance(data, data_set_intervals[-1], offset=21, weight=5)
print(pf_data)
