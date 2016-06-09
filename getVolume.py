# !/usr/bin/python2
# coding:utf-8

import requests 
import os
import string
import urllib2
import csv
import pandas as pd
import tushare as ts
from collections import deque
from bs4 import BeautifulSoup

DATA_SOURCE = 'sina'

class download:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0'
        self.headers = {'User-Agent': self.user_agent, 'Accept-encoding':'gzip, deflate'}
        self.opener = urllib2.build_opener()

    def get(self, url):
        request = urllib2.Request(url)
        response = self.opener.open(request)
        html = response.read()
        return html

def extract_text(node):
    return node.get_text()

def clean_data(html):
    results = []
    soup = BeautifulSoup(html,"html5lib") if DATA_SOURCE == 'sina' else BeautifulSoup(page)
    table = soup.find("table",id = "StockStructureHistoryTable") if DATA_SOURCE == 'sina' else\
            soup.find("table",id = "lngbbd_Table")
    trs = table.find_all('tr') if DATA_SOURCE == 'sina' else table.find_all('tr')[:2]
    for tr in trs:
        if DATA_SOURCE == 'sina':
            tds = tr.find_all('td')
            if len(tds) == 2:
                texts = map(extract_text,tds)
                results.append(texts)
        else:
            ths = tr.find_all('th')
            tds = tr.find_all('td') if len(ths) == 1 else ths = ths[2:]
            texts = map(extract_text,tds)
            results.append(texts)
    return results

def get_volume_data(urls):
    volume_infos = []
    def worker():
        D = download()
        while True:
            try:
                url = urls.popleft()
            except IndexError:
                break
            print 'Downloading: %s' % url
            html = D.get(url=url)
            volume_infos = clean_data(html)

    muilt_thread(worker, 30)
    return volume_infos

def muilt_thread(target, num_threads, wait=True):
    threads = [threading.Thread(target=target) for i in range(num_threads)]
    for thread in threads:
        thread.start()
    if wait:
        for thread in threads:
            thread.join()

def getStocks():
    stocks_df = ts.get_stock_basics()
    stocks = list(stocks_df.index)
    return stocks
        
def update_volume():
    url = 'http://money.finance.sina.com.cn/corp/go.php/vCI_StockStructureHistory/stockid/%s/stocktype/TotalStock.phtml'\
            if DATA_SOURCE=='sina' else 'http://f10.eastmoney.com/f10_v2/CapitalStockStructure.aspx?code=%s'
    urls = deque()
    for i in getStocks():
        int_stock = int(i)
        if DATA_SOURCE != 'sina':
            i = 'sh%s' % i if int_stock > 500000 else 'sz%s' % i
        urls.append(url % i)
    get_volume_data(urls)

if __name__ == '__main__':
    update_volume()
