'''
搭建量化研究函数库
'''
# 导入必备的库
import pandas as pd
import akshare as ak

# 获取基金代码列表
def GetFundName():
	return ak.fund_name_em()

# 通过基金代码读取基金的历史净值
def GetFundInfoByAkshare(fund, indicator):
	'''
	:param fund:基金代码
	:param indicator:单位净值走势、累计净值走势、累计收益率走势、同类排名走势、同类排名百分比、分红送配详情、拆分详情	-
	:return:
	'''
	return ak.fund_open_fund_info_em(fund=fund, indicator=indicator)

# 格式化基金的历史净值
def FormatData(fund_open_fund_info_em_df):
	data = fund_open_fund_info_em_df
	data.rename(columns={'净值日期': 'date', '累计净值': 'cumvalue'}, inplace=True)
	data.date = pd.to_datetime(data['date'])
	data.set_index('date', inplace=True)
	cumvalue = pd.Series(data.cumvalue)
	return cumvalue

