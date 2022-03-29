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
前工程でdfにstock pricesがある状態。
元は降順だが、今回の判定の為、昇順にする

【!!!】組み込み前なのでDBからクエリ
【!!!】ソートは重要。date ascにした場合、複数tickでばらつく。そうすると後工程で
    特定tickの数が減っていってしまう。CWEB140が5になった。
    ticker,date asc にすべし
"""
query=f'select * \
        from stock_prices \
        order by ticker,date asc;'
df = pd.read_sql_query(query, engine)

"""
df_wlist作成
"""
#tarade status on ,rtype=変数かつfundありのtickerをdf_wlistへ
query=f'select a.ticker \
        from `trade` as a \
        left join fund as b ON (a.id  = b.trade_id)\
        left join tickers as c ON (a.ticker  = c.ticker)\
        where a.status="on" and a.rtype="{app_rtype}" and \
        b.status_f ="on" and b.rtype="{app_rtype}"\
        GROUP by c.ticker '
df_wlist = pd.read_sql_query(query, engine)
if df_wlist.empty:
    logger.error(f'error:No valid trade and fund')
    sys.exit('error:')

#ここからコピペかな wlistあればいける
#用済みならこのpyは消す


"""
Tech chart追加(RSI)
"""
"""
前工程でdfにstock pricesがある状態。
元は降順だが、RSI判定の為、昇順に変更。
【!!!】ソートは重要。複数tickでdate ascにした場合、dateぐちゃる。そうすると後工程で
    レコード削除、unionがうまくできず、特定tickの数が減っていってしまう。
    CWEB140件が5件になった（恐怖）
    ticker,date asc にすべし
"""
df = df.sort_values(['ticker','date'], ascending=True) #sort trueがasc

"""
tickerごとに処理。RSI等の指標を追加
"""
#add columns
df=df.assign(b_rsi=0,
    b_sma_rsi=0,
    b_rate_rsi_sma=0,
    score_drop_warn=0,
    danger_drop_warn=0
    ) 

#tickerごとに処理
dfraw=df #全データを別変数に入れて保護
for r in df_wlist.index:
    df,df_temp='',''
    ticker = df_wlist.loc[r,'ticker']
    df=dfraw.query(f'ticker == "{ticker}"')
    #ここからticker単位の計算、列追加

    df= df.reset_index(drop=True) #add index（振り直し）旧index削除

    """
    Add rsi.一般的なRSIではなく、下落予兆が出やすいtradingview独自の計算を利用。
    https://github.com/lukaszbinden/rsi_tradingview/blob/main/rsi.py
    """
    def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True) -> pd.Series:
        delta = pd.Series(ohlc['close'].diff())
        print(delta)#あとでけす
        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1/period).mean()

        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1/period).mean()

        rsi = np.where(up == 0, 0, 
            np.where(down == 0, 100, 
            100 - (100 / (1 + up / down))))
        print(rsi)#あとでけす

        return np.round(rsi, 2) if round_rsi else rsi

    #series変数にRSI投入
    period = 14
    series = rsi_tradingview(df,period,'true')
    series = pd.Series(data=series,name=f'b_rsi')

    #dfへseriesの値を書き込み
    df['b_rsi'] = series.values
    #df = pd.concat([df, series], axis=1, join='inner') 追加カラムになっちゃう
    
    """
    Add sma.これもTrading viewと同じくRSI14からSMA14を算出
    """
    def sma(ohlc: pd.DataFrame, period=14) -> pd.Series:
        return pd.Series(ohlc['b_rsi'].rolling(period).mean(),
            name=f'b_sma_rsi',)

    #series変数にRSI投入
    series=sma(df,14)
    series=np.round(series, 2)
    #dfへseriesの値を書き込み
    df['b_sma_rsi'] = series.values

    #割り算追加
    df['b_rate_rsi_sma'] = np.round(df['b_rsi'] / df['b_sma_rsi'],2)



    #ここから新dfへまとめていく
    #不要レコードをdfから削除
    rows_to_drop = dfraw.index[dfraw["ticker"] == ticker]#行を定義
    dfraw = dfraw.drop(rows_to_drop)#dfから定義した行を削除
    #最下部に追加
    dfraw=dfraw.append(df) #union

    #debug用
    print((dfraw['id'] > 1).sum())#debug用カウント 全体
    print(dfraw['ticker'].str.endswith('CWEB').sum())#debug用カウント CWEB
    #dfraw.to_csv(f'{rootpath}\\test.csv')             #テスト用　あとでけす

"""
loop後(RSI)
"""
df = dfraw
#データ整形
df = df.sort_values(['ticker','date'], ascending=False) #sort DESC
df= df.reset_index(drop=True) #add index（振り直し）旧index削除

#df.to_csv(f'{rootpath}\\test.csv')             #テスト用　あとでけす
