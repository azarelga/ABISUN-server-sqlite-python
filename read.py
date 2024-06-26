import sqlite3
import time


def read_data():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()

    # Execute a query to retrieve data
    cursor.execute("SELECT * FROM SensorData")
    rows = cursor.fetchall()

    # Print the results
    for row in rows:
        print(row)

    conn.close()  # Close the connection


def main():
    while True:
        read_data()  # Read and display data from the table
        time.sleep(1)  # Wait for 5 seconds before reading again


if __name__ == "__main__":
    main()
