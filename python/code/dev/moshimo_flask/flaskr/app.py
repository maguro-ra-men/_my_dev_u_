#from distutils.dir_util import create_tree #不要？
from unicodedata import name
from flask import Flask, request, jsonify
from flask import render_template, redirect, url_for, request
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

#loging
import logging
logger = logging.getLogger(__name__)
filehandler = logging.FileHandler('test.log')
streamhandler = logging.StreamHandler()
logger.addHandler(filehandler)
logger.addHandler(streamhandler)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s][%(filename)s]')
streamhandler.setFormatter(formatter)
filehandler.setFormatter(formatter)

logger.debug('testlog_debug')
logger.info('testlog_info')
logger.error('testlog_error')

#app.py---------------------------------
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__, 
            static_url_path='/static',
            static_folder='static',
            template_folder='templates'
            ) 
logging.basicConfig(level=logging.DEBUG) #for loging
app.config['JSON_AS_ASCII'] = False
app.config["SECRET_KEY"] = "sample1201" #form追加の際追加　不要？
app.debug = True

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
        posts = session.query(Tickers).order_by(Tickers.create_time.desc()).all()
        return render_template ('tickers.html', posts=posts)

@app.route("/tickers_create",methods=['GET','POST'])
def tickers_create():
    form = Tickers_Form(request.form)
    if request.method == 'POST' and form.validate():
        ticker = request.form.get('ticker')
        stock_name = request.form.get('stock_name')
        purchase_format = request.form.get('purchase_format')
        currency = request.form.get('currency')
        exchange = request.form.get('exchange')
        post = Tickers(ticker=ticker,stock_name=stock_name,
                        purchase_format=purchase_format,currency=currency,
                        exchange=exchange)

        session.add(post)
        session.commit()
        return redirect('/tickers')
    else:
        return render_template ('tickers_create.html', form=form)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update_tickers(id):
    tickers = session.query(Tickers).get(id)
    form = Tickers_Form(request.form) #リファから変えて詳細追加

    if request.method == 'POST' and form.validate():#  and form.validate()　抜いたら進んだ？？
        tickers.ticker = request.form.get('ticker')
        tickers.stock_name = request.form.get('stock_name')
        tickers.purchase_format = request.form.get('purchase_format')
        tickers.currency = request.form.get('currency')
        tickers.exchange = request.form.get('exchange')
        session.commit()

        return redirect(url_for('tickers')) #(url_for('/tickers'))

    elif request.method == 'GET':
        form.stock_name.data = tickers.stock_name #(.data)が抜けてて6hハマった注意
        form.ticker.data = tickers.ticker
        form.purchase_format.data = tickers.purchase_format
        form.currency.data = tickers.currency
        form.exchange.data = tickers.exchange

    return render_template('tickers_each.html', form=form, id=id)

@app.route('/tickers/delete/<int:id>', methods=['GET','POST'])
def delete_tickers(id):
    tickers = session.query(Tickers).get(id)
    session.delete(tickers)
    session.commit()
    return redirect(url_for('tickers'))


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