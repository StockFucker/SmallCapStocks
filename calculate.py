# -*- coding: utf-8 -*-
import pandas as pd
import math
import tushare as ts


def getStocks():
    stocks_df = ts.get_stock_basics()
    stocks = list(stocks_df.index)
    return stocks

def calculateTotals(stocks):

    for stock in stocks:

        if int(stock) < 300499:
            continue

        price_df = pd.read_csv("prices/"+stock+".csv")
        to_drop = range(0,len(price_df.axes[1]))
        to_drop.remove(0)
        to_drop.remove(3)
        price_df = price_df.drop(price_df.columns[to_drop],1)
        price_df['date'] = pd.to_datetime(price_df['date'])
        price_df = price_df.set_index(['date'])
        price_df.columns = ['price']

        volume_df = pd.read_csv("volumes/"+stock+".csv",header=None,names=["date","volume"])
        volume_df = volume_df.replace({'万股': ''}, regex=True)
        volume_df['date'] = pd.to_datetime(volume_df['date'])
        volume_df = volume_df.set_index(['date'])
        volume_df.sort(ascending=False,inplace = True)

        totals = []
        for date, row in price_df.iterrows():
            selected_volumes = volume_df[volume_df.index < date]
            volume = list(selected_volumes['volume'])[0]
            total = float(volume) * float(row['price'])
            totals.append(total)

        try:
            price_df["total"] = totals
        except Exception, e:
            print price_df
            print stock
            raise e
        totals_df = price_df.drop(['price'],1)
        totals_df.columns = [stock]
        totals_df.to_csv("totals/"+stock+".csv")

    # df = pd.concat(totals_dfs, axis=1)
    # print df
    # df.to_csv('total.csv')

def concatTotals(stocks):
    total_dfs = []
    for stock in stocks:
        try:
            total_df = pd.read_csv("totals/"+stock+".csv",index_col = 0,parse_dates = True)
            total_dfs.append(total_df)
        except Exception, e:
            print "Error:" + stock
    df = pd.concat(total_dfs, axis=1)
    print df
    df.to_csv('total.csv')

def concatPrices(stocks):
    price_dfs = []
    for stock in stocks:
        try:
            price_df = pd.read_csv("prices/"+stock+".csv",index_col = 0,parse_dates = True)
            to_drop = range(0,len(price_df.axes[1]))
            to_drop.remove(2)
            price_df = price_df.drop(price_df.columns[to_drop],1)
            price_df.columns = [stock]
            price_dfs.append(price_df)
        except Exception, e:
            print "Error:" + stock
    df = pd.concat(price_dfs, axis=1)
    print df
    df.to_csv('price.csv')

def concatSTs(stocks):
    st_dfs = []
    for stock in stocks:
        try:
            st_df = pd.read_csv("st/"+stock+".csv",index_col = 0)
            st_df = st_df.set_index(['tradeDate'])
            st_df.columns = [stock]
            st_df = st_df.groupby(st_df.index).first()
            st_dfs.append(st_df)
        except Exception, e:
            print "Error:" + stock
    df = pd.concat(st_dfs, axis=1)
    df.to_csv('st.csv')

def go(): 
    concatSTs(getStocks())

go()