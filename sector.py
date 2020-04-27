import stockinator as st
import pandas as pd

data = pd.read_pickle('stocks/sectors.pkl')
periods = [144, 55, 21]

df_perf = st.get_period_performance(data, periods=periods, offset=0, weight=periods[-1])
print(df_perf.sort_values('TotalWeight', ascending=False))