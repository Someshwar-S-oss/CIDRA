from flask import jsonify
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

db_config = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12768292',
    'password': 'IhVE7WC8Xd',
    'database': 'sql12768292',
    'port': '3306'
}

def execute_sql_query(query):
    """Executes the given SQL query and returns the results."""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        # print(rows)
        result_string = "\n".join(
            [", ".join([f"{key}: {value}" for key, value in row.items()]) for row in rows]
        )
        print(result_string)
        return result_string
    except mysql.connector.Error as err:
        print(f"Error executing SQL query: {query} with error: {err}")
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def clear_chat():
    connection = None
    cursor = None
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Truncate the datatable
        cursor.execute("TRUNCATE TABLE datatable;")
        connection.commit()

        return jsonify({"message": "Chat cleared successfully"}), 200
    except mysql.connector.Error as e:
        print(f"Error truncating table: {e}")
        return jsonify({"error": "Failed to clear database table"}), 500
    except Exception as e:
        print(f"Error clearing chat: {e}")
        return jsonify({"error": "Failed to clear chat"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def database_operations(csv_path):
    # Function to create the table if it doesn't exist
    def create_table():
        create_table_query = """
        CREATE TABLE IF NOT EXISTS datatable (
            frame_nmr INT,
            timestamp VARCHAR(255),
            number_plate VARCHAR(255),
            car_model VARCHAR(255)
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

    # Function to fetch data from the database
    def fetch_data_from_db():
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT number_plate FROM datatable")
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Function to update the car model in the database
    def update_car_model_in_db(vehicle_number, car_model):
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE datatable
                SET car_model = %s
                WHERE number_plate = %s
            """, (car_model, vehicle_number))
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error updating database for {vehicle_number}: {err}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Main function to perform web scraping and update the database
    def scrape_and_update():
        data = fetch_data_from_db()
        vehicle_numbers = [item[0] for item in data]

        driver = webdriver.Chrome()  # Or use a different browser driver (e.g., Firefox)

        # Open the website once
        driver.get("https://www.carinfo.app/rc-search")
        time.sleep(1)

        for vehicle_number in vehicle_numbers:
            try:
                # Find the search input field
                search_field = driver.find_element(By.NAME, "vehicleNumber")
                search_field.clear()
                search_field.send_keys(vehicle_number)
                search_field.send_keys(Keys.RETURN)
                time.sleep(1)

                # Extract the vehicle model from the results
                try:
                    model_info = driver.find_element(By.CLASS_NAME, "input_vehical_layout_vehicalModel__1ABTF")
                    car_model = model_info.text
                except:
                    car_model = "Not Found"

                # Update the car model in the database
                update_car_model_in_db(vehicle_number, car_model)

                # Navigate back to the previous page
                driver.back()
                time.sleep(1)

            except Exception as e:
                print(f"Error processing vehicle number {vehicle_number}: {e}")
                update_car_model_in_db(vehicle_number, "Error")

        driver.quit()

    # Call the functions as needed
    create_table()
    upload_csv_to_db(csv_path)
    scrape_and_update()