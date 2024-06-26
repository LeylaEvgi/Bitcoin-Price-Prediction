import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('Qt5Agg')
import datetime as dt
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.models import Sequential
from sklearn.metrics import mean_absolute_error, mean_squared_error


crypto_currency= 'BTC'
against_currency = 'USD'

start = dt.datetime(2011,1,1)
end = dt.datetime.now()


symbol = f"{crypto_currency}-{against_currency}"
bitcoin_data = yf.download(symbol, start, end)
bitcoin_data.head()
bitcoin_data.shape


#####Prepare Data################

scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(bitcoin_data['Close'].values.reshape(-1,1))

prediction_days=60
future_day = 30


x_train, y_train = [], []

for x in range(prediction_days, len(scaled_data)-future_day):
    x_train.append(scaled_data[x-prediction_days:x, 0])
    y_train.append(scaled_data[x+future_day,0])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#Create Neural Network

model = Sequential()
model.add(LSTM(units=100, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=100, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=100))
model.add(Dropout(0.2))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=50, batch_size=32)


# Updating the model in real time
def update_model(model, new_data):
    new_data_scaled = scaler.transform(new_data.reshape(-1, 1))
    x_new = []
    x_new.append(new_data_scaled[-prediction_days:, 0])
    x_new = np.array(x_new)
    x_new = np.reshape(x_new, (x_new.shape[0], x_new.shape[1], 1))
    y_new = model.predict(x_new)
    return y_new[0][0]


######Testing the model

test_start = dt.datetime (2022,1,1)
test_end = dt.datetime.now()

symbol = f"{crypto_currency}-{against_currency}"
test_data = yf.download(symbol, test_start, test_end)

#test_data = web. DataReader (f' {crypto_currency}-{against_currency}', 'yahoo', test_start, test_end)
actual_prices = test_data['Close']. values

total_dataset = pd.concat((bitcoin_data['Close'], test_data[ 'Close']), axis=0)

model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:] .values
model_inputs = model_inputs.reshape(-1, 1)
model_inputs = scaler.fit_transform (model_inputs)

x_test = []

for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x-prediction_days:x, 0])

x_test = np.array(x_test)
x_test =np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

prediction_price = model.predict(x_test)
prediction_price = scaler.inverse_transform(prediction_price)

plt.plot(actual_prices, color='black', label='Actual Price')
plt.plot(prediction_price, color='green', label='Predicted Prices')
plt.title(f'{crypto_currency}price prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend(loc='upper left')
plt.show()

#Predict Next Day

real_data= [model_inputs[len(model_inputs) + 1 - prediction_days:len(model_inputs) + 1, 0]]
real_data= np.array(real_data)
real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

prediction = model.predict(real_data)
prediction = scaler.inverse_transform(prediction)
print("Next day prediction:", prediction)

mae = mean_absolute_error(actual_prices, prediction_price)
mse = mean_squared_error(actual_prices, prediction_price)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")


