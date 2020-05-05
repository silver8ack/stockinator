import yfinance as yf
import requests
import csv

urls = {
    'nasdaq': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
    'nyse': 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
}

line_list = []
for exchange, url in urls.items():
    resp = requests.get(url)
    lines = resp.text.split(',\r\n')

    for l in lines:
        split_line = l.split('","')
        trimmed_line = []
        for t in split_line:
            trimmed_line.append(t.replace('"', ''))
        line_list.append(trimmed_line)

columns = line_list.pop(0)





df = pd.DataFrame(line_list, columns=columns)

df = pd.read_pickle('stocks/all_1d.pkl')
df_year = df.iloc[-252:]
df_diff = df_year.dropna(thresh=600).diff()

tickers = st.unique_list([x[0] for x in df_year.columns.values])
data = {}
for t in tickers:
    if df_year[t]['Close'].iloc[-1] > 20:
        data[t] = {
            '52High': np.around(df_year[t]['High'].max(), decimals=4),
            'Last': np.around(df_year[t]['Close'].iloc[-1], decimals=4),
            '10d': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-10]) / df_year[t]['Close'].iloc[-10], 
                decimals=4),
            '1mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-21]) / df_year[t]['Close'].iloc[-21], 
                decimals=4),
            '2mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-42]) / df_year[t]['Close'].iloc[-42], 
                decimals=4),
            '3mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-63]) / df_year[t]['Close'].iloc[-63], 
                decimals=4),
            '6mo': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[-126]) / df_year[t]['Close'].iloc[-126], 
                decimals=4),
            '1yr': np.around(
                (df_year[t]['Close'].iloc[-1] - df_year[t]['Close'].iloc[0]) / df_year[t]['Close'].iloc[0], 
                decimals=4)
        }

df_highs = pd.DataFrame.from_dict(data, orient='index').dropna(how='all')
df_highs['PctHigh'] = df_highs['Last']/df_highs['52High']
df_highs = df_highs.dropna(how='any')

df_highs = df_highs[df_highs['Last'].gt(20)]
df_highs = df_highs[df_highs['6mo'].gt(0)]
df_highs = df_highs[df_highs['1mo'].gt(0)]

df_quantile = df_highs['PctHigh'].quantile(q=[.2, .4, .6, .8])
#print(df_quantile)

is_buy = df_highs['PctHigh'].gt(df_quantile.loc[0.6])
is_sell = df_highs['PctHigh'].lt(df_quantile.loc[0.2])
df_buy = df_highs[is_buy]
df_sell = df_highs[is_sell]

print('High Performing Stocks')
print(df_buy.sort_values('PctHigh', ascending=False))
df_buy.to_pickle('stocks/buy.pkl')
#print("Low Performaing Stocks")
#print(df_sell.sort_values('PctHigh', ascending=True))
df_sell.to_pickle('stocks/sell.pkl')