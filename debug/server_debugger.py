import requests
import time
import json
import random

temp = "http://10.21.95.104:5000/post-data"
url = "http://abisun-server.local:5000/post-data"  # Replace with your Flask server's IP and port

while True:
    depth = random.uniform(4.0, 5.0)
    data = {"Kedalaman": depth}
    response = requests.post(temp, json=data)
    print(f"Response status: {response.status_code}, Response data: {response.json()}")
    time.sleep(1)
