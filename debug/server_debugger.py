import requests
import time
import json
import random

url = 'http://abisun-server.local:5000/post-data'  # Replace with your Flask server's IP and port

while True:
    depth = random.uniform(0.0, 12.0)
    data = {
        "Kedalaman": depth
    }
    response = requests.post(url, json=data)
    print(f"Response status: {response.status_code}, Response data: {response.json()}")
    time.sleep(0.2)  # Wait for 1 second before the next request
