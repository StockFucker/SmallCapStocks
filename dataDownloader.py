
from dataapiclient import Client
import pandas as pd
import json

from pymongo import MongoClient

client = MongoClient()

def saveOneToMongo(json):
    global client
    db = client.data
    result = db.stocklist.insert_one({"stocklist":json})


def saveManyToMongo(json):
    global client
    db = client.data
    result = db.stockslist.insert_many(json)
    print result

def readFromMongo():
    global client
    db = client.data
    result = db.stockslist.find().pretty()
    # obj = json.dumps(result)
    print result
    print type(result)
    df = pd.read_json(result)
    print df


def fetch():
    try:
        client = Client()
        client.init('b3914afefef661cda6be2a6f897ce2676bd0596bb98a62c2afc15ffafd0836aa')
        url1='/api/master/getSecID.json?field=&assetClass=E'
        code, result = client.getData(url1)
        if code==200:
            jsonObj = json.loads(result)
            if jsonObj['retCode'] == 1:
                # print jsonObj['data']
                saveManyToMongo(json.loads(json.dumps(jsonObj['data'])))
                # df = pd.read_json(json.dumps(jsonObj['data']))
                # print df
                # file_name = "st/" + stock + ".csv"
                # df = df.drop(df.columns[[1,2,3,4]],1)
                # df.to_csv(file_name)
        else:
            print code
            print result
    except Exception, e:
        #traceback.print_exc()
        print e

readFromMongo()