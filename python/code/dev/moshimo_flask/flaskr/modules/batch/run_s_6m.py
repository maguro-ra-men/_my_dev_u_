#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append(f"{rootpath}")

#my module
from modules.db import *
from modules.cls.tbl.tickers import Tickers
from modules.cls.forms import Tickers_Form

#loging
import logging
logger = logging.getLogger(__name__)
filehandler = logging.FileHandler(f'{rootpath}/log/test.log')
streamhandler = logging.StreamHandler()
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s][%(filename)s]')
streamhandler.setFormatter(formatter)
filehandler.setFormatter(formatter)

logger.debug('testlog_debug')
logger.info('testlog_info')
logger.error('testlog_error')

"""
run_s_6m
"""
#1.run
drange='past6month'
app_rtype='simu'

"""
Run Common modules
"""
#2.Check duplicate data.

#3 create work list

#4.data fetch

#5.trade