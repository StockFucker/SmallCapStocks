# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/sgcy/anaconda/lib/python2.7/site-packages')

import tushare as ts
import pandas as pd
import math
import json
import easytrader
from getVolume import *
from datetime import datetime
from threading import Timer

def read_csv(file_name):
    try:
        df = pd.read_csv(file_name,header=None,names=["date","volume"])
        return df
    except Exception, e:
        print e
        return None

def safe_try(task):
    try:
        return task()
    except Exception, e:
        print e
        print "repeat"
        return safe_try(task)


def logIn():
    user = easytrader.use('xq')
    user.prepare('xq.json')
    return user

def getHoldStocks(positions):
    stocks = []
    for position in positions:
        stock_code = position['stock_code'][2:]
        stocks.append(stock_code)
    return stocks

def clearStock(stock,positions,user):
    for position in positions:
        stock_code = position['stock_code'][2:]
        if stock_code == stock:
            market_value = position['market_value']
            user.sell(stock,volume=market_value)
            return

def buyStock(stock,each,user):
    user.buy(stock,volume = each)

def getIndexdf():
    df = ts.get_h_data('000985', index=True)
    return df

def getTodaydf():

    df = ts.get_today_all()

    df.set_index(['code'],inplace = True)

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
            total_se[code] = float(list(volume_df["volume"])[0]) * float(row['trade'])
        except Exception, e:
            print code
            print e

    df['total'] = total_se
    df = df.sort(['total'])
    return df


def filterST(df):
    st_names = []
    for name in df['name']:
        if name.find("S") > 0:
            st_names.append(name)
    df = df[df['name'].isin(st_names) == False]
    risk_notification = ['300028','300022','300143','300372','300126','300399','300380','300135','600656']
    df = df[df.index.isin(risk_notification) == False]
    return df

def shouldClear(df):
    if df['close'][0] < 4500:
        return False
    ma1 = sum(df['close'][:20])/20
    ma2 = sum(df['close'][1:21])/20
    return ma1 < ma2
    

def getPrice(df,stock):
    return df[df.index == stock]['trade'][0]

def calculateDailyTotalValue():
    original_df = safe_try(getTodaydf)
    index_df = safe_try(getIndexdf)
    user = safe_try(logIn)
    position = user.position
    holds = getHoldStocks(position)

    #1
    df = original_df[:100]

    #2
    df = filterST(df)
    #3
    df = df[(df.index.isin(holds) == True) | (df['changepercent'] < 9.5)]
    # df.to_csv('last_should_holds.csv')
    print df
    should_holds = list(df.index[:8])
    #4
    if shouldClear(index_df):
        should_holds = []

    holds_set = set(holds)
    should_holds_set = set(should_holds)
    to_buy = should_holds_set - holds_set
    to_sell = holds_set - should_holds_set

    for stock in to_sell:
        clearStock(stock,position,user)

    if len(to_buy) == 0:
        return
 
    balance = user.balance[0]['enable_balance']
    each = balance/float(len(to_buy))
    for stock in to_buy:
        buyStock(stock,each,user)


def scheduleTask():
    update_volume()
    x=datetime.today()
    y=x.replace(day=x.day, hour=9, minute=25, second=30, microsecond=0)
    delta_t=y-x

    secs=delta_t.seconds+1

    t = Timer(secs, calculateDailyTotalValue)
    t.start()

update_volume()