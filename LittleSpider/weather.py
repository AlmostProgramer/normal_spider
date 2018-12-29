import requests
from bs4 import BeautifulSoup
import pymysql
import time

headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }

# def create_db():
#     db = pymysql.connect(host='localhost', user='root', password='123456', port=3306)
#     cursor = db.cursor()
#     cursor.execute("CREATE DATABASE weather DEFAULT CHARACTER SET utf8mb4")
#     db.close()
#
# def create_table():
#     db = pymysql.connect(host='localhost', user='root', password='123456', port=3306,db='weather')
#     cursor = db.cursor()
#     cursor.execute("CREATE TABLE IF NOT EXISTS nanchang (date VARCHAR(255) NOT NULL,quality_grade VARCHAR(255) NOT NULL,AQI INT NOT NULL,AQI_rank INT NOT NULL,PM INT NOT NULL,PRIMARY KEY (date))")
#     db.close()
# create_db()
# create_table()

def get_data():
    for i in range(1,2):
        time.sleep(5)
        url = 'http://www.tianqihoubao.com/aqi/nanchang-2018'+str('%02d' % i)+'.html'
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text,'lxml')
        trs = soup.find_all('tr')
        for j in trs[1:]:
            td = j.find_all('td')
            date = td[0].get_text().strip()
            quality_grade = td[1].get_text().strip()
            AQI = td[2].get_text().strip()
            AQI_rank = td[3].get_text().strip()
            PM = td[4].get_text()
            yield {
                'date':date,
                'quality_grade':quality_grade,
                'AQI':int(AQI),
                'AQI_rank':int(AQI_rank),
                'PM':int(PM)
            }

def save_to_mysql(data):
    table = 'nanchang'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    db = pymysql.connect(host='localhost', user='root',
                         password='123456', port=3306,db='weather')
    cursor = db.cursor()
    sql = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(table=table,keys=keys,values=values)
    if cursor.execute(sql,tuple(data.values())):
        print('successful')
        db.commit()
    db.close()

if __name__ == '__main__':

    for i in get_data():
        save_to_mysql(i)
