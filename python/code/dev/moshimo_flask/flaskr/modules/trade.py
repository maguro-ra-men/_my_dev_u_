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
from modules.variable import app_drange,app_rtype,fdate,tdate
from modules.cls.tbl_val import TBL_VAL

import pandas as pd

"""
df_wlistを作成
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
            GROUP by a.ticker,d.date\
            order by a.ticker,d.date asc'
df_wlist = pd.read_sql_query(query, engine)
#不要？？ df_wlist=df_wlist.rename_axis('index') #indexに名前を付ける
#不要？？ df_wlist.to_csv(f'{rootpath}\\wlist.csv') 

#不要？？ from modules.cls.t_val import T_R_VAL

for r in df_wlist.index:
    #不要？？ ex_rate = T_R_VAL(r).ex_rate
    #不要？？ c_price = T_R_VAL(r).c_price
    ex_rate = df_wlist.loc[r,'ex_rate']
    c_price = df_wlist.loc[r,'c_price']
    high_price = df_wlist.loc[r,'high_price']
    low_price = df_wlist.loc[r,'low_price']
    mov_avg = df_wlist.loc[r,'mov_avg']
    bb_highs = df_wlist.loc[r,'bb_highs']
    bb_lows = df_wlist.loc[r,'bb_lows']
    ticker = df_wlist.loc[r,'ticker']
    trade_id = TBL_VAL.tbl_trade_id(ticker)
    trade_phase = TBL_VAL.tbl_trade_phase(ticker)

    if trade_phase == '1' or trade_phase == '1a':
        from modules.t_stage_a import * #trade phase=1.buy初回約定？
    else:
        print('end:phase1')

    if trade_phase == '2' or trade_phase == '2a':
        from modules.t_stage_b import * #trade phase=2.sell初回約定？
    else:
        print('end:phase2')

    if trade_phase == '0':
        from modules.t_stage_c import * #trade phase=0.約定ナシ？
    else:
        print('end:phase0')
    
    