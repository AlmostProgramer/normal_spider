import pymysql
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306)
cursor = db.cursor()
cursor.execute("CREATE DATABASE lianjia DEFAULT CHARACTER SET utf8mb4")
db.close()