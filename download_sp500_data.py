import stockinator as st
import pandas as pd

if __name__ == '__main__':
    sp500 = st.get_sp_companies()
    periods = ['1d', '1wk', '1mo']
    for p in periods:
        data = st.get_stock_data(list(sp500['Symbol'].values) + ['SPX', 'VIX'], period='5y', interval=p)
        data.to_pickle(f"stocks/sp500_{p}.pkl")
