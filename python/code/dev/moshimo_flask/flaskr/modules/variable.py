#csvのフォルダpath定義
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
import pandas as pd
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