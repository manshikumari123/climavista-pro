import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib

weather_data = pd.read_csv('weatherHistory_cleaned.csv', encoding='ISO-8859-1')

weather_data['Formatted Date'] = pd.to_datetime(weather_data['Formatted Date'], utc=True)
weather_data['DayOfYear'] = weather_data['Formatted Date'].dt.dayofyear
weather_data['Year'] = weather_data['Formatted Date'].dt.year

X = weather_data[['DayOfYear', 'Year', 'Humidity', 'Wind Speed (km/h)']]
y = weather_data['Temperature (C)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae:.2f}°C')

joblib.dump(model, 'weather_model.pkl')
