import sys
import requests
import pandas as pd
import yfinance as yf
import multiprocessing as mp
import stockinator as st
from multiprocessing.dummy import Pool as ThreadPool

def get_stock_data():
    urls = {
        'nasdaq': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
        'nyse': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
        'amex': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download',
    }

    headers = []
    ticker_data = {}
    for exchange, url in urls.items():
        resp = requests.get(url)
        lines = resp.text.split(',\r\n')
        if len(headers) == 0:
            headers = lines.pop(0).replace('"' ,'').split(',')
            headers.pop(0)
        else:
            lines.pop(0)

        for line in lines:
            l = line.split('","')
            symbol = l.pop(0).replace('"','').strip()
            ticker_data[symbol] = {}
            for i, c in enumerate(l):
                ticker_data[symbol][headers[i]] = c.replace('"', '').strip()

    return ticker_data

def ta_data(df):
    df = df.dropna(how='all')
    if df.empty:
        return

    df = st.dmi(df)
    df = st.calculate_ma(df, type='ema', periods=[20, 50, 100, 150, 200])
    df = st.calculate_rsi(df)
    df = st.calculate_mfi(df)
    return df

def print_it(s):
    sys.stdout.write("Processing Stock: {}\r".format(s['Symbol']))
    sys.stdout.flush()

    return s['Symbol']

if __name__ == '__main__':
    df = pd.read_pickle('stocks/all_1d.pkl')
    symbols = [x[0] for x in df.columns.values]
    data = []
    for symbol in symbols:
        sys.stdout.write(f"Processing Stock: {symbol}\r")
        sys.stdout.flush()
        
        df = ta_data(df)
        if not df is None:
            data.append((symbol, df))

    da_ta = pd.concat([x[1] for x in data], axis=1, keys=[x[0] for x in data])
    da_ta.to_pickle('stocks/ta_data.pkl')
    #print(len(data))
    
    #periods = ['1d']
    #for p in periods:
    #    data = st.get_stock_data(tickers, period='1y', interval=p)
    #    data.to_pickle(f"stocks/all_{p}.pkl")
