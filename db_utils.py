import sqlite3
import pandas as pd


def read_data():
    try:
        conn = sqlite3.connect("sensor_data.db")
        query = "SELECT * FROM SensorData"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()
