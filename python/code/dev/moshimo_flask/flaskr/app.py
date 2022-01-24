from flask import Flask, request, jsonify
from flask import render_template, request, redirect
import datetime
import pytz #for use time zone

#from jinja2 import Template, Environment, FileSystemLoader #不要？
#from flask_sqlalchemy import SQLAlchemy #flask 使う？
#from sqlalchemy import create_engine #不要？


#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr")

#my module
from db import *
from models.tickers import Tickers
from models.forms import Tickers_Form

#app.py---------------------------------
app = Flask(__name__, 
            static_url_path='/static',
            static_folder='static',
            template_folder='templates'
            ) 
app.config['JSON_AS_ASCII'] = False
app.config["SECRET_KEY"] = "sample1201" #form追加の際追加　不要？

@app.route("/")
def index():
    return render_template ('index.html')


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/about")
def about():
    return render_template ('about.html')

"""
dfを渡す
"""
import pandas as pd

index = ['2019-12-29', '2019-12-30', '2019-12-31', '2020-01-01']
columns = ['最高気温', '最低気温', '天候']
data = [[12.4, 5.1, '曇り'], [15.2, 12.0, '曇り'], [7.9, 7.2, '晴れ'], [9.8, 1.6, '晴れ']]

df = pd.DataFrame(data=data, columns=columns, index=index)

@app.route("/df")
def test():
	df_values = df.values.tolist()   # 2次元配列（中身）
	df_columns = df.columns.tolist() # 1次元配列(ヘッダー)
	df_index = df.index.tolist()     # 1次元配列(インデックス)

	return render_template('df.html', \
		df_values = df_values, \
		df_columns = df_columns, \
		df_index = df_index)

"""
tickers
"""
@app.route("/tickers",methods=['GET','POST'])
def tickers():
    if request.method == 'GET':
        #post = Post.query.all()
        posts = session.query(Tickers).all()
    return render_template ('tickers.html', posts=posts)

@app.route("/tickers_create",methods=['GET','POST'])
def tickers_create():
    form = Tickers_Form(request.form)
    if request.method == 'POST' and form.validate():
        stock_name = request.form.get('stock_name')
        ticker = request.form.get('ticker')
        purchase_format = request.form.get('purchase_format')
        currency = request.form.get('currency')
        exchange = request.form.get('exchange')
        post = Tickers(stock_name=stock_name,ticker=ticker,
                        purchase_format=purchase_format,currency=currency,
                        exchange=exchange)

        session.add(post)
        session.commit()
        return redirect('/tickers')
    else:
        return render_template ('tickers_create.html', form=form)






"""
開発用
session.remove() #エラーの値が変更されない場合実行

通ったクエリサンプル
#select
session.query(Tickers).all()

users = session.query(Student.name, Student.id).all()
for user in users:
    print(user.name,user.id)

#where
users = session.query(Student).filter(Student.name=="sato").all()
for user in users:
    print(user.name,user.id)
"""