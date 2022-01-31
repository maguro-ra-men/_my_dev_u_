#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append(f"{rootpath}")

#loging
import logging
logger = logging.getLogger(__name__)
filehandler = logging.FileHandler(f'{rootpath}/log/dev_moshimo.log')
streamhandler = logging.StreamHandler()
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s][%(filename)s]')
streamhandler.setFormatter(formatter)
filehandler.setFormatter(formatter)
#logger.propagate = False #propagateの直訳は「伝播する」であり、この属性はLogRecordを親へ伝播させるかを指定する。

#logger.debug('testlog_debug')
#logger.info('testlog_info')
#logger.error('testlog_error')
