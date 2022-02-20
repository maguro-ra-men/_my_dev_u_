#csvのフォルダpath定義
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
import pandas as pd
"""
定数を変数に代入
"""
df = pd.read_csv(f'{rootpath}\\const.csv', index_col="index")

app_drange=df.loc[0,'drange']
app_rtype=df.loc[0,'app_rtype']
print(f'DataRange→　{app_drange}')
print(f'RunType→　{app_rtype}')

"""
date rangeの確定
"""
#app_drangeからgetする期間判定//tech chart算出の為、実際期間+21日必要。ざっくり多めに取る
import datetime
from dateutil.relativedelta import relativedelta #～日後、ヶ月後を算出可能なライブラリ
if app_drange=='past6month':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-7)
elif app_drange=='today':
    tdate=datetime.date.today()
    fdate = tdate.replace(day=1) + relativedelta(months=-1)
"""
API DATAからone dayで取り出した値を変数に代入
"""
class API_DATA_ONE_DAY():
    def one_day():
        df = pd.read_csv(f'{rootpath}\\one_day_wlist.csv', index_col="index")

        ticker = df.loc[0,'ticker']
        ex_rate = df.loc[0,'ex_rate']
        c_price = df.loc[0,'c_price']
        high_price = df.loc[0,'high_price']
        low_price = df.loc[0,'low_price']
        mov_avg = df.loc[0,'mov_avg']
        bb_highs = df.loc[0,'bb_highs']
        bb_lows = df.loc[0,'bb_lows']
        date = df.loc[0,'date']
        return ticker, ex_rate, c_price, high_price, low_price, mov_avg, bb_highs, bb_lows, date
