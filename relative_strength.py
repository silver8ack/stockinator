import yfinance as yf
import pandas as pd
from datetime import datetime

def allfridays(year):
    return pd.date_range(start=str(year), end=datetime.now().today(), 
                         freq='W-FRI').strftime('%m/%d/%Y').tolist()

if __name__ == '__main__':
    data = pd.read_pickle('stocks/sp500_1mo.pkl')
    df_diff = data.dropna(thresh=600).diff()
    for ticker, metric in data.columns:
        if df_diff[ticker]['Close'] > df_diff['SPX']['Close']:
            print(df_diff[ticker])

#start_of_week = date_obj - timedelta(days=date_obj.weekday())  # Monday
#end_of_week = start_of_week + timedelta(days=6)  # Sunday
#print(start_of_week)
#print(end_of_week)
