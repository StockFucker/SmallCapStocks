# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests 
import sys
import os
import string
import urllib2
import csv
import pandas as pd
import tushare as ts

reload(sys) 
sys.setdefaultencoding("utf8")

def getStocks():
    stocks_df = ts.get_stock_basics()
    stocks = list(stocks_df.index)
    return stocks


html_page_base = "http://f10.eastmoney.com/f10_v2/CapitalStockStructure.aspx?code="
def getData(stock):
    number = int(stock)
    stock_name = ""
    if number > 500000:
        stock_name = "sh" + stock
    else:
        stock_name = "sz" + stock
    url = html_page_base + stock_name
    if number > 300280:
        fetch_data_url(stock,url)


def extract_text(node):
    return node.get_text()

def fetch_data_url(code,url):
    header ={'User-Agent':'mozilla/5.0 (windows; U; windows NT 5.1; zh-cn)'}
    req = urllib2.Request(url,None,header)
    response = urllib2.urlopen(req)
    page = response.read()
    soup = BeautifulSoup(page)
    table = soup.find("table",id = "lngbbd_Table")
    file_name = "volumes/" + code + ".csv"
    with open(file_name, 'wb') as fp:
        csv_writer = csv.writer(fp,delimiter=',')

        #添加表内容
        trs = table.find_all('tr')[:2]
        for tr in trs:
            ths = tr.find_all('th')
            if len(ths) == 1:
                ths = tr.find_all('td')
            else:
                ths = ths[2:]
            texts = map(extract_text,ths)
            csv_writer.writerow(texts)

def fetch_data_url2(code,url):
    header ={'User-Agent':'mozilla/5.0 (windows; U; windows NT 5.1; zh-cn)'}
    req = urllib2.Request(url,None,header)
    response = urllib2.urlopen(req)
    page = response.read()
    soup = BeautifulSoup(page)
    table = soup.find("table",id = "StockStructureHistoryTable")
    file_name = "volumes/" + code + ".csv"
    with open(file_name, 'wb') as fp:
        csv_writer = csv.writer(fp,delimiter=',')
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) == 2:
                texts = map(extract_text,tds)
                csv_writer.writerow(texts)

def getData2(stock):
    number = int(stock)
    if number > 600086:
        url = "http://money.finance.sina.com.cn/corp/go.php/vCI_StockStructureHistory/stockid/" + stock + "/stocktype/TotalStock.phtml"
        fetch_data_url2(stock,url)

def go(): 
    for stock in getStocks():
        getData2(stock)

go()