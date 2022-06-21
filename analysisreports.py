# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 15:41:13 2022

@author: ZHANGWEI
"""
import pandas as pd
import quantstats as qs
import akshare as ak

import utils

# 定义格式化指数数据的函数


def formatIndex(inxdata):
    inxdata = inxdata.copy()
    inxdata = inxdata.loc[:, ['date', 'close']]
    inxdata['date'] = pd.to_datetime(inxdata['date'])
    inxdata.set_index('date', inplace=True)
    return inxdata

# 读取股票型基金及偏股型基金列表，列表包括基金代码和基金简称
# 对于同一只基金存在多种份额的，仅保留A类份额，剔除其他份额
# 剔除存续时间短于1年的基金


fundlist = pd.read_excel("data/fundlist.xlsx",
                         usecols=['code', 'abbreviation'],
                         dtype={'code': str})

# 构建业绩基准
# 业绩基准=沪深300*50%+中证500*50%
# 沪深300指数和中证500指数的数据来源为腾讯财经，目标地址：http://gu.qq.com/sh000919/zs
# 通过stock_zh_index_spot_df = ak.stock_zh_index_spot()
# 获取沪深300的指数代码为sh000300,中证500的指数代码为sh000905

sh000300 = ak.stock_zh_index_daily_tx(symbol="sh000300")
sh000905 = ak.stock_zh_index_daily_tx(symbol="sh000905")

# 格式化数据
index300 = formatIndex(sh000300)
index500 = formatIndex(sh000905)

for index in range(1768, 1769):
    f = fundlist.loc[index, 'code']
    fund_hisinfo_df = utils.GetFundInfoByAkshare(fund=f,
                                                 indicator='累计净值走势')
    fcumvalue = utils.FormatData(fund_hisinfo_df)
    returns = fcumvalue.pct_change().dropna()

    # 确定基金存续期间
    st_date = fcumvalue.index[0]
    ed_date = fcumvalue.index[-1]
    # 指数数据
    inx300 = index300.loc[st_date:ed_date, :]
    inx500 = index500.loc[st_date:ed_date, :]
    # 编制比较基准
    benchmark = inx300/inx300.iloc[0, 0] * 0.5 + inx500/inx500.iloc[0, 0] * 0.5
    ben = benchmark.pct_change().dropna()

    qs.reports.html(returns,
                    benchmark=ben,
                    output='reports/',
                    title=fundlist.loc[index, 'abbreviation'] + '分析报告',
                    download_filename=fundlist.loc[index,
                                                   'abbreviation'] + '分析报告.html',
                    benchmark_title='沪深300*50%+中证500*50%')
