import pandas as pd
import numpy as np
import stockinator as st

if __name__ == '__main__':
    df = pd.read_pickle('stocks/sp500_1d.pkl')
    df_year = df.iloc[-252:]
    df_diff = df_year.dropna(thresh=600).diff()

    tickers = st.unique_list([x[0] for x in df_year.columns.values])
    data = {}
    for t in tickers:
        data[t] = {
            '52High': np.around(df_year[t]['High'].max(), decimals=4),
            'Last': np.around(df_year[t]['Close'].iloc[-1], decimals=4)
        }

    df_highs = pd.DataFrame.from_dict(data, orient='index').dropna(how='all')
    df_highs['PctHigh'] = df_highs['Last']/df_highs['52High']

    #print(df_highs)
    df_quantile = df_highs['PctHigh'].quantile(q=[.1, .9])
    #print(df_quantile)

    is_buy = df_highs['PctHigh'].gt(df_quantile.loc[0.9])
    is_sell = df_highs['PctHigh'].lt(df_quantile.loc[0.1])
    df_buy = df_highs[is_buy]
    df_sell = df_highs[is_sell]

    print(df_buy.sort_values('PctHigh', ascending=False))
    print(df_buy.describe())