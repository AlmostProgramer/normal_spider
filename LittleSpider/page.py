import requests
import time
import tool
class page:

    def __init__(self):
        self.tool=tool.Tool()

    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))


    def getPageByUrl(self,url):
        try:
            r=requests.get(url)
            return r.text
        except:
            print('unknown error!')

