# -*- coding: utf-8 -*-
"""
#scraping test
"""

from selenium import webdriver
from time import sleep

#headlessを選択可能にする
headless=0
print(headless)
if headless==1:
    print('yes')
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome('C:\_my_dev\chrome_driver\chromedriver_win32\chromedriver',options=options)
else:
    print('no')
    driver = webdriver.Chrome('C:\_my_dev\chrome_driver\chromedriver_win32\chromedriver')


error_flg = False
driver.get('https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html')

#sec plf login
USERNAME='SVCP0971'
PASSWORD='rtsecrt0215'

if error_flg is False:
    try:
        username_input = driver.find_element_by_xpath('//input[@id="form-login-id"]')
        username_input.send_keys(USERNAME)
        sleep(1)
 
        password_input = driver.find_element_by_xpath('//input[@id="form-login-pass"]')
        password_input.send_keys(PASSWORD)
        sleep(1)
 
        username_input.submit()
        sleep(1)
        
    except Exception:
        print('ユーザー名、パスワード入力時にエラーが発生しました。')
        error_flg = True

sleep(2)

#要素の取得
from bs4 import BeautifulSoup
soup = BeautifulSoup(driver.page_source, features="html.parser")
el = soup.find(id='asset_total_asset').select("span:nth-of-type(1)")[0]
print(el)

driver.close()

#要素の整形、文字列→数値
import re
el=str(el)#無いと次がエラーになる
el=re.findall('<nobr>.*<span style="font-size:14px;font-weight:normal;">', el)
el=str(el)#無いと次がエラーになる
el=el.replace('<nobr>','')
el=el.replace('<span style="font-size:14px;font-weight:normal;">','')
el=el.replace(',','')
el=el.replace('[','')
el=el.replace(']','')
el=el.replace('\'','')
el=int(el)
print(type(el))
print(el)



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

    param = (el, 1)

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

"""
E:marketstack.com
"""
import requests

base_url='http://api.marketstack.com/v1/'
api_function='eod'
access_key='?access_key=341a1d9e554bc03a66473ae82491275a'
tickers='&symbols=aapl'

url = base_url + api_function + access_key + tickers

api_result = requests.get(url)

"""
T:データ整形
"""
import json
api_response = api_result.json()
import pandas as pd
df=api_response
df=pd.json_normalize(df, record_path='data')
df = pd.DataFrame(df)
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
L:insert & 重複排除（pandasがupsert不能の為）
"""
from sqlalchemy import create_engine
con = create_engine('mysql+mysqlconnector://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo')
# format: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
df.to_sql('stock_api', con, if_exists='append', index=False) #単純なinsert
pd.read_sql('SELECT * FROM stock_api;', con) #確認

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
        print('sql実行完了')
finally:
    connection.close()
    print('connection close')


print('end')


