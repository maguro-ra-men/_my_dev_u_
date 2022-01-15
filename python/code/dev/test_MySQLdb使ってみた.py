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
