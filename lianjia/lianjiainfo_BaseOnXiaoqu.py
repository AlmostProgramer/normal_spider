import requests
from bs4 import BeautifulSoup
import csv
import time
import pymysql
import pandas as pd

headers = {
    'Host': 'bj.lianjia.com',
    'Referer': 'https://bj.lianjia.com/chengjiao/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
}

def parse_xiaoqu(id,url,page):
    house_list = []

    r = requests.get(url,headers=headers,timeout=5)
    soup = BeautifulSoup(r.text, 'lxml')
    num = soup.select('.content .total span')[0].get_text()
    num = int(num)
    datas = soup.select('li .info')
    print('小区房源总数：', num, '第%d页房源数:' % page, len(datas))
    if len(datas)==0:
        return (num,[],0)
    for i in datas:
        data = {}
        data['id'] = id
        data['title'] = i.select('.title a')[0].get_text()
        data['info'] = i.select('.address .houseInfo')[0].get_text()
        data['floor'] = i.select('.flood .positionInfo')[0].get_text()
        data['info'] = data['info'].replace('\xa0','')
        data['date'] = i.select('.address .dealDate')[0].get_text()
        if data['date'] == '近30天内成交':
            p_url = i.select('.title a')[0].attrs['href']
            r = requests.get(p_url,headers=headers,timeout=5)
            soup = BeautifulSoup(r.text,'lxml')
            data['date'] = soup.select('.house-title .wrapper span')[0].get_text()
            data['price'] = soup.select('.overview .dealTotalPrice i')
            data['unitprice'] = soup.select('.overview .info .price b')
            if len(data['price']) == 0:
                data['price'] = '暂无价格'
            else:
                data['price'] = data['price'][0].get_text()
            if len(data['unitprice']) == 0:
                data['unitprice'] = '暂无单价'
            else:
                data['unitprice'] = data['unitprice'][0].get_text()
        else:
            data['price'] = i.select('.address .totalPrice span')
            data['unitprice'] = i.select('.flood .unitPrice span')
            if len(data['price'])==0:
                data['price'] = '暂无价格'
            else:
                data['price'] = data['price'][0].get_text()
            if len(data['unitprice'])==0:
                data['unitprice'] = '暂无单价'
            else:
                data['unitprice'] = data['unitprice'][0].get_text()
        # print(data)
        save_to_mysql(data)
        house_list.append(data)

    return (num,house_list,1)

def crow_xiaoqu(id):
    """
    抓取第一页的数据
    """
    url = 'https://bj.lianjia.com/chengjiao/c%d/' % int(id)
    h_list = []
    # fail_list = []
    try:
        result = parse_xiaoqu(id,url,1)
    except:
        time.sleep(2)
        result = parse_xiaoqu(id,url,1)
    num = result[0]
    while(num==0):
        time.sleep(2)
        result = parse_xiaoqu(id,url, 1)
        num = result[0]
    new_list = result[1]
    for data in new_list:
        if data not in h_list:
            h_list.append(data)
    # print('小区第1页抓取了'+str(len(h_list))+'条数据!')
    pages = 1
    if num > 30:
        if num%30 == 0:
            pages = num//30
        else:
            pages = num//30+1
    # 抓取第一页之后的数据
    # pages=5
    list_page = list(range(2,pages+1))
    for page in list_page:
        new_url = 'https://bj.lianjia.com/chengjiao/pg'+str(page)+'c'+str(id)
        try:
            result = parse_xiaoqu(id,new_url,page)
            status = result[2]
            if status==1:
                new_list=result[1]
                for data in new_list:
                    if data not in h_list:
                        h_list.append(data)
                # print('小区第%s页抓取了%s条数据!'.format(page,len(h_list)))
            else:
                list_page.append(page)
        except Exception as e:
            list_page.append(page)
            print(e)
    return h_list

def save_to_mysql(data):
    table = 'chengjiao'
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
    # id = '1111027381003'
    # url = 'https://bj.lianjia.com/chengjiao/c%d/'%int(id)
    # num,house_list,statu=  parse_xiaoqu(url,1)
    # print(house_list)
    # save_to_mysql(house_list[0])

    # id_list = []
    # with open('xiaoqu_id.csv','r') as f:
    #     read = csv.reader(f)
    #     for id in read:
    #         id_list.append(id[0])
    df = pd.read_csv('xiaoqu_df.csv')
    df = df[['id','title']]
    # print(df.head())
    # print(df['id'][1])
    # print(int(df['id'][1]))
    # print('{xiaoqu}小区抓取了{length}条数据！'.format(xiaoqu=df['title'][1], length=int(df['id'][1])))
    for x in range(0,3):
        print('###############正在抓取第'+str(x+1)+'个小区###################')
        time.sleep(1)
        h_list = crow_xiaoqu(int(df['id'][x]))
        print('{xiaoqu}小区抓取了{length}条数据！'.format(xiaoqu=df['title'][x],length=len(h_list)))




