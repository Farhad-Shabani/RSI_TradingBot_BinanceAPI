from BacktestStrategy import RSIStrategy
import backtrader as bt
import datetime


# Please select your crypto trading style: 'Day_Trading' or 'Swing_Trading' or 'Position_Trading'
Trading_Style = 'Swing_Trading'
From_Date = "2020-01-04"
To_Date = "2021-01-01"


def Run_Backtest(strategy, tradingstyle, fromdate, todate):

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000)

    Style_Dict = {'Day_Trading':['1M', '5M', '15M', '1H'],
                'Swing_Trading':['5M', '15M', '1H', '4H'],
                'Position_Trading':['15M', '1H', '4H', '1D']
                }
    fromdate = datetime.datetime.strptime(fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(todate, '%Y-%m-%d')
    Data_TF1 = bt.feeds.GenericCSVData(dataname='data\klines_{}.csv'.format(Style_Dict[tradingstyle][0]), dtformat=2, open=1, high=2, low=3, close=4, volume=5, timeframe=bt.TimeFrame.Minutes, fromdate= fromdate, todate=todate)
    Data_TF2 = bt.feeds.GenericCSVData(dataname='data\klines_{}.csv'.format(Style_Dict[tradingstyle][1]), dtformat=2, open=1, high=2, low=3, close=4, volume=5, timeframe=bt.TimeFrame.Minutes, fromdate= fromdate, todate=todate)
    Data_TF3 = bt.feeds.GenericCSVData(dataname='data\klines_{}.csv'.format(Style_Dict[tradingstyle][2]), dtformat=2, open=1, high=2, low=3, close=4, volume=5, timeframe=bt.TimeFrame.Minutes, fromdate= fromdate, todate=todate)
    Data_TF4 = bt.feeds.GenericCSVData(dataname='data\klines_{}.csv'.format(Style_Dict[tradingstyle][3]), dtformat=2, open=1, high=2, low=3, close=4, volume=5, timeframe=bt.TimeFrame.Minutes, fromdate= fromdate, todate=todate)

    cerebro.adddata(Data_TF1)
    cerebro.adddata(Data_TF2)
    cerebro.adddata(Data_TF3)
    cerebro.adddata(Data_TF4)

    cerebro.addstrategy(strategy)
    print('Starting Portfolio Value: %0.2f' % cerebro.broker.getvalue())

    cerebro.run()
    print('Final Portfolio Value: %0.2f' % cerebro.broker.getvalue())

    Data_TF4.plotinfo.plot = False
    # Data_TF1.plotinfo.plotlog = True
    # Data_TF4.plotinfo.plotlog = True
    cerebro.plot()

Run_Backtest(RSIStrategy, Trading_Style, From_Date, To_Date)