from binance.client import Client
import Config
import csv
from Database import DatabaseManager

# Insert the required parameters to get your symbol historical data -----
API_Keys = Config.api_keys('test')
Symbol = "ALGOUSDT"
Time_Frame = '15M'
From_Date = "1 Jan, 2020"
To_Date = "1 Jan, 2021"


# Log into Binance API --------------------------------------------------
Binance_Client = Client(API_Keys['key'], API_Keys['secret'])
print("logged In to your Binance account.")


def get_data(symbol, timeframe, fromdate, todate):
    """Function for fetching data from Binance API """
    time_frames = {'1M': Client.KLINE_INTERVAL_1MINUTE,
                   '5M': Client.KLINE_INTERVAL_5MINUTE,
                   '15M': Client.KLINE_INTERVAL_15MINUTE,
                   '1H': Client.KLINE_INTERVAL_1HOUR,
                   '4H': Client.KLINE_INTERVAL_4HOUR,
                   '1D': Client.KLINE_INTERVAL_1DAY
                   }
    klines = Binance_Client.get_historical_klines(symbol, time_frames[timeframe], fromdate, todate)
    for kline in klines:
        kline.insert(0, timeframe)
        kline.insert(0, symbol)
        kline[2] = kline[2] / 1000
        kline[8] = kline[8] / 1000
    return klines


def into_CSVfile(data):
    """Write data into CSV file"""
    filename = data[0][0] + '_klines_' + data[0][1]
    CSVfile = open('data\{}.csv'.format(filename), 'w', newline='')
    kline_writer = csv.writer(CSVfile, delimiter=',')
    for kline in data:
        kline_writer.writerow(kline)
    CSVfile.close()
    return print('Your CSV file {} has been created.'.format(filename))


if __name__ == '__main__':
    # Run Function for your desired candlesticks ---------------------------
    Data = get_data(Symbol, Time_Frame, From_Date, To_Date)
    print(Data)
    # Export data into CSV files ------------------------------------------
    into_CSVfile(Data)
    # Export data into PostgreSQL database -------------------------------------------
    dat = DatabaseManager(Config.dat_secrets())
    # dat.drop_tables()
    dat.create_tables()
    dat.into_database(Data)
