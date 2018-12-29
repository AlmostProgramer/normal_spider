import pymysql
import time

class Mysql:
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    def __init__(self):
        try:
            self.db=pymysql.connect('localhost','root','123456','aiwen')
            #获取数据库操作游标
            self.cur=self.db.cursor()
        except pymysql.Error as e:
            print (self.getCurrentTime(),'connect failed,the reason is '+e)
    #将字典数据输入数据库
    def inserData(self,table,my_dict):
        try:
            self.db.set_charset('utf8')
            cols=', '.join(my_dict.keys())
            values='"," '.join(my_dict.values())
            sql="INSERT INTO %s (%s) VALUES (%s)" %(table,cols,'"'+values+'"')
            try:
                result=self.cur.execute(sql)
                insert_id=self.db.insert_id()
                self.db.commit()
                if result:
                    return insert_id
                else:
                    return 0
            except pymysql.Error as e:
                self.db.rollback()
                if "key 'PRIMARY'" in e.args[1]:
                    print(self.getCurrentTime(),'the data is exist!')
                else:
                    print(self.getCurrentTime(),'insert failed,the reason is %d:%s'%(e.args[0],e.args[1]))
        except pymysql.Error as e:
            print(self.getCurrentTime(),'database error,the reason is %d:%s'%(e.args[0],e.args[1]))
