import pandas as pd
import numpy as np
import pymysql

conn = pymysql.connect(host='localhost',user='root',
                       passwd='123456',port=3306,
                       db='huxiu')
cursor = conn.cursor()
sql = "select * from news"
data = pd.read_sql(sql,conn)
# print(data.shape)
# print(data.info())
# print(data.head())
data['name'].replace('©','',inplace=True,regex=True)
#字符改为数值
data = data.apply(pd.to_numeric,errors='ignore')
#为了方便，将write_time列，包含几小时前和几天前的行，都替换为11月30日。
data['writetime'] = data['writetime'].replace('.*前','2018-11-30',regex=True)
data['writetime'] = pd.to_datetime(data['writetime'])

#检查是否有重复值
# print(any(data.duplicated()))
# data_duplicated = data.duplicated().value_counts()
# print(data_duplicated)
# data = data.drop_duplicates(keep='first')
# data = data.reset_index(drop=True)

data['title_length'] = data['title'].apply(len)
data['year'] = data['writetime'].dt.year

print(data.describe())