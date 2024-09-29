import asyncio
import numpy as np
import sqlite3
from bleak import BleakClient
import struct

# Rest of your code remains the same, including `notification_handler` and `connect_and_read`
# UUIDs for the BLE service and characteristic
SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD".lower()
CHARACTERISTIC_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B".lower()
DATABASE_PATH = "../data/sensor_data.db"

# Buffer to store the depth values for moving average calculation
depth_buffer = []
buffer_max_size = 10  # Assuming 10 readings per second (100ms per reading)


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


def calculate_quantile():
    return np.quantile(depth_buffer, 0.95)


# Function to insert data into the database
def store_depth_value(depth):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SensorData (depth) VALUES (?)", (depth,))
    conn.commit()
    conn.close()


# Callback function for handling notifications
def notification_handler(characteristic, value):
    global depth_buffer
    print(f"Notification received from {characteristic.uuid}: {value}")

    if len(value) <= 8:  # Check if the value length is within acceptable range
        try:
            depth_value = float(
                value.decode()
            )  # Decode the value if it's in string format
            print(f"Received depth value: {depth_value}")

            # Append the value to the buffer
            depth_buffer.append(depth_value)

            # If the buffer is full (i.e., after 1 second of data), calculate the moving average
            if len(depth_buffer) >= buffer_max_size:
                quantile = calculate_quantile()
                print(f"Quantile 95% of last 1 second: {quantile}")

                # Store the depth value in the database
                store_depth_value(quantile)

                # Clear the buffer for the next second
                depth_buffer = []

        except Exception as e:
            print(f"Error processing depth value: {e}")
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
                            await client.start_notify(
                                CHARACTERISTIC_UUID, notification_handler
                            )
                            print(f"Started notifications for {CHARACTERISTIC_UUID}")

                            # Keep the connection open to receive notifications
                            try:
                                while True:
                                    await asyncio.sleep(
                                        1
                                    )  # Adjust sleep time as needed
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
    esp32_address = "93FFAA70-335C-48BA-97B2-8EFAD1946D85".lower()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(connect_and_read(esp32_address))
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        loop.close()
