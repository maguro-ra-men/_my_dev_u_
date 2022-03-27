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
from modules.variable import app_drange,app_rtype#,fdate,tdate

import pandas as pd
from sqlalchemy.sql import text
import string
import datetime
import random

#debugのためにtableを掃除
"""
delete
"""
#id指定系
table='`trade`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()
query=text(f'ALTER TABLE {table} auto_increment = 1;')
session.execute(query)
session.commit()

table='`fund`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()
query=text(f'ALTER TABLE {table} auto_increment = 1;')
session.execute(query)
session.commit()

#全レコード
table='`order`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()
query=text(f'ALTER TABLE {table} auto_increment = 1;')
session.execute(query)
session.commit()

table='`execution`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()
query=text(f'ALTER TABLE {table} auto_increment = 1;')
session.execute(query)
session.commit()

table='`trade_results`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()
query=text(f'ALTER TABLE {table} auto_increment = 1;')
session.execute(query)
session.commit()


"""
master tickersからticker取得
"""
query=f'select id, ticker\
    from tickers\
    order by id asc;'
df = pd.read_sql_query(query, engine)

"""
create trade,fund
"""
for r in df.index:
    ticker = df.loc[r,'ticker']
    i = df.loc[r,'id']
    #tbl_ins_trade
    query=text(f'insert into `trade` (id, rtype, phase, status, \
        ticker, logic_ver) \
        values({i}, "simu",  "0", "on", \
        "{ticker}", "1");')
    session.execute(query)
    session.commit()

    #tbl_ins_fund
    query=text(f'insert into `fund` (trade_id, rtype, \
                ticker, status_f, residual_funds, update_diff_funds) \
        values({i}, "simu", "{ticker}",  \
        "on", 1000000, 0 );')
    session.execute(query)
    session.commit()


