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
from modules.variable import app_drange,app_rtype#,fdate,tdate

import pandas as pd

class TBL_VAL():
    """
    def __init__(self,ticker,trade_id=None,trade_phase=None):
        self.trade_id = trade_id
        self.trade_phase = trade_phase
        self.ticker = ticker
    """

    #def trv(self,ticker):
    #        self.ticker = ticker

    def tbl_trade_id(ticker):
        query=f'select a.id, a.ticker, a.phase, a.todays_trade\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_id = df.loc[0,'id']
        return trade_id

    def tbl_trade_phase(ticker):
        query=f'select a.id, a.ticker, a.phase, a.todays_trade\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_phase = df.loc[0,'phase']
        return trade_phase

    def tbl_trade_todays_trade(ticker):
        query=f'select a.id, a.ticker, a.phase, a.todays_trade\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_todays_trade = df.loc[0,'todays_trade']
        return trade_todays_trade


