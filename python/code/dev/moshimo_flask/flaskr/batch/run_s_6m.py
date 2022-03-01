#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from operator import index
import sys
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import logging
from conf.logger_conf import * #my module

#my module
from conf.db import *
from modules.cls.tbl.tickers import Tickers
from modules.cls.forms import Tickers_Form

"""
run_s_6m
"""
#1.run

#当appの定数を定義
main_drange='past6month'
main_rtype='simu'

#定数をcsv化
import pandas as pd
df=pd.DataFrame({'drange': [f'{main_drange}'],
    'app_rtype': [f'{main_rtype}']})
df=df.rename_axis('index') #indexに名前を付ける
df.to_csv(f'{rootpath}\\const.csv') 

#他moduleは以下から定数をimportし利用
from modules.variable import app_drange,app_rtype,fdate,tdate
print(f'DataRange→ {app_drange}')
print(f'RunType→ {app_rtype}')

"""
Run Common modules
"""
#2.Check duplicate data.
from modules.check_duplicate_data import check_results
#print(check_results()) #チェック用
if check_results() >= 1:
    print('error:table不整合')
    sys.exit('error:')

#3 fetch api data
try:
    from modules.fetch_api_data import *
except OperationalError:
    print('error:fetch_api_data')
    sys.exit('error:')

#4.trade
from modules.trade import *




print('end::::')