from pandas import ExcelWriter, read_pickle
import stockinator as st
import yfinance as yf
import pandas as pd
import requests
import datetime
import time
import os
import sys

def reset_index(df):
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df.Date)
    
    data = df.sort_values(by="Date", ascending=True).set_index("Date")#.last("59D")
    df = df.set_index('Date')

    return df, data

def calculate_rsi(df, rsi_period=14):
    df, data = reset_index(df)
    chg = data['Close'].diff(1)
    gain = chg.mask(chg < 0, 0)
    data['gain'] = gain
    loss = chg.mask(chg > 0, 0)
    data['loss'] = loss
    avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    data['avg_gain'] = avg_gain
    data['avg_loss'] = avg_loss

    rs = abs(avg_gain/avg_loss)
    rsi = 100-(100/(1+rs))
    df['RSI'] = rsi

    return df

def calculate_sma(df, sma=[50, 150, 200]):
    df, data = reset_index(df)
    for x in sma:
        df["SMA_"+str(x)] = round(df.iloc[:,4].rolling(window=x).mean(), 2)
        
    return df

if __name__ == '__main__':
    all_data = read_pickle('stocks/all_1d.pkl')
    stocklist = st.unique_list([x[0] for x in all_data.columns.values])
    total_stocks = len(stocklist)

    #final = []
    #index = []
    exportList = pd.DataFrame(columns=[
        'Stock', 'RS_Rating', 'Price', '50 SMA', 
        '150 SMA', '200 SMA', '52 Week Low', '52 Week High'])

    n = -1
    for stock in stocklist:
        n += 1
        sys.stdout.write("Index {} of {} Stock [{}] \r".format(n, total_stocks, stock))
        sys.stdout.flush()

        df = all_data[stock].dropna(how='all')
        if df.empty:
            continue

        df = calculate_rsi(df)
        df = calculate_sma(df)

        try:
            moving_average_200_21 = df["SMA_200"][-21]
        except Exception:
            moving_average_200_21 = 0

        try:
            currentClose = df["Adj Close"][-1]
            low_of_52week = min(df["Adj Close"][-260:])
            high_of_52week = max(df["Adj Close"][-260:])
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            rs_rating = df['RSI'].mean()
        except Exception:
            continue

        try:
            assert(df["SMA_50"][-1] > df["SMA_200"][-1])
            assert(df["SMA_200"][-1] > moving_average_200_21)
            assert(df["Adj Close"][-1] > df["SMA_50"][-1] > df["SMA_200"][-1])
            assert(df["Adj Close"][-1] >= (1.3 * min(df["Adj Close"][-260:])))
            assert(df["Adj Close"][-1] >= (.75 * max(df["Adj Close"][-260:])))
            assert(rs_rating > 50)
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
                    'RS_Rating': rs_rating, 
                    'Price': currentClose,
                    '50 SMA': moving_average_50, 
                    '150 SMA': moving_average_150, 
                    '200 SMA': moving_average_200, 
                    '52 Week Low': low_of_52week, 
                    '52 Week High': high_of_52week
                }, ignore_index=True)
        except Exception as e:
            print(e)

    print(exportList.sort_values('RS_Rating', ascending=False))
    exportList.sort_values('RS_Rating', ascending=False).to_csv('stocks.csv', index=False)
