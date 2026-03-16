import requests
import time

# Trigger scan and wait a bit
url = "http://localhost:5000/scan"
data = {
    "url": "http://localhost:45/",
    "scan_type": "sqli", 
    "username": "admin",
    "password": "password"
}

print("Triggering scan...")
response = requests.post(url, json=data, timeout=90)
print("Response received:")
print(response.text)

# Wait a bit to see logs
time.sleep(2)
