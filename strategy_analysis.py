#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
#  -*- coding: utf-8 -*-
#  """
#  Created on "2022/6/24 下午4:19"
#  @author: ZHANGWEI
#  """
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import empyrical
import utils

sharpe_return =pd.read_pickle('data/sharpe_strategy_returns.pkl')
calmar_return =pd.read_pickle('data/calmar_strategy_returns.pkl')
volatility_return =pd.read_pickle('data/volatility_strategy_returns.pkl')
sortino_return =pd.read_pickle('data/sortino_strategy_returns.pkl')
ben = pd.read_pickle('data/benchmark.pkl')

sharpe_cumreturn = empyrical.cum_returns(sharpe_return)
calmar_cumreturn = empyrical.cum_returns(calmar_return)
volatility_cumreturn = empyrical.cum_returns(volatility_return)
sortino_cumreturn = empyrical.cum_returns(sortino_return)
ben_cumreturn = empyrical.cum_returns(ben)

large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")

fig, ax = plt.subplots()
sharpe, = ax.plot(sharpe_cumreturn, label='sharpe')
calmar, = ax.plot(calmar_cumreturn, label='calmar')
volatility, = ax.plot(volatility_cumreturn, label='volatility')
sortino, = ax.plot(sortino_cumreturn, label='sortino')
benchmark, = ax.plot(ben_cumreturn, label='benchmark')
ax.legend(handles=[sharpe, calmar, volatility, sortino, benchmark])
plt.show()
