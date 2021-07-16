import numpy as np
import talib
import time
from binance.client import Client
from binance.enums import *
import Config


# Trading Strategy --------------------------------------------------------------------------------------------------
class AlgorithmTrading:

    def __init__(self, mainkey, secretkey, live, trade_symbol, order_size):
        self.Binance_Client = Client(mainkey, secretkey)
        self.Live = live
        self.Trade_Symbol = trade_symbol
        self.Order_Size = order_size
        self.In_Position = True
        self.buyAlert = False
        self.sellAlert1 = False
        self.sellAlert2 = False
        self.Buy_Price = 0
        self.Order = []
        if self.Live:
            Symbol_Quantity = self.Binance_Client.get_asset_balance(asset=self.Trade_Symbol[:-4])
            self.Symbol_Quantity = float(Symbol_Quantity['free'])
            USDT_Balance = self.Binance_Client.get_asset_balance(asset='USDT')
            self.USDT_Balance = float(USDT_Balance['free'])
        else:
            self.USDT_Balance = 1000
            self.Symbol_Quantity = 0

    def create_order(self, side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
        try:
            print("sending order")
            order = self.Binance_Client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
            self.Order.append(order)
            print(order)
        except Exception as e:
            print("an error occured - {}".format(e))
            return False
        return True

    def rsi_maker(self, data, period):
        data = np.array(data).astype(float)
        RSI_Data = talib.RSI(data[:, 4], timeperiod=period)
        Last_RSI_Data = round(RSI_Data[-1], 1)
        return RSI_Data, Last_RSI_Data

    def rsi_data(self, trading_style, rsi_period=14):
        Time_Frames = {'1M': [Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC"],
                       '5M': [Client.KLINE_INTERVAL_5MINUTE, "4 hours ago UTC"],
                       '15M': [Client.KLINE_INTERVAL_15MINUTE, "8 hours ago UTC"],
                       '1H': [Client.KLINE_INTERVAL_1HOUR, "2 day ago UTC"],
                       '4H': [Client.KLINE_INTERVAL_4HOUR, "4 days ago UTC"],
                       '1D': [Client.KLINE_INTERVAL_1DAY, "16 days ago UTC"]
                       }
        Style_Dict = {'Day_Trading': [Time_Frames['1M'], Time_Frames['5M'], Time_Frames['15M'], Time_Frames['1H']],
                      'Swing_Trading': [Time_Frames['5M'], Time_Frames['15M'], Time_Frames['1H'], Time_Frames['4H']],
                      'Position_Trading': [Time_Frames['15M'], Time_Frames['1H'], Time_Frames['4H'], Time_Frames['1D']]
                      }
        kline_1 = self.Binance_Client.get_historical_klines(self.Trade_Symbol, Style_Dict[trading_style][0][0],
                                                            Style_Dict[trading_style][0][1])
        kline_2 = self.Binance_Client.get_historical_klines(self.Trade_Symbol, Style_Dict[trading_style][1][0],
                                                            Style_Dict[trading_style][1][1])
        kline_3 = self.Binance_Client.get_historical_klines(self.Trade_Symbol, Style_Dict[trading_style][2][0],
                                                            Style_Dict[trading_style][2][1])
        kline_4 = self.Binance_Client.get_historical_klines(self.Trade_Symbol, Style_Dict[trading_style][3][0],
                                                            Style_Dict[trading_style][3][1])
        rsi_1, last_rsi_1 = self.rsi_maker(kline_1, rsi_period)
        rsi_2, last_rsi_2 = self.rsi_maker(kline_2, rsi_period)
        rsi_3, last_rsi_3 = self.rsi_maker(kline_3, rsi_period)
        rsi_4, last_rsi_4 = self.rsi_maker(kline_4, rsi_period)
        return rsi_1, last_rsi_1, rsi_2, last_rsi_2, rsi_3, last_rsi_3, rsi_4, last_rsi_4

    def rsi_strategy(self, trading_style, rsi_period, mark_price):
        Order_Succeeded = False
        RSI_1, Last_RSI_1, RSI_2, Last_RSI_2, RSI_3, Last_RSI_3, RSI_4, Last_RSI_4 = self.rsi_data(trading_style,
                                                                                                   rsi_period)
        if not self.In_Position and self.USDT_Balance > 10:
            if Last_RSI_2 < 30 and Last_RSI_3 < 40:
                self.buyAlert = True
                print('Buy alert is activated!')
            if Last_RSI_1 < 50 and Last_RSI_2 > 30 and Last_RSI_3 > 25 and self.buyAlert:
                Trade_Quantity = round((self.USDT_Balance / mark_price), 3) * self.Order_Size
                if self.Live:
                    Order_Succeeded = self.create_order(SIDE_BUY, Trade_Quantity, self.Trade_Symbol)
                if Order_Succeeded or not self.Live:
                    self.buyAlert, self.In_Position = False, True
                    self.Buy_Price = mark_price
                    self.Symbol_Quantity += Trade_Quantity
                    self.USDT_Balance -= self.Buy_Price * Trade_Quantity
                    print('BUY!! BUY!! BUY!! with the size of {}'.format(Trade_Quantity))

        if self.In_Position:
            if Last_RSI_4 > 67:
                self.sellAlert1 = True
                print('Sell alert1 is activated!')
            if (Last_RSI_2 < 70 and Last_RSI_4 < 60) and self.sellAlert1:
                if self.Live:
                    Order_Succeeded = self.create_order(SIDE_SELL, self.Symbol_Quantity, self.Trade_Symbol)
                if Order_Succeeded or not self.Live:
                    self.sellAlert1, self.In_Position = False, False
                    self.USDT_Balance = self.Symbol_Quantity * mark_price
                    self.Symbol_Quantity = 0
                    print('Position is closed based on SellAlert1')

            if Last_RSI_4 > 85:
                self.sellAlert2 = True
                print('Sell alert2 is activated!')
            if (Last_RSI_4 < 80) and self.sellAlert2:
                if self.Live:
                    Order_Succeeded = self.create_order(SIDE_SELL, self.Symbol_Quantity, self.Trade_Symbol)
                if Order_Succeeded or not self.Live:
                    self.sellAlert1, self.sellAlert2, self.In_Position = False, False, False
                    self.USDT_Balance = self.Symbol_Quantity * mark_price * 0.99
                    self.Symbol_Quantity = 0
                    print('Position is closed based on SellAlert2')

            # Setting Stop-Loss to close position in worst case scenario -----------------------------------------------
            if 0.82 * self.Buy_Price > mark_price > 0.8 * self.Buy_Price:
                if self.Live:
                    Order_Succeeded = self.create_order(SIDE_SELL, self.Symbol_Quantity, self.Trade_Symbol)
                if Order_Succeeded or not self.Live:
                    self.sellAlert1, self.sellAlert2, self.In_Position = False, False, False
                    self.USDT_Balance = self.Symbol_Quantity * mark_price * 0.99
                    self.Symbol_Quantity = 0
                    print('Shitt!!! Position Failed .....')

        Total_Asset = self.USDT_Balance + self.Symbol_Quantity * mark_price

        # return USDT_Balance, Total_Asset, mark_price, Last_RSI_1, Last_RSI_2, Last_RSI_3, Last_RSI_4
        print(
            '{}   |USDT_Balannce: {}  |Total_Asset: {}  |Price: {}  |RSI_1: {}  |RSI_2: {}  |RSI_3: {}  |RSI_4: '
            '{}'.format(
                time.asctime(), self.USDT_Balance, Total_Asset, mark_price, Last_RSI_1, Last_RSI_2, Last_RSI_3,
                Last_RSI_4))


if __name__ == "__main__":
    API_Keys = Config.api_keys('test')
    AT = AlgorithmTrading(API_Keys['key'], API_Keys['secret'], False, 'BTCUSDT', 1)
    AT.rsi_strategy('Day_Trading', 7, 1.7)
