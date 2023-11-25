import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Function to scrape data from the provided URL
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table on the webpage
    table = soup.find('table')

    # Extract table data using pandas
    data = pd.read_html(str(table), header=0)[0]

    return data

# Function to preprocess data and train a linear regression model using TensorFlow
def train_model(data):
    years = np.array(data.columns[1:], dtype=int).reshape(-1, 1)
    total_crimes = data.iloc[0, 1:].values.astype(int)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(years, total_crimes, test_size=0.2, random_state=42)

    # Standardize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Build the TensorFlow model
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1,)),
        tf.keras.layers.Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, epochs=100, batch_size=1, verbose=0)

    return model, scaler

# Function to predict total crimes for the next 5 years
def predict_next_5_years(model, scaler):
    future_years = np.array(range(2023, 2028)).reshape(-1, 1)

    # Standardize the input for prediction
    future_years_standardized = scaler.transform(future_years)

    # Predict using the trained model
    predictions = model.predict(future_years_standardized)

    return predictions.flatten()

# Main function
def main():
    url = "https://statbank.statistica.md/PxWeb/pxweb/en/30%20Statistica%20sociala/30%20Statistica%20sociala__12%20JUS__JUS010/JUS010300reg.px/table/tableViewLayout2/?rxid=2345d98a-890b-4459-bb1f-9b565f99b3b9"

    # Scrape data
    data = scrape_data(url)

    # Train linear regression model using TensorFlow
    model, scaler = train_model(data)

    # Predict total crimes for the next 5 years
    predictions = predict_next_5_years(model, scaler)

    # Display results
    print("Year\tPredicted Total Crimes")
    for year, prediction in zip(range(2023, 2028), predictions):
        print(f"{year}\t{int(prediction)}")

if name == "main":
    main()