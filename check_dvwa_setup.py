#!/usr/bin/env python3

import sys
sys.path.append('.')

import requests
from bs4 import BeautifulSoup

# Check DVWA setup
print("🔍 Checking DVWA Setup and Login Response...")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Get login page
response = session.get("http://localhost:45/login.php")
soup = BeautifulSoup(response.text, 'html')
user_token = soup.find('input', {'name': 'user_token'})
token_value = user_token.get('value', '') if user_token else ''

print(f"CSRF Token: {token_value}")

# Try login with different credentials
credentials = [
    ('admin', 'password'),
    ('admin', 'admin'),
    ('user', 'password'),
    ('test', 'test'),
    ('', '')
]

for username, password in credentials:
    print(f"\n🔑 Trying credentials: '{username}' / '{password}'")
    
    login_data = {
        'username': username,
        'password': password,
        'Login': 'Login',
        'user_token': token_value
    }
    
    response = session.post("http://localhost:45/login.php", data=login_data)
    print(f"Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    if 'index.php' in response.url:
        print("✅ SUCCESSFUL LOGIN!")
        
        # Test SQL injection page
        response = session.get("http://localhost:45/vulnerabilities/sqli/")
        if 'User ID:' in response.text:
            print("✅ SQL injection page accessible!")
        break
    else:
        print("❌ Login failed")
        
        # Check for error messages
        if 'Login failed' in response.text or 'incorrect' in response.text.lower():
            print("   Error message found in response")
        elif 'login.php' in response.url:
            print("   Redirected back to login")

# Check if DVWA is properly set up
print(f"\n🏗️  Checking DVWA setup page...")
response = session.get("http://localhost:45/setup.php")
if 'Create / Reset Database' in response.text:
    print("✅ DVWA setup page accessible - may need to create database")
else:
    print("❌ DVWA setup not accessible")
