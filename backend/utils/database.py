from flask import jsonify
import pandas as pd
import mysql.connector 

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
