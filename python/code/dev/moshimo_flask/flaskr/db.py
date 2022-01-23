from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#import pymysql

# エンジンの定義
database = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    "kazu",
    "11cRIudj9aSi",
    "localhost",
    "50000",
    "dev_moshimo",
)
#engine = create_engine('%s' % (database), encoding="utf-8",echo=True)

engine = create_engine(
    database,
    encoding="utf-8",
    echo=True
    )
# sqlalchemyでデータベースのテーブルを扱うための宣言
Base = declarative_base()
 
# データベースに接続するためのセッションを準備
#Session = sessionmaker(bind=engine)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)   

#Session = sessionmaker(bind=engine) #テストしたapp_bではナシで成功していたのでOFFってみる
Base.query = session.query_property()
#session = Session() #参考サイトの順番では2行上である。大丈夫か？appからだとエラーになるのでコメント化した


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models.tickers import Tickers
    from models.tickers import Student
    from models.test_class import Tickers
    Base.metadata.create_all(bind=engine)



#メモ上記でレコード追加、selectは成功した。
"""
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

"""

"""
2022/1/18 flask公式に沿いたかったが難航、原因つかめず↓に切り替えた。
【TIPS】PythonのSQLAlchemy使い方解説(SQLite/MySQL対応)
https://engineer-lifestyle-blog.com/code/python/sqlalchemy-usage-for-mysql-sqlite-postgresql/
"""