#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import conf.logger_conf
logger = getLogger(__name__)

def check_results():
    print('Hello!')
    return 1+3

    #2.Check duplicate data.
    #my module
    from modules.db import engine
    from batch.run_s_6m import drange,app_rtype

    import pandas as pd
    num_of_error=0
    check='config logic_verが2以上？' #title------------------------------
    query='select logic_ver,count(logic_ver) \
        from config GROUP by logic_ver having COUNT(logic_ver) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='stock_pricesのticker,dateが2以上？' #title------------------------------
    query='select ticker ,date,count(*) from stock_prices \
        GROUP by ticker ,date having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='tarade status on ,rtype=変数のtickerが2以上？' #title------------------------------
    query=f'select status ,rtype ,ticker_id ,count(*) from trade \
        where status="on" and rtype="{app_rtype}" GROUP by ticker_id  ,rtype,ticker_id \
        having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='tarade status on ,rtype=変数のtickerとorder status onが2以上？' #title------------------------------
    query=f'select a.status ,rtype ,ticker_id ,count(*),b.status\
        from `trade` as a\
        left join `order` as b \
        ON (a.id  = b.trade_id)\
        where a.status="on" and a.rtype="{app_rtype}" and b.status ="on"\
        GROUP by a.status, a.rtype, a.ticker_id, b.status\
        having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='tarade status on ,rtype=変数のtickerとfund status onが2以上？' #title------------------------------
    query=f'select a.status ,a.rtype ,a.ticker_id ,count(*),b.status\
        from `trade` as a left join fund as b ON (a.id  = b.trade_id)\
        where a.status="on" and a.rtype="{app_rtype}" and b.status ="on"\
        GROUP by a.status, a.rtype, a.ticker_id, b.status\
        having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='tarade status on ,rtype=変数のtickerとexe holdが2以上？' #title------------------------------
    query=f'select a.status ,a.rtype ,a.ticker_id ,count(*),b.exe_status\
        from `trade` as a left join execution as b ON (a.id  = b.trade_id)\
        where a.status="on" and a.rtype="{app_rtype}" and b.exe_status ="hold"\
        GROUP by a.status, a.rtype, a.ticker_id, b.exe_status\
        having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    check='tarade status on ,rtype=変数のtickerとtrade_resultsが2以上？' #title------------------------------
    query=f'select a.id, a.status ,a.rtype ,a.ticker_id ,count(*),b.id\
        from `trade` as a left join trade_results as b ON (a.id  = b.trade_id)\
        where a.status="on" and a.rtype="simu" and b.id >=1\
        GROUP by a.id, a.status, a.rtype, a.ticker_id\
        having COUNT(*) > 1'
    df = pd.read_sql_query(query, engine)
    if df.empty==False:
        logger.error(f'2.Check duplicate data/error:{check}')
        num_of_error=num_of_error+1

    print('end')

    