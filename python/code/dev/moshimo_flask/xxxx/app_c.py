"""
【TIPS】PythonのSQLAlchemy使い方解説(SQLite/MySQL対応)
https://engineer-lifestyle-blog.com/code/python/sqlalchemy-usage-for-mysql-sqlite-postgresql/
"""

#import sqlalchemy
#import sqlalchemy.ext.declarative
#import sqlalchemy.orm
#from sqlalchemy import *

from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

 


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