import psycopg2
from Config import dat_secrets


class DatabaseManager:
    def __init__(self, datsecrets):
        self.host = datsecrets['host']
        self.database = datsecrets['database']
        self.user = datsecrets['user']
        self.password = datsecrets['password']

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            con = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password)
            print('Connected to your PostgreSQL database.')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return con

    def create_tables(self):
        """ create tables in the PostgreSQL database"""
        con = self.connect()
        cur = con.cursor()
        commands = (
            """
            CREATE TABLE IF NOT EXISTS symbols (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(32) UNIQUE 
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS timeframes (
            id SERIAL PRIMARY KEY,
            timeframe VARCHAR(32) UNIQUE 
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sym_tf (
            id SERIAL PRIMARY KEY,
            symbol_id INTEGER REFERENCES symbols(id) ON DELETE CASCADE,
            timeframe_id INTEGER REFERENCES timeframes(id) ON DELETE CASCADE,         
            UNIQUE (symbol_id, timeframe_id)           
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS trade_data (
            id SERIAL PRIMARY KEY,
            sym_tf_id INTEGER REFERENCES sym_tf(id) ON DELETE CASCADE,
            opentime VARCHAR(32),
            openprice VARCHAR(32),
            highprice VARCHAR(32),
            lowprice VARCHAR(32),             
            closeprice VARCHAR(32),             
            volume VARCHAR(32),             
            closetime VARCHAR(32),
            UNIQUE (sym_tf_id, opentime)
            )
            """
        )
        for command in commands:
            cur.execute(command)
        # commit the changes to the database
        con.commit()
        # close connection
        cur.close()
        con.close()
        return print("Tables are Ready.")

    def drop_tables(self):
        """ Drop tables in the PostgreSQL database"""
        con = self.connect()
        cur = con.cursor()
        commands = (
            """
            DROP TABLE IF EXISTS symbols CASCADE 
            """,
            """
            DROP TABLE IF EXISTS timeframes CASCADE 
            """,
            """
            DROP TABLE IF EXISTS sym_tf CASCADE 
            """,
            """
            DROP TABLE IF EXISTS trade_data CASCADE 
            """
        )
        for command in commands:
            cur.execute(command)
        con.commit()
        cur.close()
        con.close()
        return print("Tables have been droped.")

    def into_database(self, data):
        """ insert data into the tables """
        # self.create_tables()
        con = self.connect()
        cur = con.cursor()

        symbol_sql = ("""INSERT INTO symbols(symbol)
                 VALUES(%s) ON CONFLICT DO NOTHING"""
                      )
        timeframe_sql = ("""INSERT INTO timeframes(timeframe)
                 VALUES(%s) ON CONFLICT DO NOTHING"""
                         )
        sym_tf_sql = (
            """
            INSERT INTO sym_tf(symbol_id, timeframe_id) VALUES 
            ((SELECT symbols.id FROM symbols WHERE symbols.symbol = %s),
            (SELECT timeframes.id FROM timeframes WHERE timeframes.timeframe = %s)) 
            ON CONFLICT DO NOTHING
            """
        )
        trade_data_sql = (
            """
            INSERT INTO trade_data(sym_tf_id, opentime, openprice, highprice, lowprice, closeprice, 
            volume, closetime)
            VALUES((SELECT sym_tf.id FROM sym_tf 
            JOIN symbols on sym_tf.symbol_id = symbols.id
            JOIN timeframes on sym_tf.timeframe_id = timeframes.id
            WHERE symbols.symbol = %s and timeframes.timeframe = %s),
            %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
        )
        for i in data:
            cur.execute(symbol_sql, (i[0],))
            con.commit()
            cur.execute(timeframe_sql, (i[1],))
            con.commit()
            cur.execute(sym_tf_sql, (i[0], i[1]))
            con.commit()
            cur.execute(trade_data_sql, (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]))
            con.commit()
        # close the connection
        cur.close()
        con.close()
        return print("Data have been inserted into the database.")


if __name__ == "__main__":
    sample_data = [['ETHUSDT', '4H', 1577836800.0, '0.21640000',
                    '0.22480000', '0.21490000', '0.22010000',
                    '2321528.73000000', 157792319.999, '509488.40716100',
                    4086, '989329.89000000', '217544.34249000', '0'],
                   ['ALGOUSDT', '1D', 1577923200.0, '0.22010000',
                    '0.22100000', '0.21060000', '0.21390000', '2103741.28000000',
                    1578009599.999, '453966.00840500',
                    4235, '758468.09000000', '163821.83301400', '0']]
    dat = DatabaseManager(dat_secrets())
    # dat.drop_tables()
    # dat.create_tables()
    # dat.into_database(sample_data)
