#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Test DVWA login manually
session = requests.Session()
login_url = "http://localhost:45/login.php"

# First, get the login page to see the form structure
print("Getting login page...")
response = session.get(login_url)
print(f"Login page status: {response.status_code}")

# Parse the login form
soup = BeautifulSoup(response.text, 'html')
print("\nLogin form analysis:")
for input_tag in soup.find_all('input'):
    name = input_tag.get('name', 'N/A')
    type_attr = input_tag.get('type', 'N/A')
    value = input_tag.get('value', '')
    print(f"  Input: name='{name}', type='{type_attr}', value='{value}'")

# Try different login data variations
login_attempts = [
    {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login'
    },
    {
        'username': 'admin',
        'password': 'password',
        'submit': 'Login'
    },
    {
        'username': 'admin',
        'password': 'password',
        'login': 'Login'
    }
]

for i, login_data in enumerate(login_attempts):
    print(f"\n--- Attempt {i+1} ---")
    print(f"Login data: {login_data}")
    
    response = session.post(login_url, data=login_data)
    print(f"Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Redirected: {response.url != login_url}")
    
    # Check if we're logged in by trying to access a protected page
    test_response = session.get("http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#")
    
    if "sql injection" in test_response.text.lower():
        print("✅ SUCCESS: Authentication worked!")
        break
    elif "login" in test_response.text.lower():
        print("❌ FAILED: Still redirected to login")
    else:
        print("❓ UNKNOWN: Unexpected response")
