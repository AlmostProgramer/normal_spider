from pyecharts import Bar
import pandas as pd
import numpy as np
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    passwd='123456',
    port=3306,
    db='maoyan'
)
cursor = conn.cursor()
sql = "select * from films"
db = pd.read_sql(sql,conn)