from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import time

app = Flask(__name__)
last_request_time = None

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("../data/sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SensorData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now','localtime')),
            mma_accel REAL,
            fsr REAL,
            depth REAL
        )
    """)
    conn.commit()
    conn.close()


def process_depth(depth, force):
    if force > 3000:
        return depth
    else:
        return 0


# Function to insert data into the database
def insert_data(accel, force, depth):
    conn = sqlite3.connect("../data/sensor_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO SensorData (mma_accel, fsr, depth)
        VALUES (?, ?, ?)
    """,
        (accel, force, depth),
    )
    conn.commit()
    conn.close()


@app.route("/post-data", methods=["POST"])
def post_data():
    global last_request_time
    data = request.json
    accel = data.get("Percepatan")
    force = data.get("Tekanan")
    depth = process_depth(data.get("Kedalaman"),force)
    last_request_time = time.time()
    insert_data(accel, force, depth)
    return jsonify({"status": "success"})

@app.route('/last-request-time', methods=['GET'])
def get_last_request_time():
    global last_request_time
    if last_request_time is not None:
        return jsonify({"last_request_time": last_request_time}), 200
    else:
        return jsonify({"error": "No requests received yet"}), 404


if __name__ == "__main__":
    init_db()
    app.run(host="192.168.77.185", port=5000)
