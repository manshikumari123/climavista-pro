import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your cleaned weather data
# Replace 'weatherHistory_cleaned.csv' with the actual path to your cleaned CSV file
weather_data = pd.read_csv('weatherHistory_cleaned.csv')

# Create predicted temperatures with some random noise for demonstration
np.random.seed(42)  # For reproducibility
weather_data['Predicted Temperature (C)'] = weather_data['Temperature (C)'] + np.random.normal(0, 2, len(weather_data))

# Prepare data for plotting
actual_temperatures = weather_data['Temperature (C)']
predicted_temperatures = weather_data['Predicted Temperature (C)']

# Create a scatter plot for actual vs. predicted temperatures
plt.figure(figsize=(10, 6))
plt.scatter(actual_temperatures, predicted_temperatures, alpha=0.6, color='blue', label='Predicted vs Actual')

# Line representing perfect predictions
plt.plot([actual_temperatures.min(), actual_temperatures.max()],
         [actual_temperatures.min(), actual_temperatures.max()],
         color='red', linestyle='--', label='Perfect Prediction')

# Title and labels
plt.title('Actual vs. Predicted Temperatures')
plt.xlabel('Actual Temperatures (°C)')
plt.ylabel('Predicted Temperatures (°C)')

# Grid and limits
plt.grid()
plt.xlim([actual_temperatures.min(), actual_temperatures.max()])
plt.ylim([actual_temperatures.min(), actual_temperatures.max()])

# Add legend
plt.legend()

# Show the plot
plt.show()
