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
スコアリング開始 scr_ttl_suitable_logic
配分
ssrr.score * 0.7 + sstf.score * 0.3
"""
query=f'select ssrr.ticker,ssrr.rtype,\
    round(ssrr.score * 0.7 + sstf.score * 0.3) as total_score,\
    ssrr.score as ssrr_score, sstf.score as sstf_score\
    from scr_sort_results_roi ssrr \
    left join scr_sort_trade_freq sstf on \
        (sstf.ticker = ssrr.ticker and sstf.rtype = ssrr.rtype)\
    group by ticker\
    order by total_score desc ;'
df = pd.read_sql_query(query, engine)

df=df.rename_axis('index') #indexに名前を付ける
#df= df.reset_index() #add index（ここで加えないとdateのdateの変更が不可の為）

#delete rtype指定
table='`scr_ttl_suitable_logic`'
query=text(f'DELETE FROM {table} where rtype = "{app_rtype}";')
session.execute(query)
session.commit()

#table insert(df to table)
df.to_sql('scr_ttl_suitable_logic', engine, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
#pd.read_sql('SELECT * FROM scr_sort_trade_freq', engine) #確認

"""
スコアリング開始 scr_ttl_best_time_to_buy
"""

"""
スコアリング開始 scr_ttl_all_combine_four
"""

print(f'end::::scr_total')    