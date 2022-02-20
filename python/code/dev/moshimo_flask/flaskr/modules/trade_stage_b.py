#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys

from sqlalchemy import null
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
from conf.logger_conf import *
logger = getLogger(__name__)

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype,fdate,tdate
from modules.variable import *
"""
from modules.variable import app_drange,app_rtype,fdate,tdate, \
    ticker, ex_rate, c_price, high_price, low_price, mov_avg, bb_highs, \
        bb_lows, date
"""
from modules.cls.tbl_val import TBL_VAL

import pandas as pd

class STAGE_B():
    def b():
        #get latest values
        list = API_DATA_ONE_DAY.one_day()
        ticker, ex_rate, c_price, high_price, low_price, mov_avg, \
            bb_highs, bb_lows, date = \
                list[0], list[1], list[2], list[3], list[4], list[5], \
                    list[6], list[7], list[8]
        
        print(f'start::::trade_stage_b date is {date}')

        list = TBL_VAL.tbl_trade_single(ticker)
        global trade_id
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn = \
            list[0].copy(), list[1], list[2], list[3]
        print(trade_id)#あとでけす
        print(trade_phase)#あとでけす

        try:
            list = TBL_VAL.tbl_order_single(trade_id,0,1) #trade_id,trade_phase,order_pahase
            order_id, order_price, order_quantity, order_pf_order_number = \
                list[0], list[1], list[2], list[3]
        except TypeError:
            pass

        #1日1回しか売買しないので状態チェック
        if trade_end_of_turn == 1:
            #loop終了
            print('loop終了')

        #約定確認　エラー回避策
        try:
            order_id in globals() #o idは定義済み？
        except NameError:
            order_id = None
        #約定確認
        if not order_id is None: #o idはnoneじゃない？
            list = [order_id]
            for i in list:
                #if order_idのpriceはhigh-lowの範囲？
                if order_price <= high_price and order_price >= low_price:
                    match app_rtype:
                        case 'simu':
                            #create exe
                            #def::::trade_id, exe_phase, order_id, 
                            #def::::otype, exe price, quantity, exe_status, 
                            #def::::pf_order_number, close_order_id, run_date_e
                            TBL_VAL.tbl_ins_exe(trade_id, 1, order_id, 
                                    'buy', order_price, order_quantity, 'hold', 
                                    order_pf_order_number, '', date)

                            #update fund
                            #fundで最新より1つ前のrを取得
                            fund_before_r_funds = TBL_VAL.tbl_before_fund_r_funds(trade_id)
                            #あとは新規order時のように算出してupdate
                            tmp_r_funds = \
                            fund_before_r_funds - int((order_price * ex_rate) * order_quantity)
                            tmp_diff_funds = tmp_r_funds - fund_before_r_funds
                            TBL_VAL.tbl_upd_fund_rdiff_funds(trade_id, 
                            order_id,tmp_r_funds, tmp_diff_funds, date)

                            #update trade phase=1、end_of_turn=1
                            #def::::trade_id, trade_phase, end_of_turn
                            TBL_VAL.tbl_upd_trade_after_exe(trade_id, 1, 1)

                            #update order status=off
                            TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)
                        case 'real':
                            print('あとで実装')

        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn = \
            list[0], list[1], list[2], list[3]
        try:
            list = TBL_VAL.tbl_order_single(trade_id,0,1) #trade_id,trade_phase,order_pahase
            order_id, order_price, order_quantity, order_pf_order_number = \
                list[0], list[1], list[2], list[3]
        except TypeError:
            pass

        #既存orderの確認
        if not order_id is None: #o idはnoneじゃない？
            tmp_edit_price=0
            #Y:（既存orderの価格訂正）
            #（無駄scrape減　誤差なら無視）
            tmp_edit_price=0
            if c_price <= bb_lows:
                tmp_order_price = c_price * 0.997
                if order_price >= tmp_order_price * 1.042:
                    tmp_edit_price=1
                if order_price <= tmp_order_price * 0.968:
                    tmp_edit_price=1
            else:
                tmp_order_price =bb_lows
                if order_price >= tmp_order_price * 1.042:
                    tmp_edit_price=1
                if order_price <= tmp_order_price * 0.968:
                    tmp_edit_price=1
            tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
            tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
            #価格訂正(誤差じゃない)
            if tmp_edit_price == 1:
                match app_rtype:
                    case 'simu':
                        #update order
                        TBL_VAL.tbl_upd_order_price(order_id,tmp_order_price, date)
                        #update fund
                        #fundで最新より1つ前のrを取得
                        fund_before_r_funds = TBL_VAL.tbl_before_fund_r_funds(trade_id)
                        #あとは新規order時のように算出してupdate
                        tmp_r_funds = \
                            fund_before_r_funds - int((tmp_order_price * ex_rate) * order_quantity)
                        tmp_diff_funds = tmp_r_funds - fund_before_r_funds
                        TBL_VAL.tbl_upd_fund_rdiff_funds(trade_id, 
                            order_id,tmp_r_funds, tmp_diff_funds, date)
                    case 'real':
                        print('あとで実装')
        elif trade_phase == '0':#約定前と約定後の分岐に対応(order無い＆trade p0)
            #新規order
            #最低限stock買える資金がない？
            fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
            if not fund_r_funds / ex_rate > c_price * 1.03:
                print('loop終了 fund不足。1つも買えない。trade不可能')
            #追加buy資金がない？
            if not fund_r_funds * 0.5 / ex_rate > c_price * 5:
                print('loop終了 fund不足。phase1a追加buy不可につきtrade停止')
            #新規order
            if c_price <= bb_lows:
                tmp_order_price = c_price * 0.997
            else:
                tmp_order_price =bb_lows
            tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
            tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
            import math
            tmp_ok_buy_funds = int((fund_r_funds * 0.5) / ex_rate)
            tmp_order_quantity = int(tmp_ok_buy_funds / tmp_order_price)
            match app_rtype:
                    case 'simu':
                        #simuなので架空のSEC注文番号を生成
                        tmp_pf_order_number = TBL_VAL.GetRandomStr(10)
                        #create order
                        #def::::trade_id, order_phase, status,otype, 
                        #def::::order_price, quantity, pf_order_number
                        TBL_VAL.tbl_ins_order(trade_id, 1, 'on', 'buy', 
                                tmp_order_price, tmp_order_quantity, 
                                tmp_pf_order_number, date)
                        #get lasted order_id必要
                        list = TBL_VAL.tbl_order_single(trade_id,0,1) #trade_id,trade_phase,order_pahase
                        order_id, order_price, order_quantity, order_pf_order_number = \
                        list[0], list[1], list[2], list[3]
                        #create fund
                        tmp_r_funds = \
                            fund_r_funds - int((tmp_order_price * ex_rate) * tmp_order_quantity)
                        tmp_diff_funds = tmp_r_funds - fund_r_funds
                        #def:::trade_id, order_id, exe_id, rtype, ticker, 
                        #def:::status, residual_funds, update_diff_funds, run_date_f
                        TBL_VAL.tbl_ins_fund(trade_id, order_id, 0, app_rtype, ticker, 
                                'on', tmp_r_funds, tmp_diff_funds, date)
                    case 'real':
                        print('あとで実装')


        print(f'end::::trade_stage_b date is {date}')