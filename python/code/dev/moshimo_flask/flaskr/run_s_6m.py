#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append(f"{rootpath}")
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr\\modules")

#loging
from logging import getLogger,config
from conf.logger_conf import *
logger = getLogger(__name__)

""" 不要になるはず
#loging
import logging
logger = logging.getLogger(__name__)
filehandler = logging.FileHandler(f'{rootpath}/log/test.log')
streamhandler = logging.StreamHandler()
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s][%(filename)s]')
streamhandler.setFormatter(formatter)
filehandler.setFormatter(formatter)

logger.debug('testlog_debug')
logger.info('testlog_info')
logger.error('testlog_error')
"""

#my module
from modules.db import *
from modules.cls.tbl.tickers import Tickers
from modules.cls.forms import Tickers_Form

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
from modules.check_duplicate_data import check_results
num_of_error = check_results()
print(check_results())

print(num_of_error)


from modules.ztest_a import check_resultsz
print(check_resultsz())


if num_of_error >= 1:
    sys.exit('error:table不整合')

#3 create work list




#4.data fetch

#5.trade
