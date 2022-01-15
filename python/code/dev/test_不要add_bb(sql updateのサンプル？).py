# -*- coding: utf-8 -*-
"""
不要になる。sql updateのサンプルになるかも？深く試してないような。。
"""


"""
データ追加対象record取得、dfへ
"""
import pandas as pd
from sqlalchemy import create_engine
con = create_engine('mysql+mysqlconnector://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo')
# format: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
df=pd.read_sql('select * from stock_prices   WHERE date BETWEEN DATE_SUB(date(now()), INTERVAL 200 day) AND DATE_SUB(date(now()), INTERVAL 0 day)  ORDER BY date desc limit 20;', con) #確認
df = pd.DataFrame(df)

"""
不要列の削除、計算列をnullに
"""
df=df.drop(columns=['open', 'high', 'low', 'exchange', 'volume']) #カラム削除

"""
計算列をnullに
"""
df=df.assign(a_ema20close=0,a_bb20ema=0,a_bb20high=0,a_bb20low=0,a_stdev_p=0) #列の値一括更新

"""
df内で計算結果を用意する
"""
#a_ema20close closeのdate-1～-21のAVG
i=0
for r in df.index:
    data_range=6
    s=1+i
    e=(s+data_range)
    if e > max(df.index):
        print('!!BREAK!! error：past dateが不足 s= %d e= %d r= %d' % (s,e,r))
        break
    df.at[r,'a_ema20close']=df.loc[df.index[s]:df.index[e], 'close'].mean()
    i=i+1
else:
    print('!!FINISH!!')
    print(df.a_ema20close)



#期間の区切りどうしよ。どこまであればok？
#複数symbolの処理対策
"""
↓確認用　あとでけす
"""
df
df.to_csv('to_csv_out.csv') #dirは　ls　で確認
print(df.dtypes)


"""
dfの計算結果をloop処理で1recordずつupdateする
"""
#loop箇所はsql～comitの前後かな？その範囲を複数実行して個別に成功する事は検証済み。
a=111

#add bb
import pymysql
connection = pymysql.connect(host='localhost', port=50000, user='kazu', password='11cRIudj9aSi', db='dev_moshimo')
try:
    with connection.cursor() as cursor:
        sql = ('''
               update stock_api  set work_id = %s ;
               ''')
        param = (a)#sqlは%s　paramにpython変数
    
        cursor.execute(sql, param)
        connection.commit()


        print('sql実行完了')
finally:
    connection.close()
    print('connection close')


print('end')

print(sql)


"""
tech chartがないレコード削除
"""

