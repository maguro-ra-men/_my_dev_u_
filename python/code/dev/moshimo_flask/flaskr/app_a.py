#pj用moduleのpython pathを通す。（os.path.dirname～～ではcdまでしか取れずNGだった）
import sys
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr")

from flask import Flask, request
from flask import render_template, request, redirect
from jinja2 import Template, Environment, FileSystemLoader #不要？

from db import *
from models.tickers import Tickers

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    #db_session.remove()
    if exception and session.is_active:
        db_session.rollback()
        print(1)
    else:
        #db_session.commit()
        pass
        print(2)

    db_session.close()



from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()



init_db()

u = Tickers('kazu', '11cRIudj9aSi@localhost:50000')
u = Tickers('admin', 'admin@localhost')
db_session.add(u)
db_session.commit()
print(u)

Base.metadata.create_all(engine)

db_session.flush()
print(u)
db_session.begin()
db_session.rollback()


val = Tickers.query.all()
for name in val:
    print(name)

val = Tickers.query(Tickers.stock_name).all()
print(val)
for name in val:
    print(name)

val = Tickers.query.filter(Tickers.id == 1).first()
for name in val:
    print(name)
print(val)


import pandas as pd
from sqlalchemy import create_engine
#con = create_engine('mysql+mysqlconnector://kazu:11cRIudj9aSi@localhost:50000/dev_moshimo')
con = ''
con = engine
print(con)
# format: 'mysql+mysqlconnector://[user]:[pass]@[host]:[port]/[schema]'
#df.to_sql('tickers', con, if_exists='append', index=False) #単純なinsert
#print('sql append実行完了')
pd.read_sql('SELECT * FROM tickers;', con) #確認



print(df)
Tickers.query.all().filter(Tickers.id == '1').first()
Tickers.query(id,stock_name).filter(Tickers.id == '1').first()

Tickers.query(User).filter(User.id==2).first()
print(userx.id, userx.name, userx.fullname)

import sys
print(database)