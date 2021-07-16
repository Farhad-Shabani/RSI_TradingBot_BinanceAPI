import backtrader as bt


class RSIStrategy(bt.Strategy):

    def __init__(self):
        self.order = None
        self.position.size = 0
        self.sellAlert1 = False
        self.sellAlert2 = False
        self.buyAlert = False
        self.failureNum = 0
        self.successNum = 0
        self.rsi_1 = bt.ind.RSI(self.datas[0].close, period=7)
        self.rsi_2 = bt.ind.RSI(self.datas[1].close, period=7)
        self.rsi_3 = bt.ind.RSI(self.datas[2].close, period=7)
        self.rsi_4 = bt.ind.RSI(self.datas[3].close, period=7)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                return self.log(
                    'BUY Executed at price: {} with size: {}'.format(order.executed.price, order.executed.size))

            elif order.issell():
                print('Succeeded for {} times.'.format(self.successNum))
                return self.log(
                    'SELL Executed at price: {} with size: {}'.format(order.executed.price, order.executed.size))

    def next(self):
        """Here the conditions for openinng and closing a position have been set."""
        if self.position.size == 0:
            # The condition for activating BUY function --> By checking oversold condition.
            if self.rsi_2 < 30 and self.rsi_3 < 40:
                self.buyAlert = True
            # If BUY is activated and below conditions are met, then aa buy order would be placed.
            if self.rsi_1 < 50 and self.rsi_2 > 30 and self.rsi_3 > 25 and self.buyAlert:
                size = round((self.broker.getcash() / self.data), 3)
                self.order = self.buy(size=size)
                self.buyAlert = False
                print(round(self.broker.get_cash(), 1))
                # print(self.datas[0].low[0])

        if self.position.size != 0:
            # The condition for activating SELL_1 function --> Waiting for RSI to reach overbought zone.
            if self.rsi_4 > 67:
                self.sellAlert1 = True
            # If SELL_1 is activated and below conditions are met, then a sell order would be placed.
            if (self.rsi_1 < 70 and self.rsi_4 < 60) and self.sellAlert1:
                self.close()
                self.successNum += 1
                self.sellAlert1 = False

            # The condition for activating SELL_2 function --> Activated at overbought condition with RSI>85
            if self.rsi_4 > 85:
                self.sellAlert2 = True
            # If SELL_2 is activated and below conditions are met, then a sell order would be placed.
            if (self.rsi_4 < 80) and self.sellAlert2:
                self.close()
                self.successNum += 1
                self.sellAlert1 = False
                self.sellAlert2 = False

            # Setting Stop Loss for wrongly opened position.
            if 0.82 * self.order.executed.price > self.datas[0].close > 0.8 * self.order.executed.price:
                self.close()
                self.failureNum += 1
                print('Shit !!! Failed for {} times.'.format(self.failureNum))
