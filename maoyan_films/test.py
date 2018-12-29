# import pymysql
#
# conn = pymysql.connect(host='localhost',port=3306,
#                        user='root',passwd='123456',db='maoyan')
# cur = conn.cursor()
# table='films'
# data={'length':'100mins','country':'china','name':'I am not a god','released':'2018-07-05','type':'haha','score':'10','people':123456,'box_office':0}
# keys=','.join(data.keys())
# values=','.join(['%s']*len(data))
# sql = 'INSERT INTO {table}({keys})VALUES ({values})'.format(table=table,keys=keys,values=values)
# if cur.execute(sql,tuple(data.values())):
#     print("successful")
# conn.commit()
# conn.close()
# # print(keys)
# # print(values)
# # print(tuple(data.values()))
# for i in range(30,300,30):
#     print(i)
# data = {'a':'asdf','b':'werq','c':123}
# print(data.values())
for i in range(2,3):
    print(i)