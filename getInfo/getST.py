# -*- coding: utf-8 -*-

from dataapiclient import Client
import tushare as ts
import pandas as pd
import json

def getStocks():
    stocks_df = ts.get_stock_basics()
    stocks = list(stocks_df.index)
    return stocks

def fetch(stock):
    try:
        client = Client()
        client.init('b3914afefef661cda6be2a6f897ce2676bd0596bb98a62c2afc15ffafd0836aa')
        url1='/api/equity/getSecST.json?field=&secID=&ticker='+stock+'&beginDate=20100101&endDate=20160220'
        code, result = client.getData(url1)
        if code==200:
            jsonObj = json.loads(result)
            if jsonObj['retCode'] == 1:
                df = pd.read_json(json.dumps(jsonObj['data']))
                file_name = "st/" + stock + ".csv"
                df = df.drop(df.columns[[1,2,3,4]],1)
                df.to_csv(file_name)
        else:
            print code
            print result
    except Exception, e:
        #traceback.print_exc()
        print "Error:" + stock

def go(stocks):
    # for stock in stocks:
    #     if int(stock) > 2506:
    fetch("000001")

go(getStocks())
