import datetime
import logging
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
from typing import Optional, Union

import numpy as np
import pandas as pd
import requests
import streamlit as st
from requests import Request, Session


st.set_page_config(layout="wide")


stations=('부산항', '부산항신항', '인천항', '평택당진항', '대산항',
        '군산항', '목포항', '여수광양항', '울산항', '포항항', '해운대')
station = st.sidebar.radio('select station', stations)

def get_dataframe(station=''):
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
    # stations = ['대산항', '포항항']
    if station == '':
        return pd.DataFrame()
    stations = [station]
    dfs = []
    with Session() as s:
        for station in stations:
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
    usecols = ['obsPostId', 'tt', 'wd1', 'ws1', 'taavg1m', 'twavg1m', 'qffavg1m',
       'rhavg1m', 
       'vis', 'vis20000'
       ]
    return df[usecols]
df = get_dataframe(station)
st.dataframe(df.style.highlight_null(), width=1080, height=1920)

# st.dataframe(df.style.highlight_max(axis=0))


