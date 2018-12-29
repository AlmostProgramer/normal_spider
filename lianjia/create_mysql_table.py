import pymysql
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306,db='lianjia')
cursor = db.cursor()
sql='CREATE TABLE IF NOT EXISTS chengjiao (title VARCHAR(255) NOT NULL,info VARCHAR(255) NOT NULL,floor VARCHAR(255) NOT NULL,date VARCHAR(255) NOT NULL,price VARCHAR(255) NOT NULL,unitprice VARCHAR(255) NOT NULL,PRIMARY KEY (title))'

cursor.execute(sql)
db.close()