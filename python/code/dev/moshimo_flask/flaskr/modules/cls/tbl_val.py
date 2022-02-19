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

    def tbl_trade_single(ticker):
        query=f'select a.id, a.rtype, a.phase, a.status, a.ticker, \
                a.last_run_date, cnt_run_date, end_of_turn\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and \
                a.ticker = "{ticker}" and\
                b.status ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_id = df.loc[0,'id']
        trade_phase = df.loc[0,'phase']
        trade_last_run_date = df.loc[0,'last_run_date']
        trade_end_of_turn = df.loc[0,'end_of_turn']
        return trade_id, trade_phase, trade_last_run_date, trade_end_of_turn

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

    def tbl_order_single(trade_id,trade_phase,order_pahase):
        try:
            query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase, \
            b.status, b.otype, b.order_price, b.quantity, b.pf_order_number\
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and a.phase="{trade_phase}" and\
            b.status ="on" and b.phase="{order_pahase}";'
            df = pd.read_sql_query(query, engine)
            order_id = df.loc[0,'order_id']
            order_price = df.loc[0,'order_price']
            order_quantity = df.loc[0,'quantity']
            order_pf_order_number = df.loc[0,'pf_order_number']
        except KeyError:
            pass
        else:
            return order_id, order_price, order_quantity, order_pf_order_number

    def tbl_upd_order_price(order_id,tmp_order_price):
        query=text(f'UPDATE `order` \
            SET order_price={tmp_order_price}\
            WHERE id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_order_after_exe(order_id,status):
        query=text(f'UPDATE `order` \
            SET status="{status}"\
            WHERE id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_trade_after_exe(trade_id, trade_phase, end_of_turn):
        query=text(f'UPDATE trade \
            SET phase="{trade_phase}", end_of_turn="{end_of_turn}"\
            WHERE id={trade_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_fund_rdiff_funds(trade_id, order_id, \
            residual_funds, update_diff_funds):
        query=text(f'UPDATE fund \
            SET residual_funds={residual_funds}, \
                update_diff_funds={update_diff_funds}\
            WHERE trade_id={trade_id} and order_id={order_id};')
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
        fund_r_funds = df.loc[0,'residual_funds']
        return fund_r_funds

    def tbl_before_fund_r_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        fund_before_r_funds = df.loc[1,'residual_funds']
        return fund_before_r_funds

    def tbl_fund_diff_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        update_diff_funds = df.loc[0,'update_diff_funds']
        return update_diff_funds
    
    def GetRandomStr(num):
        # 英数字をすべて取得
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        # 英数字からランダムに取得
        return ''.join([random.choice(dat) for i in range(num)])

    def tbl_ins_order(trade_id, order_phase, status,otype, 
            order_price, quantity, pf_order_number):
        query=text(f'insert into `order` (trade_id, phase, status,otype, \
            order_price, quantity, pf_order_number) \
            values({trade_id}, {order_phase}, "{status}", "{otype}", \
            {order_price}, {quantity}, "{pf_order_number}");')
        session.execute(query)
        session.commit()

    def tbl_ins_exe(trade_id, exe_phase, order_id, \
            otype, exe_price, quantity, exe_status, 
            pf_order_number, close_order_id):
        query=text(f'insert into execution (trade_id, phase, order_id, \
                otype, exe_price, quantity, exe_status,\
                pf_order_number, close_order_id) \
            values({trade_id}, {exe_phase}, "{order_id}", \
                "{otype}", {exe_price}, {quantity}, "{exe_status}"\
            "{pf_order_number}", "{close_order_id}");')
        session.execute(query)
        session.commit()

    def tbl_ins_fund(trade_id, order_id, exe_id, rtype, ticker, 
                        status, residual_funds, update_diff_funds):
        query=text(f'insert into `fund` (trade_id, order_id, exe_id, rtype, \
                    ticker, status, residual_funds, update_diff_funds) \
            values({trade_id}, {order_id}, {exe_id}, "{rtype}", "{ticker}",  \
            "{status}", {residual_funds}, {update_diff_funds});')
        session.execute(query)
        session.commit()