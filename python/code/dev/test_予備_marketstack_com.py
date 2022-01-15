# -*- coding: utf-8 -*-
"""
marketstack.comはアクセス増えると有料。有料なら当日データも取れる。1回に100行しか取れない。
日付指定も一応可能。100行しか取れないけど。
url='http://api.marketstack.com/v1/eod?date_from=2021-06-01&date_to=2022-01-05&access_key=341a1d9e554bc03a66473ae82491275a&symbols=aapl'
pandas_datareaderが無料で3年くらい取れてしまい、不要になった。
"""

"""
api get//marketstack.com//
"""
#apiアクセス変動
date_from=1
date_to=1
tickers='soxl'

#apiアクセス固定
base_url='http://api.marketstack.com/v1/'
api_function='eod'
access_key='?access_key=341a1d9e554bc03a66473ae82491275a'
syntax='&symbols='


url = base_url + api_function + access_key + syntax + tickers
import requests
api_result = requests.get(url)

#date期間長く指定しても100日しか返せない。
"""
T:データ整形
"""
#json認識、ノーマライズ、df格納
import json
api_response = api_result.json() #pyにjsonと認識させる
import pandas as pd
api_response=pd.json_normalize(api_response, record_path='data') #json_normalize()を使うと、ネストした辞書もキーごとに個別の列として変換される
df = pd.DataFrame(api_response)
#create_timeを追加
import datetime
ad_df=df
ad_df['create_time']=ad_df['date']
ad_df=ad_df.assign(create_time=datetime.datetime.now())
#dateがISO8601と思われる型だがtable格納不能。data型にする為、変換
mdf=ad_df
mdf['date'] = pd.to_datetime(mdf['date'])
mdf['date']=mdf['date'].dt.date
df=mdf


"""
↓確認用　あとでけす
"""
df
df.to_csv('to_csv_out.csv') #dirは　ls　で確認
print(df.dtypes)

"""
table insert
"""
from sqlalchemy import create_engine
con = create_engine('mysql+mysqlconnector://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo')
# format: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
df.to_sql('stock_api', con, if_exists='append', index=False) #単純なinsert
print('sql append実行完了')
pd.read_sql('SELECT * FROM stock_api;', con) #確認

"""
table 重複排除（pandasがupsert不可能でデータ重複する為）
"""
#重複排除
import pymysql
connection = pymysql.connect(host='localhost', port=50000, user='kazu', password='11cRIudj9aSi', db='dev_moshimo')
try:
    with connection.cursor() as cursor:
        sql = ('''
               DELETE FROM dev_moshimo.stock_api
               WHERE create_time IN (
                   SELECT create_time FROM (
                       SELECT create_time FROM dev_moshimo.stock_api
                       GROUP BY date,symbol
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

