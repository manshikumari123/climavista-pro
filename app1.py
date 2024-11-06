import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import joblib
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # CORS for cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS

# Secret key for session management
app.secret_key = '8eec5fa59224825ab4a7615ad969da84'  # Change this to a strong secret key

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Set your MySQL root password here
app.config['MYSQL_DB'] = 'climavista_pro'
app.config['MYSQL_PORT'] = 3307  # Set MySQL port
mysql = MySQL(app)

# Load the trained model and weather data
model = joblib.load('weather_model.pkl')
weather_data = pd.read_csv('weatherHistory_cleaned.csv', encoding='ISO-8859-1')
weather_data['Formatted Date'] = pd.to_datetime(weather_data['Formatted Date'], utc=True).dt.date
weather_data['city'] = weather_data['city'].str.strip().str.lower()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    username = data['username']
    email = data['email']
    mobile = data['mobile']
    password = generate_password_hash(data['password'])

    cur = None
    try:
        cur = mysql.connection.cursor()
        # Check if email or username already exists
        cur.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({'error': 'User with this email or username already exists'})

        # Insert new user into the database
        cur.execute("INSERT INTO users (username, email, mobile, password) VALUES (%s, %s, %s, %s)",
                    (username, email, mobile, password))
        mysql.connection.commit()

        return jsonify({'message': 'User registered successfully! Redirecting to login...'}), 200
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cur:
            cur.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json()
    username = data['username']
    password = data['password']

    print(f"Login attempt: {username}")  # Debug line to see the login attempt

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
    finally:
        if cur:
            cur.close()

    if user and check_password_hash(user[4], password):  # Assuming password is in the 5th column
        session['username'] = user[1]  # Store username in session
        print(f"Logged in user: {user[1]}")  # Check the logged-in user
        return jsonify({'message': 'Login successful!', 'user': {'username': user[1], 'email': user[2]}})
    else:
        print("Invalid credentials")  # Debug line for invalid credentials
        return jsonify({'error': 'Invalid username or password'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the user session
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city'].strip().lower()
    date = request.form['date']

    try:
        date = pd.to_datetime(date, format='%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

    if city not in weather_data['city'].values:
        return jsonify({"error": "City not found."})

    filtered_data = weather_data[(weather_data['city'] == city) & (weather_data['Formatted Date'] == date)]

    if not filtered_data.empty:
        entry = filtered_data.iloc[0]
        temperature = round(entry['Temperature (C)'], 2)  # Round temperature to 2 decimal places
        humidity = round(entry['Humidity'], 2)  # Round humidity to 2 decimal places
        wind_speed = round(entry['Wind Speed (km/h)'], 2)  # Round wind speed to 2 decimal places
        weather_description = entry['Summary']

        # Create a detailed summary
        summary = (f"On {date}, in {city.capitalize()}, the weather was {weather_description.lower()}. "
                   f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%, Wind Speed: {wind_speed:.2f} km/h.")

        forecast = {
            'temp': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'weather_description': weather_description,
            'summary': summary
        }
        return jsonify(forecast)
    else:
        return jsonify({"error": "No forecast data available for this date."})

@app.route('/predict_weather', methods=['POST'])
def predict_weather():
    city = request.form['city'].strip().lower()
    date = request.form['date']

    try:
        date = pd.to_datetime(date, format='%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

    if city not in weather_data['city'].values:
        return jsonify({"error": "City not found."})

    day_of_year = date.timetuple().tm_yday
    year = date.year

    # Get sample city's data to use average humidity and wind speed
    city_data = weather_data[weather_data['city'] == city]
    avg_humidity = round(city_data['Humidity'].mean(), 2)  # Round average humidity to 2 decimal places
    avg_wind_speed = round(city_data['Wind Speed (km/h)'].mean(), 2)  # Round wind speed to 2 decimal places

    # Prepare the feature set for prediction
    features = pd.DataFrame({
        'DayOfYear': [day_of_year],
        'Year': [year],
        'Humidity': [avg_humidity],
        'Wind Speed (km/h)': [avg_wind_speed]
    })

    # Predict temperature
    predicted_temp = round(model.predict(features)[0], 2)  # Round predicted temperature to 2 decimal places

    # Define a placeholder for weather description based on temperature
    if predicted_temp > 25:
        weather_description = 'Clear Sky'
        summary = 'Clear'
    elif predicted_temp > 15:
        weather_description = 'Partly Cloudy'
        summary = 'Partly Cloudy'
    else:
        weather_description = 'Overcast'
        summary = 'Overcast'

    # Create a detailed summary
    detailed_summary = (f"Predicted temperature: {predicted_temp:.2f}°C with average humidity of {avg_humidity:.2f}% "
                        f"and wind speed of {avg_wind_speed:.2f} km/h. Weather is expected to be {weather_description.lower()}.")

    forecast = {
        'temp': predicted_temp,
        'humidity': avg_humidity,
        'wind_speed': avg_wind_speed,
        'weather_description': weather_description,
        'summary': summary,
        'detailed_summary': detailed_summary
    }
    return jsonify(forecast)

@app.route('/get_seasonal_insights', methods=['POST'])
def get_seasonal_insights():
    city = request.form['city'].strip().lower()

    if city not in weather_data['city'].values:
        return jsonify({"error": "City not found."})

    # Filter data for the given city
    city_data = weather_data[weather_data['city'] == city]

    # Example insights based on historical weather data
    avg_temp = round(city_data['Temperature (C)'].mean(), 2)  # Round average temperature
    avg_humidity = round(city_data['Humidity'].mean(), 2)  # Round average humidity
    avg_wind_speed = round(city_data['Wind Speed (km/h)'].mean(), 2)  # Round wind speed

    # Define simple descriptors based on average temperature and humidity
    temp_insight = 'Warm' if avg_temp > 20 else 'Cool'
    humidity_insight = 'High Humidity' if avg_humidity > 75 else 'Moderate Humidity'

    insights = f"{temp_insight}, {humidity_insight}"

    return jsonify({"insights": insights})

@app.route('/get_alerts', methods=['POST'])
def get_alerts():
    city = request.form['city'].strip().lower()

    if city not in weather_data['city'].values:
        return jsonify({"error": "City not found."})

    # Example alerts based on historical data
    alerts = (f"No severe weather alerts are currently active for {city.capitalize()}.")

    return jsonify({"alerts": alerts})

if __name__ == '__main__':
    app.run(debug=True)
