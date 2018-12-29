import re
import time
import requests
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
import pymongo
import pymysql

client = pymongo.MongoClient('localhost',27017)
db = client.Maoyan
mongo_collection = db.maoyan

head = """
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.8
Cache-Control:max-age=0
Connection:keep-alive
Host:maoyan.com
Upgrade-Insecure-Requests:1
Content-Type:application/x-www-form-urlencoded; charset=UTF-8
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36
"""

def str_to_dict(header):
    """
    构造请求头，可以在不同函数里构造不同的请求头
    """
    header_dict = {}
    header = header.split('\n')
    for h in header:
        h = h.strip()
        if h:
            k,v = h.split(':',1)
            header_dict[k] = v.strip()
    return header_dict

def get_url():
    """
    获取电影详情页链接
    """
    for i in range(30, 31):
        time.sleep(5)
        url = 'http://maoyan.com/films?showType=3&yearId=13&sortId=3&offset=' + str(i)
        host = """Referer:http://maoyan.com/films?showType=3&yearId=13&sortId=3&offset=0
        """
        header = head+host
        headers = str_to_dict(header)
        response = requests.get(url=url,headers=headers)
        html = response.text
        soup = BeautifulSoup(html,'html.parser')
        #本页中所有包含电影详情页链接的div
        data_1 = soup.find_all('div', {'class': 'channel-detail movie-item-title'})
        #本页中包含评分数据（评分数据或暂无评分）的div
        data_2 = soup.find_all('div', {'class': 'channel-detail channel-detail-orange'})
        num = 0
        #遍历包含电影详情页链接的div
        for item in data_1:
            num += 1
            time.sleep(10)
            #将每个div中的详情页链接取出
            url_l = item.select('a')[0]['href']
            #只选取有评分数据的url
            if data_2[num-1].get_text()!='暂无评分':
                url = 'http://maoyan.com'+url_l
                #构造生成器
                yield url
            else:
                print("The Work Is Done")
                break

def get_message(url):
    """
    获取电影详情页里的信息
    """
    time.sleep(5)
    data = {}
    host = """refer: http://maoyan.com/news
    """
    #常规的request请求步骤
    header = head + host
    headers = str_to_dict(header)
    response = requests.get(url=url,headers=headers)
    u = response.text

    #目标网页的正式解析
    soup = BeautifulSoup(u,"html.parser")
    #包含隐藏信息的目标，包括用户评分，多少人评分，票房三项
    mw = soup.find_all('span',{'class':'stonefont'})
    #票房单位
    unit = soup.find_all('span',{'class':'unit'})
    #电影类型、（上映国家、影片时长）、上映时间
    ell = soup.find_all('li',{'class':'ellipsis'})
    #电影名
    name = soup.find_all('h3',{'class':'name'})

    #取出在标签里面的信息，保存至data
    data['name'] = name[0].get_text()
    data['type'] = ell[0].get_text()
    data['country'] = ell[1].get_text().split('/')[0].strip().replace('\n','')
    data['length'] = ell[1].get_text().split('/')[1].strip().replace('\n','')
    data['released'] = ell[2].get_text()[:10]

    #解析隐藏信息，并保存至data
    (maoyan_num_list,utf8last) = get_numbers(u)
    #因为会出现没有票房的电影，所以这里需要判断
    if unit:
        #三项隐藏信息的单位
        bom = ['分',None,unit[0].get_text()]
        #遍历三项隐藏信息，用户评分，多少人评分，票房
        for i in range(len(mw)):
            #转化为utf-8编码
            moviewish = mw[i].get_text().encode('utf-8')
            moviewish = str(moviewish,encoding='utf-8')
            #遍历隐藏编码规则，找到相应的map，替换成正确的数据
            for j in range(len(utf8last)):
                moviewish = moviewish.replace(utf8last[j],maoyan_num_list[j])
            #用户评分
            if i==0:
                data['score'] = moviewish+bom[i]
            #评分参与人数
            elif i==1:
                if '万' in moviewish:
                    data['people'] = int(float(moviewish.replace('万',''))*10000)
                else:
                    data['people'] = int(float(moviewish))
            #票房
            else:
                if '万' == bom[i]:
                    data['box_office'] = int(float(moviewish)*10000)
                else:
                    data['box_office'] = int(float(moviewish)*100000000)
    #没有票房的电影
    else:
        bom = ['分', None, 0]
        for i in range(len(mw)):
            moviewish = mw[i].get_text().encode('utf-8')
            moviewish = str(moviewish, encoding='utf-8')
            for j in range(len(utf8last)):
                moviewish = moviewish.replace(utf8last[j], maoyan_num_list[j])
            if i == 0:
                data['score'] = moviewish + bom[i]
            else:
                if '万' in moviewish:
                    data['people'] = int(float(moviewish.replace('万', '')) * 10000)
                else:
                    data['people'] = int(float(moviewish))
        data['box_office'] = bom[i]

    return data

"""
关于fontTools进行字体的反爬破解
    两个字体文件对字符（比如8）的字形定义保持一致
    font1.woff 字符8 >>> name1 >>> 字形定义 == 字形定义 <<<name2 <<<font2.woff 字符8
    根据这样一个关系，所以根据基准字体文件为新字体文件建立映射关系
"""
def get_numbers(u):
    """
        对猫眼的文字反爬进行破解
        """
    #解析出字体资源的链接
    cmp = re.compile(",\n           url\('(//.*.woff)'\) format\('woff'\)")
    rst = cmp.findall(u)
    #请求字体资源
    ttf = requests.get("http:"+rst[0],stream=True)
    # 将资源信息写入woff文件
    with open("maoyan.woff", "wb") as pdf:
        for chunk in ttf.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk)
    #woff文件的初始化
    base_font = TTFont('base.woff')
    maoyanFont = TTFont('maoyan.woff')
    #获取字体资源的name数组
    maoyan_unicode_list = maoyanFont['cmap'].tables[0].ttFont.getGlyphOrder()
    maoyan_num_list = []
    #base.woff的数字编码对应关系
    base_num_list = ['.', '4', '3', '8', '1', '2', '6', '5', '7', '9', '0']
    base_unicode_list = ['x', 'uniF7BE', 'uniF8A4','uniE9EF', 'uniE6AA','uniF0A7','uniEB96','uniEA5E','uniE7CB','uniEC07','uniF395']
    #根据name的对应关系，找到对应的数字list
    for i in range(1,12):
        for j in range(len(base_unicode_list)):
            if maoyanFont['glyf'][maoyan_unicode_list[i]] == base_font['glyf'][base_unicode_list[j]]:
                maoyan_num_list.append(base_num_list[j])
                break
    #将unicode转化为utf-8的形式，因为在源码上显示的为utf-8所以需要转化
    maoyan_unicode_list[1] = 'uni0078'
    # eval()函数用来执行一个字符串表达式，并返回表达式的值
    utf8List = [eval(r"'\u" + uni[3:] + "'").encode("utf-8") for uni in maoyan_unicode_list[1:]]
    utf8last = []
    for i in range(len(utf8List)):
        utf8List[i] = str(utf8List[i], encoding='utf-8')
        utf8last.append(utf8List[i])
    #返回（数字list,长度与数字list相同的并一一对应的utf-8编码list）
    return (maoyan_num_list, utf8last)

def to_mysql(data):
    table = 'films'
    keys = ','.join(data.keys())
    values = ','.join(['%s']*len(data))
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         port=3306,
                         db='maoyan'
                         )
    cursor = db.cursor()
    sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table,keys=keys,values=values)
    try:
        if cursor.execute(sql,tuple(data.values())):
            print("Successful")
            db.commit()
    except:
        print("Failed")
        db.rollback()
    db.close()

def to_mongodb(data):
    try:
        if mongo_collection.update_one(data,{'$set':data},upsert=True):
            print('successful saving!')
        else:
            print('saving failed!')
    except Exception as e:
        print(e)

def get_data():
    for url in get_url():
        data=get_message(url)
        print(data)
        # to_mysql(message)
        to_mongodb(data)
        print(url)
        print('---------------^^^Film_Message^^^-----------------')

if __name__ == '__main__':
    get_data()