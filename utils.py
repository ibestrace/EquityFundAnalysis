'''
搭建量化研究函数库
'''
# 导入必备的库
import pandas as pd
import numpy as np
import akshare as ak
import quantstats as qs
import empyrical


# =============================================================================
# 获取基金代码列表
# =============================================================================

def GetFundName():
    return ak.fund_name_em()


# =============================================================================
# 通过基金代码读取基金的历史净值
# =============================================================================


def GetFundInfoByAkshare(fund, indicator):
    '''
    :param fund:基金代码
    :param indicator:单位净值走势、累计净值走势、累计收益率走势、同类排名走势、同类排名百分比、分红送配详情、拆分详情	-
    :return:
    '''
    return ak.fund_open_fund_info_em(fund=fund, indicator=indicator)

# =============================================================================
# 格式化基金的历史净值，生成Series格式时间序列数据，用于单只基金的分析
# =============================================================================


def FormatData(fund_open_fund_info_em_df):
    data = fund_open_fund_info_em_df
    data.rename(columns={'净值日期': 'date', '累计净值': 'cumvalue'}, inplace=True)
    data.date = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    cumvalue = pd.Series(data.cumvalue)
    return cumvalue

# =============================================================================
# 格式化基金的历史净值，生成DataFrame格式时间序列数据，用于
# =============================================================================


def formatfData(fdata):
    data = fdata
    data.rename(columns={'净值日期': 'date', '累计净值': 'cumvalue'}, inplace=True)
    data.date = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    return data

def formatIndex(inxdata):
    inxdata = inxdata.copy()
    inxdata = inxdata.loc[:, ['date', 'close']]
    inxdata['date'] = pd.to_datetime(inxdata['date'])
    inxdata.set_index('date', inplace=True)
    return inxdata

# =============================================================================
# 计算调仓日期列表，调仓日期为每月最后一个交易日
# =============================================================================

def lastTransferDatesInMonth(trade_dates):
    '''
    Parameters
    ----------
    trade_dates : list
        交易日列表.

    Returns
    -------
    调仓日列表
    '''
    last = list()
    trade_dates = trade_dates.copy()
    trade_dates.sort()
    _transdates = pd.DataFrame(trade_dates, columns=['trade_dates'])
    _transdates['trade_dates'] = pd.to_datetime(_transdates['trade_dates'])
    _transdates.index = _transdates['trade_dates']
    _transdates['month'] = _transdates.index.month
    _transdates['last'] = _transdates['trade_dates'].where(
        _transdates['month'] != _transdates.shift(-1)['month'], np.nan)
    last += list(_transdates['last'].dropna())
    last.sort()

    return last

# =============================================================================
# 计算调仓日期列表，调仓日期为每年最后一个交易日
# =============================================================================


def lastTransferDatesInYear(trade_dates):
    last = list()
    trade_dates = trade_dates.copy()
    trade_dates.sort()
    _transdates = pd.DataFrame(trade_dates, columns=['trade_dates'])
    _transdates['trade_dates'] = pd.to_datetime(_transdates['trade_dates'])
    _transdates.index = _transdates['trade_dates']
    _transdates['year'] = _transdates.index.year
    _transdates['last'] = _transdates['trade_dates'].where(
        _transdates['year'] != _transdates.shift(-1)['year'], np.nan)
    last += list(_transdates['last'].dropna())
    last.sort()

    return last

# =============================================================================
# 计算基金列表中给定年度的夏普比率排名前n的基金列表及对应夏普比
# =============================================================================


def fsharpe_top(data, year, top=20):
    fdata = data
    year = year
    top = top

    fdataY = fdata.filter(like=year, axis=0)
    flistY = fdataY['fcode'].unique().tolist()

    sharpe = list()

    for fcode in flistY:
        _fdata = fdataY[fdataY['fcode'] == fcode]
        _fcumvalue = _fdata['close']
        returns = pd.Series(_fcumvalue.pct_change().dropna())
        _sharpe = empyrical.sharpe_ratio(returns)
        sharpe.append(_sharpe)

    fsharpe = pd.DataFrame(data=sharpe,
                           index=flistY)
    fsharpe.columns = ['sharpe']

    fsharpe_avg = fsharpe.mean()
    fsharpe_std = fsharpe.std()
    _fsharpe = fsharpe
    _fsharpe['Z'] = fsharpe['sharpe'].apply(
        lambda x: (x-fsharpe_avg)/fsharpe_std)
    _fsharpe.sort_values(by='Z',
                         ascending=False,
                         inplace=True)

    return _fsharpe.head(top)
