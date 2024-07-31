from flask import Flask, request, jsonify
from zeroconf import Zeroconf, ServiceInfo
import sqlite3
import socket
from datetime import datetime
import time

app = Flask(__name__)
last_request_time = None

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

YOUR_LOCAL_IP = get_local_ip()
YOUR_LOCAL_HOST = "abisun-server"   

# Advertise the service
zeroconf = Zeroconf()
info = ServiceInfo(
    "_http._tcp.local.",
    f"{YOUR_LOCAL_HOST}._http._tcp.local.",
    addresses=[socket.inet_aton(YOUR_LOCAL_IP)],
    port=5000,
    properties={},
    server=f"{YOUR_LOCAL_HOST}.local."
)
zeroconf.register_service(info)


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("../data/sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SensorData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now','localtime')),
            depth REAL
        )
    """)
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data(depth):
    conn = sqlite3.connect("../data/sensor_data.db")
    cursor = conn.cursor()
    cursor.execute( 
        """
        INSERT INTO SensorData (depth)
        VALUES (?)
        """,
        (depth,),
    )
    conn.commit()
    conn.close()


@app.route("/post-data", methods=["POST"])
def post_data():
    global last_request_time
    data = request.json
    depth = data.get("Kedalaman")
    last_request_time = time.time()
    insert_data(depth)
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
    app.run(host="0.0.0.0", port=5000)
