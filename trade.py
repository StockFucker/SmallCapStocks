#!/usr/bin/env python2
# coding: utf-8

import re
import easytrader

PLATFORM = 'xq'
CONFIG_FILE = 'account.json'

class trade:
    def __init__(self):
        self.user = easytrader.use(PLATFORM)
        self.user.prepare(CONFIG_FILE)
        self.holding = self.user.position

    def get_holding_stocks(self):
        return [i.get('stock_code') for i in self.holding]

    def buy(self, stock, amount, price):
        self.user.buy(stock, amount, price)

    def sell(self, stock, amount, price):
        self.user.sell(stock, amount, price)

if __name__ == '__main__':
    t = trade()
    t.get_holding_stocks()
