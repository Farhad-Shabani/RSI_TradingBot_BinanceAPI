from BacktestStrategy import RSIStrategy
import backtrader as bt
import datetime

# Please insert the parameters and your trading style: 'Day_Trading' or 'Swing_Trading' or 'Position_Trading'
Symbol = "ALGOUSDT"
Trading_Style = "Position_Trading"
Default_Cash = 1000
From_Date = "2020-01-04"
To_Date = "2021-01-01"


def style_timeframes(style):
    style_dict = {'Day_Trading': ['1M', '5M', '15M', '1H'],
                  'Swing_Trading': ['5M', '15M', '1H', '4H'],
                  'Position_Trading': ['15M', '1H', '4H', '1D']
                  }
    return style_dict[style]


def date_format(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d')


def data_from_file(symbol, tradingstyle, fromdate, todate):
    """ to import desired data from CSV files. """
    tfs = style_timeframes(tradingstyle)
    fromdate = date_format(fromdate)
    todate = date_format(todate)
    data = []
    for i in range(4):
        filename = 'data\{}_klines_{}.csv'.format(symbol, tfs[i])
        data_TF = bt.feeds.GenericCSVData(dataname=filename, dtformat=2, datetime=2,
                                          open=3, high=4, low=5, close=6, volume=7,
                                          timeframe=bt.TimeFrame.Minutes,
                                          fromdate=fromdate, todate=todate)
        data.append(data_TF)
    return data


def run_backtest(strategy, data, cash):
    """To run backtest based on selected strategy and imported data """
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)
    for dt in data:
        cerebro.adddata(dt)

    cerebro.addstrategy(strategy)
    print('Starting Portfolio Value: %0.2f' % cerebro.broker.getvalue())

    cerebro.run()
    print('Final Portfolio Value: %0.2f' % cerebro.broker.getvalue())

    data[1].plotinfo.plot = False
    data[3].plotinfo.plot = False
    data[0].plotinfo.plotlog = True
    data[3].plotinfo.plotlog = True
    cerebro.plot()


if __name__ == "__main__":
    Data = data_from_file(Symbol, Trading_Style, From_Date, To_Date)
    run_backtest(RSIStrategy, Data, Default_Cash)
