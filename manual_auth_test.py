#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
import requests

# Manual authentication test
print("🔍 Manual DVWA Authentication Test...")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Step 1: Get login page and CSRF token
print("\n1️⃣ Getting login page...")
response = session.get("http://localhost:45/login.php")
print(f"Status: {response.status_code}")

from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html')
user_token = soup.find('input', {'name': 'user_token'})
token_value = user_token.get('value', '') if user_token else ''
print(f"CSRF Token: {token_value}")

# Step 2: Login
print("\n2️⃣ Attempting login...")
login_data = {
    'username': 'admin',
    'password': 'password',
    'Login': 'Login',
    'user_token': token_value
}

response = session.post("http://localhost:45/login.php", data=login_data)
print(f"Login Status: {response.status_code}")
print(f"Login URL: {response.url}")
print(f"Response length: {len(response.text)}")

# Step 3: Check if we can access protected page
print("\n3️⃣ Testing access to SQL injection page...")
response = session.get("http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit")
print(f"SQLi Page Status: {response.status_code}")
print(f"SQLi Page URL: {response.url}")

if 'login.php' in response.url:
    print("❌ Still redirected to login - authentication failed")
else:
    print("✅ Successfully authenticated!")

# Check content
if 'User ID:' in response.text:
    print("✅ SQL injection form found")
else:
    print("❌ SQL injection form not found")
    
print(f"\n📄 Response preview (first 300 chars):")
print(response.text[:300])
