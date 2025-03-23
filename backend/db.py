from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import mysql.connector
import pandas as pd

db_config = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12768292',
    'password': 'IhVE7WC8Xd',
    'database': 'sql12768292',
    'port': '3306'
}

# Function to create the table if it doesn't exist
def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS datatable (
        frame_nmr INT,
        timestamp VARCHAR(255),
        number_plate VARCHAR(255)
    );
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'datatable' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Function to upload CSV data into the database
def upload_csv_to_db(csv_path):
    data = pd.read_csv(csv_path)
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        for _, row in data.iterrows():
            cursor.execute(
                "INSERT INTO datatable (frame_nmr, timestamp, number_plate) VALUES (%s, %s, %s)",
                (row['frame_nmr'], row['timestamp'], row['number_plate'])
            )
        connection.commit()
        print("CSV data inserted into MySQL table successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Execution flow
if __name__ == "__main__":
    csv_path = './ocr_results_with_timestamps.csv'  # Path to your CSV file
    create_table()
    upload_csv_to_db(csv_path)