from sqlalchemy import * #Column, Integer, String
from conf.db import Base

class Tickers(Base):  
    __tablename__ = 'tickers'  
    __table_args__ = {'extend_existing': True}
    id=Column(Integer, primary_key=True, autoincrement=True)
    stock_name = Column(String)
    ticker = Column(String)
    purchase_format = Column(String)
    currency = Column(String)
    exchange = Column(String)

    def __init__(self, stock_name=None, ticker=None, purchase_format=None, currency=None, exchange=None):
        self.stock_name = stock_name
        self.ticker = ticker
        self.purchase_format = purchase_format
        self.currency = currency
        self.exchange = exchange
        
    def __repr__(self):
        #return f'<Tickers {self.ticker!r}>'
        return f'<Tickers( {self.id},{self.stock_name})>'
  

#if __name__ == '__main__':
#    print("これは自作モジュールです")

#if __name__ == '__main__':  
#    main(sys.argv)