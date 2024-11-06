import pandas as pd
file_path = 'weatherHistory_with_city.csv'  
df = pd.read_csv(file_path)
print(df.head())
df = df[['Formatted Date', 'city', 'Summary', 'Temperature (C)', 'Humidity', 'Wind Speed (km/h)']]
df = df.dropna()
df['Formatted Date'] = pd.to_datetime(df['Formatted Date'], utc=True)
df.to_csv('weatherHistory_cleaned.csv', index=False)
print("Dataset cleaned and saved as 'weatherHistory_cleaned.csv'")
