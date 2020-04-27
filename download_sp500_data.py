import stockinator as st
import pandas as pd

if __name__ == '__main__':
    sp500 = st.get_sp_companies()

    data = st.get_stock_data(list(sp500['Symbol'].values) + ['SPY'], period='10y', interval='1d')
    data.to_pickle('stocks/sp500.pkl')
