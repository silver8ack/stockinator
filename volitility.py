import stockinator as st
import pandas as pd

t = {
    'VIX9D': {}, 
    'VIX': {}, 
    'VIX3M': {}, 
    'VIX6M': {}, 
    'VIX1Y': {}
}

for k, v in t.items():
    t[k] = st.get_stock_data([f"^{k}"], period='1d', interval='1d')


df = pd.DataFrame(
    columns=['Short', 'Mid', 'Long'])

df = df.append({
        'Short': t['VIX9D']['Close'][-1]/t['VIX']['Close'][-1] * 100,
        'Mid': t['VIX']['Close'][-1]/t['VIX3M']['Close'][-1] * 100,
        'Long': t['VIX3M']['Close'][-1]/t['VIX1Y']['Close'][-1] * 100
    }, ignore_index=True)

print(df)

tickers = ['^VIX9D', '^VIX', '^VIX3M', '^VIX6M', '^VIX1Y']
df = st.get_stock_data(tickers, period='1d', interval='1d')
print(df)