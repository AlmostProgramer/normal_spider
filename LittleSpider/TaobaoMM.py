import requests
from bs4 import BeautifulSoup
import tool
import os
import urllib.request as urlrequest
import pandas as pd
from pandas import Series,DataFrame

class TaobaoMM:
    #初始化函数，定义类变量
    def __init__(self):
        self.baseUrl='http://mm.taobao.com/json/request_top_list.htm'
        self.tool=tool.Tool()

    #基于index参数获取相应URL中页面text函数
    def getpage(self,pageIndex):
        url=self.baseUrl+'?page='+str(pageIndex)
        r=requests.get(url)
        return r.text

    #解析text并返回目标内容
    def getContents(self,pageIndex):
        page=self.getpage(pageIndex)
        soup=BeautifulSoup(page,'lxml')
        items=soup.find_all('div',class_='list-item')
        contents=[]
        for item in items:
            content=[]
            content.append(item.find('div',class_='pic s60').a['href'])
            content.append(item.find('p',class_='top').a.get_text())
            content.append(item.find('p',class_='top').strong.get_text())
            content.append(item.find('p',class_='top').span.get_text())
            contents.append(content)
        return contents

    #直接获取URL（参数infoUrl）页面text
    def getDetailPage(self,infoUrl):
        url='http:'+infoUrl
        r=requests.get(url)
        return r.text

    #获取页面(参数page)中所有目标图片的URL，以列表结构返回
    def getAllImg(self,page):
        soup=BeautifulSoup(page,'lxml')
        images=soup.find('div',class_='mm-aixiu-content').find_all('img')
        imageUrls=[]
        for image in images:
            #利用try，except方法，剔除一些异常的标签数据
            try:
                imageUrls.append(image['src'])
            except:
                continue
        return imageUrls

    #将单个URL（imageUrl）中的图片写入路径（fileName)中
    def saveImg(self,imageUrl,fileName):
        url='http:'+imageUrl
        # r=requests.get(url)  为什么r没有read（）属性或方法？？？
        try:
            data=urlrequest.urlopen(url).read()
            with open(fileName,'wb') as f:
                f.write(data)
            f.close()
        except:
            pass

    # 根据参数（name)获得path，遍历（imageURLs）循环writeData
    def  saveImgs(self,imageUrls,name):
        num=1
        print('discover'+name+'have'+str(len(imageUrls))+'photos')

        for imageUrl in imageUrls:
            #将图片的后缀名格式全部改为jpg格式
            splitPath=imageUrl.split('.')
            fTail=splitPath.pop()
            if len(fTail)>3:
                fTail='jpg'
            fileName=name+'/'+str(num)+'.'+fTail
            self.saveImg(imageUrl,fileName)
            num=num+1
            #避免下载太久，只选了前5张照片
            if num>5:
                break

    #创建以参数（path）命名的文件夹
    def mkdir(self,path):
        path=path.strip()
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            print ('the'+path+'file already exist!')
            return False

    #传入页码，保存该页所有MM的图片
    def run_SavingAllbyIndex(self,pageIndex):
        num=0
        for mm in self.getContents(pageIndex):
            href=mm[0]
            name=mm[1]
            self.mkdir(name)
            imagesUrl = self.getAllImg(self.getDetailPage(href))
            self.saveImgs(imagesUrl,name)
            num=num+1
        print('there are '+str(num)+' MM\'s photos '+'saved')

def main():
    spider=TaobaoMM()
    spider.run_SavingAllbyIndex(1)


if __name__ == '__main__':
    main()
