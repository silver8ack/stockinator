import pandas as pd
import requests
import csv
import stockinator as st

if __name__ == '__main__':
    urls = [
        'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
        'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
    ]

    line_list = []
    for url in urls:
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

    periods = ['1d']
    for p in periods:
        data = st.get_stock_data(list(df['Symbol'].values) + ['SPX', 'VIX'], period='3y', interval=p)
        data.to_pickle(f"stocks/nyse_{p}.pkl")
