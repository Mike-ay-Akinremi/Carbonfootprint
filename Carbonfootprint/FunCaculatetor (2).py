import os
import pickle
import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64 
from utils import get_data, get_data_by_id, save_count, train_model, predict_carbon_footprint

# Initialize session state
if 'total_carbon_footprint' not in st.session_state:
    st.session_state.total_carbon_footprint = 0
if 'total_electricity_footprint' not in st.session_state:
    st.session_state.total_electricity_footprint = 0
if 'total_transportation_footprint' not in st.session_state:
    st.session_state.total_transportation_footprint = 0
if 'total_food_footprint' not in st.session_state:
    st.session_state.total_food_footprint = 0
if 'total_waste_footprint' not in st.session_state:
    st.session_state.total_waste_footprint = 0
if 'pk' not in st.session_state:
    st.session_state.pk = None

pickle_file_path = 'record_count.pickle'


# Function to check if additional samples are needed and retrain the model
def check_and_retrain_model(conn, cursor):
    cursor.execute("SELECT COUNT(*) FROM carbon_footprint")
    total_samples = cursor.fetchone()[0]

    if os.path.exists(pickle_file_path):
        # Load the record count from the pickle file
        with open(pickle_file_path, 'rb') as pickle_file:
            record_count = pickle.load(pickle_file)
    else:
        # Initialize the record count
        record_count = 0
        # Create the pickle file with the initial record count
        with open(pickle_file_path, 'wb') as pickle_file:
            pickle.dump(record_count, pickle_file)

    # Check if additional 1500 samples have been added
    if total_samples - record_count >= 1500 :
    # if True:
        # Retrieve all data from the database
       
        df = get_data(conn, cursor)
        # Retrain the model with the updated data
        train_model(df)
        save_count(conn, cursor)



# Create a new SQLite database connection and cursor for each thread
# # def create_db_connection():
#     conn = sqlite3.connect('carbon_footprint.db')
#     cursor = conn.cursor()

#     # Create the 'carbon_footprint' table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS carbon_footprint (
#             id INTEGER PRIMARY KEY,
#             Electricity_and_Energy_Consumption REAL,
#             Transportation_and_Commuting REAL,
#             Diet_and_Food_Choices REAL,
#             Waste_Management REAL,
#             Estimated_Carbon_Footprint REAL
#         )
#     ''')
#     conn.commit()
#     return conn, cursor

def create_db_connection():
    # Connect to the SQLite database 'carbon_footprint.db' and create the table if it doesn't exist
    conn = sqlite3.connect('carbon_footprint.db')
    cursor = conn.cursor()

    # Create the 'carbon_footprint' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_footprint (
            id INTEGER PRIMARY KEY,
            Electricity_and_Energy_Consumption REAL,
            Transportation_and_Commuting REAL,
            Diet_and_Food_Choices REAL,
            Waste_Management REAL,
            Natural_Gas_Consumption REAL,
            Heating_Oil_Consumption REAL,
            Coal_Consumption REAL,
            LPG_Consumption REAL,
            Propane_Consumption REAL,
            Wooden_Pellets_Consumption REAL,
            Number_of_Members INTEGER,
            Bus_Distance_Travelled REAL,
            Coach_Distance_Travelled REAL,
            Local_Train_Distance_Travelled REAL,
            Long_Distance_Train_Distance_Travelled REAL,
            Tram_Distance_Travelled REAL,
            Subway_Distance_Travelled REAL,
            Taxi_Distance_Travelled REAL,
            Organic_Food_Choices REAL,
            Meat_Dairy_Choices REAL,
            Food_Miles_Choices REAL,
            Packaging_Choices REAL,
            Composting_Choices REAL,
            Plastic_Waste_Kilograms REAL,
            Paper_Waste_Kilograms REAL,
            Glass_Waste_Kilograms REAL,
            Metal_Waste_Kilograms REAL,
            Organic_Waste_Kilograms REAL,
            Estimated_Carbon_Footprint REAL
        )
    ''')
    conn.commit()
    return conn, cursor
# Close the SQLite connection
def close_db_connection(conn):
    conn.close()



# Define custom CSS to add a background image
custom_css = f"""
    body {{
        background-image: url('data:image/png;base64,{base64.b64encode(open('background.png', 'rb').read()).decode()}');
        background-size: cover;
    }}
"""
def collect_household_data(conn, cursor):
    st.subheader("Enter Data")
    
    with st.form(key='household_form'):
        noofmembers = st.number_input("Enter Number of Members in your Household", min_value=1)
        electricity = st.number_input("Enter the kWh of Electricity Used per month")
        naturalgas = st.number_input("Enter kWh of Natural Gas Used per month")
        heatingoil = st.number_input("Enter Litres of Heating Oil Used per month")
        coal = st.number_input("Enter Metric Tons of Coal Used per month")
        lpg = st.number_input("Enter Litres of LPG Used per month")
        propane = st.number_input("Enter Litres of Propane Used per month")
        woodenpellets = st.number_input("Enter Metric Tons of Wooden Pellets Used per month")

        submitted = st.form_submit_button('Calculate Household Carbon Footprint')
        
        if submitted:
            # Calculate and store the household carbon footprint
            f_electricity = ((electricity / 1000) * 0.207074)
            f_naturalgas = ((naturalgas / 1000) * 0.20)
            f_heatingoil = ((heatingoil / 1000) * 0.27)
            f_coal = (coal * 2195.88)
            f_lpg = ((lpg / 100) * 0.23)
            f_propane = ((propane / 100) * 0.23)
            f_woodenpellets = (woodenpellets * 0.07)
            total = (f_electricity + f_coal + f_heatingoil + f_lpg + f_naturalgas + f_propane + f_woodenpellets) / noofmembers
            st.session_state.total_electricity_footprint = total
            # Insert the calculated value into the database
            cursor.execute('INSERT INTO carbon_footprint (Electricity_and_Energy_Consumption, Number_of_Members) VALUES (?, ?)', (total, noofmembers))
            conn.commit()
            
            # Display the calculated carbon footprint
            st.header('Your monthly Household Carbon Footprint is' + " " + str(round(total, 4)) + " " + "Metric Tonnes")

            # Store the primary key in session state
            st.session_state.pk = cursor.lastrowid

            # Check if there is a primary key (pk) in session state
            if 'pk' in st.session_state and st.session_state.pk is not None:
                # Update existing household data using the primary key (pk)
                cursor.execute('''
                    UPDATE carbon_footprint
                    SET 
                        Electricity_and_Energy_Consumption = ?,
                        Natural_Gas_Consumption = ?,
                        Heating_Oil_Consumption = ?,
                        Coal_Consumption = ?,
                        LPG_Consumption = ?,
                        Propane_Consumption = ?,
                        Wooden_Pellets_Consumption = ?,
                        Number_of_Members = ?
                    WHERE id = ?
                ''', (electricity, naturalgas, heatingoil, coal, lpg, propane, woodenpellets, noofmembers, st.session_state.pk))
            else:
                # Insert a new instance of household data
                cursor.execute('''
                    INSERT INTO carbon_footprint (
                        Electricity_and_Energy_Consumption,
                        Natural_Gas_Consumption,
                        Heating_Oil_Consumption,
                        Coal_Consumption,
                        LPG_Consumption,
                        Propane_Consumption,
                        Wooden_Pellets_Consumption,
                        Number_of_Members
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (electricity, naturalgas, heatingoil, coal, lpg, propane, woodenpellets, noofmembers))
           

            conn.commit()

            st.success("Household data has been recorded!")
        # If there was no primary key, retrieve the last inserted primary key (pk)
        if 'pk' not in st.session_state or st.session_state.pk is None:
            cursor.execute('SELECT last_insert_rowid()')
            st.session_state.pk = cursor.fetchone()[0]

        


def household(conn, cursor):
    global total, noofmembers
    noofmembers = st.number_input("Enter Number of Members in your Household", min_value=1)
    electricity = st.number_input("Enter the kWh of Electricity Used")
    naturalgas = st.number_input("Enter kWh of Natural Gas Used ")
    heatingoil = st.number_input("Enter Litres of Heating Oil Used")
    coal = st.number_input("Enter Metric Tons of Coal Used")
    lpg = st.number_input("Enter Litres of LPG Used")
    propane = st.number_input("Enter Litres of Propane Used")
    woodenpellets = st.number_input("Enter Metric Tons of Wooden Pellets Used")
    f_electicity = ((electricity / 1000) * 0.207074)
    f_naturalgas = ((naturalgas / 100) * 0.20)* 0.001
    f_heatingoil = ((heatingoil / 100) * 0.27)
    f_coal = (coal * 0.37)
    f_lpg = ((lpg / 100) * 0.23)
    f_propane = ((propane / 100) * 0.23)
    f_woodenpellets = (woodenpellets * 0.07)
    total = (f_electicity + f_coal + f_heatingoil + f_lpg + f_naturalgas + f_propane + f_woodenpellets) / noofmembers
    
    cursor.execute('INSERT INTO carbon_footprint (Electricity_and_Energy_Consumption) VALUES (?)', (total,))
    conn.commit()
    st.title(f'Your Carbon Footprint is' + " " + str(round(total, 4)) + " " + "Metric Tonnes")

def collect_public_transport_data(conn, cursor):
    st.subheader("Enter Data")
    
    with st.form(key='public_transport_form'):
        bus = st.number_input("Enter the Distance Travelled in Bus monthly (in kilometers)")
        coach = st.number_input("Enter the Distance Travelled in Coach monthly (in kilometers)")
        localtrain = st.number_input("Enter the Distance Travelled in Local Train monthly (in kilometers)")
        longdistancetrain = st.number_input("Enter the Distance Travelled in Long Distance Train monthly (in kilometers)")
        tram = st.number_input("Enter the Distance Travelled in Tram monthly (in kilometers)")
        subway = st.number_input("Enter the Distance Travelled in Subway monthly (in kilometers)")
        taxi = st.number_input("Enter the Distance Travelled in Taxi monthly (in kilometers)")
        
        submitted = st.form_submit_button('Calculate Public Transport Carbon Footprint')
        
        if submitted:
            # Calculate and store the public transport carbon footprint
            bus_footprint = (bus / 1000) * 0.10
            coach_footprint = (coach / 1000) * 0.03
            localtrain_footprint = (localtrain / 1000) * 0.04
            longdistancetrain_footprint = (longdistancetrain / 1000) * 0.05
            tram_footprint = (tram / 1000) * 0.03
            subway_footprint = (subway / 1000) * 0.03
            taxi_footprint = (taxi / 50) * 0.01
            total_public_transport_footprint = (bus_footprint + coach_footprint + localtrain_footprint + 
                                                longdistancetrain_footprint + tram_footprint + 
                                                subway_footprint + taxi_footprint) / 0.001
            st.session_state.total_transportation_footprint = total_public_transport_footprint
            
            if 'pk' in st.session_state and st.session_state.pk is not None:
                # Update existing record with primary key
                cursor.execute('''
                    UPDATE carbon_footprint
                    SET Transportation_and_Commuting = ?
                    WHERE id = ?
                ''', (total_public_transport_footprint, st.session_state.pk))
            else:
                # Insert the calculated value into the database
                cursor.execute('INSERT INTO carbon_footprint (Transportation_and_Commuting) VALUES (?)', (total_public_transport_footprint,))
                # Store the primary key in session state
                st.session_state.pk = cursor.lastrowid
            
            conn.commit()
            
            # Display the calculated carbon footprint
            st.title('Your monthly Public Transport Carbon Footprint is' + " " + str(round(total_public_transport_footprint, 4)) + " " + "Metric Tonnes")


def publictransport(conn, cursor):
    global total1
    bus = ((st.number_input("Enter the Distance Travelled in Bus per month ") / 1000) * 0.10)
    coach = ((st.number_input("Enter the Distance Travelled in Coach per month") / 1000) * 0.03)
    localtrain = ((st.number_input("Enter the Distance Travelled Locally by train per month ") / 1000) * 0.04)
    longdistancetrain = ((st.number_input("Enter the Distance Travelled in Long Distance Train per month") / 10000) * 0.05)
    tram = ((st.number_input("Enter the Distance Travelled in tram monthly") / 1000) * 0.03)
    subway = ((st.number_input("Enter the Distance Travelled in subway per month") / 1000) * 0.03)
    taxi = ((st.number_input("Enter the Distance Travelled in taxi per month") / 50) * 0.01)
    total1 = (bus + coach + localtrain + longdistancetrain + tram + subway + taxi)
    cursor.execute('INSERT INTO carbon_footprint (Transportation_and_Commuting) VALUES (?)', (total,))
    conn.commit()
    st.title('Your Carbon Footprint is' + " " + str(round(total1 , 4)) + " " + "Metric Tonnes")


def carbonfootprint(conn, cursor):
    car_size_options = {
        'Sports car or large SUV (35 mpg)': 35,
        'Small or medium SUV, or MPV (46 mpg)': 46,
        'City, small, medium, large or estate car (52 mpg)': 52
    }
    mileage_options = {
        'Choose an Option': 0,
        'Low (6,000 miles)': 6000,
        'Average (9,000 miles)': 9000,
        'High (12,000 miles)': 12000
    }

    carsize = st.selectbox('Select Car Size', list(car_size_options.keys()))
    carmileage = st.selectbox('Select 12-month car mileage', list(mileage_options.keys()))

    size = car_size_options.get(carsize, 0)
    mileage = mileage_options.get(carmileage, 0)

    carfootprint123 = (((((mileage / size) * 14.3) / 1000) * 0.907185) / 1)
    st.title('Your Carbon Footprint is' + " " + str(round(carfootprint123, 4)) + " " + "Metric Tonnes")


def food(conn, cursor):
    global total_diet
    food_options = {
        'Organic_None': 0.7, 'Organic_Some': 0.5, 'Organic_Most': 0.2,
        'Organic_All': 0, 'Meat_Above-average': 0.6, 'Meat_Average': 0.4,
        'Meat_Below-average': 0.25, 'Lacto-vegetarian': 0.1, 'Vegan': 0,
        'Local_Very little': 0.5, 'Local_Average': 0.3, 'Local_Above average': 0.2,
        'Local_Almost all': 0.1, 'Packaging_Above average': 0.6, 'Packaging_Average': 0.4,
        'Packaging_Below average': 0.2, 'Packaging_Very little': 0.05,
        'Composting_None': 0.2, 'Composting_Some': 0.1, 'Composting_All': 0
    }

    food1 = st.selectbox('How much of the food that you eat is organic?', list(food_options.keys())[0:4])
    food2 = st.selectbox('How much meat/dairy do you eat personally?', list(food_options.keys())[4:9])
    food3 = st.selectbox('How much of your food is produced locally?', list(food_options.keys())[9:13])
    food4 = st.selectbox('How much of your food is packaged or processed?', list(food_options.keys())[13:17])
    food5 = st.selectbox('How much do you compost potato peelings, leftover and unused food etc?', list(food_options.keys())[17:])

    organic = food_options.get(food1, 0)
    meat = food_options.get(food2, 0)
    foodmiles = food_options.get(food3, 0)
    package = food_options.get(food4, 0)
    composting = food_options.get(food5, 0)

    total_diet = (organic + meat + foodmiles + package + composting)
    cursor.execute('INSERT INTO carbon_footprint (Diet_and_Food_Choices) VALUES (?)', (total_diet,))
    conn.commit()
    st.title('Your Carbon Footprint is' + " " + str(round(total_diet, 4)) + " " + "Tonnes")


def collect_food_data(conn, cursor):
    st.subheader("Enter Data")
    
    with st.form(key='food_form'):
        food_options = {
            'Organic-None': 0.7, 'Organic-Some': 0.5, 'Organic-Most': 0.2,
            'Organic All': 0, 'Meat-Above-average': 0.6, 'Meat-Average': 0.4,
            'Meat-Below-average': 0.25, 'Lacto-vegetarian': 0.1, 'Vegan': 0,
            'Local-Very-little': 0.5, 'Local-Average': 0.3, 'Local-Above-average': 0.2,
            'Local-Almost-all': 0.1, 'Packaging-Above-average': 0.6, 'Packaging-Average': 0.4,
            'Packaging-Below average': 0.2, 'Packaging-Very little': 0.05,
            'Composting-None': 0.2, 'Composting-Some': 0.1, 'Composting-All': 0
        }

        food1 = st.selectbox('How much of the food that you eat is organic?', list(food_options.keys())[0:4])
        food2 = st.selectbox('How much meat/dairy do you eat personally?', list(food_options.keys())[4:9])
        food3 = st.selectbox('How much of your food is produced locally?', list(food_options.keys())[9:13])
        food4 = st.selectbox('How much of your food is packaged or processed?', list(food_options.keys())[13:17])
        food5 = st.selectbox('How much do you compost potato peelings, leftover and unused food etc?', list(food_options.keys())[17:])

        submitted = st.form_submit_button('Calculate Food Carbon Footprint')
        
        if submitted:
            # Calculate and store the food carbon footprint
            organic = food_options.get(food1, 0)
            meat = food_options.get(food2, 0)
            foodmiles = food_options.get(food3, 0)
            package = food_options.get(food4, 0)
            composting = food_options.get(food5, 0)
            total_food_footprint = organic + meat + foodmiles + package + composting
            st.session_state.total_food_footprint = total_food_footprint
            
            if 'pk' in st.session_state and st.session_state.pk is not None:
                # Update existing record with primary key
                cursor.execute('''
                    UPDATE carbon_footprint
                    SET Diet_and_Food_Choices = ?
                    WHERE id = ?
                ''', (total_food_footprint, st.session_state.pk))
            else:
                # Insert the calculated value into the database
                cursor.execute('INSERT INTO carbon_footprint (Diet_and_Food_Choices) VALUES (?)', (total_food_footprint,))
                # Store the primary key in session state
                st.session_state.pk = cursor.lastrowid
            
            conn.commit()
            
            # Display the calculated carbon footprint
            st.title('Your Food Carbon Footprint is' + " " + str(round(total_food_footprint, 4)) + " " + "Tonnes")
def collect_waste_management_data(conn, cursor):
    global noofmembers
    st.subheader("Enter Data")
    
    with st.form(key='waste_management_form'):
        plastic_waste = st.number_input("How many kilograms of plastic waste do you dispose per month?")
        paper_waste = st.number_input("How many kilograms of paper waste do you dispose per month?")
        glass_waste = st.number_input("How many kilograms of glass waste do you dispose per month?")
        metal_waste = st.number_input("How many kilograms of metal waste do you dispose per month?")
        organic_waste = st.number_input("How many kilograms of organic waste (e.g., food scraps) do you dispose per month?")
        
        submitted = st.form_submit_button('Calculate Waste Management Carbon Footprint')
        
        if submitted:
            # Carbon conversion equivalents (sample values in kgCO2/kg of waste)
            carbon_equivalents = {
                "Plastic": 6.0,
                "Paper": 1.0,
                "Glass": 0.6,
                "Metal": 2.5,
                "Organic": 0.2,
            }

            # Calculate carbon footprint based on waste disposal
            total_carbon_footprint = 0
            for waste_type, waste_amount in zip(carbon_equivalents.keys(),
                                                [plastic_waste, paper_waste, glass_waste, metal_waste, organic_waste]):
                if waste_amount > 0:
                    carbon_equivalent = carbon_equivalents.get(waste_type, 0)
                    carbon_footprint = (waste_amount * carbon_equivalent)
                    total_carbon_footprint += carbon_footprint
            st.session_state.total_waste_footprint = total_carbon_footprint
                    
            if 'pk' in st.session_state and st.session_state.pk is not None:
                # Update existing record with primary key
                cursor.execute('''
                    UPDATE carbon_footprint
                    SET Waste_Management = ?
                    WHERE id = ?
                ''', (total_carbon_footprint, st.session_state.pk))
            else:
                # Insert the calculated value into the database
                cursor.execute('INSERT INTO carbon_footprint (Waste_Management) VALUES (?)', (total_carbon_footprint,))
                # Store the primary key in session state
                st.session_state.pk = cursor.lastrowid
            
            conn.commit()
            final_total = (st.session_state.total_waste_footprint+
                           st.session_state.total_food_footprint+
                           st.session_state.total_transportation_footprint+
                           st.session_state.total_electricity_footprint)
            st.session_state.total_carbon_footprint = final_total
            cursor.execute('''
                    UPDATE carbon_footprint
                    SET Estimated_Carbon_Footprint = ?
                    WHERE id = ?
                ''', (st.session_state.total_carbon_footprint, st.session_state.pk))
            st.success("Data has been recorded!")
            # Display the estimated carbon footprint
            st.subheader("Estimated Carbon Footprint from Waste")
            st.write(
                f"Your estimated carbon footprint from waste disposal is approximately {total_carbon_footprint:.2f} Metric tonnes CO2e "
                f"per monthly.")


def estimate_carbon_footprint_from_waste(conn, cursor):
    global total_carbon_footprint
    st.title("Estimate Data")

    # Questions about waste disposal
    st.subheader("Waste Disposal Habits")
    plastic_waste = st.number_input("How many kilograms of plastic waste do you dispose per month?")
    paper_waste = st.number_input("How many kilograms of paper waste do you dispose of per month?")
    glass_waste = st.number_input("How many kilograms of glass waste do you dispose of per month?")
    metal_waste = st.number_input("How many kilograms of metal waste do you dispose of per month?")
    organic_waste = st.number_input(
        "How many kilograms of organic waste (e.g., food scraps) do you dispose of per month?")

    # Carbon conversion equivalents (sample values in kgCO2/kg of waste)
    carbon_equivalents = {
        "Plastic": 6.0,
        "Paper": 1.0,
        "Glass": 0.6,
        "Metal": 2.5,
        "Organic": 0.2,
    }

    # Calculate carbon footprint based on waste disposal
    total_carbon_footprint = 0
    for waste_type, waste_amount in zip(carbon_equivalents.keys(),
                                        [plastic_waste, paper_waste, glass_waste, metal_waste, organic_waste]):
        if waste_amount > 0:
            carbon_equivalent = carbon_equivalents.get(waste_type, 0)
            carbon_footprint = (waste_amount * carbon_equivalent)
            total_carbon_footprint += carbon_footprint
        cursor.execute('INSERT INTO carbon_footprint (Waste_Management) VALUES (?)', (total_carbon_footprint,))
        conn.commit()

        # Display the estimated carbon footprint
    st.subheader("Estimated Carbon Footprint from Waste")
    st.write(
        f"Your estimated carbon footprint from waste disposal is approximately {total_carbon_footprint:.2f} Metric tonnes CO2e "
        f"per month.")


def pico(conn, cursor):
    global total, total1, total_diet, total_carbon_footprint
    st.title("Calculator")
    if st.button("Calculate"):
        # Calculate the total carbon footprint
        total_carbon_footprint = total + total1 + total_diet

        # Insert the total carbon footprint into the database
        cursor.execute('INSERT INTO carbon_footprint (Estimated_Carbon_Footprint) VALUES (?)', (total_carbon_footprint,))
        conn.commit()
        st.success("Data has been recorded!")

        # Display the doughnut chart for the most recent carbon footprint values
        cursor.execute('SELECT * FROM carbon_footprint ORDER BY ID DESC LIMIT 1')  # Select the most recent row
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=['ID', 'Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
                                             'Diet_and_Food_Choices', 'Waste_Management', 'Estimated_Carbon_Footprint'])
            st.title("Carbon Footprint Breakdown for the Most Recent Entry")

            # Exclude the 'ID' column
            df = df.drop(columns=['ID'])

            # Get the carbon footprint values for the selected variables
            selected_variables = ['Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
                                  'Diet_and_Food_Choices', 'Waste_Management']
            total_footprint = df.loc[0, selected_variables]

            # Plot a doughnut chart for the carbon footprint breakdown
            plt.figure(figsize=(6, 6))
            plt.title("Carbon Footprint Breakdown")
            plt.pie(total_footprint.values, labels=total_footprint.index, autopct='%1.1f%%', startangle=140,
                    colors=sns.color_palette("Set3"))
            # Draw a circle at the center to make it a doughnut chart
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            plt.axis('equal')
            st.pyplot(plt)
        else:
            st.warning("No data available to plot the doughnut chart.")
    close_db_connection(conn)



def display_carbon_footprint_breakdown(conn, cursor):
    cursor.execute('''
    SELECT 
        ID,
        Electricity_and_Energy_Consumption,
        Transportation_and_Commuting,
        Diet_and_Food_Choices,
        Waste_Management,
        Estimated_Carbon_Footprint
    FROM carbon_footprint
    ORDER BY ID DESC
    LIMIT 1
''')
    data = cursor.fetchall()
    
    if data:
        df = pd.DataFrame(data, columns=['ID', 'Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
                                         'Diet_and_Food_Choices', 'Waste_Management', 'Estimated_Carbon_Footprint'])
        st.title("Carbon Footprint Breakdown for the Most Recent Entry")

        # Exclude the 'ID' column
        df = df.drop(columns=['ID'])

        # Get the carbon footprint values for the selected variables
        selected_variables = ['Electricity_and_Energy_Consumption', 'Transportation_and_Commuting',
                              'Diet_and_Food_Choices', 'Waste_Management']
        total_footprint = df.loc[0, selected_variables]

        # Plot a doughnut chart for the carbon footprint breakdown
        plt.figure(figsize=(6, 6))
        plt.title("Carbon Footprint Breakdown")
        plt.pie(total_footprint.values, 
                labels=[i.replace("_", " ") for i in total_footprint.index], 
                autopct='%1.1f%%', 
                startangle=140,
                colors=sns.color_palette("Set3"))
        # Draw a circle at the center to make it a doughnut chart
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.axis('equal')
        st.pyplot(plt)
    else:
        st.warning("No data available to plot the doughnut chart.")

def predict_total_carbon_footprint(conn, cursor, id):

    if id is None: st.error("You need to enter your data before footprint can be estimated")
    else:
        input_data = get_data_by_id(conn, cursor, id)
        print(input_data)

        if input_data.all():
            prediction = predict_carbon_footprint(input_data)
            st.header('Based on your input, your predicted carbon footprint is ' + " " + str(round(prediction[0], 4)) + " " + "Metric tonnes CO2")
        else: st.error("You need to enter your data before footprint can be estimated")
    

def main():
    # Apply the custom CSS
    st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    st.title("Carbon Footprint Calculator")

    conn, cursor = create_db_connection()

    # Call the check_and_retrain_model function to check and retrain if necessary
    check_and_retrain_model(conn, cursor)

    st.sidebar.header("Category")
    option = st.sidebar.selectbox("Select a category:", ["Household", "Public Transport", "Food", "Waste Management"])

    if option == "Household":
        st.header("Household Carbon Footprint")
        collect_household_data(conn, cursor)
    elif option == "Public Transport":
        st.header("Public Transport")
        collect_public_transport_data(conn, cursor)
    elif option == "Food":
        st.header("Food Carbon Footprint")
        collect_food_data(conn, cursor)
    elif option == "Waste Management":
        st.header("Waste Management Carbon Footprint")
        collect_waste_management_data(conn, cursor)

    if st.sidebar.button("Carbon Footprint Breakdown"):

        display_carbon_footprint_breakdown(conn, cursor)

    if st.sidebar.button("Predict total Carbon Footprint"):
        print(f"Session state: {st.session_state.pk}")
        predict_total_carbon_footprint(conn, cursor, st.session_state.pk)

    close_db_connection(conn)

if __name__ == "__main__":
    main()




