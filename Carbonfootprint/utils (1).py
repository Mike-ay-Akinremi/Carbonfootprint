import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import pickle

def get_data(conn, cursor):

    # Initialize SQLite database connection and cursor
    conn = sqlite3.connect('carbon_footprint.db')
    cursor = conn.cursor()
    # Load data from the database
    cursor.execute('''
        SELECT 
            ID,
            Electricity_and_Energy_Consumption,
            Transportation_and_Commuting,
            Diet_and_Food_Choices,
            Waste_Management,
            Estimated_Carbon_Footprint
        FROM carbon_footprint
    ''')
    data = cursor.fetchall()
        # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['ID', 'Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
                                    'Diet_and_Food_Choices', 'Waste_Management', 'Estimated_Carbon_Footprint']).dropna(subset=["Estimated_Carbon_Footprint"])

    df.index = df.ID
    df.drop("ID", axis=1, inplace=True)
    return df
    


def get_data_by_id(conn, cursor, id_to_fetch):
    # try:
    # Load data with the specified ID from the database
    cursor.execute('''
        SELECT 
            ID,
            Electricity_and_Energy_Consumption,
            Transportation_and_Commuting,
            Diet_and_Food_Choices,
            Waste_Management,
            Estimated_Carbon_Footprint
        FROM carbon_footprint
        WHERE ID = ?
    ''', (id_to_fetch,))
    data = cursor.fetchone()
    print(list(data))
    if data:
        # # Create a DataFrame from the fetched data
        # df = pd.DataFrame(list(data), columns=['ID', 'Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
        #                                     'Diet_and_Food_Choices', 'Waste_Management', 'Estimated_Carbon_Footprint'])
        # df.index = df.ID
        # df.drop("ID", axis=1, inplace=True)
        print(data[1:-1])
        return np.array(data[1:-1]).reshape(1, -1)
    else:
        print(f"No data found for ID {id_to_fetch}")
        return None
    # except Exception as e:
    #     print(f"Error fetching data: {str(e)}")
    #     return None

def train_model(data):
    # Assuming 'data' is a DataFrame with the following columns:
    # 'Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
    # 'Diet_and_Food_Choices', 'Waste_Management', 'Estimated_Carbon_Footprint'

    # Split the data into features (X) and target (y)
        # Split the data into features (X) and target variable (y)
    X = data.drop(columns=['Estimated_Carbon_Footprint'])
    y = data['Estimated_Carbon_Footprint']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize a machine learning model (e.g., Random Forest Regressor)
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train the model on the training data
    model.fit(X_train, y_train)

    # Evaluate the model on the testing data (optional)
    test_score = model.score(X_test, y_test)
    print(f"Model Test Score: {test_score:.2f}")

    # Save the trained model using joblib
    joblib.dump(model, 'carbon_footprint_model.pkl')


def predict_carbon_footprint(input_data):
    # Load the trained model
    model = joblib.load('carbon_footprint_model.pkl')

    # Make predictions using the loaded model
    predicted_carbon_footprint = model.predict(input_data)

    return predicted_carbon_footprint


def save_count(conn, cursor):
    # Get the current record count
    cursor.execute("SELECT COUNT(*) FROM carbon_footprint")
    total_samples = cursor.fetchone()[0]

    # Define the path to the pickle file
    pickle_file_path = 'record_count.pickle'

    # Save the record count to a pickle file
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(total_samples, pickle_file)
