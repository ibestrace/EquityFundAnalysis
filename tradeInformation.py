# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 23:07:40 2022

@author: ZHANGWEI
"""

import pandas as pd
import empyrical
import utils

# 读取格式化后的基金数据，基金净值数据格式化为‘OHLC'格式，用于后续计算
fdata = pd.read_pickle('data/fdata.pkl')

# 确定所有交易日
trade_dates = fdata.index.unique().tolist()
trade_dates.sort()

# 按月调仓，确定每月最后一个交易日
trans_dates = utils.lastTransferDatesInYear(trade_dates)  # trans_dates为调仓日列表
tdates = pd.DataFrame(trans_dates, columns=['tdate'])
tdates['tdate'] = pd.to_datetime(tdates['tdate'])
tdates.index = tdates['tdate'].apply(lambda x: x.year)

trade_info = pd.DataFrame()

st_year = 2006
ed_year = 2022
top = 20

for Y in range(st_year, ed_year):
    _trade_info = pd.DataFrame()
    fsharpe = utils.fsharpe_top(data=fdata, year=str(Y), top=top)
    _trade_info['fcode'] = fsharpe.index
    _trade_info['trade_date'] = tdates.loc[Y, 'tdate']
    _trade_info['weight'] = 1/top
    trade_info = pd.concat([trade_info, _trade_info])

trade_info = trade_info[['trade_date', 'fcode', 'weight']]
trade_info.to_pickle('data/trade_info.pkl')
