import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE = os.getenv('mysql')
USER = os.getenv('kazu')
PASSWORD = os.getenv('11cRIudj9aSi')
HOST = os.getenv('localhost')
PORT = os.getenv('50000')
DB_NAME = os.getenv('dev_moshimo')

CONNECT_STR = '{}://{}:{}@{}:{}/{}'.format(DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME)
"""
CONNECT_STR = 'mysql+pymysql://{user}:{password}@{host}/{db-name}?charset=utf8'.format(**{
      'user': 'kazu',
      'password': '11cRIudj9aSi',
      'host': 'localhost',
      'port':'50000',
      'db_name': 'dev_moshimo'
  })
"""
print(CONNECT_STR)
print(CONNECT_STR)
ENGINE = create_engine(
    CONNECT_STR,
    encoding = "utf-8",
    echo=False
)

# Sessionの作成
# ORM実行時の設定。自動コミットするか、自動反映するなど。
session = scoped_session(
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()