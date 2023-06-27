import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor


# My custom accuracy metric to return the percentage of the time that the predicted price
# has the same direction with the actual price compared to the previous close price
def direction_accuracy(y_true, y_pred):
    y_true = np.ndarray.flatten(y_true.values)
    y_pred = np.ndarray.flatten(y_pred)
    y_pred_direction = np.signbit(y_pred[1:] - y_true[:-1])
    y_true_direction = np.signbit(y_true[1:] - y_true[:-1])
    accuracy = np.mean(y_pred_direction == y_true_direction)
    return accuracy


def train_and_test_models(models, df, test_size):
    # Define X and y data
    X = df.drop(columns=['Predict', 'time'])
    y = df['Predict']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)

    # Train and evaluate each model
    for name, model in models.items():
        print('Training', name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        accuracy = direction_accuracy(y_test, y_pred)
        print('MSE:', mse)
        print('R^2:', r2)
        print('Movement accuracy: ', accuracy)
        print('')
        dump(model, filename="models/{}_{}_{}.joblib".format(symbol, timeframe, name))


if __name__ == '__main__':
    # Read data from the saved csv file
    symbol = 'XAUUSD'
    timeframe = 'm5'
    df = pd.read_csv('data/{}_{}.csv'.format(symbol, timeframe))
    test_size = 0.001
    # Define the models to be tested
    models = {
        'linear_regression': LinearRegression(),
        'decision_tree': DecisionTreeRegressor(),
        'random_forest': RandomForestRegressor(),
        'knn': KNeighborsRegressor()
    }

    train_and_test_models(models, df, test_size)
