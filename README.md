```python
import yfinance as yf
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)
```


```python
balance = 10000
tickers = ['SPY', 'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU']
etfs = {}
for ticker in tickers:
    stock = yf.Ticker(ticker)
    etfs[ticker] = {}
    etfs[ticker]['info'] = stock.info
    h = stock.history(period='10y', interval='1mo')
    h['Change'] = h['Close'] - h['Open']
    h['%Change'] = h['Change'] / h['Open'] * 100
    etfs[ticker]['history'] = h
```


```python
data = pd.DataFrame()
for ticker in tickers:
    df = etfs[ticker]['history']
    df = df[df['%Change'].notnull()]
    data[ticker] = df['%Change']

data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>SPY</th>
      <th>VOX</th>
      <th>VCR</th>
      <th>VDC</th>
      <th>VDE</th>
      <th>VFH</th>
      <th>VHT</th>
      <th>VIS</th>
      <th>VGT</th>
      <th>VAW</th>
      <th>VNQ</th>
      <th>VPU</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2010-05-01</th>
      <td>-8.383725</td>
      <td>-4.794683</td>
      <td>-7.709520</td>
      <td>-5.041860</td>
      <td>-12.367388</td>
      <td>-9.562044</td>
      <td>-7.199832</td>
      <td>-9.408974</td>
      <td>-8.200234</td>
      <td>-9.544837</td>
      <td>-6.136878</td>
      <td>-6.009144</td>
    </tr>
    <tr>
      <th>2010-06-01</th>
      <td>-4.742547</td>
      <td>-1.478326</td>
      <td>-8.804469</td>
      <td>-1.623120</td>
      <td>-4.535528</td>
      <td>-5.791191</td>
      <td>-0.482870</td>
      <td>-5.977062</td>
      <td>-5.544851</td>
      <td>-6.884127</td>
      <td>-4.825901</td>
      <td>-1.257862</td>
    </tr>
    <tr>
      <th>2010-07-01</th>
      <td>6.894109</td>
      <td>9.211196</td>
      <td>8.118715</td>
      <td>6.447713</td>
      <td>7.891037</td>
      <td>7.130510</td>
      <td>0.830641</td>
      <td>9.974184</td>
      <td>7.110507</td>
      <td>12.046474</td>
      <td>9.498094</td>
      <td>7.559092</td>
    </tr>
    <tr>
      <th>2010-08-01</th>
      <td>-5.969338</td>
      <td>-2.007383</td>
      <td>-6.189944</td>
      <td>-2.682927</td>
      <td>-6.399617</td>
      <td>-8.942766</td>
      <td>-3.276836</td>
      <td>-8.416156</td>
      <td>-8.061821</td>
      <td>-4.055266</td>
      <td>-2.854696</td>
      <td>-0.386183</td>
    </tr>
    <tr>
      <th>2010-09-01</th>
      <td>6.925271</td>
      <td>7.988853</td>
      <td>10.930889</td>
      <td>4.605138</td>
      <td>8.470588</td>
      <td>4.780362</td>
      <td>8.300669</td>
      <td>10.195721</td>
      <td>11.111111</td>
      <td>7.091413</td>
      <td>2.352599</td>
      <td>0.956633</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2020-01-01</th>
      <td>-0.559614</td>
      <td>0.053056</td>
      <td>0.477891</td>
      <td>-0.789016</td>
      <td>-12.289395</td>
      <td>-2.773761</td>
      <td>-2.915604</td>
      <td>-1.175706</td>
      <td>2.885006</td>
      <td>-6.965471</td>
      <td>0.789445</td>
      <td>5.905512</td>
    </tr>
    <tr>
      <th>2020-02-01</th>
      <td>-8.377403</td>
      <td>-6.385441</td>
      <td>-8.073404</td>
      <td>-8.413957</td>
      <td>-14.847285</td>
      <td>-11.672942</td>
      <td>-6.816607</td>
      <td>-9.532857</td>
      <td>-7.389435</td>
      <td>-9.417398</td>
      <td>-6.977992</td>
      <td>-10.216513</td>
    </tr>
    <tr>
      <th>2020-03-01</th>
      <td>-13.569670</td>
      <td>-15.271430</td>
      <td>-18.234100</td>
      <td>-6.778510</td>
      <td>-38.399869</td>
      <td>-23.477601</td>
      <td>-5.633723</td>
      <td>-20.995032</td>
      <td>-11.482010</td>
      <td>-16.232062</td>
      <td>-20.305853</td>
      <td>-10.675317</td>
    </tr>
    <tr>
      <th>2020-04-01</th>
      <td>12.549399</td>
      <td>11.405405</td>
      <td>18.713367</td>
      <td>10.563275</td>
      <td>19.541779</td>
      <td>7.503100</td>
      <td>15.000000</td>
      <td>7.031842</td>
      <td>12.545153</td>
      <td>12.048976</td>
      <td>9.833108</td>
      <td>10.178312</td>
    </tr>
    <tr>
      <th>2020-04-23</th>
      <td>-0.502692</td>
      <td>0.374215</td>
      <td>-0.394808</td>
      <td>-0.661939</td>
      <td>0.174978</td>
      <td>-0.498180</td>
      <td>-0.080326</td>
      <td>0.175670</td>
      <td>-0.757150</td>
      <td>0.249832</td>
      <td>-1.132797</td>
      <td>-1.776336</td>
    </tr>
  </tbody>
</table>
<p>121 rows × 12 columns</p>
</div>




```python
data.idxmin(axis=1)
```




    Date
    2010-05-01    VDE
    2010-06-01    VCR
    2010-07-01    VHT
    2010-08-01    VFH
    2010-09-01    VPU
                 ... 
    2020-01-01    VDE
    2020-02-01    VDE
    2020-03-01    VDE
    2020-04-01    VIS
    2020-04-23    VPU
    Length: 121, dtype: object




```python

```


```python

```
