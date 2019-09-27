from selenium import webdriver
from PIL import Image
import pytesseract
import time
from io import BytesIO
import pandas as pd
##from selenium.webdriver.common.by import By
##from selenium.webdriver.support import expected_conditions as EC
##from selenium.webdriver.support.wait import WebDriverWait
browser = webdriver.Chrome('e:/spider/webdriver/chromedriver.exe')
browser.maximize_window()
##wait = WebDriverWait(browser,10)
def begin():
    browser.get('https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?###')
##print(browser.page_source)


#填入关键词显示的下拉框，返回下拉框选项的个数（用来遍历）
def selectcode_length(key_word):
    browser.find_element_by_name("subjectCode").send_keys(key_word)#先填入关键词
    time.sleep(1)#加载下拉框
    div = browser.find_elements_by_class_name("ac_results")[0]#找到下拉框
    return len(div.find_elements_by_tag_name('li'))

#点击填入关键词显示的下拉框选项
def summit_subjectcode(key_word,n):
    browser.find_element_by_name("subjectCode").clear()
    browser.find_element_by_name("subjectCode").send_keys(key_word)#先填入关键词
    time.sleep(1)#加载下拉框
    div = browser.find_elements_by_class_name("ac_results")[0]#找到下拉框
    div.find_elements_by_tag_name('li')[n].click()#对元素进行点击

##browser.find_element_by_name("f_subjectCode_hideId").send_keys("G0301")
##browser.find_element_by_name("f_subjectCode_hideName").send_keys("博弈论与信息经济")
##browser.execute_script('$("input[name=\'f_subjectCode_hideId\']").val("G01")')
##browser.execute_script('$("input[name=\'subjectCode_hideName\']").val("G01.管理科学与工程")')

#填入资助类别
def summit_grantcode(value):
    grandcode = browser.find_element_by_id("f_grantCode")
    if value==0: #面上项目
        grandcode.find_element_by_xpath("//option[@value='218']").click()
    elif value==1: #青年科学基金项目
        grandcode.find_element_by_xpath("//option[@value='630']").click()
    else: #国家杰出青年科学基金项目
        grandcode.find_element_by_xpath("//option[@value='429']").click()

#识别验证码
def checkcode(ratio):
    #先把整个页面截图
    screenshot = browser.get_screenshot_as_png()
    #找到验证码元素
    element = browser.find_element_by_id('img_checkcode')
    #分别获取验证码图片的四个参数
    left = int(element.location['x'])
    top = int(element.location['y'])
    right = int(element.location['x']+element.size['width'])
    bottom = int(element.location['y']+element.size['height'])
    im = Image.open(BytesIO(screenshot))
    #四个参数都要乘以1.5是因为我的电脑显示比例为150%
    im = im.crop((left*ratio,top*ratio,right*ratio,bottom*ratio))
    return pytesseract.image_to_string(im)

def clicksearch(ratio):
    #验证是否跳转了网页,并检查验证码是否识别准确（最多验证10次）
    i = 0
##    while((browser.current_url != 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list' )&(i<=10)):
    while(i<10):
        #清除原有验证码再次识别填入新的验证码
        browser.find_element_by_id('f_checkcode').clear()
        browser.find_element_by_id('f_checkcode').send_keys(checkcode(ratio))
        #点击查询
        browser.find_element_by_id('searchBt').click()
        #通过能否定位验证码错误弹出框，来验证验证码是否正确
        try:
            #如果定位到了，则继续循环输入验证码
            browser.find_element_by_id('scmtip_container')
            print("get wrong checkcode!")
        except:
            #如果没有定位到，截断报错异常来终止循环
            print("checkcode is right!")
            break
##        time.sleep(2) 
        i=i+1
    ##print(browser.page_source)

#返回搜索结果有多少页
def get_pages():
        try:
            return int(browser.find_element_by_id('sp_1_TopBarMnt').text)
        except:
            return 0


#提取信息
def get_info(pages,ratio):
    print("this search have {} pages".format(pages))
    #如果页数大于0，开始提取信息
    if pages>0:
        #将这一页每一条数据保存在一个空list
        list = []
        #遍历表格提取信息
        for page in range(1,pages+1):
            table = browser.find_element_by_id('dataGrid')
            tr = table.find_elements_by_tag_name('tr')
            #将这一页的数据保存在一个二维数组里
            for i in range(1,len(tr)):
                td = tr[i].find_elements_by_tag_name('td')
                a = []
                for i in range(1,len(td)):
                    a.append(td[i].text)
                list.append(a)#二维数组
            #如果页面不是最后一页，则输入验证码点击翻页
            if page != pages:
                while True:
                    #清除原有验证码再次识别填入新的验证码
                    browser.find_element_by_id('checkCode').clear()
                    browser.find_element_by_id('checkCode').send_keys(checkcode(ratio))
                    #点击下一页
                    browser.find_element_by_id('next_t_TopBarMnt').click()
                    #与上面一样
                    try:
                        browser.find_element_by_id('scmtip_container')
                        print("get wrong checkcode!")
                    except:
                        print("checkcode is right!")
                        break
        #将二维数组数据转化为dataframe
        df = pd.DataFrame(list,columns=['prjNo','subjectCode','title','name','collage','totalAmt','startEndDate'])
        print("this part is get {0} data".format(len(df)))
        return df
    #没有数据，返回None
    else:
        print("this part is have no data")
        return None

def close():
    browser.close()

def main():
    #关键词代码列表（自行添加）
    subjectcodes = ['G0304']
    #电脑显示比例
    ratio = 1.5
    #创建一个空dataframe
    df = pd.DataFrame(columns=['prjNo','subjectCode','title','name','collage','totalAmt','startEndDate'])
    #浏览器请求网址
    begin()
    #遍历关键词列表
    for subcode in subjectcodes:
        #遍历下拉框
        for i in range(0,selectcode_length(subcode)):
            #遍历三个不同类型的资质类型
            for j in range(1,3):
                summit_subjectcode(subcode,i)
                summit_grantcode(j)
                clicksearch(ratio)
                df = df.append(get_info(get_pages(),ratio))
                time.sleep(3)
                #浏览器重新请求网址
                begin()
    print(df)
    df.to_excel('data.xlsx')

main()  
