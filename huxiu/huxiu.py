import requests
from pyquery import PyQuery as pq
import json
import pymysql
import re
import datetime

headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }

def get_page_index():
    #这个url我找不到了，之前是虎嗅用的是这个网址post来实现Ajax动态爬取的
    #现在它用的是get来完成Ajax的，但是这个之前的网址还是有用
    url = "https://www.huxiu.com/v2_action/article_list"
    for page in range(10,100):
        response = requests.post(url=url,data={'page':page},headers=headers)
        if response.status_code==200:
            #也是为了熟悉yield原理，所以实践了一下（不是很有必要，代码不好阅读）
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
            'writetime': parse_writetime(item('.time').text()),
            'comment': item('.icon-cmt+ em').text(),
            'favorites': item('.icon-fvr+ em').text(),
            'abstract': item('.mob-sub').text()
            }
    # print (data)

#将几天前格式的日期转化为正确格式日期
def parse_writetime(writetime):
    pattern = re.compile('([0-9])天前')
    timedelta = re.search(pattern,writetime)
    if timedelta:
        return str(datetime.date.today()-datetime.timedelta(days=int(timedelta.group(1))))
    else:
        return writetime


#保存字典类型数据至MySQL(通用，但要记得要创建相应的数据库和表才能成功保存）
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
    except Exception as e:
        print(e)
        db.rollback()

def main():
    for index in get_page_index():
        for data in parse_page_index(index):
            print(data)
            save_to_mysql(data)
            print('-----------next--------------')



if __name__ == '__main__':
    main()
