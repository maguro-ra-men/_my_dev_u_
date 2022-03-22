#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys

from sqlalchemy import null
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import logging
from conf.logger_conf import * #my module

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype,fdate,tdate
from modules.variable import *
from modules.cls.tbl_val import TBL_VAL

import pandas as pd
from sqlalchemy.sql import text
import string
import datetime
from datetime import date,timedelta
"""
rtype
このスコアは区別ナシ。チャート情報のみで構成。
"""
"""
drange設定
このスコアリングは latest 1 day で固定。
"""
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta #～日後、ヶ月後を算出可能なライブラリ

#jst0を跨ぐと日付変更してしまう為、実行日固定させる
tmp_date = datetime.datetime.now()
hour = tmp_date.hour
reference_date = datetime.date.today()

#日付変わった時間？
if 0 <= hour <= 21:
    # 日を求める timedelta
    td = timedelta(days=1)
    #前日を代入
    reference_date = reference_date - td

#global変数を定義
tmp_tdate = reference_date
tmp_fdate = reference_date


"""
スコアリング開始
"""
#dateは1日なので市場非開催=noneなら過去dateを取得する
for i in range(10):
    query=f'select ticker,date,`close` ,a_ema20close ,a_bb20low ,a_bb20high \
        from stock_prices\
        where date  between "{tmp_fdate}" and "{tmp_tdate}"\
        group by ticker,date \
        order by ticker asc ;'
    df = pd.read_sql_query(query, engine)
    if not df.empty:
        break
    else:
        # 日を求める timedelta
        td = timedelta(days=i)
        #前日を代入
        reference_date = reference_date - td
        tmp_tdate = reference_date
        tmp_fdate = reference_date


df=df.rename_axis('index') #indexに名前を付ける
#df= df.reset_index() #add index（ここで加えないとdateのdateの変更が不可の為）

#raw整形：カラム追加
df=df.assign(score=None) 

#score判定、記入
for r,ticker in enumerate(df.ticker):
    scr_edit = 0
    close = df.loc[r,'close']
    a_ema20close = df.loc[r,'a_ema20close']
    a_bb20low = df.loc[r,'a_bb20low']
    a_bb20high = df.loc[r,'a_bb20high']
    if scr_edit == 0 and close <= a_bb20low:
        df.loc[r,'score']=10
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.15)+a_bb20low:
        df.loc[r,'score']=9
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.3)+a_bb20low:
        df.loc[r,'score']=8
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.50)+a_bb20low:
        df.loc[r,'score']=7
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.7)+a_bb20low:
        df.loc[r,'score']=6
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.8)+a_bb20low:
        df.loc[r,'score']=5
        scr_edit = 1
    if scr_edit == 0 and close <= ((a_ema20close - a_bb20low)*0.9)+a_bb20low:
        df.loc[r,'score']=4
        scr_edit = 1
    if scr_edit == 0 and  close > a_ema20close and \
            close < a_bb20high-((a_bb20high-a_ema20close)/2):
        df.loc[r,'score']=3
        scr_edit = 1
    if scr_edit == 0 and  close > a_ema20close+((a_bb20high-a_ema20close)/2) and \
            close < a_bb20high:
        df.loc[r,'score']=2
        scr_edit = 1
    if scr_edit == 0 and close >= a_bb20high:
        df.loc[r,'score']=1
        scr_edit = 1

df = df.sort_values(['score'], ascending=False) #sort DESC

#delete 全レコード
table='`scr_entry_bb_low`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()

#table insert(df to table)
df.to_sql('scr_entry_bb_low', engine, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
#pd.read_sql('SELECT * FROM scr_entry_bb_low', engine) #確認


print(f'end::::scr_entry_bb_low')