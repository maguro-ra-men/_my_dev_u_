# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (
    "kazu",
    "11cRIudj9aSi",
    "localhost",
    "50000",
    "dev_moshimo",
)
ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
)
session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)
Base = declarative_base()
Base.query = session.query_property()

"""
これは通った
import pandas as pd
pd.read_sql('SELECT * FROM stock_prices;', ENGINE) #確認
"""