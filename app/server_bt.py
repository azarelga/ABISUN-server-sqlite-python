import asyncio
import sqlite3
from bleak import BleakClient
import struct

# Rest of your code remains the same, including `notification_handler` and `connect_and_read`
# UUIDs for the BLE service and characteristic
SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD".lower()
CHARACTERISTIC_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B".lower()
DATABASE_PATH = "../data/sensor_data.db"

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
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
def store_depth_value(depth):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SensorData (depth) VALUES (?)", (depth,))
    conn.commit()
    conn.close()

# Callback function for handling notifications
def notification_handler(characteristic, value):
    print(f"Notification received from {characteristic.uuid}: {value}")
    if len(value) <= 8:  # Check if the value length is 4 bytes
        depth_value = float(value)
        print(f"Received depth value: {depth_value}")
        # Store the depth value in the database
        store_depth_value(depth_value)
    else:
        print(f"Unexpected value length: {len(value)} bytes")

async def connect_and_read(address):
    async with BleakClient(address) as client:
        if client.is_connected:
            print(f"Connected to {address}")

            # Check if the characteristic supports notifications
            services = client.services
            for service in services:
                if service.uuid == SERVICE_UUID:
                    print(f"Found service {SERVICE_UUID}")
                    for char in service.characteristics:
                        if char.uuid == CHARACTERISTIC_UUID:
                            print(f"Found characteristic {CHARACTERISTIC_UUID}")

                            # Start notifications
                            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                            print(f"Started notifications for {CHARACTERISTIC_UUID}")

                            # Keep the connection open to receive notifications
                            try:
                                while True:
                                    await asyncio.sleep(1)  # Adjust sleep time as needed
                            except KeyboardInterrupt:
                                print("Stopping notifications.")
                                await client.stop_notify(CHARACTERISTIC_UUID)
                                break
        else:
            print(f"Could not connect to device at {address}")

async def scan_for_device(target_address):
    devices = await BleakScanner.discover()
    for device in devices:
        if device.address == target_address:
            return device
    return None

if __name__ == "__main__":
    # Initialize the database
    init_db()

    # Replace with your ESP32's BLE MAC address
    esp32_address = "93FFAA70-335C-48BA-97B2-8EFAD1946D85"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(connect_and_read(esp32_address))
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        loop.close()
