from urllib.error import HTTPError

from pandas import Series,DataFrame
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urlrequest

from selenium import webdriver
import time
import os

class LOL_crawl:
    def __int__(self):
        pass

    def get_info(self):
        str=input("请输入想要爬取壁纸的英雄昵称或名字，爬取全部英雄请输入‘ALL’：")
        return str

    def create_lolfile(self):

        lolfile='D:\LOLbizhi'
        if not os.path.exists(lolfile):
            os.makedirs(lolfile)

    def get_heroframe(self):
        #解析JS文件，生成ID对应英雄的字典
        content=urlrequest.urlopen('http://lol.qq.com/biz/hero/champion.js').read()
        str1=r'champion={"keys":'
        str2=r',"data":{"Aatrox":'
        champion=str(content).split(str1)[1].split(str2)[0]
        herodict0=eval(champion)
        herodict=dict((k,v) for v,k in herodict0.items())
        # print(herodict)

        #Selenium+PhantomJS实现动态加载
        url_Allhero='http://lol.qq.com/web201310/info-heros.shtml#Navi'
        driver=webdriver.PhantomJS(executable_path=r'E:\phantomjs-2.1.1-windows\bin\phantomjs')
        driver.get(url_Allhero)
        time.sleep(1)
        pagesource=driver.page_source
        driver.close()
        bs0bj=BeautifulSoup(pagesource,'lxml')
        #利用BeautifulSoup解析网页，生成全部英雄信息
        herolist=bs0bj.find('ul',{'class':'imgtextlist'})
        m=0
        heroframe=pd.DataFrame(index=range(0,len(herolist)),columns=['herolink','heronickname','heroname','Englishname','heroid'])
        heroinflist=herolist.find_all('a')
        for heroinf in heroinflist:
            herolink=heroinf['href']
            heronickname=heroinf['title'].split(' ')[0].strip()
            heroname=heroinf['title'].split(' ')[1].strip()
            heroframe['herolink'][m] = herolink
            heroframe['heronickname'][m] = heronickname
            heroframe['heroname'][m] = heroname
            heroframe['Englishname'][m]=heroframe['herolink'][m][21:]
            heroframe['heroid'][m]=herodict[heroframe['Englishname'][m]]
            m=m+1

        # heroframe.to_csv('./LOL/heroframe.csv',encoding='gbk',index=False)
        return heroframe

    def get_image(self,heroid,heroframe):
        #创建存放该英雄壁纸的子文件夹
        line=heroframe[heroframe.heroid==heroid].index.tolist()
        nickname=heroframe['heronickname'][line].values
        name=heroframe['heroname'][line].values
        nickname_name=str((nickname+' '+name)[0][:])
        filehero='D:\LOLbizhi'+'\\'+nickname_name
        if not os.path.exists(filehero):
            os.makedirs(filehero)

        #爬取壁纸
        for k in range(21):
            url='http://ossweb-img.qq.com/images/lol/web201310/skin/big'+str(heroid)+'0'*(3-len(str(k)))+str(k)+'.jpg'
            try:
                image=urlrequest.urlopen(url).read()
                imagename=filehero+'\\'+'0'*(3-len(str(k)))+str(k)+'.jpg'
                with open(imagename,'wb') as f:
                    f.write(image)
            except HTTPError as e:
                continue
        print('英雄' + nickname_name + '所有壁纸已爬取成功\n')

    def run(self):
        self.create_lolfile()
        inputcontent=self.get_info()
        heroframe=self.get_heroframe()

        if inputcontent.lower()=='ALL':
            try:
                allline=len(heroframe)
                for i in range(1,allline):
                    heroid=heroframe['heroid'][[i]].values[:][0]
                    self.get_image(heroid,heroframe)
            except:
                print('爬取失败或部分失败，请检查错误！')
        else:
            try:
                hero=inputcontent.strip()
                line=heroframe[(heroframe.heronickname==hero) | (heroframe.heroname==hero)].index.tolist()
                heroid = heroframe['heroid'][line].values[:][0]
                self.get_image(heroid,heroframe)
                print('完成爬取任务！\n')
            except:
                print('错误！请按照提示正确输入！\n')


def main():
    spider=LOL_crawl()
    spider.run()

if __name__ == '__main__':
    main()