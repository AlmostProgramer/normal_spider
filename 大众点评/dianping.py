import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from lxml import etree
import re
headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }

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
    header_dict = {}
    header = header.split('\n')
    for h in header:
        h = h.strip()
        if h:
            k,v = h.split(':',1)
            header_dict[k] = v.strip()
    return header_dict

def fix_url(url):
    return 'http:'+url

#
def get_css_url():
    url = "http://www.dianping.com/nanchang/ch10"
    host = """Referer:http://dianping.com/
            """
    header = head + host
    headers = str_to_dict(header)
    response = requests.get(url,headers=headers)
    content = response.text
    matched = re.search(r'href="([^"]+svgtextcss[^"]+)"',content,re.M)
    if not matched:
        raise Exception("cannot find svgtextcss file")
    css_url = matched.group(1)
    css_url = fix_url(css_url)
    return css_url

def get_svg(css_url):
    response = requests.get(css_url,headers=headers)
    content = response.text
    matched = re.search(r'span\[class\^="hs\-"\].*?background\-image: url\((.*?)\);', content)
    if not matched:
        raise Exception("cannot fid svg file")
    svg_url = matched.group(1)
    svg_url = fix_url(svg_url)
    r = requests.get(svg_url,headers=headers)
    content = r.text
    matched = re.search(r'class="textStyle">(\d+)</text>',content)
    if not matched:
        raise Exception("cannot find digits")
    digits = list(matched.group(1))
    return digits


def get_class_offset(css_url):
    r = requests.get(css_url,headers=headers)
    content = r.text
    matched = re.findall(r'(\.[a-zA-Z0-9-]+)\{background:(\-\d+\.\d+)px',content)
    result = {}
    for item in matched:
        css_class = item[0][1:]
        offset = item[1]
        result[css_class] = offset
    return result

def get_review_num(page_url,class_offset,digits):
    data={}
    r = requests.get(page_url,headers=headers)
    content = r.text
    doc = pq(content)
    list = doc('#shop-all-list li').items()
    for item in list:
        data['name'] = item('.tit a')[0].attrib["title"]
        review_num_node = item('.comment b')[0]
        num = 0
        if review_num_node.text:
            num = num * 10 + int(review_num_node.text)
        for digit_node in review_num_node:
            css_class = digit_node.attrib['class']
            offset = class_offset[css_class]
            index = int((float(offset)+7)/-12)
            digit = int(digits[index])
            num = num*10 + digit
        last_digit = review_num_node[-1].tail
        if last_digit:
            num = num*10 + int(last_digit)
        data['review_num'] = num
        print("restaurant: {}, review num: {}".format(data['name'], data['review_num']))
    return data


if __name__ == '__main__':

    r = requests.get('http://www.dianping.com/nanchang/ch10',headers=headers)

    css_url = get_css_url()
    digits = get_svg(css_url)
    class_offset = get_class_offset(css_url)
    url = 'http://www.dianping.com/nanchang/ch10'
    get_review_num(url, class_offset, digits)

