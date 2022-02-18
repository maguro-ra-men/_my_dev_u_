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

#1日1回しか売買しないので状態チェック
trade_end_of_turn=TBL_VAL.tbl_trade_end_of_turn(ticker)
if trade_end_of_turn == 1:
    #loop終了
    print('loop終了')

#約定確認



#既存orderの確認
trade_phase = TBL_VAL.tbl_trade_phase(ticker)
order_id = TBL_VAL.tbl_order_id_single(trade_id,0,1) #trade_id,trade_phase,order_pahase
order_price = TBL_VAL.tbl_order_price_single(trade_id,0,1) #trade_id,trade_phase,order_pahase
if not order_id is None: #o idは空じゃない？
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
    #価格訂正(誤差じゃない)
    if tmp_edit_price == 1:
        match app_rtype:
            case 'simu':
                trade_phase = TBL_VAL.tbl_upd_order_price(order_id,tmp_order_price)
            case 'real':
                print('あとで実装')
elif trade_phase == 0:#約定前と約定後の分岐に対応(order無い＆trade p0)
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
    import math
    tmp_ok_buy_funds = int(fund_r_funds * 0.5 / ex_rate)
    tmp_order_quantity = int(tmp_ok_buy_funds / tmp_order_price)
    match app_rtype:
            case 'simu':
                #simuなので架空のSEC注文番号を生成
                pf_order_number = TBL_VAL.GetRandomStr(10)
                #create order
                

            case 'real':
                print('あとで実装')


print('end::::trade_stage_c')