# -*- coding: utf-8 -*-
import pandas as pd
import math
import tushare as ts
from ggplot import *

def calculateHold(df,date,stocks_num):
    total_df = df[df.index == date]
    total_df = total_df.T
    total_df = total_df.sort([date])
    holds = list(total_df.index)[:stocks_num]
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


def shouldBuy(price_df,sh,stock,date):
    # return True
    sh_index = list(sh.index).index(date)
    last_sh_index = sh_index

    if last_sh_index < 0:
        return True
    sh_change = sh.iloc[sh_index]["close"]/sh.iloc[last_sh_index]["close"] - 1 

    price_change = price_df.iloc[sh_index][stock]/price_df.iloc[last_sh_index][stock] - 1
    if math.isnan(price_change):
        return True

    change_delta = price_change - sh_change
    if sh_change == 0:
        return True
    return change_delta/abs(sh_change) < -0.5
    # return change_delta < -0.1

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
        hold = calculateHold(total_df,date,stocks_num)
        not_st = notST(st_df,date)
        hold = filter(not_st, hold)
        hold_set = set(hold)

        date_index = list(sh.index).index(date)
        if date_index > 0:
            last_index = date_index - 1
            last_close = sh.iloc[last_index]["close"]
            if row['close']/last_close < 0.97:
                hold_set = set([])
        
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
        #     if math.isnan(price) or not shouldBuy(fill_price_df,sh,stock,date):
        #         hold_set.remove(stock)
        #         should_not_buy.add(stock)

        # to_buy = to_buy - should_not_buy

        each = money/len(to_buy)
        for stock in to_buy:
            price = getTradePrice(price_df,stock,date,True)
            if each < 0.00001 or math.isnan(price):
                hold_set.remove(stock)
                continue
            hold_amount[stock] = each/price
            money = money - each
            if TRADE_DETAIL_LOG:
                print "[BUY]" + stock + "--"  + str(price) + "--" + str(each/price) +  "--" + str(money)

        current_hold = hold_set

        if TRADE_DETAIL_LOG:
            print hold_amount

    #return list(my_values)[-1]
    df['my_value'] = my_values
    df['index_value'] = index_values
    df = df.reset_index()
    df = df.fillna(method="ffill",axis=0)
    df['date'] = pd.to_datetime(df['date'])
    df = pd.melt(df,id_vars = ["date"],value_vars = ['my_value','index_value']) 
    plot = ggplot(df,aes(x = "date", y = "value",color = "variable")) + geom_line()
    print plot


def calculate_stocks_num():
    se = pd.Series(index=range(1,50))
    for i in range(1,50):
        value = trade(i)
        se[i] = value
    df = pd.DataFrame(se)
    df = df.reset_index()
    df.columns = ["stocks_num","value"]
    print df
    df.to_csv('stocks_num_result.csv')
    plot = ggplot(df,aes(x = "stocks_num", y = "value")) + geom_line()
    print plot
        
trade(7)