import asyncio
from bleak import BleakClient, BleakScanner
import struct
import sqlite3

SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD".lower()
CHARACTERISTIC_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B".lower()
DATABASE_PATH = "../data/sensor_data.db"

# Notification handler for receiving data from BLE device
async def notification_handler(characteristic, value):
    print(f"Notification from {characteristic}: {value}")
    if len(value) == 4:  # Assuming 4 bytes represent a float value
        depth_value = struct.unpack("f", value)[0]
        print(f"Depth value: {depth_value}")
    else:
        print(f"Unexpected data length: {len(value)}")

async def connect_and_subscribe(address):
    # Connect to the device
    async with BleakClient(address) as client:
        if client.is_connected:
            print(f"Connected to {address}")

            # Subscribe to notifications for the characteristic
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

            # Keep receiving notifications until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("Stopping notifications...")
                await client.stop_notify(CHARACTERISTIC_UUID)

if __name__ == "__main__":
    # Replace this with your BLE device's MAC address
    esp32_address = "93FFAA70-335C-48BA-97B2-8EFAD1946D85"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(connect_and_subscribe(esp32_address))
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        loop.close()
