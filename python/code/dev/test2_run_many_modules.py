# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 12:34:59 2022

@author: kazu
"""

from _my_lib_ import test3_write_db_one_field as test
a=100
b=200
d =test.dbw(a,b)
print(d)




"""
↓確認用　あとでけす
"""
df
df.to_csv('to_csv_out.csv') #dirは　ls　で確認
print(df.index)
print(df.dtypes)




