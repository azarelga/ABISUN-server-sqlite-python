from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SensorData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            accel_x REAL,
            accel_y REAL,
            accel_z REAL,
            force REAL
        )
    """)
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data(accel_x, accel_y, accel_z, force):
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO SensorData (accel_x, accel_y, accel_z, force)
        VALUES (?, ?, ?, ?)
    """,
        (accel_x, accel_y, accel_z, force),
    )
    conn.commit()
    conn.close()


@app.route("/post-data", methods=["POST"])
def post_data():
    data = request.json
    accel_x = data.get("accel_x")
    accel_y = data.get("accel_y")
    accel_z = data.get("accel_z")
    force = data.get("force")
    insert_data(accel_x, accel_y, accel_z, force)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
