import pandas as pd
from pandas import Series,DataFrame
from bs4 import BeautifulSoup
import urllib.request as urlrequest
from selenium import webdriver
import time
# import matplotlib.pyplot as plt


def main():
    df=pd.read_excel(r'C:\Users\lenovo\Desktop\data.xlsx')
    df2=df.set_index(['class'])
    quan=Series([0.2,0.3,0.15,0.35],index=df2.columns)
    df_jiaquan=df2.mul(quan)
    df_jiaquan['sum']=df_jiaquan.sum(axis=1)
    df_jiaquan_sorted=df_jiaquan.sort_values(by='sum',ascending=False)
    print(df_jiaquan_sorted)

if __name__ == '__main__':
    main()