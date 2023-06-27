import datetime
import time
import joblib
import numpy as np
import MetaTrader5 as mt5
from fetch_data import timeframes, init_mt5, fetch_data

# NOTE: I redeclare mt5 config here because I use 2 different brokers for fetching test data and front testing,
# you can import the config from fetch_data.py file if you use the same broker
mt5_config = {
    'path': '',
    'server': '',
    'login': '',
    'password': ''
}

# Waiting threshold for each timeframe, I will just declare the most common used timeframes
timedeltas = {
    mt5.TIMEFRAME_M5: datetime.timedelta(minutes=5),
    mt5.TIMEFRAME_M15: datetime.timedelta(minutes=15),
    mt5.TIMEFRAME_H1: datetime.timedelta(hours=1),
    mt5.TIMEFRAME_H4: datetime.timedelta(hours=4),
    mt5.TIMEFRAME_D1: datetime.timedelta(days=1),
}


# Fetch current data and use the trained models to predict,
# return True if the predicted value is higher than the current price else False,
def predict(symbol_models, symbol, timeframe):
    df = fetch_data(datetime.datetime(2019, 1, 1), datetime.datetime.now(), symbol, timeframe, mt5_config, for_fetching=False)
    predictions = []
    for model in symbol_models:
        predictions.append(model.predict(df))
    final_prediction = np.mean(predictions, axis=0)
    return final_prediction[-1] > df['Close'].values[-1]


# The main function to predict the price and execute orders
def front_test(models, symbols, timeframe):
    for symbol, lot_size in symbols.items():
        # Predict the price of a pair
        direction = predict(models[symbol], symbol, timeframe)
        print("{} - Action for {}: {}".format(datetime.datetime.now(), symbol,
                                              "Buy" if direction == True else "Sell"))

        # Check the current position, keep the position if the prediction has the same direction
        # to prevent unnecessary fees and spreads, else close the current position and open a new one
        init_mt5(mt5_config)
        current_position_id = None
        positions = mt5.positions_get(symbol=symbol)
        if len(positions) > 0:
            if (positions[0].type == 0 and direction == True) or (positions[0].type == 1 and direction == False):
                does_execute_order = False
            else:
                does_execute_order = True
                current_position_id = positions[0].ticket
        else:
            does_execute_order = True
        if does_execute_order is True:
            if current_position_id is not None:
                mt5.Close(symbol=symbol)

            # Prevent requote error when opening the position, ignore market close error
            code = 10004
            while code == 10004:
                order = mt5.order_send({
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY if direction == True else mt5.ORDER_TYPE_SELL,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "price": mt5.symbol_info_tick(symbol).ask if direction == True else mt5.symbol_info_tick(
                        symbol).bid
                })
                code = int(order[0])


if __name__ == '__main__':
    # Define the pairs you want to trade and volume for each order in lot size
    test_symbols = {
        'XAUUSD': 0.05
    }

    test_timeframe = mt5.TIMEFRAME_M5
    test_models = {}
    # Define the models you want to use. You can use multiple models to predict and it will return the average value
    test_model_names = ['linear_regression']
    # Load the models trained and saved to 'models' directory
    for test_symbol, _ in test_symbols.items():
        test_symbol_models = []
        for test_model_name in test_model_names:
            test_symbol_models.append(
                joblib.load('models/{}_{}_{}.joblib'.format(test_symbol, timeframes[test_timeframe], test_model_name)))
        test_models[test_symbol] = test_symbol_models

    # Wait for the next candle close
    to = datetime.datetime.now() + (datetime.datetime.min - datetime.datetime.now()) % timedeltas[test_timeframe] - datetime.timedelta(seconds=5)
    print(to)
    time.sleep((to - datetime.datetime.now()).seconds)

    # The algo will run automatically at the end of each candle
    while True:
        now = datetime.datetime.now()
        front_test(test_models, test_symbols, test_timeframe)
        # Wait for the next candle close
        to = now + (datetime.datetime.min - now) % timedeltas[test_timeframe] + timedeltas[test_timeframe] - datetime.timedelta(seconds=5)
        print(to)
        time.sleep((to - datetime.datetime.now()).seconds)
