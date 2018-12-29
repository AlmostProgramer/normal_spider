import requests
import pymysql
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import json
headers = {
    'Host': 'bj.lianjia.com',
    'Referer': 'https://bj.lianjia.com/chengjiao/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
}

#ip限制，故只取前20页的小区
def get_xiaoqu():
    id_list = []
    page = 20
    l = list(range(1,page+1))
    for i in l:
        url = 'http://bj.lianjia.com/xiaoqu/pg'+str(i)
        try:
            r = requests.get(url,headers=headers,timeout=3)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text,'lxml')

                for li in soup.select('.xiaoquListItem'):
                    data = {}
                    id = li['data-id']
                    title = li.select('.info .title a')[0].get_text()
                    data['id'] = id
                    data['title'] = title
                    save_to_mysql(data)
                    id_list.append(data)
            else:
                print(url)
                l.append(i)
        except Exception as e:
            print(e)
    return id_list
def save_to_mysql(data):
    table = 'xiaoqu'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    db = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        port=3306,
        db='lianjia'
    )
    cursor = db.cursor()
    sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table,keys=keys,values=values)
    # cursor.execute(sql,tuple(data.values()))
    try:
        if cursor.execute(sql,tuple(data.values())):
            db.commit()
    except Exception as e:
        print(e)
        print('Data failed insert mysql!')
    db.close()

if __name__ == '__main__':

    s = get_xiaoqu()
    df = pd.DataFrame(s)

    print(df.head())
    print(len(df))

    df.to_csv('xiaoqu_df.csv')

    # print(len(s))
    # with open('xiaoqu_id.csv','a',newline='',encoding='utf-8') as f:
    #     write = csv.writer(f)
    #     for data in s:
    #         write.writerow([data])
    #     f.close()