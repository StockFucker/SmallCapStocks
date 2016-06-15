#!/usr/bin/python
# coding:utf8
# return 8 minimum volume stocks, excluding ST and risk notification stocks

import json
import threading
from collections import deque
from common import *
from download import download

THREADS_NUM = 800
ADJUST_STOCK_NUM = 8
SRC = 'http://qt.gtimg.cn/q=%s'

def risk_stocks():
    ''' get all risk notification stocks'''
    url = 'http://hqdigi2.eastmoney.com/EM_Quote2010NumericApplication/index.aspx?type=s&sortType=C&sortRule=-1&pageSize=100&page=1&jsName=quote_123&style=2850022'
    html = download().get(url)
    return re.compile('"\d+,([^,]+),').findall(html) or []

def muilt_thread(target, num_threads, wait=True):
    threads = [threading.Thread(target=target) for i in range(num_threads)]
    for thread in threads:
        thread.start()
    if wait:
        for thread in threads:
            thread.join()

def select_stock():
    bag_price = []
    names = deque()
    for i in get_stock_prefix_codes():
        names.append(SRC % i)
    # risk stocks
    list_risk_stocks = risk_stocks()

    def worker():
        while True:
            try:
                url = names.popleft()
            except IndexError:
                break
            try:
                html = download().get(url)
            except Exception, e:
                names.append(url)
                continue
            stock = html.split('~')
            if len(stock) <= 49:
                continue
            bag = {
                'name': stock[1],
                'code': stock[2],
                'now': float(stock[3]),
                'close': float(stock[4]),
                'open': float(stock[5]),
                'volume': float(stock[6]) * 100,
                'up_down': float(stock[31]),
                'up_down(%)': float(stock[32]),
                'high': float(stock[33]),
                'low': float(stock[34]),
                'market_value': float(stock[45]) if stock[44] != '' else None,
                'PB': float(stock[46]),
                'limit_up': float(stock[47]),
                'limit_down': float(stock[48])
            }
            if 'S' not in bag['name'] and bag['code'] not in list_risk_stocks and bag['market_value']: 
                #filter stock with ST or risk notification
                bag_price.append(bag)

    muilt_thread(worker, THREADS_NUM)
    bag_price = sorted(bag_price, key = lambda x:x['market_value'])
    return bag_price[:ADJUST_STOCK_NUM]


if __name__ == '__main__':
    print select_stock()
