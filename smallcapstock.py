#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

from selector import select
from trader import trader
from common import get_current_five_price

class smallCapStock:
    def __init__(self, target_num=10):
        ''' 当日全部股票 '''
        self.stocks_info = select(read_cache=True)
        self.target_num = target_num
        self.trader = trader()

    def min_volume_stocks(self):
        sort_stocks = sorted(self.stocks_info.values(), key=lambda x: float(x['market_value']))
        target_stocks = sort_stocks[:self.target_num]
        return {i['code']:i for i in target_stocks}, sort_stocks[self.target_num]

    def adjust(self):
        # 10支最小市值股票 
        target_stocks_info, target_add_stock = self.min_volume_stocks()
        # 目标股票
        target_stocks = target_stocks_info.keys()
        # 持仓股票
        holding_stocks = self.trader.holding.keys()

        # 清仓 
        self.sell_out([i for i in holding_stocks if i not in target_stocks])
        # 开仓
        self.buy_in([i for i in target_stocks if i not in holding_stocks])

        # 再次清仓, 针对雪球1% 无法清仓的情况调整
        self.sell_out([i for i in holding_stocks if i not in target_stocks], first=False)

        # 剩余余额买target_num+1标的
        self.buy_in([target_add_stock.get('code')], first=False)

    def sell_out(self, stocks, first=True):
        ''' 清仓
            first 针对雪球1%无法清仓的情况对应处理
        '''
        if not first:
            # 重新获取交易信息
            self.trader = trader()
        for stock in stocks:
            amount = self.trader.holding.get(stock).get('enable_amount') or 0
            if not first or (first and amount > 100):
                trade_price = self.trade_price_decision(stock, 'sell')
                self.trader.sell(stock, amount, trade_price)

    def buy_in(self, stocks, first=True):
        ''' 开仓 
            first 针对剩余金额全部购买一支标的进行处理
        '''
        if not first:
            # 重新获取交易信息
            self.trader = trader()
        # 账户可用余额
        enable_balance = self.trader.enable_balance
        #print self.trader.balance
        for stock in stocks:
            trade_price = trade_price_decision(stock, 'buy')
            amount = int(enable_balance/self.target_num/trade_price/100) * 100 if first else\
                    int(enable_balance/trade_price/100) * 100
            if amount>=100:
                self.trader.buy(stock, amount, trade_price)

    def trade_price_decision(self, stock, direction):
        '''交易价格决策'''
        # 五档数据
        prices = get_current_five_price(stock)
        sort_prices = sorted(a.keys(), key = lambda x:float(x))
        if direction == 'sell':
            # 卖 取买一
            return sort_prices[4]
        else:
            # 买 取卖一
            return sort_prices[5]

if __name__ == '__main__':
    scs = smallCapStock()
    scs.adjust()
