#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys

from sqlalchemy import null
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import logging
from conf.logger_conf import * #my module

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype,fdate,tdate
from modules.variable import *
from modules.cls.tbl_val import TBL_VAL

import pandas as pd

class STAGE_B():
    def b():
        #get latest values(stage standard)
        list = API_DATA_ONE_DAY.one_day()
        ticker, ex_rate, c_price, high_price, low_price, mov_avg, \
            bb_highs, bb_lows, date = \
                list[0], list[1], list[2], list[3], list[4], list[5], \
                    list[6], list[7], list[8]
        
        print(f'start::::trade_stage_b date is {date}')

        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #1日1回しか売買しないので状態チェック(stage standard)
        if trade_end_of_turn == 1:
            #loop終了
            logger.debug(f'return trade_end_of_turn = 1')
            return

        #get latest values
        #select order（都度指定）必要な各tableのphase指定が必要
        list = TBL_VAL.tbl_order_single(trade_id,'1','1a') #trade_id,trade_phase,order_pahase
        order_id, order_price, order_quantity, order_pf_order_number = \
            list[0], list[1], list[2], list[3]

        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, '1', 'hold') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]
        
        #ini r funds取得
        ini_fund_r_funds = TBL_VAL.tbl_fund_select_f_id(trade_initial_fund_id)


        #現在価格は移動平均線より下?-----------------------------
        if c_price <= mov_avg:
            #既存orderの確認 buy増し(1a order中は1つしか存在しない)
            if not order_id is None: #o idはnoneじゃない？
                tmp_edit_price=0
                #Y:（既存orderの価格訂正）
                #（無駄scrape減　誤差なら無視）
                tmp_edit_price=0
                if c_price <= exe_price:
                    tmp_order_price = c_price * 0.997
                    if order_price >= tmp_order_price * judg_upper_price_rate:
                        tmp_edit_price=1
                    if order_price <= tmp_order_price * judg_lower_price_rate:
                        tmp_edit_price=1
                else:
                    tmp_order_price = exe_price * 0.997
                    if order_price >= tmp_order_price * judg_upper_price_rate:
                        tmp_edit_price=1
                    if order_price <= tmp_order_price * judg_lower_price_rate:
                        tmp_edit_price=1
                tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                #価格訂正(誤差じゃない) buy増し
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
                                order_id, 0, tmp_r_funds, tmp_diff_funds, date)
                        case 'real':
                            print('あとで実装')


                #約定確認（準備）
                #get latest values
                list=TBL_VAL.tbl_trade_single(ticker)
                trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
                trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
                    list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                #get latest values
                #（都度指定）必要な各tableのphase指定が必要
                list = TBL_VAL.tbl_order_single(trade_id,1,'1a') #trade_id,trade_phase,order_pahase
                order_id, order_price, order_quantity, order_pf_order_number = \
                    list[0], list[1], list[2], list[3]

                #約定確認 buy増し(1a order中は1つしか存在しない)
                if not order_id is None: #o idはnoneじゃない？
                    loop_list = [order_id]
                    for i in loop_list:
                        #if order_idのpriceはhigh-lowの範囲？
                        if order_price <= high_price and order_price >= low_price:
                            match app_rtype:
                                case 'simu':
                                    #create exe
                                    #def::::trade_id, phase_e, order_id, 
                                    #def::::otype, exe_price, quantity, status_e, 
                                    #def::::pf_order_number, close_order_id, run_date_e
                                    TBL_VAL.tbl_ins_exe(trade_id, '1a', order_id, 
                                            'buy', order_price, order_quantity, 'hold', 
                                            order_pf_order_number, '', date)
                                    #selct exe
                                    list = TBL_VAL.tbl_exe_latest(trade_id, order_id)
                                    exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                                        exe_quantity, exe_pf_order_number = \
                                        list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                                    #update fund
                                    #fundで最新より1つ前のrを取得
                                    fund_before_r_funds = TBL_VAL.tbl_before_fund_r_funds(trade_id)
                                    #あとは新規order時のように算出してupdate
                                    tmp_r_funds = \
                                    fund_before_r_funds - int((order_price * ex_rate) * order_quantity)
                                    tmp_diff_funds = tmp_r_funds - fund_before_r_funds
                                    TBL_VAL.tbl_upd_fund_rdiff_funds(trade_id, 
                                    order_id, exe_id, tmp_r_funds, tmp_diff_funds, date)

                                    #update trade （都度指定）
                                    #def::::trade_id, trade_phase, end_of_turn
                                    TBL_VAL.tbl_upd_trade_after_exe(trade_id, 1, 1)

                                    #update order status_o=off
                                    TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)
                                case 'real':
                                    print('あとで実装')

            elif trade_phase == '1':#約定前と約定後の分岐に対応(order無い＆trade p1)
                #新規order buy増し
                #追加buy資金がある？あるなら何度でも追加buy実行
                fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
                fund_id = TBL_VAL.tbl_fund_latest(trade_id)
                if fund_r_funds / ex_rate > c_price * 1.01:
                    #資金はある
                    #指値の決定
                    if c_price <= exe_price:
                        tmp_order_price = c_price * 0.997
                    else:
                        tmp_order_price = exe_price * 0.997
                    tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                    tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                    #数量の決定
                    import math
                    if ini_fund_r_funds * 0.1 <= fund_r_funds:
                        #in_fundの 10% で数量設定
                        tmp_ok_buy_funds = int((ini_fund_r_funds * 0.1) / ex_rate)
                        tmp_order_quantity = int(tmp_ok_buy_funds / tmp_order_price)
                    else:
                        #in_fundの10%以下。fund残金すべてで数量設定
                        tmp_ok_buy_funds = int(fund_r_funds / ex_rate)
                        tmp_order_quantity = int(tmp_ok_buy_funds / tmp_order_price)
                    #新規order
                    match app_rtype:
                            case 'simu':
                                #simuなので架空のSEC注文番号を生成
                                tmp_pf_order_number = TBL_VAL.GetRandomStr(10)
                                #create order
                                #def::::trade_id, phase_o, status_o,otype, 
                                #def::::order_price, quantity, pf_order_number
                                TBL_VAL.tbl_ins_order(trade_id, '1a', 'on', 'buy', 
                                        tmp_order_price, tmp_order_quantity, 
                                        tmp_pf_order_number, 0, date)
                                #get lasted order_id必要
                                list = TBL_VAL.tbl_order_single(trade_id,'1','1a') #trade_id,trade_phase,order_pahase
                                order_id, order_price, order_quantity, order_pf_order_number = \
                                list[0], list[1], list[2], list[3]
                                #create fund
                                tmp_r_funds = \
                                    fund_r_funds - int((tmp_order_price * ex_rate) * tmp_order_quantity)
                                tmp_diff_funds = tmp_r_funds - fund_r_funds
                                #def:::trade_id, order_id, exe_id, rtype, ticker, 
                                #def:::status_f, residual_funds, update_diff_funds, run_date_f
                                TBL_VAL.tbl_ins_fund(trade_id, order_id, 0, app_rtype, ticker, 
                                        'on', tmp_r_funds, tmp_diff_funds, date)
                                #update fund status_f=off
                                TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                            case 'real':
                                print('あとで実装')
        
        #現在価格は移動平均線より上?-----------------------------
        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #select order（都度指定）必要な各tableのphase指定が必要
        list = TBL_VAL.tbl_order_single(trade_id,1,'2') #trade_id,trade_phase,order_pahase
        order_id, order_price, order_quantity, order_pf_order_number = \
            list[0], list[1], list[2], list[3]

        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, 1, 'hold') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #DEBUG　あとでけす
        if ticker == 'SDY' and date == '2022-02-25':
            123
        #現在価格は移動平均線より上?
        if c_price >= mov_avg:
            #既存orderの確認　初回50％sell order
            if not order_id is None: #o idはnoneじゃない？
                #Y:（既存orderの価格訂正）
                #（無駄scrape減　誤差なら無視）
                tmp_edit_price=0
                if c_price >= bb_highs:
                    tmp_order_price = c_price * 1.003
                    if order_price >= tmp_order_price * judg_upper_price_rate:
                        tmp_edit_price=1
                    if order_price <= tmp_order_price * judg_lower_price_rate:
                        tmp_edit_price=1
                else:
                    tmp_order_price = bb_highs
                    if order_price >= tmp_order_price * judg_upper_price_rate:
                        tmp_edit_price=1
                    if order_price <= tmp_order_price * judg_lower_price_rate:
                        tmp_edit_price=1
                #下落相場で損しない対策
                if tmp_order_price <= exe_price:
                    tmp_order_price = exe_price * 1.01
                    if order_price == tmp_order_price:	
                        tmp_edit_price=0
                    else:	
                        tmp_edit_price=1
                #小数点を整形
                tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                #価格訂正(誤差じゃない)
                if tmp_edit_price == 1:
                    match app_rtype:
                        case 'simu':
                            #update order
                            TBL_VAL.tbl_upd_order_price(order_id,tmp_order_price, date)
                        case 'real':
                            print('あとで実装')


                #約定確認（準備）
                #get latest values
                list=TBL_VAL.tbl_trade_single(ticker)
                trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
                trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
                    list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                #select order（都度指定）必要な各tableのphase指定が必要
                list = TBL_VAL.tbl_order_single(trade_id,1,'2') #trade_id,trade_phase,order_pahase
                order_id, order_price, order_quantity, order_pf_order_number = \
                    list[0], list[1], list[2], list[3]

                #selct exe（都度指定）
                list = TBL_VAL.tbl_exe_single(trade_id, '1', 'hold') #trade_id, phase_e, status_e
                exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                    exe_quantity, exe_pf_order_number = \
                    list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                #最新fund取得
                fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
                fund_id = TBL_VAL.tbl_fund_latest(trade_id)

                #約定確認　初回50％sell order
                if not order_id is None: #o idはnoneじゃない？
                    loop_list = [order_id]
                    for i in loop_list:
                        #if order_idのpriceはhigh-lowの範囲？
                        if order_price <= high_price and order_price >= low_price:
                            match app_rtype:
                                case 'simu':
                                    #upd exe 今回sellの遂になるbuyのexeの
                                    # status_e = close、close_order_id
                                    #def::::exe_id, status_e, close_order_id
                                    TBL_VAL.tbl_upd_exe_fin_buy_info(exe_id, 'close', order_id)

                                    #create exe
                                    #def::::trade_id, phase_e, order_id, 
                                    #def::::otype, exe_price, quantity, status_e, 
                                    #def::::pf_order_number, close_order_id, run_date_e
                                    TBL_VAL.tbl_ins_exe(trade_id, '2', order_id, 
                                            'sell', order_price, order_quantity, 'close', 
                                            order_pf_order_number, order_id, date)
                                    #selct exe
                                    list = TBL_VAL.tbl_exe_latest(trade_id, order_id)
                                    exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                                        exe_quantity, exe_pf_order_number = \
                                        list[0], list[1], list[2], list[3], list[4], list[5], list[6]
                                    #create fund
                                    tmp_r_funds = \
                                        fund_r_funds + int((order_price * ex_rate) * order_quantity)
                                    tmp_diff_funds = tmp_r_funds - fund_r_funds
                                    #def:::trade_id, order_id, exe_id, rtype, ticker, 
                                    #def:::status_f, residual_funds, update_diff_funds, run_date_f
                                    TBL_VAL.tbl_ins_fund(trade_id, order_id, exe_id, app_rtype, ticker, 
                                            'on', tmp_r_funds, tmp_diff_funds, date)
                                    #update fund status_f=off
                                    TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                                    #update trade （都度指定）
                                    #def::::trade_id, trade_phase, end_of_turn
                                    TBL_VAL.tbl_upd_trade_after_exe(trade_id, 2, 1)

                                    #update order status_o=off
                                    TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)

                                case 'real':
                                    print('あとで実装')


                            #buy増し注文の破棄。初回sell50％売れた時点で未約定のbuy増しは注文取消
                            #order_id_list へ代入
                            try:
                                #（都度指定）必要な各tableのphase指定が必要
                                order_id_list = TBL_VAL.tbl_order_list(trade_id,2,'1a') #trade_id,trade_phase,order_pahase
                            except TypeError:
                                order_id_list = None

                            #buy増し注文の破棄
                            if not order_id_list is None: #o idはnoneじゃない？
                                for order_id in order_id_list:
                                    match app_rtype:
                                        case 'simu':
                                            #fundのorder_idのdiff取得
                                            tmp_diff_funds = TBL_VAL.tbl_fund_select_o_id(trade_id,order_id)
                                            #マイナスなので正の整数化
                                            tmp_diff_funds = tmp_diff_funds * -1
                                            #最新fund取得
                                            fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
                                            #update fund status_f=off
                                            fund_id = TBL_VAL.tbl_fund_latest(trade_id)
                                            TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                                            #create fund
                                            tmp_r_funds = fund_r_funds + tmp_diff_funds
                                            #def:::trade_id, order_id, exe_id, rtype, ticker, 
                                            #def:::status_f, residual_funds, update_diff_funds, run_date_f
                                            TBL_VAL.tbl_ins_fund(trade_id, order_id, 0, app_rtype, ticker, 
                                                    'on', tmp_r_funds, tmp_diff_funds, date)
                                            #update order status_o=off
                                            TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)
                                        case 'real':
                                            print('あとで実装')


            elif trade_phase == '1':#約定前と約定後の分岐に対応(order無い＆trade p1)
                #新規order　初回50％sell order
                #指値の決定
                if c_price >= bb_highs:
                    tmp_order_price = c_price * 1.003
                else:
                    tmp_order_price = bb_highs
                #下落相場で損しない対策
                if tmp_order_price <= exe_price:
                    tmp_order_price = exe_price * 1.01
                #小数点の整形
                tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                #数量の決定
                tmp_order_quantity = exe_quantity
                #新規order
                match app_rtype:
                        case 'simu':
                            #simuなので架空のSEC注文番号を生成
                            tmp_pf_order_number = TBL_VAL.GetRandomStr(10)
                            #create order
                            #def::::trade_id, phase_o, status_o,otype, 
                            #def::::order_price, quantity, pf_order_number
                            TBL_VAL.tbl_ins_order(trade_id, '2', 'on', 'sell', 
                                    tmp_order_price, tmp_order_quantity, 
                                    tmp_pf_order_number, 0, date)
                        case 'real':
                            print('あとで実装')
        
        
        print(f'end::::trade_stage_b date is {date}')