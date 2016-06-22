#!/usr/bin/python2
#coding: utf-8 

from __future__ import division

from selector import select
from trader import trader
from common import get_current_five_price, get_current_ten_price

# 交易 溢价
PREMIUM = 1.02

LIMIT_DOWN = -1
LIMIT_UP = -2
STOCKS_NUM = 8

class smallCapStock:
    def __init__(self, target_num=10):
        ''' 当日全部股票 '''
        self.stocks_info = select(read_cache=False)
        self.target_num = target_num
        self.trader = trader()

    def adjust(self):
        # 持仓股票
        holding_stocks = self.trader.holding.keys()

        # 目标股票决策
        target_stocks_info, target_add_stock = self.target_stocks_decision(holding_stocks)
        target_stocks = target_stocks_info.keys()

        ## 清仓 
        self.sell_out([i for i in holding_stocks if i not in target_stocks])
        ## 开仓
        self.buy_in([i for i in target_stocks if i not in holding_stocks])

        ## 剩余余额买市值最小标的
        self.buy_in([target_add_stock.get('code')])

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
                    print '--------------------------------------------------------------------------\n'
                    print 'Sell stock: %s, amount: %s, trade price: %s\n, YES or NO' % (stock, amount, trade_price)
                    print '--------------------------------------------------------------------------\n'
                    ensure = raw_input('Sell stock: %s, amount: %s, trade price: %s, Y/N\n' % (stock, amount, trade_price))
                    if ensure.lower() == 'y' or ensure.lower() == 'yes':
                        self.trader.sell(str(stock), int(amount), trade_price)

    def buy_in(self, stocks):
        ''' 开仓 
        '''
        # 重新获取账户 可用余额
        enable_balance = self.trader.user.balance[0].get('enable_balance')
        # 每支调仓股票可用余额
        each_enable_balance = enable_balance/len(stocks)
        #print self.trader.balance
        for stock in stocks:
            amount, trade_price = self.trade_price_decision(stock, each_enable_balance, 'buy')
            if amount>=100 and int(trade_price) != 0:
                print '------------------------------------------------------------------------------\n'
                print 'Buy stock: %s, amount: %s, trade price: %s, market value: %s, YES or NO\n' % (stock, amount, trade_price, amount*trade_price)
                print '------------------------------------------------------------------------------\n'
                ensure = raw_input('Buy stock: %s, amount: %s, trade price: %s, market value: %s, Y/N\n' % (stock, amount, trade_price, amount*trade_price))
                if ensure.lower() == 'y' or ensure.lower() == 'yes':
                    self.trader.buy(str(stock), amount, trade_price)

    def target_stocks_decision(self, holding_stocks):
        ''' 考虑目标股票中存在涨停或者跌停的情况
            如果持仓中没有这些目标股票，则跳过，顺序替补次小市值股票。如果有，则持仓
        '''
        result = {}
        # target_num 支最小市值股票 
        sort_stocks = sorted(self.stocks_info.values(), key=lambda x: float(x['market_value']))
        for stock in sort_stocks:
            if len(result.keys()) >= self.target_num:
                break
            if (stock['now'] == stock['limit_up'] and stock['code'] in holding_stocks) or \
            (stock['now'] == stock['limit_down'] and stock['code'] not in holding_stocks):
                # 涨停并在持仓中  或者跌停不在持仓中 则加入目标股票池
                result[stock['code']] = stock
            elif (stock['now'] != stock['limit_up'] and stock['now'] != stock['limit_down']):
                # 非涨停跌停 加入目标池
                result[stock['code']] = stock
        add_stock = sorted(result.values(), key=lambda x: float(x['market_value']))[0]
        return result, add_stock

    def trade_price_decision(self, stock, value, direction):
        '''交易价格决策, 按十档委托数量定价
           direction: 交易方向sell 或 buy
           value: 交易方向是sell时是可用仓位, buy是可用现金
        '''
        # 十档数据
        prices = get_current_ten_price(stock)
        prices_num = len(prices)
        assert prices 

        sort_prices = sorted(prices.keys(), key = lambda x:float(x))
        sort_volumes = [prices[i] for i in sort_prices]
        if direction == 'sell':
            '''卖出'''
            if '0.00' in sort_prices and LIMIT_DOWN in sort_volumes:
                # 跌停
                raise Exception('Limit down, can not sell! Stock code: %s' % stock )
            
            # 涨停或正常交易
            price = sort_prices[int(prices_num/2)-1] if prices_num%5 == 0  else sort_prices[-1]
            num_range = int(prices_num/2) if prices_num%5 == 0 else prices_num
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
            if '0.00' in sort_prices and LIMIT_UP in sort_volumes:
                # 涨停
                raise Exception('Limit up, can not buy! Stock code: %s' % stock )

            # 跌停 或正常交易
            price = sort_volumes[int(prices_num/2):] if prices_num%5 == 0 else sort_prices[1]
            num_range = int(prices_num/2) if prices_num%5 == 0 else prices_num
            for k in range(num_range):
                idx = num_range + k
                volumes = sort_volumes[idx]
                price = sort_prices[idx]
                if not volumes:
                    continue
                if int(volumes) * float(price) * 100 > value * PREMIUM:
                    price = sort_prices[idx]
                    break
            price = float(price)
            amount = int(value/price/100) * 100
            return amount, price

if __name__ == '__main__':
    scs = smallCapStock(target_num=STOCKS_NUM)
    scs.adjust()
    #print scs.trade_price_decision(i['code'], 100000, 'buy')
