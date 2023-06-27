from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta

# Timeframe name to save the data file, I will just declare the most common used timeframes
timeframes = {
    mt5.TIMEFRAME_M5: 'm5',
    mt5.TIMEFRAME_M15: 'm15',
    mt5.TIMEFRAME_H1: 'h1',
    mt5.TIMEFRAME_H4: 'h4',
    mt5.TIMEFRAME_D1: 'd1',
}

# mt5 config values, including:
# mt5_path: path to metatrader 5 terminal file, typically 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
# mt5_server: the server of your broker on metatrader 5
# mt5_login: your metatrader 5 username
# mt5_password: your metatrader 5 password
mt5_config = {
    'path': '',
    'server': '',
    'login': '',
    'password': ''
}


def init_mt5(config):
    mt5.initialize(config['path'])
    if not mt5.login(server=config['server'], login=config['login'], password=config['password']):
        print(mt5.last_error())
        quit()


def fetch_data(time_from, time_to, symbol, timeframe, config, for_fetching=True):
    # Init meta trader 5
    init_mt5(config)

    # Fetch data from meta trader 5,
    # The return columns are 'time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'
    bars = mt5.copy_rates_range(symbol, timeframe, time_from, time_to)
    raw_df = pd.DataFrame(bars)

    # Manipulate data before saving to a file, in this example I will add some EMA indicators and RSI, Predict column
    # is the value of the next day's Close price, which I want the model to predict
    df = pd.DataFrame()
    df['time'] = raw_df['time'].apply(lambda x: datetime.fromtimestamp(x))
    df['Open'] = raw_df['open']
    df['High'] = raw_df['high']
    df['Low'] = raw_df['low']
    df['Close'] = raw_df['close']
    df['ema_10'] = ta.ema(raw_df['close'], length=10)
    df['ema_34'] = ta.ema(raw_df['close'], length=34)
    df['ema_89'] = ta.ema(raw_df['close'], length=89)
    df['ema_200'] = ta.ema(raw_df['close'], length=200)
    df['rsi'] = ta.rsi(raw_df['close'], length=14)
    if for_fetching == True:
        df['Predict'] = df['Close'].shift(-1)
    df.set_index('time', inplace=True)
    df.dropna(inplace=True)

    # Optional: round the values
    df = df.applymap(lambda x: round(float(x), 2))
    return df


if __name__ == '__main__':
    fetch_symbol = 'XAUUSD'
    fetch_timeframe = mt5.TIMEFRAME_H4
    fetch_time_from = datetime(2000, 1, 1)
    fetch_time_to = datetime.now()
    fetch_df = fetch_data(fetch_time_from, fetch_time_to, fetch_symbol, fetch_timeframe, mt5_config)

    # Save the data
    path_save = 'data/{}_{}.csv'.format(fetch_symbol, timeframes[fetch_timeframe])
    fetch_df.to_csv(path_save, index=True)
