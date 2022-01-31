#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from sqlite3 import Cursor
import sys

from numpy import empty
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
from conf.logger_conf import *
logger = getLogger(__name__)


#2.Check duplicate data.
from modules.db import *
from batch.run_s_6m import drange,app_rtype

import pandas as pd
num_of_error=0
check='config logic_verが2以上？' #title------------------------------
query='select logic_ver,count(logic_ver) \
    from config GROUP by logic_ver having COUNT(logic_ver) > 1'
df = pd.read_sql_query(query, engine)
if df.empty==False:
    logger.error(f'2.Check duplicate data/error:{check}')
    num_of_error=num_of_error+1

check='stock_pricesのticker,dateが2以上？' #title------------------------------
query='select ticker ,date,count(*) from stock_prices \
    GROUP by ticker ,date having COUNT(*) > 1'
df = pd.read_sql_query(query, engine)
if df.empty==False:
    logger.error(f'2.Check duplicate data/error:{check}')
    num_of_error=num_of_error+1

check='tarade status on ,rtype=変数のtickerが2以上？' #title------------------------------
query=f'select status ,rtype ,ticker_id ,count(*) from trade \
    where status="on" and rtype="{app_rtype}" GROUP by ticker_id  ,rtype,ticker_id \
    having COUNT(*) > 1'
df = pd.read_sql_query(query, engine)
if df.empty==False:
    logger.error(f'2.Check duplicate data/error:{check}')
    num_of_error=num_of_error+1

check='tarade status on ,rtype=変数のtickerとorder status onが2以上？' #title------------------------------
query=f'select a.status ,rtype ,ticker_id ,count(*),b.status\
    from `trade` as a\
    left join `order` as b \
    ON (a.id  = b.trade_id)\
    where a.status="on" and a.rtype="simu" and b.status ="on"\
    GROUP by a.status, a.rtype, a.ticker_id, b.status\
    having COUNT(*) > 1'
df = pd.read_sql_query(query, engine)
if df.empty==False:
    logger.error(f'2.Check duplicate data/error:{check}')
    num_of_error=num_of_error+1



print('end')
"""
tarade status on ,rtype=変数のtickerとfund status onが2以上
tarade status on ,rtype=変数のtickerとexe holdが2以上
tarade status on ,rtype=変数のtickerとtrade_resultsが2以上
"""




def check_results():
    return num_of_error