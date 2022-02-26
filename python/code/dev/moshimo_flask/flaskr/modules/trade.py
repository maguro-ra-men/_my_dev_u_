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
        	b.status_f ="on" and b.rtype="{app_rtype}" and \
        	d.date between "{fdate}" and "{tdate}"\
            GROUP by a.ticker,d.date\
            order by a.ticker,d.date asc'
df_wlist = pd.read_sql_query(query, engine)
#不要？？ df_wlist=df_wlist.rename_axis('index') #indexに名前を付ける
#不要？？ df_wlist.to_csv(f'{rootpath}\\wlist.csv') 

#不要？？ from modules.cls.t_val import T_R_VAL
r=0 #あとで消す
for r in df_wlist.index:
    ticker = df_wlist.loc[r,'ticker']
    ex_rate = df_wlist.loc[r,'ex_rate']
    c_price = df_wlist.loc[r,'c_price']
    high_price = df_wlist.loc[r,'high_price']
    low_price = df_wlist.loc[r,'low_price']
    mov_avg = df_wlist.loc[r,'mov_avg']
    bb_highs = df_wlist.loc[r,'bb_highs']
    bb_lows = df_wlist.loc[r,'bb_lows']
    date = df_wlist.loc[r,'date']
    #out csv
    df=pd.DataFrame({
        'ticker': [f'{ticker}'], 'ex_rate': [f'{ex_rate}'],
        'c_price': [f'{c_price}'], 'high_price': [f'{high_price}'],
        'low_price': [f'{low_price}'], 'mov_avg': [f'{mov_avg}'],
        'bb_highs': [f'{bb_highs}'], 'bb_lows': [f'{bb_lows}'],
        'date': [f'{date}'],
        })
    df=df.rename_axis('index') #indexに名前を付ける
    df.to_csv(f'{rootpath}\\one_day_wlist.csv') 
    #get latest values
    list=TBL_VAL.tbl_trade_single(ticker)
    trade_id, trade_phase, trade_last_run_date, trade_end_of_turn = \
        list[0], list[1], list[2], list[3]    

    if not date == trade_last_run_date: #trade保持のdateが異なる？
        TBL_VAL.tbl_upd_trade_turn_start(ticker,date) #turn開始前にtrade idの3項目を更新。

    				


    #Trade stageへ
    if trade_phase == '1xxxxxxxxxxxxxxxxxxxxxx': #trade phase=1.buy初回約定？
        from modules.trade_stage_b import STAGE_B #trade phase=0.約定ナシ？
        STAGE_B.b()
    else:
        print('end::::phase1_STAGE_B')

    """ tradeが動く順番に作ろう
    if trade_phase == '2': #trade phase=2.sell初回約定？
        from modules.trade_stage_c import STAGE_C #trade phase=0.約定ナシ？
        STAGE_C.c()
    else:
        print('end::::phase2_STAGE_C')
    """
    if trade_phase == '0': #trade phase=0.約定ナシ？
        from modules.trade_stage_a import STAGE_A
        STAGE_A.a()
    else:
        print('end::::phase0_STAGE_A')
print(f'end::::trade date is {date}')
    