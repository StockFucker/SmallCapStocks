# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/sgcy/anaconda/lib/python2.7/site-packages')

import tushare as ts
import pandas as pd
import math
import json


def read_csv(file_name):
    try:
        df = pd.read_csv(file_name,header=None,names=["date","volume"])
        return df
    except Exception, e:
        print e
        return None

def calculateDailyTotalValue():
    df = ts.get_today_all()

    df.set_index(['code'],inplace = True)

    total_se = pd.Series(index = df.index)
    for code, row in df.iterrows():
        file_name = "volumes/" + code + ".csv"
        volume_df = read_csv(file_name)
        if volume_df is None:
            continue
        volume_df = volume_df.replace({'万股': ''}, regex=True)
        volume_df['date'] = pd.to_datetime(volume_df['date'])
        volume_df = volume_df.set_index(['date'])
        volume_df.sort(ascending=False,inplace = True)
        # isnan?
        try:
            total_se[code] = float(list(volume_df["volume"])[0]) * float(row['settlement'])
        except Exception, e:
            print code
            print e

    df['total'] = total_se
    df = df.sort(['total'])

    print df

calculateDailyTotalValue()
