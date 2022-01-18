"""
【TIPS】PythonのSQLAlchemy使い方解説(SQLite/MySQL対応)
https://engineer-lifestyle-blog.com/code/python/sqlalchemy-usage-for-mysql-sqlite-postgresql/
"""

from multiprocessing import connection
import sqlalchemy
from sqlalchemy import *
from sqlalchemy import create_engine
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#import pymysql
 
# エンジンの定義
#engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
#engine = sqlalchemy.create_engine('mysql+pymysql:///test_mysql.db', echo=True)
engine = sqlalchemy.create_engine('mysql+pymysql://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo?charset=utf8mb4', echo=True)
database = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    "kazu",
    "11cRIudj9aSi",
    "localhost",
    "50000",
    "dev_moshimo",
)
engine = create_engine(
    database,
    encoding="utf-8",
    echo=True
session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)   

 
# sqlalchemyでデータベースのテーブルを扱うための宣言
#Base = sqlalchemy.ext.declarative.declarative_base()
Base = declarative_base()
 
# テーブルのフィールドを定義
class Student(Base):
    __tablename__ = 'students'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    name = sqlalchemy.Column(sqlalchemy.String(30))
 
# データベースにテーブルを作成
Base.metadata.create_all(bind=engine)
 
# データベースに接続するためのセッションを準備
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()
 


from flask import Flask, request
from flask import render_template, request, redirect
from jinja2 import Template, Environment, FileSystemLoader #不要？

from db import *
from models.tickers import Tickers

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
    if exception and session.is_active:
        session.rollback()
        print(1)
    else:
        #session.commit()
        pass
        print(2)

    session.close()

session.connection()
print(session)
print(connection)


# レコードを準備し、セッションを通してデータベースに送る
s1 = Student(name='あべしがｄあであだが')
session.add(s1)
s2 = Student(name='Tanaka')
session.add(s2)
s3 = Student(name='Sato')
session.add(s3)
 
# データベースに送らたデータを実際に書き込む
session.commit()
session.remove() #エラーの値が変更されない場合実行
 
# データベースからテーブル情報を取得する
students = session.query(Student).all()
for student in students:
    print(student.id, student.name)
 
print('##############')
 
# 名前を更新する場合
s4 = session.query(Student).filter_by(name='Sato').first()
s4.name = 'Suzuki'
session.add(s4)
session.commit()
 
# データベースからテーブル情報を取得する
students = session.query(Student).all()
for student in students:
    print(student.id, student.name)
 
print('##############')
 
# レコードを削除する場合
s5 = session.query(Student).filter_by(name='Tanaka').first()
session.delete(s5)
session.commit()
 
# データベースからテーブル情報を取得する
students = session.query(Student).all()
for student in students:
    print(student.id, student.name)