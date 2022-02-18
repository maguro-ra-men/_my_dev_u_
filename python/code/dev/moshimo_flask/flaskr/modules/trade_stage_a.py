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

trade_end_of_turn=TBL_VAL.tbl_trade_end_of_turn(ticker)

if trade_end_of_turn == 1:
    #loop終了
    print('loop終了')

if c_price <= mov_avg: #現在価格は移動平均線より下？
    

Y:変数Residual funds_for_buy = fund residual funds - Executionのbuyの複数のExecution priceの合計
（buy増しする資金がある？）Residual funds_for_buy > trade invest funds X 0.95