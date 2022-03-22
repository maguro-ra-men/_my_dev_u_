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

"""
rtype
起動programのrtypeのみを更新
"""
"""
drange設定
このスコアリングは past6month で固定。
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
tmp_tdate=reference_date
tmp_fdate = tdate.replace(day=1) + relativedelta(months=-7)


"""
スコアリング開始
"""
#最新のtrade_resultsを取得
query=f'select tr.ticker,t.rtype,avg(roi) as roi_avg ,\
        sum(start_funds) as start_funds_sum,\
	    sum(last_funds) as last_funds_sum,\
        sum(realized_gain_and_loss) as realized_gain_and_loss_sum\
    from trade_results tr \
    left join trade t ON (t.id  = tr.trade_id)\
    where t.start_run_date  between "{tmp_fdate}" and "{tmp_tdate}" and \
        t.rtype="{app_rtype}"\
    group by ticker \
    order by avg(roi)  desc;'
df = pd.read_sql_query(query, engine)

df=df.rename_axis('index') #indexに名前を付ける
#df= df.reset_index() #add index（ここで加えないとdateのdateの変更が不可の為）

#raw整形：カラム追加
df=df.assign(score=None) 

#score判定、記入
for r,ticker in enumerate(df.ticker):
    reference_value = 0.22
    scr_edit = 0
    roi_avg = df.loc[r,'roi_avg']
    if scr_edit == 0 and roi_avg >= (reference_value * 1):
        df.loc[r,'score']=10
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.9):
        df.loc[r,'score']=9
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.8):
        df.loc[r,'score']=8
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.7):
        df.loc[r,'score']=7
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.6):
        df.loc[r,'score']=6
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.5):
        df.loc[r,'score']=5
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.4):
        df.loc[r,'score']=4
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.3):
        df.loc[r,'score']=3
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.2):
        df.loc[r,'score']=2
        scr_edit = 1
    if scr_edit == 0 and roi_avg >= (reference_value * 0.1):
        df.loc[r,'score']=1
        scr_edit = 1

df = df.sort_values(['score'], ascending=False) #sort DESC

#delete rtype指定
table='`scr_sort_results_roi`'
query=text(f'DELETE FROM {table} where rtype = "{app_rtype}";')
session.execute(query)
session.commit()

#table insert(df to table)
df.to_sql('scr_sort_results_roi', engine, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
#pd.read_sql('SELECT * FROM scr_sort_results_roi', engine) #確認


print(f'end::::scr_sort_results_roi')    