#csvのフォルダpath定義
rootpath='C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr'
import pandas as pd
df = pd.read_csv(f'{rootpath}\\wlist.csv', index_col="index")

class T_R_VAL():
    def trv(self,r):
            self.r = r

    ex_rate = df.loc[r,'ex_rate']
    c_price = df.loc[r,'c_price']
        #print(r)
        #print(ex_rate)

    def __init__(self,ex_rate=None,c_price=None):
        self.ex_rate = ex_rate
        self.c_price = c_price

    def __repr__(self):
        return f'<T_R_VAL( {self.ex_rate},{self.c_price})>'