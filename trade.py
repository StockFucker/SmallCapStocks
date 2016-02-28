# -*- coding: utf-8 -*-
import pandas as pd
import math
import tushare as ts
from ggplot import *

def calculateHold(df,date):
    total_df = df[df.index == date]
    total_df = total_df.T
    total_df = total_df.sort([date])
    holds = list(total_df.index)[:30]
    return holds

def getPrice(price_df,stock,date):
    idx = list(price_df.index).index(date)
    price = price_df.iloc[idx][stock]
    return price

def getTradePrice(price_df,stock,date,isBuy):

    idx = list(price_df.index).index(date)
    price = price_df.iloc[idx][stock]

    if idx == 0:
        return price
    else:
        last_price = price_df.iloc[idx-1][stock]
        change = (price - last_price)/last_price
        if math.isnan(last_price) or math.isnan(price):
            return float('nan')
        elif (change > 0.098 or (change > 0.049 and change < 0.051)) and isBuy:
            return float('nan')
        elif (change < -0.098 or (change > -0.049 and change < -0.051)) and not isBuy:
            return float('nan')
        else:
            return price

def notST(st_df,date):
    def make_filter(stock):
        if not stock in st_df.columns:
            return True
        else:
            idx = list(st_df.index).index(date)
            value = st_df.iloc[idx][stock]
            try:
                if math.isnan(value):
                    return True
            except Exception, e:
                #print "ST:" + stock + "--" + date
                return False
    return make_filter

def getRecentPrices(price_df,stock,date,days):
    df = price_df[price_df.index <= date]
    prices = list(df[stock])
    return prices[len(prices)-days:len(prices)]

def should_hold(price_df,date):
    def make_filter(stock):
        try:
            prices = getRecentPrices(price_df,stock,date,4)
            if prices[3]/prices[0] < 0.92 or prices[3]/prices[1] < 0.95:
                #print "[DELETE]:" + stock
                return False
            return True
        except Exception, e:
            return True
    return make_filter

def not_new_stock(price_df,date):
    def make_filter(stock):
        if date < "2013-02-18":
            return True
        try:
            prices = getRecentPrices(price_df,stock,date,4)
            if prices[3]/prices[2] > 1.098 and prices[2]/prices[1] > 1.098 and prices[1]/prices[0] > 1.098:
                return False
            return True
        except Exception, e:
            return False
    return make_filter

TRADE_DETAIL_LOG = False

def trade(stocks_num):

    total_df = pd.read_csv('total.csv',index_col = 0)

    st_df = pd.read_csv('st.csv',index_col = 0)

    price_df = pd.read_csv('price.csv',index_col = 0)
    price_df = price_df[price_df.index != "2015-02-24"]
    price_df = price_df[price_df.index != "2015-10-07"]
    fill_price_df = price_df.fillna(method="ffill",axis=0)

    sh = pd.read_csv('sh.csv',index_col = 0)
    sh.sort(ascending=True,inplace = True)

    current_hold = set([])

    money = 1.0
    hold_amount = {}

    df = pd.DataFrame(index = sh.index)
    my_values = pd.Series(index = sh.index)
    index_values = pd.Series(index = sh.index)
    first_index_value = sh.iloc[0]['close']

    for date, row in sh.iterrows():

        #计算净值
        index_value = row['close']/first_index_value
        index_values[date] = index_value

        total_asset = money
        for stock in current_hold:
            price = getPrice(fill_price_df,stock,date)
            amount = hold_amount[stock]
            total_asset = total_asset + price * amount * 0.998
        my_values[date] = total_asset

        if TRADE_DETAIL_LOG:
            print "=========================================="
            print total_asset

        #计算持仓
        hold = calculateHold(total_df,date)

        hold = hold[:stocks_num]

        not_st_filter = notST(st_df,date)
        hold = list(filter(not_st_filter, hold))

        # not_new_filter = not_new_stock(price_df,date)
        # hold = list(filter(not_new_filter, hold))


        # should_hold_filter = should_hold(price_df,date)
        # hold = list(filter(should_hold_filter, hold))

        hold_set = set(hold)
        
        to_sell = current_hold - hold_set
        to_buy = hold_set - current_hold

        if TRADE_DETAIL_LOG:
            print date + "|" + str(hold_set)

        #计算卖出
        for stock in to_sell:
            price = getTradePrice(price_df,stock,date,False)
            if math.isnan(price):
                hold_set.add(stock)
                continue
            amount = hold_amount[stock]
            money = money + price * amount * 0.998
            hold_amount.pop(stock, None)
            if TRADE_DETAIL_LOG:
                print "[SELL]" + stock + "--" + str(price) + "--" + str(amount) +  "--" + str(money)

        if len(to_buy) == 0:
            current_hold = hold_set
            continue

        #计算买入
        # should_not_buy = set([])
        # for stock in to_buy:
        #     price = getTradePrice(price_df,stock,date,True)
        #     if math.isnan(price):
        #         try:
        #             hold_set.remove(stock)
        #         except Exception, e:
        #             print hold_set
        #         should_not_buy.add(stock)

        # to_buy = to_buy - should_not_buy

        each = money/len(to_buy)

        # if each > total_asset/(stocks_num):
        #     each = total_asset/(stocks_num)

        for stock in to_buy:
            price = getTradePrice(price_df,stock,date,True)
            if each < 0.00001 or math.isnan(price) :
                hold_set.remove(stock)
                continue
            hold_amount[stock] = each/price
            money = money - each
            if TRADE_DETAIL_LOG:
                print "[BUY]" + stock + "--"  + str(price) + "--" + str(each/price) +  "--" + str(money)

        current_hold = hold_set

        if TRADE_DETAIL_LOG:
            print hold_amount

    #股数－收益
    return list(my_values)[-1]

    #股数－回撤
    # max_redraw = 0
    # max_value = 0
    # for i in range(1,len(list(my_values))):
    #     max_value = max(max_value,list(my_values)[i])
    #     change = list(my_values)[i]/max_value - 1
    #     if change < 0:
    #         redraw = abs(change)
    #         max_redraw = max(redraw,max_redraw)

    # return max_redraw

    #绘制
    # df['my_value'] = my_values
    # df['index_value'] = index_values
    # df = df.reset_index()
    # df = df.fillna(method="ffill",axis=0)
    # df['date'] = pd.to_datetime(df['date'])
    # df = pd.melt(df,id_vars = ["date"],value_vars = ['my_value','index_value']) 
    # plot = ggplot(df,aes(x = "date", y = "value",color = "variable")) + geom_line()
    # print plot


def calculate_stocks_num():
    from_to = range(3,30)
    se = pd.Series(index=from_to)
    for i in from_to:
        value = trade(i)
        print value
        se[i] = value
    df = pd.DataFrame(se)
    df = df.reset_index()
    df.columns = ["stocks_num","value"]
    print df
    df.to_csv('redraw_result.csv')
    plot = ggplot(df,aes(x = "stocks_num", y = "value")) + geom_line()
    print plot

calculate_stocks_num()
#trade(8)