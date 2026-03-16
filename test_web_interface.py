#!/usr/bin/env python3

import requests
import json

# Test the web interface scan endpoint with DVWA authentication
url = "http://localhost:5000/scan"

# Test 1: http://localhost:45/
print("=== Testing http://localhost:45/ ===")
data1 = {
    "url": "http://localhost:45/",
    "scan_type": "sqli",
    "username": "admin",
    "password": "password"
}

try:
    response = requests.post(url, json=data1, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result.get('status')}")
        print(f"Vulnerabilities: {len(result.get('vulnerabilities', []))}")
        if result.get('vulnerabilities'):
            for vuln in result['vulnerabilities'][:2]:  # Show first 2
                print(f"  - {vuln.get('type', 'Unknown')}: {vuln.get('url', 'N/A')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

print("\n" + "="*50 + "\n")

# Test 2: http://localhost:45/index.php
print("=== Testing http://localhost:45/index.php ===")
data2 = {
    "url": "http://localhost:45/index.php",
    "scan_type": "sqli",
    "username": "admin",
    "password": "password"
}

try:
    response = requests.post(url, json=data2, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result.get('status')}")
        print(f"Vulnerabilities: {len(result.get('vulnerabilities', []))}")
        if result.get('vulnerabilities'):
            for vuln in result['vulnerabilities'][:2]:  # Show first 2
                print(f"  - {vuln.get('type', 'Unknown')}: {vuln.get('url', 'N/A')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
