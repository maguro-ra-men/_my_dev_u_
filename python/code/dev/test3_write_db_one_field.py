# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 12:36:50 2022

@author: kazu
"""

"""
#db接続、書き込みテスト
"""
def dbw(a,b):
    a=a+1
    b=b+2
    import mysql.connector
    
    cnx = None
    
    try:
        cnx = mysql.connector.connect(
            user='kazu',  # ユーザー名
            password='11cRIudj9aSi',  # パスワード
            host='localhost',  # ホスト名(IPアドレス）
            database='dev_moshimo',  # データベース名
            port='50000'
        )
    
        cursor = cnx.cursor()
    
        cursor.execute("SELECT * FROM trade WHERE id = 1")
        print(cursor.fetchone())
    
        sql = ('''
        UPDATE  trade
        SET     Investment_funds = %s
        WHERE   id = %s
        ''')
    
        param = ('123', 1)
    
        cursor.execute(sql, param)
        cnx.commit()
    
        cursor.execute("SELECT * FROM trade WHERE id = 1")
        print(cursor.fetchone())
    
        cursor.close()
    
    except Exception as e:
        print(f"Error Occurred: {e}")
    
    finally:
        if cnx is not None and cnx.is_connected():
            cnx.close()

    a=a+100
    b=b+200
    return a,b


    
