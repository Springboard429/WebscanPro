#!/usr/bin/env python3

import requests
import json

# Test the web interface scan endpoint with DVWA authentication
url = "http://localhost:5000/scan"

# Test with detailed error output
data = {
    "url": "http://localhost:45/",
    "scan_type": "sqli",
    "username": "admin",
    "password": "password"
}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print(f"\nParsed JSON:")
        print(f"  Status: {result.get('status')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Vulnerabilities: {len(result.get('vulnerabilities', []))}")
    else:
        print("Response is not JSON")
        
except Exception as e:
    print(f"Request failed: {e}")
