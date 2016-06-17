#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

from selector import select
from trader import trader
from common import get_current_five_price, get_current_ten_price

# 交易 溢价
PREMIUM = 1.02

class smallCapStock:
    def __init__(self, target_num=10):
        ''' 当日全部股票 '''
        self.stocks_info = select(read_cache=True)
        self.target_num = target_num
        #self.trader = trader()

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

        # 剩余余额买target_num+1标的
        self.buy_in([target_add_stock.get('code')], first=False)

    def sell_out(self, stocks):
        ''' 清仓
        '''
        for stock in stocks:
            amount = self.trader.holding.get(stock).get('enable_amount') or 0
            if amount > 100:
                # amount 单位是股票数，不是手数
                decision = self.trade_price_decision(stock, amount, 'sell')
                trade_price = decision[1]
                if int(trade_price) != 0:
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
            amount, trade_price = trade_price_decision(stock, enable_balance, 'buy', first)
            if amount>=100 and int(trade_price) != 0:
                self.trader.buy(stock, amount, trade_price)

    def trade_price_decision(self, stock, value, direction, first=False):
        '''交易价格决策, 按十档委托数量定价
           direction: 交易方向sell 或 buy
           value: 交易方向是sell时是可用仓位, buy是可用现金
           first: 是否全仓买入
        '''
        # 十档数据
        prices = get_current_ten_price(stock)
        prices_num = len(prices)
        assert prices 

        sort_prices = sorted(prices.keys(), key = lambda x:float(x))
        sort_volumes = [prices[i] for i in sort_prices]
        if direction == 'sell':
            '''卖出'''
            if '0.00' in sort_prices and -1 in sort_volumes:
                # 跌停
                raise Exception('Limit down, can not sell! Stock code: %s' % stock )
            
            # 涨停或正常交易
            price = sort_prices[int(prices_num/2)-1] if prices_num == 10 or prices_num == 20 else sort_prices[-1]
            num_range = int(prices_num/2) if prices_num == 10 or prices_num == 20 else prices_num
            for k in range(num_range):
                idx = num_range-k-1
                volumes = sort_volumes[idx]
                if not volumes:
                    #部分成交
                    continue
                price = sort_prices[idx]
                if int(volumes)*100 > int(value) * PREMIUM:
                    price = sort_prices[idx]
                    break
            return None, float(price)
        else:
            '''买入'''
            if '0.00' in sort_prices and -2 in sort_volumes:
                # 涨停
                raise Exception('Limit up, can not buy! Stock code: %s' % stock )

            # 跌停 或正常交易
            price = sort_volumes[int(prices_num/2):] if prices_num == 10 or prices_num == 20 else sort_prices[1]
            num_range = int(prices_num/2) if prices_num == 10 or prices_num == 20 else prices_num
            for k in range(num_range):
                idx = num_range+k
                volumes = sort_volumes[idx]
                price = sort_prices[idx]
                if not volumes:
                    continue
                if int(volumes) * float(price) * 100 > value * PREMIUM:
                    price = sort_prices[idx]
                    break
            price = float(price)
            amount = int(value/self.target_num/price/100) * 100 if first else\
                    int(value/price/100) * 100
            return amount, price

if __name__ == '__main__':
    scs = smallCapStock()
    #scs.adjust()
    print scs.trade_price_decision('600446', 45900, 'sell')
