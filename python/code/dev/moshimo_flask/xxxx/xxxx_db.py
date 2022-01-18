from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql


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
)
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)   
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models.tickers import Tickers
    Base.metadata.create_all(bind=engine)

#if __name__ == '__main__':
#    print("これは自作モジュールです")
"""
#これは通った
import pandas as pd
pd.read_sql('SELECT * FROM stock_prices;', engine) #確認
"""
