#csvのフォルダpath定義
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
import pandas as pd
df = pd.read_csv(f'{rootpath}\\const.csv', index_col="index")

app_drange=df.loc[1,'drange']
app_rtype=df.loc[1,'app_rtype']
print(f'DataRange→　{app_drange}')
print(f'RunType→　{app_rtype}')