#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import logging
from conf.logger_conf import * #my module

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype,fdate,tdate

import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta


"""

"""
#
query=f'select * \
        from stock_prices \
        where ticker="SOXL"\
        order by date asc;'
df = pd.read_sql_query(query, engine)
list(df.index)
df.set_index("date", inplace=True)


"""
MatplotlibでOHLC作成
https://ichi.pro/python-trading-toolbox-matplotlib-de-ohlc-cha-to-o-donyu-164602670864200
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Loading data into dataframe:
datafile = df
data = df
# Converting the dates from string to datetime format:

#####data.index = df['date']

# We need to exctract the OHLC prices into a list of lists:
dvalues = data[['open', 'high', 'low', 'close']].values.tolist()

# Dates in our index column are in datetime format, we need to comvert them 
# to Matplotlib date format (see https://matplotlib.org/3.1.1/api/dates_api.html):
pdates = mdates.date2num(data.index)

# If dates in our index column are strings instead of datetime objects, we should use:
# pdates = mpl.dates.datestr2num(data.index)

# We prepare a list of lists where each single list is a [date, open, high, low, close] sequence:
ohlc = [ [pdates[i]] + dvalues[i] for i in range(len(pdates)) ]
print(ohlc)





"""
rsi_tradingview
https://github.com/lukaszbinden/rsi_tradingview/blob/main/rsi.py
"""
""" Implements the RSI indicator as defined by TradingView on March 15, 2021.
The TradingView code is as follows:
//@version=4
study(title="Relative Strength Index", shorttitle="RSI", format=format.price, precision=2, resolution="")
len = input(14, minval=1, title="Length")
src = input(close, "Source", type = input.source)
up = rma(max(change(src), 0), len)
down = rma(-min(change(src), 0), len)
rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
plot(rsi, "RSI", color=#8E1599)
band1 = hline(70, "Upper Band", color=#C0C0C0)
band0 = hline(30, "Lower Band", color=#C0C0C0)
fill(band1, band0, color=#9915FF, transp=90, title="Background")
:param ohlc:
:param period:
:param round_rsi:
:return: an array with the RSI indicator values
"""
123

def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True) -> pd.Series:
    print(123)

    test = pd.Series(ohlc['close'].rolling(period).mean(),
        name=f'testt {period}',
        )
    delta = pd.Series(ohlc['close'].diff())
    print(delta)
    up = delta.copy()
    up[up < 0] = 0
    up = pd.Series.ewm(up, alpha=1/period).mean()

    down = delta.copy()
    down[down > 0] = 0
    down *= -1
    down = pd.Series.ewm(down, alpha=1/period).mean()

    rsi = np.where(up == 0, 0, \
        np.where(down == 0, 100, \
        100 - (100 / (1 + up / down))))
    print(rsi)

    return np.round(rsi, 2) if round_rsi else rsi

test_rsi=rsi_tradingview(df,14,'true')
print(test_rsi)
"""
smaでテスト出来た
"""
def sma(ohlc: pd.DataFrame, period=21) -> pd.Series:
    return pd.Series(ohlc['close'].rolling(period).mean(),
        name=f'SMA {period}',)

test_sma=sma(df,14)
print(test_sma)

#以下描画
import mpl_finance as mpf # This is the old mpl-finance library - note the '_' in the library name
# We can now feed the ohlc matrix into mpl-finance to create a candle stick chart:
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots(figsize = (12,6))
mpf.plot_day_summary_ohlc(ax, ohlc[-50:], ticksize = 5)
ax.set_xlabel('date')
ax.set_ylabel('close ($)')
ax.set_title('test SOXL ETF Trust - Bar Chart')
# Choosing to display the dates as "Month Day":
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
# This is to automatically arrange the date labels in a readable way:
fig.autofmt_xdate()
# plt.show() # add this if you're not using Jupyter Notebook



dfa = pd.DataFrame({'YYYY-MM-DD':data, 'open':open, 'high':high, 'low':low, 'close':close})
 
