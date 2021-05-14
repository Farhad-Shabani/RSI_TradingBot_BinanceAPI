import Config, csv
from binance.client import Client


Main_Key = Config.API_Key
Secret_Key = Config.API_Secret
Symbol = "ALGOUSDT"
From_Date = "1 Jan, 2020"
To_Date = "7 May, 2021"


Binance_Client = Client(Main_Key, Secret_Key)
print("logged In")

def Database_Maker(filename, symbol, timeframe, fromdate, todate):

    Time_Frames = {'1M':Client.KLINE_INTERVAL_1MINUTE,
                    '5M':Client.KLINE_INTERVAL_5MINUTE,
                    '15M':Client.KLINE_INTERVAL_15MINUTE,
                    '1H':Client.KLINE_INTERVAL_1HOUR,
                    '4H':Client.KLINE_INTERVAL_4HOUR,
                    '1D':Client.KLINE_INTERVAL_1DAY          
                }
    kline_maker = Binance_Client.get_historical_klines(symbol, Time_Frames[timeframe], fromdate, todate)
    CSVfile = open('data\{}.csv'.format(filename), 'w', newline='') 
    kline_Writer = csv.writer(CSVfile, delimiter=',')
    for kline in kline_maker:
        kline[0] = kline[0] / 1000
        kline_Writer.writerow(kline)
    CSVfile.close()

    return print('Database for {} has been updated.'.format(filename))

Database_Maker("klines_15M", Symbol, '15M', From_Date, To_Date)
Database_Maker("klines_1H", Symbol, '1H', From_Date, To_Date)
Database_Maker("klines_4H", Symbol, '4H', From_Date, To_Date)
Database_Maker("klines_1D", Symbol, '1D', From_Date, To_Date)
