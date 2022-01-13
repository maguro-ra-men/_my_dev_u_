"""
get stock data
    米国開始時間　jst23:30 夏時間jst22:30
    sample米国:df = data.DataReader('SOXL', 'yahoo',"2022-01-05","2022-01-07")#当日取れた
    sample日本:df = data.DataReader('4293.T', 'yahoo',"2022-01-05","2022-01-06")#当日取れた
"""
#関数引数で渡されるはずのdrange
drange='past6month'
drange='today'

#引数で渡されるはずのdf
import pandas as pd
df_wlist=pd.DataFrame(
    data={'ticker': ['PFE','MSFT','AAPL','SOXL']}
    ) #仮で作成

#drangeからgetする期間判定//tech chart算出の為、実際期間+21日必要。ざっくり多めに取る
import datetime
from dateutil.relativedelta import relativedelta #～日後、ヶ月後を算出可能なライブラリ
if drange=='past6month':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-7)
elif drange=='today':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-1)

#get stock data
from pandas_datareader import data
df,df_temp='',''
for r in df_wlist.index:
    df_temp = data.DataReader(df_wlist.at[r,'ticker'], 'yahoo',fdate,tdate)
    df_temp=df_temp.assign(ticker=df_wlist.at[r,'ticker']) 
    if len(df)==0:
        df=df_temp
    else:
        df=df.append(df_temp)

"""
df整形
"""
import pandas as pd
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
Tech chart追加
"""
#明確なloop終了日を算出 (m6)6ヶ月前の1日　（today）前回稼働で未確定のcloseがあるかも。-5日にしよう
if drange=='past6month':
    edate = tdate.replace(day=1) + relativedelta(months=-6)
elif drange=='today':
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
table insert
"""
from sqlalchemy import create_engine
con = create_engine('mysql+mysqlconnector://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo')
# format: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
df.to_sql('stock_prices', con, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
pd.read_sql('SELECT * FROM stock_prices;', con) #確認

"""
table 重複排除（pandasがupsert不可能でデータ重複する為）
"""
#重複排除
import pymysql
connection = pymysql.connect(host='localhost', port=50000, user='kazu', password='11cRIudj9aSi', db='dev_moshimo')
try:
    with connection.cursor() as cursor:
        sql = ('''
               DELETE FROM dev_moshimo.stock_prices
               WHERE create_time IN (
                   SELECT create_time FROM (
                       SELECT create_time FROM dev_moshimo.stock_prices
                       GROUP BY date,ticker
                       HAVING COUNT(*) > 1
                       ) AS tmp
                   );
               ''')
        cursor.execute(sql)
        connection.commit()
        print('sql重複削除 実行完了')
finally:
    connection.close()
    print('connection close')


print('end')

