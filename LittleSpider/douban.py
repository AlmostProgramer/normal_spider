import requests
from bs4 import BeautifulSoup

import pandas as pd
from pandas import Series,DataFrame

import codecs
DOWNLOAD_OAD_URL='http://www.chyxx.com/industry/201702/496273.html'

def download_page(url):
    headers={
        'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'

    }
    data=requests.get(url,headers=headers).content
    return data

def parse_html(html):
    soup=BeautifulSoup(html,"lxml")
    PublicBudgetIncome_province_list_soup=soup.find('table',attrs={'class':'datatable'})

    PublicBudgetIncome_province_list=[]

    for province_tr in PublicBudgetIncome_province_list_soup.find_all('tr'):
        province_info = []
        for td in province_tr.find_all('td'):
            province_info.append(td.get_text())
        # print(province_info)
        PublicBudgetIncome_province_list.append(province_info)
    return PublicBudgetIncome_province_list
def main():
    url=DOWNLOAD_OAD_URL


    # with codecs.open('movies','wb',encoding='utf-8') as fp:

    html=download_page(url)
    frame=DataFrame(parse_html(html))
    print(frame)
    frame.to_csv('F:/PublicBudgetIncome.csv')
        # fp.write(u'{movies}\n'.format(movies='\n'.join(movies)))



if __name__=='__main__':
    main()

