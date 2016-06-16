#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

from selector import select
from trader import trader

class smallCapStock:
    def __init__(self, target_num=10):
        ''' 当日全部股票 '''
        self.target_num = target_num
        self.trader = trader()
        self.stocks_info = select(read_cache=True)

    def min_volume_stocks(self):
        sort_stocks = sorted(self.stocks_info.values(), key=lambda x: float(x['market_value']))
        target_stocks = sort_stocks[:self.target_num]
        return {i['code']:i for i in target_stocks}

    def adjust(self):
        # 10支最小市值股票
        target_stocks_info = self.min_volume_stocks()
        # 目标股票
        target_stocks = target_stocks_info.keys()
        # 持仓股票
        holding_stocks = self.trader.holding.keys()

        # 清仓股票 
        self.sell_out([i for i in holding_stocks if i not in target_stocks])
        # 开仓股票
        self.buy_in([i for i in target_stocks if i not in holding_stocks])

        # 剩余余额买价格最低的标的

    def sell_out(self, stocks):
        ''' 清仓'''
        for stock in stocks:
            amount = self.trader.holding.get(stock).get('enable_amount') or 0
            if amount > 100 :
                current_price = float(self.stocks_info.get(stock).get('now'))
                trade_price = float(current_price) - 0.01
                self.trader.sell(stock, amount, current_price)

    def buy_in(self, stocks):
        ''' 开仓 '''
        # 账户可用余额
        enable_balance = self.trader.enable_balance
        print self.trader.balance
        for stock in stocks:
            current_price = float(self.stocks_info.get(stock).get('now'))
            amount = int(enable_balance/self.target_num/current_price/100) * 100
            self.trader.buy(stock, amount, current_price)



if __name__ == '__main__':
    scs = smallCapStock()
    scs.adjust()
