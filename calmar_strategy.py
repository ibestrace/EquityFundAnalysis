#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
#  -*- coding: utf-8 -*-
#  """
#  Created on "2022/6/24 下午1:11"
#  @author: ZHANGWEI
#  """
import datetime

import akshare as ak
import backtrader as bt
import pandas as pd
import quantstats as qs

import utils

# =============================================================================
# 第一步：根据calmar比率指标计算调仓列表
# =============================================================================
# 读取格式化后的基金数据，基金净值数据格式化为‘OHLC'格式，用于后续计算
print("------------------------开始计算调仓列表------------------------")
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
pnum = 20

for Y in range(st_year, ed_year):
	_trade_info = pd.DataFrame()
	fcalmar = utils.fcalmar_prefer(data=fdata, year=str(Y), pnum=pnum)
	_trade_info['fcode'] = fcalmar.index
	_trade_info['trade_date'] = tdates.loc[Y, 'tdate']
	_trade_info['weight'] = 1 / pnum
	trade_info = pd.concat([trade_info, _trade_info])
	print(Y, 'Done!')

trade_info = trade_info[['trade_date', 'fcode', 'weight']]
trade_info.to_pickle('data/calmar_strategy_trade_info.pkl')
print("--------------------调仓列表已完成--------------------")

# =============================================================================
# 第二步：根据调仓列表进行回测
# =============================================================================

class CalmarStrategy(bt.Strategy):
	# =========================================================================
	#     基于调仓表的单因子选集
	# =========================================================================
	def __init__(self):
		# =====================================================================
		#         读取调仓表，表结构如下所示：
		#               trade_date  fcode    weight
		#         0     2006-12-31  481004   0.05
		#         1     2006-12-31  240009   0.05
		#         ...   ...         ...         ...
		#         19    2021-12-31  005669   0.05
		#                                    等权重
		# =====================================================================
		self.buy_fund = pd.read_pickle("data/calmar_strategy_trade_info.pkl")
		# 读取调仓日期，即每年的最后一个交易日，回测时，会在这一天下单，然后在下一个交易日，以净值申购
		self.trade_dates = pd.to_datetime(
			self.buy_fund['trade_date'].unique()).tolist()
		print(self.trade_dates)
		self.order_list = []  # 记录以往订单，方便调仓日对未完成订单做处理
		self.buy_funds_pre = []  # 记录上一期持仓
		print('------------------初始化完成!------------------')

	def log(self, txt, dt=None):
		''' 策略日志打印函数'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def next(self):
		dt = self.datas[0].datetime.date(0)  # 获取当前的回测时间点
		# print('运行中', dt)
		# 如果是调仓日，则进行调仓操作
		if dt in self.trade_dates:
			print("--------------{} 为调仓日----------".format(dt))
			# 在调仓之前，取消之前所下的没成交也未到期的订单
			if len(self.order_list) > 0:
				for od in self.order_list:
					self.cancel(od)  # 如果订单未完成，则撤销订单
				self.order_list = []  # 重置订单列表
			# 提取当前调仓日的持仓列表
			buy_funds_data = self.buy_fund.query(f"trade_date=='{dt}'")
			long_list = buy_funds_data['fcode'].tolist()
			print('long_list', long_list)  # 打印持仓列表
			# 对现有持仓中，调仓后不再继续持有的基金进行卖出平仓
			sell_fund = [i for i in self.buy_funds_pre if i not in long_list]
			print('sell_fund', sell_fund)  # 打印平仓列表
			if len(sell_fund) > 0:
				print("-----------对不再持有的基金进行平仓--------------")
				for fund in sell_fund:
					data = self.getdatabyname(fund)
					if self.getposition(data).size > 0:
						od = self.close(data=data)
						self.order_list.append(od)  # 记录卖出订单
			# 买入此次调仓的基金：多退少补原则
			print("-----------买入此次调仓期的基金--------------")
			for fund in long_list:
				w = buy_funds_data.query(f"fcode=='{fund}'")[
					'weight'].iloc[0]  # 提取持仓权重
				data = self.getdatabyname(fund)
				order = self.order_target_percent(
					data=data, target=w * 0.95)  # 为减少可用资金不足的情况，留 5% 的现金做备用
				self.order_list.append(order)
			self.buy_funds_pre = long_list  # 保存此次调仓的基金列表

	def notify_order(self, order):
		# 未被处理的订单
		if order.status in [order.Submitted, order.Accepted]:
			return
		# 已经处理的订单
		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Fund: %s' %
					(order.ref,  # 订单编号
					 order.executed.price,  # 成交价
					 order.executed.value,  # 成交额
					 order.executed.comm,  # 佣金
					 order.executed.size,  # 成交量
					 order.data._name))  # 基金名称
			else:  # Sell
				self.log('SELL EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Fund: %s' %
				         (order.ref,
				          order.executed.price,
				          order.executed.value,
				          order.executed.comm,
				          order.executed.size,
				          order.data._name))


# 实例化 cerebro
cerebro = bt.Cerebro()
# 读取行情数据
daily_price = pd.read_pickle("data/fdata.pkl")
daily_price['volume'] = 0
daily_price['openinterest'] = 0
# 按基金代码，依次循环传入数据
for fund in daily_price['fcode'].unique():
	# 日期对齐
	data = pd.DataFrame(index=daily_price.index.unique().sort_values())  # 获取回测区间内所有交易日
	df = daily_price.query(f"fcode=='{fund}'")[
		['open', 'high', 'low', 'close', 'volume', 'openinterest']]
	data_ = pd.merge(data, df, left_index=True, right_index=True, how='left')
	# 缺失值处理：日期对齐时会使得有些交易日的数据为空，所以需要对缺失数据进行填充
	data_.loc[:, ['volume', 'openinterest']] = data_.loc[:,
	                                           ['volume', 'openinterest']].fillna(0)
	data_.loc[:, ['open', 'high', 'low', 'close']] = data_.loc[:,
	                                                 ['open', 'high', 'low', 'close']].fillna(method='pad')
	data_.loc[:, ['open', 'high', 'low', 'close']] = data_.loc[:,
	                                                 ['open', 'high', 'low', 'close']].fillna(0)
	# 导入数据
	datafeed = bt.feeds.PandasData(dataname=data_,
	                               fromdate=datetime.datetime(2006, 12, 22),
	                               todate=datetime.datetime(2022, 6, 22))
	cerebro.adddata(datafeed, name=fund)  # 通过 name 实现数据集与基金的一一对应
	print(f"{fund} Done !")

print("-----------------------数据导入完成，开始策略回测。-----------------------")
# 初始资金 100,000,000
cerebro.broker.setcash(100000000.0)
# strcash = cerebro.Broker.getvalue()

# 佣金，双边各 0.0001
cerebro.broker.setcommission(commission=0.0001)
# 滑点：双边各 0.0001
# cerebro.broker.set_slippage_perc(perc=0.0001)

cerebro.addstrategy(CalmarStrategy)

cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
result = cerebro.run()
# fnlcash = cerebro.Broker.getvalue()
# print('\t起始资金 Starting Portfolio Value: %.2f' % strcash)
# print('\t资产总值 Final Portfolio Value: %.2f' % fnlcash)
returns = result[0].analyzers.returns
ret = pd.Series(returns.get_analysis())
ret.to_pickle('data/calmar_strategy_returns.pkl')

# 构建业绩基准
# 业绩基准=沪深300*50%+中证500*50%
# 沪深300指数和中证500指数的数据来源为腾讯财经，目标地址：http://gu.qq.com/sh000919/zs
# 通过stock_zh_index_spot_df = ak.stock_zh_index_spot()
# 获取沪深300的指数代码为sh000300,中证500的指数代码为sh000905
sh000300 = ak.stock_zh_index_daily_tx(symbol="sh000300")
sh000905 = ak.stock_zh_index_daily_tx(symbol="sh000905")
# 格式化数据
index300 = utils.formatIndex(sh000300)
index500 = utils.formatIndex(sh000905)

st_date = ret.index[0]
ed_date = ret.index[-1]

inx300 = index300.loc[st_date:ed_date, :]
inx500 = index500.loc[st_date:ed_date, :]

benchmark = inx300 / inx300.iloc[0, 0] * 0.5 + inx500 / inx500.iloc[0, 0] * 0.5
ben = benchmark.pct_change().dropna()

qs.reports.html(returns=ret,
                benchmark=ben,
                title='Calmar Strategy Tearsheet',
                output='EquityFundAnalysis\reports',
                download_filename='CalmarStrategyReport.html',
                benchmark_title='沪深300*50%+中证500*50%')
print("--------------------策略回测完成，策略分析报告生成完毕。--------------------")