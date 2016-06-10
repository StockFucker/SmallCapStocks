# !/usr/bin/python2
# coding: utf-8

import threading
import tushare as ts
import pandas as pd
from common import get_stock_code
from collections import deque

def get_price(): 
    stocks = deque()
    for stock in get_stock_code():
        stocks.append(stock)

    prices = []
    def worker():
        while True:
            try:
                stock = stocks.popleft()
            except IndexError:
                break
            print 'Get Price data from tushare: %s' % stock
            try:
                df = ts.get_hist_data(stock) #两个日期之间的前复权数据
            except Exception:
                stocks.append(stock)
                continue
            df['stock_id'] = stock
            prices.append(df)
    muilt_thread(worker, 30)
    write_2_csv(prices)

def muilt_thread(target, num_threads, wait=True):
    threads = [threading.Thread(target=target) for i in range(num_threads)]
    for thread in threads:
        thread.start()
    if wait:
        for thread in threads:
            thread.join()

def write_2_csv(prices):
    file_name = 'csv/prices.csv'
    result = reduce(lambda x,y:x+y, prices)
    if result is not None:
        result.to_csv(file_name)

if __name__ == '__main__':
    get_price()
