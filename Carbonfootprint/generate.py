import random
import sqlite3

# Initialize SQLite database connection and cursor
conn = sqlite3.connect('carbon_footprint.db')
cursor = conn.cursor()

# Number of samples to generate
num_samples = 2000

for _ in range(num_samples):
    # Generate random values for each attribute
    random_data = {
        'Electricity_and_Energy_Consumption': random.uniform(1, 100),
        'Transportation_and_Commuting': random.uniform(1, 50),
        'Diet_and_Food_Choices': random.uniform(1, 10),
        'Waste_Management': random.uniform(0.1, 5),
        'Estimated_Carbon_Footprint': random.uniform(5, 50),
    }

    # Insert the random data into the database
    cursor.execute('''
        INSERT INTO carbon_footprint (
            Electricity_and_Energy_Consumption,
            Transportation_and_Commuting,
            Diet_and_Food_Choices,
            Waste_Management,
            Estimated_Carbon_Footprint
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        random_data['Electricity_and_Energy_Consumption'],
        random_data['Transportation_and_Commuting'],
        random_data['Diet_and_Food_Choices'],
        random_data['Waste_Management'],
        random_data['Estimated_Carbon_Footprint'],
    ))

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()

print(f'Generated {num_samples} random samples.')
