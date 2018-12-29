import requests
from bs4 import BeautifulSoup
import tool
import re
import os
import MySql

class Aiwen:
    def __init__(self):
        self.baseUrl=''
        self.tool=tool.Tool()
        self.mysql=MySql.Mysql()

     # 通过网页的页码数来获取HTML
    def getPageByNum(self, page_num=1):
        page_url = "http://iask.sina.com.cn/c/74-all-" + str(page_num) + "-new.html"
        r= requests.get(page_url)
        return r.text

    def getPageByUrl(self,url):
        try:
            r=requests.get(url)
            return r.text
        except:
            print('unknown error!')
            return None

    def getAllAnswerUrl(self,page):
        soup=BeautifulSoup(self.getPageByNum(),'lxml')
        items=soup.find('ul',class_='list-group').find_all('li')
        answerurl=[]
        for item in items:
            try:
                answerurl.append(item.find('div',class_='question-title').a['href'])
            except:
                continue
        return answerurl


    # 分析问题的代码,得到问题的提问者,问题内容,回答个数,提问时间,返回page中问题信息字典的数组
    def getQuestionInfo(self, page):
        soup=BeautifulSoup(self.getPageByNum(),'lxml')
        items=soup.find('ul',class_='list-group').find_all('li')
        questionInfo=[]
        for item in items:
            questioner=item.find('div',class_='user-img').img['alt']
            text=item.find('div',class_='question-title').a.get_text()
            url=item.find('div',class_='question-title').a['href']
            ans_num0=item.find('div',class_='queation-other').find_all('span')[0].get_text()
            ans_num=ans_num0.strip('回答')
            date=item.find('div',class_='queation-other').find_all('span')[1].get_text()
            dict={
                'questioner':questioner,
                'text':text,
                'ans_num':ans_num,
                'date':date,
                'url':url
            }
            questionInfo.append(dict)
        return questionInfo

    def getText(self,html):
        pattern=re.compile('<pre.*?>(.*?)</pre>',re.S)
        match=re.search(pattern,html)
        if match:
            return match.group(1)
        else:
            return None

    # 获取问题的答案,字典内容包括回答人，回答内容，问题ID，是否最佳，时间，返回答案字典的列表
    def getAllAnswers(self, questionUrl,question_id):
        Allanswers=[]
        url='https://iask.sina.com.cn'+questionUrl
        html=self.getPageByUrl(url)
        soup=BeautifulSoup(html,'lxml')
        # text=soup.select('div.good_point div.answer_text pre')
        # if len(text)>0:
        #     ansText=self.getText(str(text[0]))
        #     ansText=self.tool.replace(ansText)
        g_answerer=soup.find('div',class_='good_point').find('div',class_='answer_tip').a.get_text()
        g_date=soup.find('div',class_='good_point').find('div',class_='answer_tip').span.get_text()
        g_text=soup.find('div',class_='good_point').find('div',class_='answer_text').pre.get_text()
        g_ans_dict={
            'answerer':g_answerer,
            'text':g_text,
            'date':g_date,
            'question_id':question_id,
            'is_good':str(1)
        }
        Allanswers.append(g_ans_dict)

        # otherAnss=soup.find('div',id='other_answer').find_all('li')
        # if otherAnss:
        #     for otherAns in otherAnss:
        #         text=otherAns.find('pre').get_text()
        #         answerer=otherAns.find('div',class_='answer_tj').find('span',class_='user_wrap').a.get_text()
        #         date=otherAns.find('div',class_='answer_tj').find('span',class_='answer_t').get_text()
        #         otheransdict={
        #             'answerer':answerer,
        #             'text':text,
        #             'date':date,
        #             'question_id':question_id,
        #             'is_good':0
        #         }
        #         Allanswers.append(otheransdict)
        return Allanswers

    def savingQueToMysqlReturnID(self,question):
        #这个段代码就完成了所有数据库存储操作，并返回了插入问题的自增ID
        insert_id=self.mysql.inserData('iask_questions',question)
        return insert_id

    def savingAnsToMysql(self,answer):
        if answer is not None:
            self.mysql.inserData('iask_answers',answer)
        else:
            print('there is no answer for this question!')

def main():
    spider=Aiwen()
    questions=spider.getQuestionInfo(spider.getPageByNum())
    for question in questions:
        id=spider.savingQueToMysqlReturnID(question)
        allanswers=spider.getAllAnswers(question['url'],str(id))
        print(allanswers)
        for answer in allanswers:
            spider.savingAnsToMysql(answer)



if __name__ == '__main__':
    main()



