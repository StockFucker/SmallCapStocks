#!/usr/bin/python
# coding:utf8
# return all stocks information include price and voloum, excluding ST and risk notification stocks

import json
import threading
from common import *
from collections import deque
from download import download
from datetime import datetime, timedelta

THREADS_NUM = 30
SRC = 'http://qt.gtimg.cn/q=%s'
BLACK_LIST = ['300126']
SEARCHKEY = '退市;暂停上市;立案调查事项进展暨风险提示;'

def risk_stocks():
    return []
    ''' get all risk notification stocks'''
    url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
    names = deque()
    result = []

    def get_page_stock(pagenum):
        stocks = []
        post_data = {}
        post_data['searchkey'] = SEARCHKEY
        post_data['column'] = 'sse'
        post_data['columnTitle'] = '历史公告查询'
        post_data['pageNum'] = pagenum
        post_data['pageSize'] = '30'
        post_data['tabName'] = 'fulltext'
        today = datetime.today()
        today_last_year = today + timedelta(days=-365)
        post_data['seDate'] = '%s ~ %s' % (today_last_year.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))

        html = download().post(url, post_data)
        html = html.decode('utf-8')
        jdata = json.loads(html)
        announcements = jdata.get('announcements') if jdata else ''
        recordnum = jdata.get('totalRecordNum') if jdata else '0'
        if announcements:
            for k in announcements:
                seccode = k['secCode']
                if seccode not in stocks:
                    stocks.append(seccode)
        return stocks, recordnum

    def worker():
        while True:
            try:
                pagenum = names.popleft()
            except IndexError:
                break
            for i in get_page_stock(pagenum)[0]:
                if i not in result:
                    result.append(i)

    # add pagenum to deque
    result, recordnum = get_page_stock(pagenum='1')
    page_num = recordnum/30 + 2
    for k in range(2, page_num):
        names.append(str(k))

    muilt_thread(worker, page_num-1)
    result.sort()
    return result

def muilt_thread(target, num_threads, wait=True):
    threads = [threading.Thread(target=target) for i in range(num_threads)]
    for thread in threads:
        thread.start()
    if wait:
        for thread in threads:
            thread.join()

def get_prices():
    uniq_list = []
    bag_price = []
    names = deque()
    for i in get_stock_prefix_codes(is_A=True):
        names.append(SRC % i)
    # risk stocks
    list_risk_stocks = risk_stocks()

    def worker():
        while True:
            try:
                url = names.popleft()
            except IndexError:
                break
            html = download().get(url)
            try:
                html = download().get(url)
            except Exception, e:
                print e
                names.append(url)
                continue
            stock = html.split('~')
            if len(stock) <= 49:
                print 'Error %s' % url
                continue
            bag = {
                'name': stock[1],
                'code': stock[2],
                'now': float(stock[3]),
                'close': float(stock[4]),
                'open': float(stock[5]),
                'volume': int(stock[6]),
                'up_down': float(stock[31]),
                'up_down(%)': float(stock[32]),
                'high': float(stock[33]),
                'low': float(stock[34]),
                'high_day': float(stock[41]),
                'low_day': float(stock[42]),
                'market_value': float(stock[45]) if stock[44] != '' else None,
                'PB': float(stock[46]),
                'limit_up': float(stock[47]),
                'limit_down': float(stock[48]),
                'PE': float(stock[39]) if stock[39] != '' else None
            }
            if '*' not in bag['name'] and 'S' not in bag['name'] and bag['code'] not in list_risk_stocks and bag['market_value']: 
                #filter stock with ST or risk notification
                if bag['limit_up'] > 0  and bag['code'] not in uniq_list and bag['code'] not in BLACK_LIST:
                    # excluding new stock
                    uniq_list.append(bag['code'])
                    bag_price.append(bag)
    muilt_thread(worker, THREADS_NUM)
    bag_price = sorted(bag_price, key = lambda x:x['market_value'])
    return bag_price

def select(read_cache=False, write_cache=True):
    if read_cache:
        result = []
        with open('.cache') as f:
            for inum, i in enumerate(f):
                i = i.strip()
                bag = {}
                if inum == 0:
                    FIELDS = i.split(',')
                    continue
                for jnum, j in enumerate(i.split(',')):
                    bag[FIELDS[jnum]] = j
                result.append(bag)
        return {i['code']:i for i in result}

    result = get_prices()

    if write_cache:
        with open('.cache', 'w') as f:
             for inum, i in enumerate(result):
                 if inum == 0:
                     info = ','.join([str(k) for k in i.keys()])
                     f.write('%s\n' % info)
                 info = ','.join([str(k) for k in i.values()])
                 f.write('%s\n' % info)
    return {i['code']:i for i in result}

if __name__ == '__main__':
    select(read_cache=False)
