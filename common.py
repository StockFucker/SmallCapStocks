#!/usr/bin/env python2
# coding: utf-8

import re
import requests
from download import download

FIVE_PRICE_URL = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=%s'
TEN_PRICE_URL = 'https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=%s'

LIMIT_DOWN = -1
LIMIT_UP = -2

def get_stock_prefix(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(stock_code) is str, 'stock code need str type'
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '90', '110', '113', '132', '204')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'

def get_all_stock_codes(is_A=False):
    """默认获取所有A股股票 ID"""
    result = []
    url = 'http://www.shdjt.com/js/lib/astock.js'
    html = download().get(url)
    stock_codes = re.compile('~(\d+)`').findall(html) or []
    stock_codes = list(set(stock_codes))

    if not is_A:
        return stock_codes
    else:
        for i in stock_codes:
            if i.startswith('0') or i.startswith('3') or i.startswith('6'):
                result.append(i)
        return result

def get_stock_prefix_codes(is_A=False):
    return [get_stock_prefix(str(i))+str(i)  for i in get_all_stock_codes(is_A)]

def get_current_five_price(stock):
    ''' 从东方财富获取当前时间五档价格数据 
        注: 返回的委托量为买/卖委托总量
    '''
    bag_prices = {}
    url = FIVE_PRICE_URL % stock + '1' if stock.startswith('6') else FIVE_PRICE_URL % stock + '2'
    html = download().get(url)
    m = re.compile('"Value":\[([^\]]+)\]').search(html) if html else ''
    if m:
        string = m.groups()[0]
        infos = string.split('","')
        assert len(infos) > 50

        for i in range(10):
            bag_prices[infos[i+3]] = sum([ int(k) for k in infos[13+i/5*5:i+14] ])
        if infos[3] == '0.00':
            # 跌停
            bag_prices['0.00'] = LIMIT_DOWN
        elif infos[8] == '0.00':
            # 涨停
            bag_prices['0.00'] = LIMIT_UP
    return bag_prices

def get_current_ten_price(stock):
    ''' 获取当前时间十档价格数据 
        注: 返回的委托量为买/卖委托总量
    '''
    bag_prices = {}
    url =  TEN_PRICE_URL % stock
    html = download().get(url)
    prices = re.compile(r'"price":([\d\.]+),').findall(html)
    volumes = re.compile(r'"volume":([\d\.]+)\}').findall(html)
    assert len(prices) == len(volumes)
    assert prices
    for inum, i in enumerate(prices):
        if i == '0.0':
            i = '0.00'
        bag_prices[i] = sum([ int(float(k)) for k in volumes[inum/10*10:inum+1] ])
    if prices[0] == '0.00':
        # 跌停
        bag_prices['0.00'] = LIMIT_DOWN
    elif prices[10] == '0.0':
        # 涨停
        bag_prices['0.00'] = LIMIT_UP
    return bag_prices

if __name__ == '__main__':
    print get_current_ten_price('300151')
