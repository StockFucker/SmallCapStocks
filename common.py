#!/usr/bin/env python2
# coding: utf-8

import re
import tushare

def get_stock_code():
    stocks_df = tushare.get_stock_basics()
    stocks = list(stocks_df.index)
    stocks.sort()
    return stocks

if __name__ == '__main__':
    print get_stock_code()
