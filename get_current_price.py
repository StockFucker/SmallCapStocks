#!/usr/bin/python
#coding:utf8

import threading
from collections import deque
from common import *
from download import download

def get_current_price():
    bag_price = []
    src = 'http://qt.gtimg.cn/q=%s'
    names = deque()
    for i in get_stock_prefix_codes():
        names.append(src % i)
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

            print 'Downloading %s' % url

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
            bag_price.append(bag)
    muilt_thread(worker, 800)
    return bag_price

def muilt_thread(target, num_threads, wait=True):
    threads = [threading.Thread(target=target) for i in range(num_threads)]
    for thread in threads:
        thread.start()
    if wait:
        for thread in threads:
            thread.join()

if __name__ == '__main__':
    print get_today_all_stocks_price()
