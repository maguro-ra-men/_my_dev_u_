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
update
"""
#upd trade
for i in range(1,6):#最後は1つ多くする。最後は無視される
    trade_id=i
    query=text(f'UPDATE trade \
        SET initial_fund_id=null, phase="0", status="on", \
            cnt_run_date=null, end_of_turn=null\
        WHERE id={trade_id};')
    session.execute(query)
    session.commit()

#upd fund
for i in range(1,6):#最後は1つ多くする。最後は無視される
    fund_id=i
    query=text(f'UPDATE `fund` \
        SET status_f="on", run_date_f=null\
        WHERE id={fund_id};')
    session.execute(query)
    session.commit()


"""
delete
"""
#id指定系
table='`trade`'
query=text(f'DELETE FROM {table} where id >= 6;')
session.execute(query)
session.commit()

table='`fund`'
query=text(f'DELETE FROM {table} where id >= 6;')
session.execute(query)
session.commit()

#全レコード
table='`order`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()

table='`execution`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()

table='`trade_results`'
query=text(f'DELETE FROM {table};')
session.execute(query)
session.commit()

