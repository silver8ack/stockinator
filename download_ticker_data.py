import os
import sys
import yfinance as yf

def get_stock_data(tickers, start=None, end=None, interval='1d', period=None):
    return yf.download(
        tickers=' '.join(tickers),
        start=start,
        end=end,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=True,
        threads=True
    )

if __name__ == '__main__':
    tickers = [
        'SPY', 'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 
        'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU',
    ]

    data = get_stock_data(tickers, period='10y', interval='1d')
    data.to_pickle('stocks/sectors.pkl')