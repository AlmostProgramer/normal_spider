import requests
from pyquery import PyQuery as pq
import json
import pymysql

headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }

def get_page_index():
    url = "https://www.huxiu.com/v2_action/article_list"
    for page in range(10,100):
        response = requests.post(url=url,data={'page':page},headers=headers)
        if response.status_code==200:
            yield response

def parse_page_index(response):
    content = response.json()['data']
    doc = pq(content)
    lis = doc('.mod-art').items()
    for item in lis:
        yield {
            'title':item('.msubstr-row2').text(),
            'url': 'https://www.huxiu.com' + str(item('.msubstr-row2').attr('href')),
            'name': item('.author-name').text(),
            'writetime': item('.time').text(),
            'comment': item('.icon-cmt+ em').text(),
            'favorites': item('.icon-fvr+ em').text(),
            'abstract': item('.mob-sub').text()
            }
    # print (data)


def save_to_mysql(data):
    table = 'news'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         port=3306,
                         db='huxiu')
    cursor = db.cursor()
    sql = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(table=table,keys=keys,values=values)
    # cursor.execute(sql, tuple(data.values()))
    # db.close()
    try:
        if cursor.execute(sql,tuple(data.values())):
            print('successful')
            db.commit()
    except:
        print('failed')
        db.rollback()

def main():
    for index in get_page_index():
        for data in parse_page_index(index):
            print(data)
            save_to_mysql(data)
            print('-----------next--------------')



if __name__ == '__main__':
    main()
