import requests
import time
import json
import random

url = 'http://abisun-server.local:5000/post-data'  # Replace with your Flask server's IP and port

while True:
    mma = random.uniform(0.0, 1200.0)
    fsr = random.uniform(0.0, 4095.0)
    depth = random.uniform(6.0, 12.0)
    data = {
        "Percepatan": mma,
        "Tekanan": fsr,
        "Kedalaman": depth
    }
    response = requests.post(url, json=data)
    print(f"Response status: {response.status_code}, Response data: {response.json()}")
    time.sleep(1)  # Wait for 1 second before the next request
