# -*- coding: utf-8 -*-

import sys
# sys.path.append('/Users/sgcy/anaconda/lib/python2.7/site-packages')

import math
import json
import time
import easytrader
import pandas as pd
from datetime import datetime
from threading import Timer
from collections import deque
from common import *
from get_current_price import get_current_price

def read_csv(file_name):
    try:
        df = pd.read_csv(file_name,header=None,names=["date","volume"])
        return df
    except Exception as e:
        # print(e)
        return None

def safe_try(task):
    try:
        return task()
    except Exception as e:
        print(e)
        print("repeat")
        return safe_try(task)


def logIn():
    user = easytrader.use('ht')
    user.prepare('../ht.json')
    return user

def getHoldStocks(positions):
    stocks = []
    if type(positions) != type([]):
        return []
    for position in positions:
        stock_code = position['stock_code']
        stocks.append(stock_code)
    return stocks

def getHoldStockPrice(positions,stock):
    for position in positions:
        if stock == position['stock_code']:
            return position['last_price']
    return 0

def getHoldStockMarketValue(positions,stock):
    for position in positions:
        if stock == position['stock_code']:
            return position['market_value']
    return 0

def clearStock(stock,positions,user):
    for position in positions:
        stock_code = position['stock_code']
        if stock_code == stock:
            amount = position['current_amount']
            price = float(round(float(position['last_price']) * 0.99 * 100.0)/100.0)
            print(amount) 
            print(price)
            user.sell(stock,amount = amount,price = price)
            return

def buyStock(stock,each,user,df):
    price = df[df.index == stock]['price'][0]
    price = price * 1.01
    amount = each // price // 100 * 100
    price = round(price * 100.0)/100.0
    if amount > 0:
        user.buy(stock,amount = amount,price = price)

def stockFilter(stock):
    head = stock[:1]
    return head == "0" or head == "3" or head == "6"

def getTodaydf():
    data = get_current_price()
    df = pd.DataFrame(data)
    df = df.T
    to_drop = list(df.columns)
    to_drop.remove("now")
    to_drop.remove("涨跌(%)")
    to_drop.remove("总市值")
    to_drop.remove("name")
    to_drop.remove("unknown")
    df = df.drop(pd.Index(to_drop),1)

    stocks = filter(stockFilter,list(df.index))
    df = df[df.index.isin(stocks) == True] 
    df.columns = ["name","price","unknown","total_value","changepercent"]
    # df = df.sort(['total'])
    # df = df[df['price'] > 0]

    total_se = pd.Series(index = df.index)
    for code, row in df.iterrows():
        file_name = "volumes/" + code + ".csv"
        volume_df = read_csv(file_name)
        if volume_df is None:
            continue
        volume_df = volume_df.replace({'万股': ''}, regex=True)
        volume_df['date'] = pd.to_datetime(volume_df['date'])
        volume_df = volume_df.set_index(['date'])
        volume_df.sort(ascending=False,inplace = True)
        # isnan?
        try:
            total_se[code] = float(list(volume_df["volume"])[0]) * float(row['price'])
        except Exception as e:
            print(code)
            print(e)

    df['total'] = total_se
    df = df.sort(['total_value'])
    return df


def filterST(df):
    st_names = []
    for name in df['name']:
        if name.find("S") >= 0:
            st_names.append(name)
    df = df[df['name'].isin(st_names) == False]
    risk_notification = ['300028','300022','300143','300372','300126','300399','300380','300135','600656']
    df = df[df.index.isin(risk_notification) == False]
    return df

def shouldClear():
    # if df['close'][0] < 4500:
    #     return False
    # ma1 = sum(df['close'][:20])/20
    # ma2 = sum(df['close'][1:21])/20
    # return ma1 < ma2
    return False
    

def getPrice(df,stock):
    return df[df.index == stock]['trade'][0]

def calculateDailyTotalValue():
    df = safe_try(getTodaydf)
    user = safe_try(logIn)
    position = user.position

    holds = getHoldStocks(position)
    # holds = []

    df = df[(df.index.isin(holds) == True) | (df['unknown'] == "")]
    df = df[(df.index.isin(holds) == True) | (df['price'] > 0)]

    #1
    df = df[:100]

    #2
    df = filterST(df)
    #3
    df = df[(df.index.isin(holds) == True) | (df['changepercent'] < 9.5)]
    df.to_csv('last_should_holds_3.csv')

    print(df)

    should_holds = list(df.index[:8])
    #4
    if shouldClear():
        should_holds = []

    holds_set = set(holds)
    should_holds_set = set(should_holds)
    to_buy = should_holds_set - holds_set
    to_sell = holds_set - should_holds_set
   
    print("BUY:" + str(to_buy))
    print("SELL:" + str(to_sell))

    go = input("Continue?(Y/N)")
    if go != "Y":
        return

    market_value = 0.0
    for stock in to_sell:
        clearStock(stock,position,user)
        market_value = market_value + getHoldStockMarketValue(position,stock)

    place_order(user,to_buy,df,market_value)

def place_order(user,to_buy,df,market_value):

    balance = user.balance[0]['enable_balance']

    if balance < market_value * 0.99:
        time.sleep(3)
        print("未成交:" + str(market_value - balance))
        place_order(user,to_buy,df,market_value)
        return

    print("已全成交")
    
    if len(to_buy) == 0 or balance < 0:
        return

    each = balance/float(len(to_buy))
    # each = 14000
    for stock in to_buy:
        buyStock(stock,each,user,df)

def scheduleTask():
    x=datetime.today()
    y=x.replace(day=x.day, hour=14, minute=55, second=30, microsecond=0)
    delta_t=y-x

    secs=delta_t.seconds+1

    t = Timer(secs, calculateDailyTotalValue)
    t.start()

calculateDailyTotalValue()
