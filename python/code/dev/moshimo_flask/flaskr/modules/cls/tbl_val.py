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
from sqlalchemy.sql import text
import random
import string

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
        query=f'select a.id, a.ticker, a.phase, a.end_of_turn\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_id = df.loc[0,'id']
        return trade_id

    def tbl_trade_phase(ticker):
        query=f'select a.id, a.ticker, a.phase, a.end_of_turn\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_phase = df.loc[0,'phase']
        return trade_phase

    def tbl_trade_end_of_turn(ticker):
        query=f'select a.id, a.ticker, a.phase, a.end_of_turn\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_end_of_turn = df.loc[0,'end_of_turn']
        return trade_end_of_turn

    def tbl_trade_last_run_date(ticker):
        query=f'select a.id, a.ticker, a.phase, a.last_run_date\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_last_run_date = df.loc[0,'last_run_date']
        return trade_last_run_date

    def tbl_upd_trade_turn_start(ticker,date):
        query=f'select a.id, a.ticker, a.phase, a.last_run_date, a.cnt_run_date\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_id = df.loc[0,'id'] #id取得
        cnt_run_date = df.loc[0,'cnt_run_date']
        cnt_run_date = cnt_run_date +1
        #turn開始前にidの3項目を更新。
        query=text(f'UPDATE trade \
            SET last_run_date="{date}", end_of_turn=0, cnt_run_date={cnt_run_date}\
            WHERE id={trade_id};')
        session.execute(query)
        session.commit()

    def tbl_order_id_single(trade_id,trade_phase,order_pahase):
        query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase, \
            b.order_price\
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and a.phase="{trade_phase} and\
            b.status ="on" and b.phase="{order_pahase}";'
        df = pd.read_sql_query(query, engine)
        order_id = df.loc[0,'order_id']
        return order_id

    def tbl_order_price_single(trade_id,trade_phase,order_pahase):
        query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase, \
            b.order_price\
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and a.phase="{trade_phase} and \
            "b.status ="on" and b.phase="{order_pahase}";'
        df = pd.read_sql_query(query, engine)
        order_price = df.loc[0,'order_price']
        return order_price

    def tbl_upd_order_price(order_id,tmp_order_price):
        query=text(f'UPDATE order \
            SET order_price="{tmp_order_price}"\
            WHERE id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_fund_r_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        fund_r_funds = df.loc[0,'b.residual_funds']
        return fund_r_funds
    
    def GetRandomStr(num):
        # 英数字をすべて取得
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        # 英数字からランダムに取得
        return ''.join([random.choice(dat) for i in range(num)])