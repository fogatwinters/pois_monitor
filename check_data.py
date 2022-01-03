import argparse
import win32api
import win32com
import webbrowser
import itertools
import time
import operator
import os
import pickle
import re
import shutil
import sys
import time
from functools import reduce
from io import StringIO
from pathlib import Path
import pandas as pd
import requests
from requests import Session, Request
import tqdm
from pandas.tseries.offsets import MonthBegin, MonthEnd, YearBegin
from datetime import datetime, timedelta
import logging
import sqlite3
from typing import Optional, Union
import datetime
import numpy as np


def get_status():
    lookup = pd.DataFrame(
        index=['부산항', '부산항신항', '인천항', '평택당진항', '대산항',
            '군산항', '목포항', '여수광양항', '울산항', '포항항', '해운대'],
        data={
            'obsPostId': ['SF_0001', 'SF_0002', 'SF_0003', 'SF_0004', 'SF_0006', 'SF_0005', 'SF_0007', 'SF_0008', 'SF_0010', 'SF_0011', 'SF_0009'],
            'obsPostId2': ['BUSAN', 'BUSANNEW', 'INCHEON', 'IPPADO', '220', '18', '15', '9', '5', '475', 'HAE'],
            'obsType': ['Buoy', 'Buoy', 'Buoy', 'Buoy', 'DT', 'DT', 'DT', 'DT', 'DT', 'DT', 'Buoy']
        })


    end_date = datetime.datetime.now()
    # start_date =  end_date - datetime.timedelta(days=1)
    start_date =  end_date - pd.Timedelta(hours=1)
    startDate = start_date.strftime('%Y%m%d%H%M')
    endDate = end_date.strftime('%Y%m%d%H%M')

    stations=['부산항', '부산항신항', '인천항', '평택당진항', '대산항',
            '군산항', '목포항', '여수광양항', '울산항', '포항항', '해운대']
    # stations = ['대산항','군산항', '목포항', '여수광양항', '울산항', '포항항', '해운대']
    stations = ['대산항']

    dfs = []
    with Session() as s:
        for station in tqdm.tqdm(stations):
            endpoint = 'http://www.khoa.go.kr/oceanmap/pois/weatherDataDownList.do'
            data = {}
            data['obsPostId'] = lookup.loc[station, 'obsPostId']
            data['obsPostId2'] = lookup.loc[station, 'obsPostId2']
            data['obsType'] = lookup.loc[station, 'obsType']
            data['startDate'] = startDate
            data['endDate'] = endDate
            data['interval'] = '1'
            # data['checkboxValues'] = 'GET_ANGLE_STRING(WD1) AS WD1,WS1,WS2,TAAVG1M,TWAVG1M,QFFAVG1M,RHAVG1M,PRSUM1M,VIS,VIS_20000'
            data['checkboxValues'] = 'GET_ANGLE_STRING(WD1) AS WD1,WS1,TAAVG1M,TWAVG1M,QFFAVG1M,RHAVG1M,PRSUM1M,VIS,VIS_20000'
            data['obsText'] = ''
            data['dataInterval'] = '10'


            req = Request(method='post', url=endpoint, data=data)
            prep = req.prepare()
            res = s.send(prep, timeout=10)

            assert res.status_code == 200
            numeric_cols = [
                'ws1', 'taavg1m', 'qffavg1m',
                'rhavg1m', 
                'vis20000',
                ]
            df = pd.DataFrame(res.json()['selectWeatherDataList'])
            # df = df.replace('-', pd.NA)
            for col in numeric_cols:
                # df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = pd.to_numeric(df[col])
            df['tt'] = pd.to_datetime((df.tt))
            dfs.append(df)

    df = pd.concat(dfs)

    # drop_rows = df[numeric_cols].isna().all(axis=1)
    # station_count = (
    #     df.loc[~drop_rows]
    #     .groupby('obsPostId')
    #     ['vis20000']
    #     .count()
    # )
    # lines = []
    # for k,v in station_count.items():
    #     lines.append(f'{k}:{v:02d}')
    # stdout = '\n'.join(lines)
    # return stdout

    usecols = ['obsPostId', 'tt', 'wd1', 'ws1', 'taavg1m', 'twavg1m', 'qffavg1m',
       'rhavg1m', 
    #    'vis', 'vis20000'
       ]

    print(f'from {start_date} to {end_date}')
    return df[usecols].dropna(how='all').set_index(df.tt).sort_index().groupby('obsPostId').last()


def success_job():
    url = 'https://docs.python.org/'
    webbrowser.open_new(url)
    webbrowser.open_new(url)
    webbrowser.open_new(url)
if __name__ =='__main__':

    # while 1:
    #     station, _count = get_status().split(':')
    #     count = int(_count)
    #     if count > 6:
    #         url = 'https://docs.python.org/'
    #         webbrowser.open_new(url)
    #         webbrowser.open_new(url)
    #         webbrowser.open_new(url)
    #         raise
    #     else:
    #         time.sleep(30)

    def end_cond_meet(result) -> bool:
        try:
            pd.to_numeric(result.twavg1m)
        except ValueError:
            return False
        else:
            return True
    
    while 1:
        result = get_status()
        print(result)
        if end_cond_meet(result):
            success_job()
            break

        time.sleep(10)



    # assert len(result) == 7
    # while 1:
    #     result = get_status()
    #     cond = len(result.index.tolist()) > 4

    #     if cond:
    #         success_job()
    #         break
    #     time.sleep(10)


# shell = win32com.client.Dispatch("WScript.Shell")
# shell.Run(r"H:\test\1day\seafog_incheon.stream_2020-07-06-06.01.58.028-KST_0.mp4")
        
            
# value_vars = ['wd1', 'ws1', 'taavg1m', 'twavg1m', 'qffavg1m',
#        'rhavg1m', 'prsum1m', 'vis', 'vis20000']

# table = df[df['obsPostId'] =='SF_0009']

# table[table[value_vars].isna().all(axis=1)]



# pois = pd.read_csv(
#     r"D:\2021\니아\qt_품질처리\nia matplotlib qc\data\raw\대산항.csv",
#     usecols = ['시간','수온(℃)'],
#     index_col=['시간'],
#     parse_dates=['시간'])

# koofs_files = [
# r"D:\모니터\대산_DT_220_2020.txt",
# r"D:\모니터\대산_DT_220_2019.txt",
# ]
# koofs = pd.concat([pd.read_csv(
#     file, 
#     skiprows=3, sep='\t', parse_dates=['관측시간'], 
#     usecols=['관측시간','수온(℃)'],
#     dtype={'수온(℃)':np.float64},
#     na_values=['-'],
#     index_col=['관측시간'],
#     ) for file in koofs_files])

# pois.columns = ['pois']
# koofs.columns = ['koofs']

# sst = pois.join(koofs, how='inner') # 
# sst.loc[sst.koofs.isna(), 'pois'].isna().mean()


# 해무관측소 결측, 조위관측소 결측
# 해무관측소 + 조위관측소
# 해무관측소, 해무관측소 대체(조위관측소), 조위관측소
# ~해무관측소 vs 조위관측소
