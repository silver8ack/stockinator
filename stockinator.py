import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
from mplfinance.original_flavor import candlestick_ohlc
import requests
import time
import sys
import datetime
import json
import requests
import csv
import os
from collections import OrderedDict

#df.loc[:, 'bb_high'], df.loc[:, 'bb_mid'], df.loc[:, 'bb_low'] = ta.BBANDS(df.loc[:, 'adjclose'], matype=ta.MA_Type.T3)

# get stock data from yahoo finance
def get_stock_data(tickers, start=None, end=None, interval='1d', period=None):
    return yf.download(
        tickers=' '.join(tickers),
        start=start,
        end=end,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=False,
        threads=False
    )

def unique_list(l):
    list_set = set(l) 
    return list(OrderedDict.fromkeys(l))
    #return list(list_set)

def reset_index(df):
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df.Date)
    
    data = df.sort_values(by="Date", ascending=True).set_index("Date")#.last("59D")
    df = df.set_index('Date')

    return df, data

def adx(df, periods=14):
    df, data = reset_index(df)
    df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=periods)
    return df

def plus_di(df, periods=14):
    df, data = reset_index(df)
    df['DI+'] = ta.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=periods)
    return df

def minus_di(df, periods=14):
    df, data = reset_index(df)
    df['DI-'] = ta.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=periods)
    return df

def aroon(df, periods=14):
    df, data = reset_index(df)
    df['AroonUp'], df['AroonDown'] = ta.AROON(df['High'], df['Low'], timeperiod=periods)
    return df

def atr(df, periods=14):
    df, data = reset_index(df)
    df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=periods)
    return df

def dmi(df, periods=14):
    df, data = reset_index(df)
    df = adx(df, periods)
    df = plus_di(df, periods)
    df = minus_di(df, periods)
    return df

def calculate_rsi(df, periods=14):
    df, data = reset_index(df)
    df[f"RSI_{periods}"] = ta.RSI(df.Close.values, periods)
    
    return df

def calculate_ema(df, periods=[50, 150, 200]):
    df, data = reset_index(df)
    for i, x in enumerate(periods):
        df[f"EMA_{i+1}"] = ta.EMA(df.Close.values, timeperiod=x)
        
    return df

def calculate_ma(df, type='sma', periods=[50, 150, 200]):
    if not type.lower() in ['ema', 'sma']:
        return None
    
    func = getattr(ta, type.upper())
    df, data = reset_index(df)
    for i, x in enumerate(periods):
        df[f"{type.upper()} {x}"] = func(df.Close.values, timeperiod=x)
        
    return df

def calculate_volume(df, periods=[90, 10]):
    df, data = reset_index(df)

    df['OBV'] = ta.OBV(df.Close, df.Volume)
    df['OBV MA'] = ta.EMA(df.OBV.values, timeperiod=21)
    for x in periods:
        df[f"{x} Avg Volume"] = round(df.Volume.rolling(window=x).mean(), 2)
        
    return df

def calculate_mfi(df, period=14):
    df, data = reset_index(df)
    df['MFI'] = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=period)
    
    return df

def get_sp_companies():
    data = pd.read_csv('stocks/sp500.csv')
    return data

def plot_chart(data, n, ticker):
    
    # Filter number of observations to plot
    data = data.iloc[-n:]
    
    # Create figure and set axes for subplots
    fig = plt.figure()
    fig.set_size_inches((20, 16))
    ax_candle = fig.add_axes((0, 0.72, 1, 0.32))
    #ax_macd = fig.add_axes((0, 0.48, 1, 0.2), sharex=ax_candle)
    ax_rsi = fig.add_axes((0, 0.24, 1, 0.2), sharex=ax_candle)
    ax_vol = fig.add_axes((0, 0, 1, 0.2), sharex=ax_candle)
    
    # Format x-axis ticks as dates
    ax_candle.xaxis_date()
    
    # Get nested list of date, open, high, low and close prices
    ohlc = []
    for date, row in data.iterrows():
        openp, highp, lowp, closep = row[:4]
        ohlc.append([date2num(date), openp, highp, lowp, closep])
 
    # Plot candlestick chart
    ax_candle.plot(data.index, data["EMA_1"], label="EMA_1")
    ax_candle.plot(data.index, data["EMA_2"], label="EMA_2")
    ax_candle.plot(data.index, data["EMA_3"], label="EMA_3")
    candlestick_ohlc(ax_candle, ohlc, colorup="g", colordown="r", width=0.8)
    ax_candle.legend()
    
    # Plot MACD
    #ax_macd.plot(data.index, data["macd"], label="macd")
    #ax_macd.bar(data.index, data["macd_hist"] * 3, label="hist")
    #ax_macd.plot(data.index, data["macd_signal"], label="signal")
    #ax_macd.legend()
    
    # Plot RSI
    # Above 70% = overbought, below 30% = oversold
    ax_rsi.set_ylabel("(%)")
    ax_rsi.plot(data.index, [70] * len(data.index), label="overbought")
    ax_rsi.plot(data.index, [30] * len(data.index), label="oversold")
    ax_rsi.plot(data.index, data["RSI"], label="RSI")
    ax_rsi.legend()
    
    # Show volume in millions
    ax_vol.bar(data.index, data["Volume"] / 1000000)
    ax_vol.set_ylabel("(Million)")
   
    # Save the chart as PNG
    fig.savefig("charts/" + ticker + ".png", bbox_inches="tight")
    
    plt.show()

def get_period_performance(data, periods=[360], offset=0, weight=1):
    tickers = unique_list([x[0] for x in data.columns.values])
    columns = periods.copy()
    if offset > 0:
        columns += [f"Next_{offset}"]
    df = pd.DataFrame(columns=columns, index=tickers)

    for i, period in enumerate(periods):
        if offset > 0:
            if i == len(periods)-1: 
                chunk = data.iloc[-((period + offset) + 1):-offset]
            else:
                chunk = data.iloc[-((period + offset) + 1):-(offset + periods[i+1])]
        else:
            if i == len(periods)-1: 
                chunk = data.iloc[-(period + 1):]
            else:
                chunk = data.iloc[-(period + 1):-periods[i+1]]

        for ticker in tickers:
            _first = chunk[ticker]['Close'].iloc[0]
            _last = chunk[ticker]['Close'].iloc[-1]
            
            pct_performance = ((_last - _first) / _first) * 100
            df.at[ticker, period] = pct_performance

            df.at[ticker, f"{period}_Weighted"] = pct_performance * (weight / period)
            #df.at[ticker, f"{period}_Weighted"] = pct_performance * (period / weight)
            #df.at[ticker, f"{period}_Weighted"] = pct_performance * (i + 1)

            #check if offset is used and we're at the last data period
            if offset > 0 and i == len(periods)-1:
                next_chunk = data.iloc[-(offset):]
                _next_first = next_chunk[ticker]['Close'].iloc[0]
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


