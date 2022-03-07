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
"""
from modules.variable import app_drange,app_rtype,fdate,tdate, \
    ticker, ex_rate, c_price, high_price, low_price, mov_avg, bb_highs, \
        bb_lows, date
"""
from modules.cls.tbl_val import TBL_VAL

import pandas as pd
import datetime

class STAGE_C():
    def c():
        #get latest values
        list = API_DATA_ONE_DAY.one_day()
        ticker, ex_rate, c_price, high_price, low_price, mov_avg, \
            bb_highs, bb_lows, date = \
                list[0], list[1], list[2], list[3], list[4], list[5], \
                    list[6], list[7], list[8]
        
        print(f'start::::trade_stage_b date is {date}')

        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]
        
        #1日1回しか売買しないので状態チェック
        if trade_end_of_turn == 1:
            #loop終了
            logger.debug(f'return trade_end_of_turn = 1')
            return

        #select order
        try:
            #（都度指定）必要な各tableのphase指定が必要
            #diff::::trade_id,trade_phase,order_pahase
            df_order = TBL_VAL.tbl_order_df(trade_id,'2','2a') 
            print(df_order)#あとでけす
        except TypeError:
            df_order = None
        
        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, 2, 'close') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number, exe_create_time = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7]
        #この実行日を変数化
        tmp_run_date = date
        #検索値に必要なのでtimestampをdateに変換
        tmp_exe_crat_date = str(exe_create_time)
        tmp_exe_crat_date = date.split(tmp_exe_crat_date)#何故かリストになる
        tmp_exe_crat_date = tmp_exe_crat_date[0]        

        #stock_pricesからexe_dateの次営業日を取得。
        #もしなければ約定当日なのでtodayを代入
        next_business_day = TBL_VAL.tbl_st_prices_next_biz_day\
            (ticker, tmp_exe_crat_date) #ticker,wheredate

        
        #現在価格は移動平均線より下?-----------------------------
        if c_price < exe_price:
            """
            不要？
            #約定確認 エラー回避策
            try:
                order_id in globals() #o idは定義済み？
            except NameError:
                order_id = None
            """
            #実行dateはphase2約定日の次営業日？
            if tmp_run_date == next_business_day:
                #y 約定の次営業日は何もしない
                #update trade （都度指定）
                #def::::trade_id, trade_phase, end_of_turn
                TBL_VAL.tbl_upd_trade_after_exe(trade_id, 2, 1)
                #loop終了
                logger.debug(f'return tmp_run_date = {next_business_day}')
                return
            
            #約定確認 sell 2a 全決済
            if not df_order.empty: #o idはnoneじゃない？
                for r in df_order.index:
                    #df_orderから取り出し
                    order_id = df_order.loc[r,'order_id']
                    order_price = df_order.loc[r,'order_price']
                    order_quantity = df_order.loc[r,'quantity']
                    order_pf_order_number= df_order.loc[r,'pf_order_number']
                    order_hold_exe_id = df_order.loc[r,'hold_exe_id']
                    #if order_idのpriceはhigh-lowの範囲？
                    if order_price <= high_price and order_price >= low_price:
                        match app_rtype:
                            case 'simu':
                                #orderのhold_exe_idから対のbuyのexe特定
                                #diff::::trade_id, order_id
                                exe_id = TBL_VAL.tbl_exe_select_o_id(trade_id, order_hold_exe_id)

                                #upd exe 今回sellの遂になるbuyのexeの
                                # status_e = close、close_order_id
                                #def::::exe_id, status_e, close_order_id
                                TBL_VAL.tbl_upd_exe_fin_buy_info(exe_id, 'close', order_id)

                                #create exe
                                #def::::trade_id, phase_e, order_id, 
                                #def::::otype, exe_price, quantity, status_e, 
                                #def::::pf_order_number, close_order_id, run_date_e
                                TBL_VAL.tbl_ins_exe(trade_id, '2a', order_id, 
                                        'sell', order_price, order_quantity, 'close', 
                                        order_pf_order_number, order_id, date)
                                #selct exe
                                list = TBL_VAL.tbl_exe_latest(trade_id, order_id)
                                exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                                    exe_quantity, exe_pf_order_number = \
                                    list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                                #最新fund取得
                                fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)

                                #update fund status_f=off
                                fund_id = TBL_VAL.tbl_fund_latest(trade_id)
                                TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                                #create fund
                                tmp_r_funds = \
                                    fund_r_funds + int((order_price * ex_rate) * order_quantity)
                                tmp_diff_funds = tmp_r_funds - fund_r_funds
                                #def:::trade_id, order_id, exe_id, rtype, ticker, 
                                #def:::status_f, residual_funds, update_diff_funds, run_date_f
                                TBL_VAL.tbl_ins_fund(trade_id, order_id, exe_id, app_rtype, ticker, 
                                    'on', tmp_r_funds, tmp_diff_funds, date)

                                #update order status_o=off
                                TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)
                            case 'real':
                                print('あとで実装')

            #get latest values
            list=TBL_VAL.tbl_trade_single(ticker)
            trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
            trade_initial_fund_id, trade_fund_id, trade_in_residual_funds, \
            trade_logic_ver = \
                list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7]

            try:
                #（都度指定）必要な各tableのphase指定が必要
                list = TBL_VAL.tbl_order_single(trade_id,1,'1a') #trade_id,trade_phase,order_pahase
                order_id, order_price, order_quantity, order_pf_order_number = \
                    list[0], list[1], list[2], list[3]
            except TypeError:
                order_id = None

            #selct exe（都度指定）
            list = TBL_VAL.tbl_exe_single(trade_id, 1, 'hold') #trade_id, phase_e, status_e
            exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                exe_quantity, exe_pf_order_number = \
                list[0], list[1], list[2], list[3], list[4], list[5], list[6]
            
            #最新fund取得
            fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
            fund_id = TBL_VAL.tbl_fund_latest(trade_id)

            #すべて約定？ sell 2a
            tmp_count = TBL_VAL.tbl_count_o_e_active(trade_id)
            if tmp_count == 0:
                #tradeの終了処理

                #update trade （都度指定）
                #def::::trade_id, trade_phase, status, end_of_turn
                TBL_VAL.tbl_upd_trade_finish(trade_id, 3, 'off', 1)

                #trade_results用に変数作成
                tmp_start_funds = TBL_VAL.tbl_fund_select_f_id(trade_initial_fund_id) #fund_id
                temp_real_gal = fund_r_funds - tmp_start_funds
                tmp_roi = temp_real_gal / tmp_start_funds

                #ins trade_results
                #diff::::trade_id, ticker, rtype, start_funds, 
                #diff::::last_funds, realized_gain_and_loss, roi, run_date_r
                TBL_VAL.tbl_ins_trade_results(trade_id, ticker, app_rtype, tmp_start_funds, \
                    fund_r_funds, temp_real_gal, tmp_roi, date)

                #ins trade（次回用）
                #diff::::rtype, initial_fund_id, phase, status, ticker, logic_ver
                TBL_VAL.tbl_ins_trade(app_rtype, fund_id+1, '0', 'on', \
                    ticker, trade_logic_ver)
                
                #select trade ticker,max_id
                trade_id = TBL_VAL.tbl_trade_max_id(ticker)

                #update trade （都度指定）※こえないと最新tradeのexe無いエラーに繋がる
                #def::::trade_id, trade_phase, end_of_turn
                TBL_VAL.tbl_upd_trade_after_exe(trade_id, 0, 1)

                #create fund
                #def:::trade_id, order_id, exe_id, rtype, ticker, 
                #def:::status_f, residual_funds, update_diff_funds, run_date_f
                TBL_VAL.tbl_ins_fund(trade_id, 0, 0, app_rtype, ticker, 
                    'on', fund_r_funds, 0, date)
                
                #update fund status_f=off
                TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                #loop終了
                logger.debug(f'return stage all finish 219')
                return

            #get latest values
            #select order
            try:
                #（都度指定）必要な各tableのphase指定が必要
                #diff::::trade_id,trade_phase,order_pahase
                df_order = TBL_VAL.tbl_order_df(trade_id,2,'2a') 
                print(df_order)#あとでけす
            except TypeError:
                df_order = None


            #sell 2a全決済　＝処分価格に変更。処分目的で発注済みorderの指値をc_priceに変更すること
            if not df_order.empty: #o idはnoneじゃない？
                for r in df_order.index:
                    #df_orderから取り出し
                    order_id = df_order.loc[r,'order_id']
                    order_pf_order_number= df_order.loc[r,'pf_order_number']
                    #指値決定
                    tmp_order_price = c_price * 0.997
                    tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                    tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                    #価格訂正(分岐は無い。実行)
                    match app_rtype:
                        case 'simu':
                            #update order
                            TBL_VAL.tbl_upd_order_price(order_id,tmp_order_price, date)
                        case 'real':
                            print('あとで実装')            
            elif trade_phase == '2':#約定前と約定後の分岐に対応(order無い＆trade p2)
                #新規order：exe close売れ残り処分=sell増し 2a
                #価格下落の緊急事態の為、連続でorder実行
                #select order
                try:
                    #selct exe df（都度指定）
                    #diff::::#trade_id, phase_e, status_e
                    df_h_exe = TBL_VAL.tbl_exe_df(trade_id, '1a', 'hold')
                except TypeError:
                    df_h_exe = None

                #exeのstatus_e=holdがある？あればsell増し続行            
                if not df_h_exe.empty: #o idはnoneじゃない？
                    #exe holdはある
                    for r in df_h_exe.index:
                        #dfから取り出し
                        h_exe_quantity = df_h_exe.loc[r,'quantity']
                        h_exe_order_id = df_h_exe.loc[r,'order_id']
                        #指値の決定
                        tmp_order_price = c_price * 0.997
                        tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                        tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                        #数量の決定
                        tmp_order_quantity = h_exe_quantity
                        #新規order
                        match app_rtype:
                                case 'simu':
                                    #simuなので架空のSEC注文番号を生成
                                    tmp_pf_order_number = TBL_VAL.GetRandomStr(10)
                                    #create order
                                    #def::::trade_id, phase_o, status_o,otype, 
                                    #def::::order_price, quantity, hold_exe_id, pf_order_number
                                    TBL_VAL.tbl_ins_order(trade_id, '2a', 'on', 'sell', 
                                            tmp_order_price, tmp_order_quantity, 
                                            tmp_pf_order_number, h_exe_order_id, date)
                                case 'real':
                                    print('あとで実装')

        #現在価格は移動平均線より上?-----------------------------
        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #select order
        try:
            #（都度指定）必要な各tableのphase指定が必要
            #diff::::trade_id,trade_phase,order_pahase
            df_order = TBL_VAL.tbl_order_df(trade_id,'2','2a') 
            print(df_order)#あとでけす errorおきたとこ
            #df_order.to_csv(f'{rootpath}\\debug_de_order.csv') #あとでけす
        except TypeError:
            df_order = None

        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, '2', 'close') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #現在価格は移動平均線より上?
        #約定確認 sell 2a 全決済
        if not df_order.empty: #o idはnoneじゃない？
            for r in df_order.index:
                #df_orderから取り出し
                order_id = df_order.loc[r,'order_id']                
                order_price = df_order.loc[r,'order_price']
                order_quantity = df_order.loc[r,'quantity']
                order_pf_order_number= df_order.loc[r,'pf_order_number']
                order_hold_exe_id = df_order.loc[r,'hold_exe_id']
                #if order_idのpriceはhigh-lowの範囲？
                if order_price <= high_price and order_price >= low_price:
                    match app_rtype:
                        case 'simu':
                            #orderのhold_exe_idから対のbuyのexe特定
                            #diff::::trade_id, order_id
                            exe_id = TBL_VAL.tbl_exe_select_o_id(trade_id, order_hold_exe_id)

                            #upd exe 今回sellの遂になるbuyのexeの
                            # status_e = close、close_order_id
                            #def::::exe_id, status_e, close_order_id
                            TBL_VAL.tbl_upd_exe_fin_buy_info(exe_id, 'close', order_id)

                            #create exe
                            #def::::trade_id, phase_e, order_id, 
                            #def::::otype, exe_price, quantity, status_e, 
                            #def::::pf_order_number, close_order_id, run_date_e
                            TBL_VAL.tbl_ins_exe(trade_id, '2a', order_id, 
                                    'sell', order_price, order_quantity, 'close', 
                                    order_pf_order_number, order_id, date)
                            #selct exe
                            list = TBL_VAL.tbl_exe_latest(trade_id, order_id)
                            exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                                exe_quantity, exe_pf_order_number = \
                                list[0], list[1], list[2], list[3], list[4], list[5], list[6]

                            #最新fund取得
                            fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
                            fund_id = TBL_VAL.tbl_fund_latest(trade_id)

                            #update fund status_f=off
                            TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

                            #create fund
                            tmp_r_funds = \
                                fund_r_funds + int((order_price * ex_rate) * order_quantity)
                            tmp_diff_funds = tmp_r_funds - fund_r_funds
                            #def:::trade_id, order_id, exe_id, rtype, ticker, 
                            #def:::status_f, residual_funds, update_diff_funds, run_date_f
                            TBL_VAL.tbl_ins_fund(trade_id, order_id, exe_id, app_rtype, ticker, 
                                'on', tmp_r_funds, tmp_diff_funds, date)

                            #update order status_o=off
                            TBL_VAL.tbl_upd_order_after_exe(order_id, 'off', date)
                        case 'real':
                            print('あとで実装')

        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds, \
        trade_logic_ver = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7]

        try:
            #（都度指定）必要な各tableのphase指定が必要
            list = TBL_VAL.tbl_order_single(trade_id,1,'1a') #trade_id,trade_phase,order_pahase
            order_id, order_price, order_quantity, order_pf_order_number = \
                list[0], list[1], list[2], list[3]
        except TypeError:
            order_id = None

        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, 2, 'hold') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]
        
        #最新fund取得
        fund_r_funds = TBL_VAL.tbl_fund_r_funds(trade_id)
        fund_id = TBL_VAL.tbl_fund_latest(trade_id)

        #すべて約定？ sell 2a
        tmp_count = TBL_VAL.tbl_count_o_e_active(trade_id)
        if tmp_count == 0:
            #tradeの終了処理

            #update trade （都度指定）
            #def::::trade_id, trade_phase, status, end_of_turn
            TBL_VAL.tbl_upd_trade_finish(trade_id, 3, 'off', 1)

            #trade_results用に変数作成
            tmp_start_funds = TBL_VAL.tbl_fund_select_f_id(trade_initial_fund_id) #fund_id
            temp_real_gal = fund_r_funds - tmp_start_funds
            tmp_roi = temp_real_gal / tmp_start_funds

            #ins trade_results
            #diff::::trade_id, ticker, rtype, start_funds, 
            #diff::::last_funds, realized_gain_and_loss, roi, run_date_r
            TBL_VAL.tbl_ins_trade_results(trade_id, ticker, app_rtype, tmp_start_funds, \
                fund_r_funds, temp_real_gal, tmp_roi, date)

            #ins trade（次回用）
            #diff::::rtype, initial_fund_id, phase, status, ticker, logic_ver
            TBL_VAL.tbl_ins_trade(app_rtype, fund_id, '0', 'on', \
                ticker, trade_logic_ver)

            #select trade ticker,max_id
            trade_id = TBL_VAL.tbl_trade_max_id(ticker)

            #update trade （都度指定）※こえないと最新tradeのexe無いエラーに繋がる
            #def::::trade_id, trade_phase, end_of_turn
            TBL_VAL.tbl_upd_trade_after_exe(trade_id, 0, 1)

            #create fund
            #def:::trade_id, order_id, exe_id, rtype, ticker, 
            #def:::status_f, residual_funds, update_diff_funds, run_date_f
            TBL_VAL.tbl_ins_fund(trade_id, 0, 0, app_rtype, ticker, 
                'on', fund_r_funds, 0, date)
            
            #update fund status_f=off
            TBL_VAL.tbl_upd_fund_after_ins(fund_id, 'off', date)

            #loop終了
            logger.debug(f'return stage all finish')
            return



        #get latest values
        list=TBL_VAL.tbl_trade_single(ticker)
        trade_id, trade_phase, trade_last_run_date, trade_end_of_turn, \
        trade_initial_fund_id, trade_fund_id, trade_in_residual_funds = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]

        #select order
        try:
            #（都度指定）必要な各tableのphase指定が必要
            #diff::::trade_id,trade_phase,order_pahase
            df_order = TBL_VAL.tbl_order_df(trade_id,2,'2a') 
            print(df_order)#あとでけす
        except TypeError:
            df_order = None

        #selct exe（都度指定）
        list = TBL_VAL.tbl_exe_single(trade_id, 2, 'close') #trade_id, phase_e, status_e
        exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
            exe_quantity, exe_pf_order_number = \
            list[0], list[1], list[2], list[3], list[4], list[5], list[6]


        #既存orderの確認　sell増し
        if not df_order.empty: #o idはnoneじゃない？
            for r in df_order.index:
                #df_orderから取り出し
                order_id = df_order.loc[r,'order_id']
                order_price = df_order.loc[r,'order_price']
                order_quantity = df_order.loc[r,'quantity']
                order_pf_order_number= df_order.loc[r,'pf_order_number']
                order_hold_exe_id = df_order.loc[r,'hold_exe_id']
                #Y:（既存orderの価格訂正）
                #（無駄scrape減　誤差なら無視）
                tmp_edit_price=0
                if c_price >= exe_price:
                    tmp_order_price = c_price * 1.003
                    if order_price >= tmp_order_price * 1.042:
                        tmp_edit_price=1
                    if order_price <= tmp_order_price * 0.968:
                        tmp_edit_price=1
                else:
                    tmp_order_price = exe_price
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
                        case 'real':
                            print('あとで実装')

        elif trade_phase == '2':#約定前と約定後の分岐に対応(order無い＆trade p1)
            #新規order sell増し 2a
            #selct exe（都度指定）
            try:
                list = TBL_VAL.tbl_exe_min_price(trade_id, '1a', 'hold') #trade_id, phase_e, status_e
                m_exe_id, m_exe_trade_id, m_phase_e, m_exe_order_id, m_exe_price, \
                    m_exe_quantity, m_exe_pf_order_number, m_exe_create_time = \
                    list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7]
            except TypeError:
                m_exe_id = None
            #exeのstatus_e=holdがある？あればsell増し続行            
            if not m_exe_id is None: #o idはnoneじゃない？
                #exe holdはある
                #selct exe（都度指定）基準として約定価格が必要
                list = TBL_VAL.tbl_exe_single(trade_id, 2, 'close') #trade_id, phase_e, status_e
                exe_id, exe_trade_id, phase_e, exe_order_id, exe_price, \
                    exe_quantity, exe_pf_order_number = \
                    list[0], list[1], list[2], list[3], list[4], list[5], list[6]
                #指値の決定
                if c_price >= exe_price:
                    tmp_order_price = c_price * 1.003
                else:
                    tmp_order_price = exe_price
                tmp_order_price = '{:.2f}'.format(tmp_order_price)#小数点2位まで
                tmp_order_price = float(tmp_order_price)#何故かstrになったのでfloatへ
                #数量の決定
                tmp_order_quantity = m_exe_quantity
                #新規order
                match app_rtype:
                        case 'simu':
                            #simuなので架空のSEC注文番号を生成
                            tmp_pf_order_number = TBL_VAL.GetRandomStr(10)
                            #create order
                            #def::::trade_id, phase_o, status_o,otype, 
                            #def::::order_price, quantity, pf_order_number
                            TBL_VAL.tbl_ins_order(trade_id, '2a', 'on', 'sell', 
                                    tmp_order_price, tmp_order_quantity, 
                                    tmp_pf_order_number, m_exe_order_id, date)
                        case 'real':
                            print('あとで実装')
        
        
        print(f'end::::trade_stage_c date is {date}')