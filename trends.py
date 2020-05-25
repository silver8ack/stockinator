import sys
import multiprocessing as mp
import pandas as pd
import stockinator as st
from multiprocessing.dummy import Pool as ThreadPool

def trending(df_tuple):
    sys.stdout.write(f"Processing Stock: {df_tuple[0]} \r")
    sys.stdout.flush()
    df = df_tuple[1].dropna(how='all')
    if df.empty:
        return

    if df['Close'][-1] < 5:
        return

    df = st.dmi(df)
    if df['ADX'][-1] > 50:
        return (df_tuple[0], df)

if __name__ == '__main__':
    # Setup multiprocessing
    manager = mp.Manager()
    max_processes = (mp.cpu_count() * 2) - 1
    pool = mp.Pool(processes=max_processes)
    mlist = manager.list()
    
    # Get dataframe and list of symbols
    df = pd.read_pickle('stocks/all_1d.pkl')
    stocklist = st.unique_list([x[0] for x in df.columns.values])
    total_stocks = len(stocklist)
    stock_dfs = []
    for stock in stocklist:
        stock_dfs.append((stock, df[stock]))

    print(f"Creating threadpool with {max_processes} threads.")
    tp = ThreadPool(max_processes)
    #data = pool.map(trending, stock_dfs)
    data = tp.map(trending, stock_dfs)
    #pool.close()
    tp.close()
    tp.join()
    for d in data:
        if not d is None:
            print(d)
    

    

