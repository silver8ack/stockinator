import sys
import requests
import pandas as pd
import stockinator as st
import multiprocessing as mp
import yfinance as yf
import concurrent.futures

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

def historical(ticker):
    sys.stdout.write(f"Processing Stock: [{ticker}] \r")
    sys.stdout.flush()

    try:
        df = yf.Ticker(ticker).history(period='10y', interval='1d')
        return (ticker, df)
    except:
        return (None, None)

if __name__ == '__main__':
    tickers = get_stock_data()
    df_tickers = pd.DataFrame.from_dict(tickers)
    df_tickers = df_tickers.T
    df_tickers.to_pickle('stocks/stock_info.pkl')

    futures = []
    #max_processes = (mp.cpu_count() * 2) - 1
    max_processes = mp.cpu_count() * 2
    print(f"Processing stocks with ThreadPool using {max_processes} workers.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_processes) as exectutor:
        for ticker in list(df_tickers.index):
            future = exectutor.submit(historical, ticker)
            futures.append(future)

    dfs = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        ticker = result[0]
        df = result[1]

        if df is None:
            continue

        df = df.dropna(how='all')
        if df.empty:
            continue

        df = st.dmi(df)
        df = st.calculate_ma(df, type='ema', periods=[20, 50, 100, 150, 200])
        df = st.calculate_rsi(df)
        df = st.calculate_mfi(df)
        df['Sector'] = df_tickers.loc[ticker]['Sector']
        df['Industry'] = df_tickers.loc[ticker]['industry']
        df['Name'] = df_tickers.loc[ticker]['Name']
        dfs.append((ticker, df))

    panel = pd.concat([x[1] for x in dfs], axis=1, keys=[x[0] for x in dfs])

    print("Writing data to disk...")
    panel.to_pickle('stocks/stock_data.pkl')