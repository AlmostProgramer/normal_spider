import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode
import os
headers = {
'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

#第一步，获取索引页的网页源码
def get_page_index(i):
    #多页
    paras = {
        'nodeids':25635,
        'pageidx':i
    }
    url = 'https://www.thepaper.cn/load_index.jsp?'+urlencode(paras)
    u = requests.get(url,headers=headers)
    if u.status_code==200: #status_code=200表示请求正常
        print('success')
        return u.text
    else:
        print("request fail")

#第二步，参数为网页源码，解析索引页网页源码，得到每个文章名和文章的详情页
def parse_page_index(html):
    soup = BeautifulSoup(html,'lxml')
    #每页文章数
    num = soup.find_all(name='div',class_='news_li')
    print(len(num))
    for i in range(len(num)):
        yield {
            'title':soup.select('h2 a')[i].get_text(),
            'url':'https://www.thepaper.cn/' + soup.select('h2 a')[i].attrs['href']
        }


# def test():
#     for i in range(5):
#         yield {
#             'url':'asdf{}.com'.format(i)
#         }
# haha = test()
# for i in haha:
#     print(i.values())

#参数为包含文章名和文章详情url的字典，输出详情url的源码
def get_page_detail(item):
    #字典的get函数，返回字典指定键的值，如果指定的键不存在返回默认值（NONE）
    url = item.get('url')
    print(url)
    try:
        u = requests.get(url,headers=headers)
        if u.status_code == 200:
            return u.text
    except RequestException:
        print('Request failed')
        return None


#第四步，解析详情url的源码，参数为网页html源码,输出包含文章标题，图片地址，图片编号的字典
def parse_page_detail(html):
    soup = BeautifulSoup(html,'lxml')

    if soup.h1:
        title = soup.h1.string
        items = soup.find_all(name='img',width=['100%','600'])
        for i in range(len(items)):
            pic_adress = items[i].attrs['src']
            yield {
                'title':title,
                'pic':pic_adress,
                'num':i+1 #图片编号
            }

#参数为字典，保存至本地文件
def save_pic(pic):
    title = pic.get('title')
    # 标题规范命名：去掉符号非法字符| 等
    title = re.sub('[\/:*?"<>|]','-',title).strip()
    url = pic.get('pic')
    num = pic.get('num')

    if not os.path.exists(title):
        os.mkdir(title)

    response = requests.get(url,headers=headers)
    try:
        if response.status_code==200:
            file_path = '{0}\{1}.{2}'.format(title,num,'jpg')
            if not os.path.exists(file_path):
                #download pictures
                with open(file_path,'wb') as f:
                    f.write(response.content)
                    print('文章"{0}"的第{1}张图片下载完成'.format(title,num))
            else:
                print('该图片%s 已下载' %title)
    except RequestException as e:
        print(e,'图片获取失败')
        return None

def main(i):

    html = get_page_index(i)
    data = parse_page_index(html)
    for item in data:
        html = get_page_detail(item)
        data2 = parse_page_detail(html)
        for pic in data2:
            save_pic(pic)

if __name__ == '__main__':
    for i in range(1,2):
        main(i)

