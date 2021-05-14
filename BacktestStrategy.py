import backtrader as bt
import talib
import datetime

class RSIStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))


    def __init__(self):
        self.order = None
        self.position.size == 0
        self.sellAlert1 = False
        self.sellAlert2 = False
        self.buyAlert = False
        self.failureNum = 0
        self.successNum = 0 
        self.rsi_1 = bt.ind.RSI(self.datas[0].close, period=7)
        self.rsi_2 = bt.ind.RSI(self.datas[1].close, period=7)
        self.rsi_3 = bt.ind.RSI(self.datas[2].close, period=7)
        self.rsi_4 = bt.ind.RSI(self.datas[3].close, period=7)
   

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                buyComment = self.log('BUY Executed at price: {} with size: {}'.format(order.executed.price, order.executed.size))
                return buyComment
            
            elif order.issell():
                sellComment = self.log('SELL Executed at price: {} with size: {}'.format(order.executed.price, order.executed.size)) 
                print('Succeeded for {} times.'.format(self.successNum))
                return sellComment


    def next(self):

        if self.position.size == 0:
            if self.rsi_1 < 30 and self.rsi_2 < 30:
                self.buyAlert = True

            if self.rsi_2 > 25 and self.rsi_3 > 25 and self.buyAlert:
                size = round((self.broker.getcash() / self.data),3)
                self.order = self.buy(size = size)
                self.buyAlert = False
                print(round(self.broker.get_cash(),1))
                # print(self.datas[0].low[0])


        if self.position.size != 0:
            if self.rsi_4 > 70:
                self.sellAlert1 = True
            if  self.rsi_1 < 70 and self.sellAlert1:
                self.close()
                self.successNum += 1
                self.sellAlert1 = False

            if self.rsi_4 > 85:
                self.sellAlert2 = True
            if (self.rsi_4 < 80) and self.sellAlert2:
                self.close()
                self.successNum += 1
                self.sellAlert1 = False
                self.sellAlert2 = False

                # Setting Stop Loss -----------------------------------
            if  0.82 * self.order.executed.price > self.datas[0].close and 0.8 * self.order.executed.price < self.datas[0].close:
                self.close()
                self.failureNum += 1
                print('Position failed for {} times.'.format(self.failureNum))
