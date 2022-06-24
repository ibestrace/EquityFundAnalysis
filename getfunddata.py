# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 17:38:53 2022

@author: ZHANGWEI
"""
import pandas as pd
import akshare as ak

from utils import *

fundlist = pd.read_excel("data/fundlist.xlsx",
                         usecols=['code', 'abbreviation'],
                         dtype={'code': str})

fdata = pd.DataFrame()
fcount = len(fundlist['code'])

for fcode in fundlist.code:
    _fdata = GetFundInfoByAkshare(fund=fcode, indicator='累计净值走势')
    _fdata = formatfData(_fdata)
    _fdata['code'] = fcode
    fdata = pd.concat([fdata, _fdata])
    fcount -= 1
    print(fcode, '已完成。', '剩余：', fcount)

fdata['open'] = fdata['cumvalue']
fdata['high'] = fdata['cumvalue']
fdata['low'] = fdata['cumvalue']
fdata.rename(columns={'cumvalue': 'close', 'code': 'fcode'}, inplace=True)
_fdata = fdata[['fcode', 'open', 'high', 'low', 'close']]

_fdata.to_pickle('data/fdata.pkl')
