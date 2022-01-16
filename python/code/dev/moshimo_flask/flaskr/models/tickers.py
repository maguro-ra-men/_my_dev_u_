# coding=utf-8  
  
import sys  
from setting import ENGINE, Base  
from sqlalchemy import Column, Integer, String  
  
  
class Tickers(Base):  
    __tablename__ = 'tickers'  
    id = Column('id', Integer, primary_key=True)  
    stock_name = Column(String)
  
def main(args):  
    # Base と ENGINE をDB接続設定からインポート
    Base.metadata.create_all(bind=ENGINE)  
  
  
if __name__ == '__main__':  
    main(sys.argv)