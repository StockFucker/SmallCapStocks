# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd

def getStocks():
    stocks_df = ts.get_stock_basics()
    stocks = list(stocks_df.index)
    return stocks

def tryGetData(stock):
    try:
        df = ts.get_hist_data(stock) #两个日期之间的前复权数据
        return df 
    except Exception, e:
        print "[Error]:" + stock
        return tryGetData(stock)

def getData(stock):
    df = tryGetData(stock)
    file_name = "prices/" + stock + ".csv"
    if df is not None:
        df.to_csv(file_name)
    else:
        print "[Miss]:" + stock

def go(): 
    for stock in getStocks():
        getData(stock)

go()