import Config
import json
import websocket
from binance.client import Client
from MainStrategy import AlgorithmTrading

# ---------------------------------------- Set Your Trading Parameters -----------------------------------------------
# Declare your Binance API connection keys:
API_Keys = Config.api_keys('test')

# Please set the algorithm Status: Live or Test
Live = False

# Please select your trading style: 'Day_Trading' or 'Swing_Trading' or 'Position_Trading'
Trading_Style = 'Day_Trading'

# Please choose your trading symbol, order size (proportion of you balance) and set the period of RSI indicator
Trade_Symbol = "ALGOUSDT"
Order_Size = 1
RSI_PERIOD = 7


# Socket Functions ----------------------------------------------------------------------------------------------------
class RunBot:
    def __init__(self, mainkey, secretkey, live, trading_style, trade_symbol, order_size, rsi_period):
        self.Live = live
        self.Trading_Style = trading_style
        self.Trade_Symbol = trade_symbol
        self.Order_Size = order_size
        self.Rsi_Period = rsi_period
        self.Binance_Client = Client(mainkey, secretkey)
        print("logged In")
        self.AT = AlgorithmTrading(mainkey, secretkey, self.Live, self.Trade_Symbol, self.Order_Size)
        self.SOCKET_miniTicker = "wss://stream.binance.com:9443/ws/{}@miniTicker".format(self.Trade_Symbol.lower())
        WS = websocket.WebSocketApp(self.SOCKET_miniTicker, on_open=self.on_open,
                                    on_close=self.on_close, on_message=self.on_message)
        WS.run_forever()

    def on_open(self, ws):
        print('Opened connection')

    def on_close(self, ws):
        print('Closed connection')
        WS = websocket.WebSocketApp(self.SOCKET_miniTicker, on_open=self.on_open,
                                    on_close=self.on_close, on_message=self.on_message)
        WS.run_forever()

    def on_message(self, ws, message):
        Listen_Key = self.Binance_Client.stream_get_listen_key()
        self.Binance_Client.stream_keepalive(Listen_Key)
        json_message = json.loads(message)
        Mark_Price = float(json_message['c'])
        self.AT.rsi_strategy(self.Trading_Style, self.Rsi_Period, Mark_Price)


if __name__ == "__main__":
    RunBot(API_Keys['key'], API_Keys['secret'], Live, Trading_Style, Trade_Symbol, Order_Size, RSI_PERIOD)
