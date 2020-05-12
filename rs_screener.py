import stockinator as st
import yfinance as yf
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt
import requests
import datetime
import time
import os
import sys

if __name__ == '__main__':
    all_data = pd.read_pickle('stocks/all_1d.pkl')
    stocklist = st.unique_list([x[0] for x in all_data.columns.values])
    total_stocks = len(stocklist)

    #final = []
    #index = []
    exportList = pd.DataFrame(columns=[
        'Stock', 'RSI', 'Price', '90 Avg Volume', '10 Avg Volume', '50 EMA', 
        '150 EMA', '200 EMA', '52 Week Low', '52 Week High'])

    offset = 21
    n = -1
    for stock in stocklist:
        n += 1
        #print("Index {} of {} Stock [{}] \r".format(n, total_stocks, stock))
        sys.stdout.write("Index {} of {} Stock [{}] \r".format(n, total_stocks, stock))
        sys.stdout.flush()

        df = all_data[stock]
        if offset > 0:
            df = df[:-offset]

        df = df.dropna(how='all')
        if df.empty:
            continue

        df = st.calculate_rsi(df)
        df = st.calculate_ema(df)
        df = st.calculate_volume(df)

        try:
            moving_average_200_21 = df["EMA_200"][-21]
        except Exception:
            moving_average_200_21 = 0

        try:
            currentClose = df["Adj Close"][-1]
            low_of_52week = min(df["Adj Close"][-260:])
            high_of_52week = max(df["Adj Close"][-260:])
            moving_average_50 = df["EMA_50"][-1]
            moving_average_150 = df["EMA_150"][-1]
            moving_average_200 = df["EMA_200"][-1]
            avg_volume_90 = df['90 Avg Volume'][-1]
            avg_volume_10 = df['10 Avg Volume'][-1]
            rsi = df['RSI'][-1]
            rsi_21 = df['RSI'][-21]
        except Exception:
            continue

        try:
            assert(moving_average_50 > moving_average_200)
            assert(moving_average_200 > moving_average_200_21)
            assert(currentClose > moving_average_50 > moving_average_200)
            assert(currentClose >= (1.3 * low_of_52week))
            assert(currentClose >= (.75 * high_of_52week))
            #assert(rsi > 60)
            assert(rsi > rsi_21)
        except AssertionError:
            continue
        except IndexError as e:
            continue
        except Exception as e:
            print(e)

        try:
            #final.append(stock)
            #index.append(n)
            #dataframe = pd.DataFrame(list(zip(final, index)), columns =['Company', 'Index'])
            #dataframe.to_csv('stocks.csv')
            
            exportList = exportList.append(
                {
                    'Stock': stock, 
                    'RSI': rsi, 
                    'Price': currentClose,
                    '90 Avg Volume': avg_volume_90,
                    '10 Avg Volume': avg_volume_10,
                    '50 EMA': moving_average_50, 
                    '150 EMA': moving_average_150, 
                    '200 EMA': moving_average_200, 
                    '52 Week Low': low_of_52week, 
                    '52 Week High': high_of_52week
                }, ignore_index=True)
        except Exception as e:
            print(e)

    print(exportList.sort_values('RSI', ascending=False))
    exportList.sort_values('RSI', ascending=False).to_csv('stocks.csv', index=False)
