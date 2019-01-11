import os
import time
import json
import requests
import pymongo

def get_image_by_page(page_no):
    url='https://unsplash.com/napi/collections/1065976/photos?page={}&per_page=10&order_by=latest&share_key=a4a197fc196734b74c9d87e48cc86838'.format(page_no)
    r=requests.get(url,verify=False)
    data = r.json()
    return data

def get_images():
    page_no = 1
    client = pymongo.MongoClient('localhost:27017')
    db = client.unsplash
    while True:
        result = get_image_by_page(page_no)
        if len(result)==0:
            break
        db.wallpapers.insert_many(result)
        print(page_no)
        page_no+=1
        time.sleep(10)

def get_top_liked_images():
    client = pymongo.MongoClient('localhost:27017')
    db = client.unsplash
    cursor = db.wallpapers.aggregate([
        {'$match':{'likes':{'$gte':1500}}}
    ])

    path = os.path.dirname(__file__)
    path = os.path.join(path,"wallpaper")
    for item in cursor:
        url = item["urls"]["raw"]
        width = item["width"]
        height = item["height"]
        likes = item["likes"]
        if width<=height:
            continue
        r = requests.get(url,verify=False)
        filename = "{0}({1}likes).jpg".format(int(time,time()),likes)
        filepath = os.path.join(path,filename)
        with open(filepath,"wb") as f:
            f.write(r.content)
        print(filepath)
        time.sleep(10)

if __name__ == '__main__':
    # get_images()
    # print(os.path.join(os.path.dirname(__file__),"wallpaper"))
    get_top_liked_images()

# print(get_image_by_page(1))