#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Setup DVWA with CSRF token
print("🔧 DVWA Database Setup with CSRF Token...")

session = requests.Session()

# Get setup page and CSRF token
response = session.get("http://localhost:45/setup.php")
soup = BeautifulSoup(response.text, 'html')

# Extract CSRF token
user_token = soup.find('input', {'name': 'user_token'})
token_value = user_token.get('value', '') if user_token else ''
print(f"CSRF Token: {token_value}")

# Try setup with CSRF token
setup_data = {
    'create_db': 'Create / Reset Database',
    'user_token': token_value
}

print("🎯 Submitting setup with CSRF token...")
response = session.post("http://localhost:45/setup.php", data=setup_data)
print(f"Setup status: {response.status_code}")
print(f"Setup URL: {response.url}")

# Check if setup worked
if 'login.php' in response.text.lower() or 'successfully' in response.text.lower():
    print("✅ Database setup successful!")
    
    # Now test authentication
    print("\n🔑 Testing authentication after setup...")
    
    # Get login page
    response = session.get("http://localhost:45/login.php")
    soup = BeautifulSoup(response.text, 'html')
    user_token = soup.find('input', {'name': 'user_token'})
    token_value = user_token.get('value', '') if user_token else ''
    
    # Try login
    login_data = {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login',
        'user_token': token_value
    }
    
    response = session.post("http://localhost:45/login.php", data=login_data)
    print(f"Login status: {response.status_code}")
    print(f"Login URL: {response.url}")
    
    if 'index.php' in response.url:
        print("✅ Authentication successful!")
        
        # Test SQL injection page
        response = session.get("http://localhost:45/vulnerabilities/sqli/")
        if 'User ID:' in response.text:
            print("✅ SQL injection page accessible - DVWA is ready!")
        else:
            print("❌ SQL injection page not accessible")
    else:
        print("❌ Authentication still failed")
else:
    print("❌ Database setup may have failed")
    print("📄 Response preview:")
    print(response.text[:500])
