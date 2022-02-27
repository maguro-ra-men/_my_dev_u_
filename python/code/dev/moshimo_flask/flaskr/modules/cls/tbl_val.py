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
import datetime

class TBL_VAL():
    """
    def __init__(self,ticker,trade_id=None,trade_phase=None):
        self.trade_id = trade_id
        self.trade_phase = trade_phase
        self.ticker = ticker
    """

    def tbl_trade_single(ticker):
        query=f'select a.id, a.rtype, a.phase, a.status, a.ticker, \
                a.last_run_date, cnt_run_date, end_of_turn, initial_fund_id, \
                b.id as fund_id, residual_funds, a.logic_ver\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and \
                a.ticker = "{ticker}" and\
                b.status_f ="on" and b.rtype="{app_rtype}"'
        df = pd.read_sql_query(query, engine)
        trade_id = df.loc[0,'id']
        trade_phase = df.loc[0,'phase']
        trade_last_run_date = df.loc[0,'last_run_date']
        trade_end_of_turn = df.loc[0,'end_of_turn']
        trade_initial_fund_id = df.loc[0,'initial_fund_id']
        trade_fund_id = df.loc[0,'fund_id']
        trade_in_residual_funds = df.loc[0,'residual_funds']
        trade_logic_ver = df.loc[0,'logic_ver']
        return trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
            trade_initial_fund_id, trade_fund_id, trade_in_residual_funds, \
            trade_logic_ver

    def tbl_upd_trade_turn_start(ticker,date):
        query=f'select a.id, a.ticker, a.phase, a.last_run_date, a.cnt_run_date\
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.status="on" and a.rtype="{app_rtype}" and a.ticker = "{ticker}" and\
            b.status_f ="on" and b.rtype="{app_rtype}"'
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
            query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase_o, \
            b.status_o, b.otype, b.order_price, b.quantity, b.pf_order_number, \
            hold_exe_id \
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id) \
            where a.id={trade_id} and a.phase="{trade_phase}" and \
            b.status_o ="on" and b.phase_o="{order_pahase}"'
            df = pd.read_sql_query(query, engine)
            order_id = df.loc[0,'order_id']
            order_price = df.loc[0,'order_price']
            order_quantity = df.loc[0,'quantity']
            order_pf_order_number = df.loc[0,'pf_order_number']
            order_hold_exe_id = df.loc[0,'hold_exe_id']
        except KeyError:
            pass
        else:
            return order_id, order_price, order_quantity, order_pf_order_number, \
                order_hold_exe_id

    def tbl_order_list(trade_id,trade_phase,order_pahase):
        try:
            query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase_o, \
            b.status_o, b.otype, b.order_price, b.quantity, b.pf_order_number \
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id) \
            where a.id={trade_id} and a.phase="{trade_phase}" and \
            b.status_o ="on" and b.phase_o="{order_pahase}"'
            df = pd.read_sql_query(query, engine)
            order_id_list = df['order_id'].tolist()
        except KeyError:
            pass
        else:
            return order_id_list
    
    def tbl_order_df(trade_id,trade_phase,order_pahase):
        try:
            query=f'select a.id, a.ticker, a.phase, b.id as order_id, b.phase_o, \
            b.status_o, b.otype, b.order_price, b.quantity, b.pf_order_number, \
            hold_exe_id \
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id) \
            where a.id={trade_id} and a.phase="{trade_phase}" and \
            b.status_o ="on" and b.phase_o="{order_pahase}"'
            df_order = pd.read_sql_query(query, engine)
        except KeyError:
            pass
        else:
            return df_order


    def tbl_exe_latest(trade_id, order_id):
        query=f'select id, trade_id, phase_e, order_id, otype, exe_price, \
            quantity, status_e, pf_order_number, close_order_id, \
            run_date_e\
            from execution\
            where trade_id={trade_id} and order_id ={order_id} and\
            id=(select max(id) from execution)\
            ORDER BY id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        exe_id = df.loc[0,'id']
        exe_trade_id = df.loc[0,'trade_id']
        phase_e = df.loc[0,'phase_e']
        exe_order_id = df.loc[0,'order_id']
        exe_price = df.loc[0,'exe_price']
        exe_quantity = df.loc[0,'quantity']
        exe_pf_order_number = df.loc[0,'pf_order_number']
        return exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, exe_quantity, exe_pf_order_number

    def tbl_exe_single(trade_id, phase_e, status_e):
        query=f'select id, trade_id, phase_e, order_id, otype, exe_price, \
            quantity, status_e, pf_order_number, close_order_id, run_date_e, \
            create_time \
            from execution \
            where trade_id={trade_id} and phase_e ="{phase_e}" and \
            status_e = "{status_e}" and \
            id=(select max(id) from execution) \
            ORDER BY id DESC \
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        exe_id = df.loc[0,'id']
        exe_trade_id = df.loc[0,'trade_id']
        phase_e = df.loc[0,'phase_e']
        exe_order_id = df.loc[0,'order_id']
        exe_price = df.loc[0,'exe_price']
        exe_quantity = df.loc[0,'quantity']
        exe_pf_order_number = df.loc[0,'pf_order_number']
        exe_create_time = df.loc[0,'create_time']
        return exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, exe_quantity, \
            exe_pf_order_number, exe_create_time

    def tbl_exe_min_price(trade_id, phase_e, status_e):
        query=f'select id, trade_id, phase_e, order_id, otype, exe_price, \
            quantity, status_e, pf_order_number, close_order_id, run_date_e, \
            create_time \
            from execution \
            where trade_id={trade_id} and phase_e ="{phase_e}" and \
            status_e = "{status_e}" and \
            id=(select max(exe_price) from execution) \
            ORDER BY id ASC \
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        m_exe_id = df.loc[0,'id']
        m_exe_trade_id = df.loc[0,'trade_id']
        m_phase_e = df.loc[0,'phase_e']
        m_exe_order_id = df.loc[0,'order_id']
        m_exe_price = df.loc[0,'exe_price']
        m_exe_quantity = df.loc[0,'quantity']
        m_exe_pf_order_number = df.loc[0,'pf_order_number']
        m_exe_create_time = df.loc[0,'create_time']
        return m_exe_id, m_exe_trade_id, m_phase_e, m_exe_order_id, m_exe_price, \
            m_exe_quantity, m_exe_pf_order_number, m_exe_create_time

    def tbl_exe_select_o_id(trade_id, order_id):
        query=f'select id, trade_id, phase_e, order_id, otype, exe_price, \
            quantity, status_e, pf_order_number, close_order_id, run_date_e, \
            create_time \
            from execution \
            where trade_id={trade_id}, order_id~{order_id};'
        df = pd.read_sql_query(query, engine)
        exe_id = df.loc[0,'id']
        return exe_id
        
    def tbl_st_prices_next_biz_day(ticker,wheredate):
        try:
            query=f'select date, ticker\
                from stock_prices\
                where ticker="{ticker}" and date > "{wheredate}" \
                order by date asc \
                limit 1;'
            df = pd.read_sql_query(query, engine)
            next_business_day = df.loc[0,'date']
        except KeyError:
            #もしなければ約定当日なのでtodayを代入
            next_business_day = datetime.date.today()
        return next_business_day

    def tbl_count_o_e_active(trade_id):
        query=f'select * \
            from `trade` as a \
            left join `order` as b ON (a.id  = b.trade_id) \
            left join execution as c ON (a.id  = c.trade_id) \
            where a.id={trade_id} and b.status_o ="on" or c.status_e ="hold" ;'
        df = pd.read_sql_query(query, engine)
        tmp_count = len(df)
        return tmp_count

    def tbl_upd_order_price(order_id,tmp_order_price, run_date_o):
        query=text(f'UPDATE `order` \
            SET order_price={tmp_order_price}, run_date_o="{run_date_o}"\
            WHERE id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_order_after_exe(order_id,status_o, run_date_o):
        query=text(f'UPDATE `order` \
            SET status_o="{status_o}", run_date_o="{run_date_o}"\
            WHERE id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_trade_after_exe(trade_id, trade_phase, end_of_turn):
        query=text(f'UPDATE trade \
            SET phase="{trade_phase}", end_of_turn="{end_of_turn}"\
            WHERE id={trade_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_trade_finish(trade_id, trade_phase, status, end_of_turn):
        query=text(f'UPDATE trade \
            SET phase="{trade_phase}", end_of_turn="{end_of_turn}", \
                status="{status}" \
            WHERE id={trade_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_fund_rdiff_funds(trade_id, order_id, exe_id, \
            residual_funds, update_diff_funds, run_date_f):
        query=text(f'UPDATE fund \
            SET exe_id={exe_id}, residual_funds={residual_funds}, \
                update_diff_funds={update_diff_funds}, \
                run_date_f="{run_date_f}"\
            WHERE trade_id={trade_id} and order_id={order_id};')
        session.execute(query)
        session.commit()

    def tbl_upd_exe_fin_buy_info(exe_id, status_e, close_order_id):
        query=text(f'UPDATE `execution` \
            SET status_e="{status_e}", close_order_id={close_order_id}\
            WHERE id={exe_id};')
        session.execute(query)
        session.commit()

    def tbl_fund_r_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status_f ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        fund_r_funds = df.loc[0,'residual_funds']
        return fund_r_funds

    def tbl_fund_latest(trade_id):
        query=f'select id, ticker, status_f, residual_funds, \
            update_diff_funds \
            from fund \
            where trade_id="{trade_id}" and status_f ="on" and \
                id=(select max(id) from fund)\
            ORDER BY id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        fund_id = df.loc[0,'id']
        return fund_id

    def tbl_before_fund_r_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status_f ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 2;'
        df = pd.read_sql_query(query, engine)
        fund_before_r_funds = df.loc[1,'residual_funds']
        return fund_before_r_funds

    def tbl_fund_diff_funds(trade_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id)\
            where a.id="{trade_id}" and b.status_f ="on" and \
                b.id=(select max(b.id) from fund)\
            ORDER BY fund_id DESC\
            LIMIT 1;'
        df = pd.read_sql_query(query, engine)
        update_diff_funds = df.loc[0,'update_diff_funds']
        return update_diff_funds

    def tbl_fund_select_o_id(trade_id, order_id):
        query=f'select a.id, a.ticker, a.phase, b.residual_funds, \
            b.update_diff_funds, b.id as fund_id \
            from `trade` as a \
            left join fund as b ON (a.id  = b.trade_id) \
            where a.id="{trade_id}" and b.order_id ={order_id} ;'
        df = pd.read_sql_query(query, engine)
        update_diff_funds = df.loc[0,'update_diff_funds']
        return update_diff_funds

    def tbl_fund_select_f_id(fund_id):
        query=f'select id, residual_funds, update_diff_funds \
            from fund \
            where id={fund_id} ;'
        df = pd.read_sql_query(query, engine)
        ini_fund_r_funds = df.loc[0,'residual_funds']
        return ini_fund_r_funds

    def GetRandomStr(num):
        # 英数字をすべて取得
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        # 英数字からランダムに取得
        return ''.join([random.choice(dat) for i in range(num)])

    def tbl_ins_order(trade_id, phase_o, status_o,otype, 
            order_price, quantity, pf_order_number, hold_exe_id, run_date_o):
        query=text(f'insert into `order` (trade_id, phase_o, status_o,otype, \
            order_price, quantity, pf_order_number, hold_exe_id, run_date_o) \
            values({trade_id}, {phase_o}, "{status_o}", "{otype}", \
            {order_price}, {quantity}, "{pf_order_number}", \
            {hold_exe_id}, "{run_date_o}");')
        session.execute(query)
        session.commit()

    def tbl_ins_exe(trade_id, phase_e, order_id, \
            otype, exe_price, quantity, status_e, 
            pf_order_number, close_order_id, run_date_e):
        query=text(f'insert into execution (trade_id, phase_e, order_id, \
                otype, exe_price, quantity, status_e,\
                pf_order_number, close_order_id, run_date_e) \
            values({trade_id}, "{phase_e}", {order_id}, \
                "{otype}", {exe_price}, {quantity}, "{status_e}", \
            "{pf_order_number}", "{close_order_id}", "{run_date_e}");')
        session.execute(query)
        session.commit()

    def tbl_ins_fund(trade_id, order_id, exe_id, rtype, ticker, 
                        status_f, residual_funds, update_diff_funds, run_date_f):
        query=text(f'insert into `fund` (trade_id, order_id, exe_id, rtype, \
                    ticker, status_f, residual_funds, update_diff_funds, \
                    run_date_f) \
            values({trade_id}, {order_id}, {exe_id}, "{rtype}", "{ticker}",  \
            "{status_f}", {residual_funds}, {update_diff_funds}, \
            "{run_date_f}");')
        session.execute(query)
        session.commit()

    def tbl_ins_trade(rtype, initial_fund_id, phase, status, ticker, logic_ver):
        query=text(f'insert into `trade` (rtype, initial_fund_id, phase, status, \
            ticker, logic_ver) \
            values("{rtype}", {initial_fund_id}, "{phase}", "{status}", "{ticker}",  \
            "{logic_ver}");')
        session.execute(query)
        session.commit()

    def tbl_ins_trade_results(trade_id, ticker, rtype, start_funds, \
            last_funds, realized_gain_and_loss, roi, run_date_r):
        query=text(f'insert into `fund` (trade_id, ticker, rtype, start_funds, \
            last_funds, realized_gain_and_loss, roi, run_date_r) \
            values({trade_id}, "{ticker}", "{rtype}", {start_funds}, \
                {last_funds}, {realized_gain_and_loss}, {roi}, "{run_date_r}");')
        session.execute(query)
        session.commit()