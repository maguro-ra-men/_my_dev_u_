#modulesのpath通し、logに利用
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
from locale import currency
import sys
sys.path.append(f"{rootpath}")

#loging
from logging import getLogger,config
import logging
from conf.logger_conf import * #my module

#my module
from conf.db import engine,session
from modules.variable import app_drange,app_rtype,fdate,tdate

import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta


"""
df_wlist作成
"""
#tarade status on ,rtype=変数かつfundありのtickerをdf_wlistへ
query=f'select a.ticker  ,c.currency \
        from `trade` as a \
        left join fund as b ON (a.id  = b.trade_id)\
        left join tickers as c ON (a.ticker  = c.ticker)\
        where a.status="on" and a.rtype="{app_rtype}" and \
        b.status_f ="on" and b.rtype="{app_rtype}"\
        GROUP by c.ticker '
df_wlist = pd.read_sql_query(query, engine)
if df_wlist.empty:
    logger.error(f'error:No valid trade and fund')
    sys.exit('error:')

#currency listを作成
df_clist = df_wlist
#raw整形：カラム削除
df_clist=df_clist.drop(columns=['ticker']) 
#raw整形：カラム単位の重複値を削除
df_clist=df_clist.drop_duplicates()


"""
get exchange rate
通貨コード一覧  https://support.yahoo-net.jp/PccFinance/s/article/H000006607
元コード result = data.get_data_yahoo('USDJPY=X',start='2022-1-1')
※注意：平日2/4が取れず2/7月曜に取れた例がある。API元の格納エラーがあり得る
"""
from pandas_datareader import data,get_quote_yahoo
#get exchange rate
df,df_temp='',''
for r in df_clist.index:
    currency=df_clist.at[r,'currency']
    df_temp = data.get_data_yahoo(f'{currency}JPY=X',start=f'{fdate}')
    df_temp=df_temp.assign(currency=df_clist.at[r,'currency']) 
    if len(df)==0:
        df=df_temp
    else:
        df=df.append(df_temp)

"""
df整形(currency)
"""
import pandas as pd
df= df.reset_index() #add index（ここで加えないとdateのdateの変更が不可の為）
#raw整形：カラム削除
df=df.drop(columns=['High','Low','Open','Volume','Adj Close']) 
#raw整形：小文字に統一
df=df.rename(columns = {'Date':'date', 'Close':'close'})
#raw整形：カラム順番変更
df=df.reindex(columns=['currency','date','close'])
#raw整形：datetimeからdateへ変更
df['date']=df['date'].dt.date

#add整形:カラム追加、値追加、ソート
df=df.assign(create_time=datetime.datetime.now()) #add create_date
df = df.sort_values(['currency','date'], ascending=False) #sort DESC
df= df.reset_index() #add index（振り直し）
df= df.drop(columns=['index'])  #元のindex列削除
#（余計なindex列が残るなー。。。。まあいいか）

"""
table insert(currency)
"""
df.to_sql('currency', engine, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
#pd.read_sql('SELECT * FROM currency', engine) #確認

"""
table 重複排除(currency)（pandasがupsert不可能でデータ重複する為）
    重複しているデータでidが最大のもの以外をdelete
    https://chaika.hatenablog.com/entry/2019/02/21/120000
"""
from sqlalchemy.sql import text
query=text(f'WITH dup_list AS (\
            SELECT * FROM currency AS t1\
            WHERE 1 < (\
                SELECT COUNT(*) FROM currency AS t2\
                WHERE t1.currency  = t2.currency \
                    AND t1.date  = t2.date\
                    AND t1.id  <= t2.id  ))\
            DELETE FROM currency\
            WHERE id  IN (SELECT id  FROM dup_list);')
session.execute(query)
session.commit()


"""
get stock data
    米国開始時間　jst23:30 夏時間jst22:30
    sample米国:df = data.DataReader('SOXL', 'yahoo',"2022-01-05","2022-01-07")#当日取れた
    sample日本:df = data.DataReader('4293.T', 'yahoo',"2022-01-05","2022-01-06")#当日取れた
"""
#get stock data
df,df_temp='',''
for r in df_wlist.index:
    df_temp = data.DataReader(df_wlist.at[r,'ticker'], 'yahoo',fdate,tdate)
    df_temp=df_temp.assign(ticker=df_wlist.at[r,'ticker']) 
    if len(df)==0:
        df=df_temp
    else:
        df=df.append(df_temp)

"""
df整形(stock)
"""
df= df.reset_index() #add index（ここで加えないとdateのdateの変更が不可の為）
#raw整形：カラム削除
df=df.drop(columns=['Adj Close']) 
#raw整形：小文字に統一
df=df.rename(columns = {'Date':'date','High':'high','Low':'low','Open':'open',
                        'Close':'close','Volume':'volume'})
#raw整形：カラム順番変更
df=df.reindex(columns=['ticker','date','high','low','open','close','volume'])
#raw整形：datetimeからdateへ変更
df['date']=df['date'].dt.date

#add整形:カラム追加、値追加、ソート
df=df.assign(create_time=datetime.datetime.now()) #add create_date
df=df.assign(a_ema20close=0,a_bb20ema=0,a_bb20high=0,a_bb20low=0,a_stdev_p=0) #add tech chart Multiple columns
df = df.sort_values(['ticker','date'], ascending=False) #sort DESC
df= df.reset_index() #add index（振り直し）
df= df.drop(columns=['index'])  #元のindex列削除

"""
Tech chart追加(stock)
"""
#明確なloop終了日を算出 (m6)6ヶ月前の1日　（today）前回稼働で未確定のcloseがあるかも。-5日にしよう
if app_drange=='past6month':
    edate = tdate.replace(day=1) + relativedelta(months=-6)
elif app_drange=='today':
    edate=datetime.date.today()+ relativedelta(days=-5)

#edateはdfに含むdateの範囲で確定
i=0
for i in range(1000):
    if edate in df['date'].values:
        print('!!BREAK!! edate確定 %s 処理count: %d' % (edate,i))
        break
    edate = edate + relativedelta(days=+1)
    print('!!false:再度検索!! %s 処理count: %d' % (edate,i))

df_multi_val=df #tickごとの処理する前に全データとして保管

#tickerごとにdf_temp生成しtech chartを追加、dfに足していく
import statistics
df,df_temp,ia='','',0
for ia,ticker in enumerate(df_wlist.ticker):
    val=df_wlist.loc[df_wlist.index[ia],'ticker'] #ticker value取り出し。（1行でやったら認識ｓれない為）
    df_temp=df_multi_val[df_multi_val['ticker'] == val] #tempに1ticekrのみで展開
    df_temp= df_temp.reset_index() #add index（振り直し）
    df_temp= df_temp.drop(columns=['index'])  #元のindex列削除
    #Add Tech chart!------------------------------------
    for r,date in enumerate(df_temp.date):
        #a_ema20close closeのdate-1～-20のAVG------------
        data_range=20
        s=r+1
        e=(s+(data_range-1))
        df_temp.loc[r,'a_ema20close']=round(df_temp.loc[df_temp.index[s]:df_temp.index[e], 'close'].mean(),2) #代入(atダメ。locならok)
        #error対策
        if e > max(df_temp.index):
            print('!!BREAK!! error：past dateが不足 date+21= %d r= %d' % (e,r))
            break
        #a_bb20ema closeのdate-0～-19のAVG------------
        data_range=20
        s=r
        e=(s+(data_range-1))
        df_temp.loc[r,'a_bb20ema']=round(df_temp.loc[df_temp.index[s]:df_temp.index[e], 'close'].mean(),2) #代入(atダメ。locならok)
        #a_stdev_p closeのdate-0～-19の標準偏差------------
        data_range=20
        s=r
        e=(s+(data_range-1))
        df_temp.loc[r,'a_stdev_p']=statistics.pstdev(df_temp.loc[df_temp.index[s]:df_temp.index[e], 'close']) #代入(atダメ。locならok)
        #a_bb20high bb20ema　+　2　ｘ　標準偏差
        df_temp.loc[r,'a_bb20high']=df_temp.loc[r,'a_bb20ema'] + 2 * df_temp.loc[r,'a_stdev_p']
        #a_bb20low bb20ema　-　2　ｘ　標準偏差
        df_temp.loc[r,'a_bb20low']=df_temp.loc[r,'a_bb20ema'] - 2 * df_temp.loc[r,'a_stdev_p']
        #loop date終了日で抜ける------------------------
        if date == edate:
            print('!!BREAK!! finish:ticker単位 tick= %s r= %d date= %s edate= %s' % (ticker,r,date,edate))
            break
    #ticker単位のdfを結合
    if len(df)==0:
        df=df_temp
    else:
        df=df.append(df_temp)

#計算結果が無い＝不要行を削除
df=df.drop(df.index[df['a_bb20ema'] == 0].values)
#重複して不正なindexを振り直すべき
df= df.reset_index() #add index（振り直し）
df= df.drop(columns=['index'])  #元のindex列削除

"""
data check 
    バッチ時間に関わらず、today dateがなければエラー
"""
if app_drange =='today':
    if not tdate == df.loc[0,'date']: #todayの日付がstock apiにない？
        print('error:stock apiにtoday dateが無い')
        sys.exit('error:')  


"""
table insert(stock)
"""
df.to_sql('stock_prices', engine, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
#pd.read_sql('SELECT * FROM stock_prices;', engine) #確認

"""
table 重複排除(stock)（pandasがupsert不可能でデータ重複する為）
    重複しているデータでidが最大のもの以外をdelete
    https://chaika.hatenablog.com/entry/2019/02/21/120000
"""
from sqlalchemy.sql import text
query=text(f'WITH dup_list AS (\
            SELECT * FROM stock_prices AS t1\
            WHERE 1 < (\
                SELECT COUNT(*) FROM stock_prices AS t2\
                WHERE t1.ticker  = t2.ticker \
                    AND t1.date  = t2.date\
                    AND t1.id  <= t2.id  ))\
            DELETE FROM stock_prices\
            WHERE id  IN (SELECT id  FROM dup_list);')
session.execute(query)
session.commit()


print('end[fetch_api_data]')