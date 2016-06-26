#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

from selector import select
from trader import trader

class smallCapStock:
    def __init__(self, target_num=10):
        ''' 当日全部股票 '''
        self.stocks_info = select(read_cache=False)
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
        clear_stocks = [i for i in holding_stocks if i not in target_stocks]
        if len(holding_stocks) == 1 and len(clear_stocks) != 0:
            self.sell_out(clear_stocks, weight = 1)
        elif len(holding_stocks) == len(clear_stocks):
            self.sell_out(clear_stocks, weight = -1)
        else:
            self.sell_out(clear_stocks)
        # 开仓
        self.buy_in([i for i in target_stocks if i not in holding_stocks])

        # 剩余余额买target_num+1标的
        self.buy_in([target_add_stock.get('code')], first=False)

    def sell_out(self, stocks, weight=0):
        ''' 清仓
        '''
        for num, stock in enumerate(stocks):
            d_weight =  0 if weight == -1 else weight
            if weight == -1 and num == len(stocks)-1:
                d_weight = 1
            if d_weight <= 100 and d_weight >= 0:
                self.trader.sell(stock, d_weight)

    def buy_in(self, stocks, first=True):
        ''' 开仓 
            first 针对剩余金额全部购买一支标的进行处理
        '''
        # 重新获取交易信息
        self.trader = trader()
        # 账户可用余额(百分比)
        enable_balance = 100 - sum([i['weight'] for i in self.trader.holding.values()])
        for stock in stocks:
            weight = (enable_balance/len(stocks)) if first else enable_balance
            if weight <=100 and weight>=0:
                self.trader.buy(stock, int(weight))

if __name__ == '__main__':
    scs = smallCapStock()
    scs.adjust()
