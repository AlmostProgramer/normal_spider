import pymysql
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306,db='huxiu')
cursor = db.cursor()
sql='CREATE TABLE IF NOT EXISTS news (title VARCHAR(255) NOT NULL,url VARCHAR(255) NOT NULL,name VARCHAR(255) NOT NULL,writetime VARCHAR(255) NOT NULL,conment INT NOT NULL,favorites INT NOT NULL,abstract VARCHAR（255） NOT NULL,PRIMARY KEY (title))'

cursor.execute(sql)
db.close()