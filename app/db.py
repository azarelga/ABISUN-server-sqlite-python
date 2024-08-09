import sqlite3
from datetime import datetime, timedelta
import os
import pandas as pd

def read_df():
    try:
        conn = sqlite3.connect("../data/sensor_data.db")
        query = "SELECT * FROM SensorData"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()

def read_df_60_seconds(start):
    try:
        conn = sqlite3.connect("../data/sensor_data.db")
        query = f"""
        SELECT * FROM SensorData
        WHERE timestamp > "{start}"
        ORDER BY timestamp ASC
        """
        df = pd.read_sql_query(query, conn)
        print(df)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()

def has_recent_entry(seconds=10):
    try:
        conn = sqlite3.connect("../data/sensor_data.db")
        cursor = conn.cursor()

        # Calculate the timestamp 10 seconds ago
        ten_seconds_ago = datetime.now() - timedelta(seconds=seconds)
        ten_seconds_ago_str = ten_seconds_ago.strftime('%Y-%m-%d %H:%M:%S')

        # Query to check if there are any entries in the last 10 seconds
        query = f"SELECT EXISTS(SELECT 1 FROM SensorData WHERE timestamp > ?)"
        cursor.execute(query, (ten_seconds_ago_str,))
        result = cursor.fetchone()[0]

        conn.close()
        return bool(result)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False

def latest_data():
    try:
        conn = sqlite3.connect("../data/sensor_data.db")
        query = "SELECT * FROM Sensordata ORDER BY timestamp DESC LIMIT 1;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()

def read_data():
    try:
        conn = sqlite3.connect("../data/sensor_data.db")
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
