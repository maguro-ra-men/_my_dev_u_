from sqlite3 import Timestamp
from time import time
from sqlalchemy import Column, Integer, String, DateTime
from db import Base
from datetime import datetime
import pytz #for use time zone


# テーブルのフィールドを定義
class Student(Base):
    __tablename__ = 'students'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))

# データベースにテーブルを作成
#Base.metadata.create_all(bind=engine)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
                
    def __repr__(self):
        #return f'<Tickers {self.ticker!r}>'
        return f'<Stundent( {self.id},{self.name})>'

#以前↓
class Tickers(Base):  
    __tablename__ = 'tickers'  
    #__table_args__ = {'extend_existing': True}
    __table_args__=({"mysql_charset": "utf8mb4"})
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    purchase_format = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, stock_name=None, ticker=None, purchase_format=None,
                 currency=None, exchange=None, create_time=None):
        self.stock_name = stock_name
        self.ticker = ticker
        self.purchase_format = purchase_format
        self.currency = currency
        self.exchange = exchange
        self.create_time = create_time
        
    def __repr__(self):
        #return f'<Tickers {self.ticker!r}>'
        return f'<Tickers( {self.id},{self.stock_name},{self.create_time})>'
  

#if __name__ == '__main__':
#    print("これは自作モジュールです")

#if __name__ == '__main__':  
#    main(sys.argv)