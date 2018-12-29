import pymysql
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306,db='lianjia')
cursor = db.cursor()
sql='CREATE TABLE IF NOT EXISTS xiaoqu (id VARCHAR(255) NOT NULL,title VARCHAR(255) NOT NULL,PRIMARY KEY (id))'

cursor.execute(sql)
db.close()