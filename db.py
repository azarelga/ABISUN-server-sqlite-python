import sqlite3
import os
import pandas as pd

def read_df():
    try:
        conn = sqlite3.connect("sensor_data.db")
        query = "SELECT * FROM SensorData"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()

def read_df_60_seconds():
    try:
        conn = sqlite3.connect("sensor_data.db")
        query = "SELECT * FROM SensorData ORDER BY timestamp DESC LIMIT 60;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()


def latest_data():
    try:
        conn = sqlite3.connect("sensor_data.db")
        query = "SELECT * FROM Sensordata ORDER BY timestamp DESC LIMIT 1;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()

def read_data():
    try:
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()

        # Execute a query to retrieve data
        cursor.execute("SELECT * FROM SensorData")
        rows = cursor.fetchall()

        # Print the results
        for row in rows:
            print(row)

        conn.close()  # Close the connection
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
