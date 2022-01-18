from flask import Flask, request
from flask import render_template, request, redirect

from jinja2 import Template, Environment, FileSystemLoader #不要？
from flask_sqlalchemy import SQLAlchemy #flask 使う？
from sqlalchemy import create_engine #不要？

from datetime import datetime
import pytz #for use time zone

#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr")

#my module
from db import *
from models.tickers import Tickers

#app.py---------------------------------
app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template ('index.html')



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
        posts = Tickers.query(Tickers.stock_name).all()
    return render_template ('tickers.html', posts=posts)

@app.route("/tickers_create",methods=['GET','POST'])
def tickers_create():
    if request.method == 'POST':
        stock_name = request.form.get('stock_name')
        post = post(stock_name=stock_name)

        db.session.add(post)
        db.session.comit()
        return redirect('/tickers')
    else:
        return render_template ('tickers_create.html')


"""
おためし
"""
#from sqlalchemy import create_engine,Column, Integer, String #不要？
#from sqlalchemy.orm import scoped_session, sessionmaker #不要？
#from sqlalchemy.ext.declarative import declarative_base #不要？

#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr")

#my module
from db import *
from models.tickers import Tickers,Student

 # レコードを準備し、セッションを通してデータベースに送る
s1 = Student(name='Miura')
session.add(s1)
s2 = Student(name='Tanaka')
session.add(s2)
s3 = Student(name='Sato')
session.add(s3)
 
# データベースに送らたデータを実際に書き込む
session.commit()
 
# データベースからテーブル情報を取得する
students = session.query(Student).all()
for student in students:
    print(student.id, student.name)

#理想に置き換え-------------------------------------
session.remove()
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    #db_session.remove()
    if exception and session.is_active:
        session.rollback()
        print(1)
    else:
        #db_session.commit()
        pass
        print(2)

    session.close()

print(session)

#insert
        #name = request.form.get('name')
        name = 'test'
        post = Student(name=name)
        session.add(post)
        session.commit()

result = Student.query.filter_by(id).all()



#select
users = session.query(Student.name, Student.id).all()
for user in users:
    print(user.name,user.id)

#where
users = session.query(Student).filter(Student.name=="sato").all()
for user in users:
    print(user.name,user.id)