import pandas as pd
import numpy as np
import stockinator as st

offset = 0

df = pd.read_pickle('stocks/all_1d.pkl')
df_year = df.iloc[-250:]
df_diff = df.dropna(thresh=600).diff()

tickers = st.unique_list([x[0] for x in df_year.columns.values])
data = {}
for t in tickers:
    fifty_avg = np.around(df_year[t][-50:].mean(), decimals=2),
    two_hundred_avg = np.around(df_year[t][-200:].mean(), decimals=2)
    last_price = df_year[t]['Close'].iloc[-1]

    if last_price > 20:
        data[t] = {
            '52High': np.around(df_year[t]['High'].max(), decimals=2),
            'Last': np.around(df_year[t]['Close'].iloc[-1], decimals=2),
            '10d': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-10]) / df_year[t]['Close'].iloc[-10], 
                decimals=2),
            '1mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-21]) / df_year[t]['Close'].iloc[-21], 
                decimals=2),
            '2mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-42]) / df_year[t]['Close'].iloc[-42], 
                decimals=2),
            '3mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-63]) / df_year[t]['Close'].iloc[-63], 
                decimals=2),
            '6mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-126]) / df_year[t]['Close'].iloc[-126], 
                decimals=2),
            '1yr': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[0]) / df_year[t]['Close'].iloc[0], 
                decimals=2),
            '50': np.around(df_year[t][-50:]['Close'].mean(), decimals=2),
            '200': np.around(df_year[t][-200:]['Close'].mean(), decimals=2),
        }

df_highs = pd.DataFrame.from_dict(data, orient='index').dropna(how='all')
df_highs['PctHigh'] = df_highs['Last']/df_highs['52High']
df_highs = df_highs.dropna(how='any')

df_highs = df_highs[df_highs['Last'].gt(20)]
df_highs = df_highs[df_highs['6mo'].gt(0)]
df_highs = df_highs[df_highs['1mo'].gt(0)]

df_quantile = df_highs['PctHigh'].quantile(q=[.5])
#print(df_quantile)

is_buy = df_highs['PctHigh'].gt(df_quantile.loc[0.5])
is_sell = df_highs['PctHigh'].lt(df_quantile.loc[0.5])
df_buy = df_highs[is_buy]
df_sell = df_highs[is_sell]

print('High Performing Stocks')
print(df_buy.sort_values('PctHigh', ascending=False))
df_buy.to_pickle('stocks/buy.pkl')
#print("Low Performaing Stocks")
#print(df_sell.sort_values('PctHigh', ascending=True))
df_sell.to_pickle('stocks/sell.pkl')
