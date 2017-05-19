#_*_ coding: utf-8 _*_

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pymongo
import requests
from config import *
import os,time
from multiprocessing import Pool

page_urls =[]
img_urls = []
client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB]

browser = webdriver.Chrome()
browser.get('http://www.meizitu.com/a/list_1_1.html')
wait = WebDriverWait(browser,10)

total_page = 90
def next_page(page_num):

    for i in range(1,page_num):
        if i == 1:
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#wp_page_numbers > ul > li:nth-child(17) > a')))
        else:
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#wp_page_numbers > ul > li:nth-child(18) > a')))
        html = browser.page_source
        get_img_page(html)
        submit.click()

        print(type(html))

        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.thisclass'),str(i+1)))

def get_img_page(url):

    soup = BeautifulSoup(url,'html.parser')
    for item in soup.select('.pic > a'):
        get_img_info(item['href'])

def download_img(url):

    res = requests.get(url,stream=True)


    file_path = '{}/{}'.format(os.getcwd(),"".join(url.split('/')[-4:]))

    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            for bloc in res.iter_content(1024):
                if bloc:
                    f.write(bloc)




def get_img_info(url):

    res = requests.get(url)
    res.encoding = 'gbk'
    soup = BeautifulSoup(res.text, 'html.parser')
    one_page_img_url = []
    title = ''
    for item in soup.select('#picture > p > img'):
        print('downloading {}'.format(item['src']))
        download_img(item['src'])
        one_page_img_url.append(item['src'])
        title = item['alt']
    result = {
        'title':title.split(u'，')[0],
        'img_urls':one_page_img_url
    }

    save_to_mongodb(result)

def save_to_mongodb(result):
    if db[MONGODB_TABLE].insert(result):
        print('save to mongo OK   ',result['title'])

    else:
        print('save to mongodb error')

def main():

    next_page(total_page)




if __name__ == '__main__':
    main()