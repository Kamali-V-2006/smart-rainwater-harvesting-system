import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib

# Load dataset
df = pd.read_csv("rainwater_data.csv", parse_dates=["date"])

# Use only required features
data = df[["rainfall_mm", "inflow_liters", "usage_liters", "tank_level_liters"]].values

# Normalize using MinMaxScaler
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# Create sequences (30 days input to predict next day)
X, y = [], []
for i in range(30, len(scaled_data)):
    X.append(scaled_data[i-30:i])  # past 30 days
    y.append(scaled_data[i][[0, 3]])  # next day's rainfall and tank level

X = np.array(X)
y = np.array(y)

# Define LSTM model
model = Sequential([
    LSTM(64, activation='relu', input_shape=(30, 4)),
    Dense(2)  # 2 outputs: rainfall and tank level
])

model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=30, batch_size=16)

# Save model and scaler for later use
model.save("lstm_model.h5")
joblib.dump(scaler, "scaler.gz")

print("✅ Model trained and saved as 'lstm_model.h5'")
