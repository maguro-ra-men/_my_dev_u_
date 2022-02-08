#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
from conf.logger_conf import *
logger = getLogger(__name__)

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype

import pandas as pd

"""
date rangeの確定
"""
#app_drangeからgetする期間判定//tech chart算出の為、実際期間+21日必要。ざっくり多めに取る
import datetime
from dateutil.relativedelta import relativedelta #～日後、ヶ月後を算出可能なライブラリ
if app_drange=='past6month':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-7)
elif app_drange=='today':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-1)

"""
df_wlistを作成

{tdate}
{fdate}
{app_rtype}
"""

#tarade status on ,rtype=変数かつfundありのtickerをdf_wlistへ
query=f'select a.ticker, d.date, e.close as ex_rate, d.close as c_price,\
	d.high as high_price, d.low as low_price,\
	d.a_ema20close as	mov_avg, d.a_bb20high as bb_highs, d.a_bb20low as bb_lows \
        from `trade` as a \
        left join fund as b ON (a.id  = b.trade_id)\
        left join tickers as c ON (a.ticker  = c.ticker)\
        left join stock_prices as d on (a.ticker = d.ticker)\
        left join currency as e on (c.currency = e.currency and d.date = e.date)\
        where a.status="on" and a.rtype="{app_rtype}" and \
        	b.status ="on" and b.rtype="{app_rtype}" and \
        	d.date between "{fdate}" and "{tdate}"\
            GROUP by a.ticker,d.date '
df_wlist = pd.read_sql_query(query, engine)

