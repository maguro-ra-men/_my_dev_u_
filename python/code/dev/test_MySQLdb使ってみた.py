# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 23:18:36 2022

@author: kazu
"""

import MySQLdb
# データベースへの接続とカーソルの生成
connection = MySQLdb.connect(
    host='localhost',
    #port='50000',
    user='kazu',
    passwd='11cRIudj9aSi',
    db='dev_moshimo')
cursor = connection.cursor()
 
# ここに実行したいコードを入力します
cursor.execute('SET @i := 0; update stock_api  set work_id=(@i := @i +1)  ORDER BY date desc;')
 
# 保存を実行
connection.commit()
 
# 接続を閉じる
connection.close()


"""
旧　table 重複排除(stock)（pandasがupsert不可能でデータ重複する為）
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