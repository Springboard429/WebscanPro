#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
import requests

# Debug DVWA authentication
print("🔍 Debugging DVWA Authentication...")
print("="*60)

# Test direct connection to DVWA
print("1️⃣ Testing DVWA connectivity...")
try:
    response = requests.get("http://localhost:45/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    if 'login.php' in response.url:
        print("   ✅ DVWA is running and requires login")
    else:
        print("   ❌ DVWA might not be properly configured")
except Exception as e:
    print(f"   ❌ Cannot connect to DVWA: {str(e)}")
    exit(1)

# Test authentication with WebCrawler
print("\n2️⃣ Testing WebCrawler authentication...")
try:
    crawler = WebCrawler("http://localhost:45/", username='admin', password='password')
    
    # Check if authentication worked by accessing a protected page
    response = crawler.session.get("http://localhost:45/index.php")
    print(f"   Index page status: {response.status_code}")
    print(f"   Index page URL: {response.url}")
    
    if 'login.php' in response.url:
        print("   ❌ Authentication failed - still redirected to login")
    else:
        print("   ✅ Authentication successful")
        
    # Try accessing SQL injection page directly
    response = crawler.session.get("http://localhost:45/vulnerabilities/sqli/")
    print(f"   SQLi page status: {response.status_code}")
    print(f"   SQLi page URL: {response.url}")
    
    if 'login.php' in response.url:
        print("   ❌ Cannot access SQLi page - session lost")
    else:
        print("   ✅ SQLi page accessible")
        
except Exception as e:
    print(f"   ❌ Authentication error: {str(e)}")

# Test manual authentication
print("\n3️⃣ Testing manual authentication...")
session = requests.Session()

# Get login page
try:
    response = session.get("http://localhost:45/login.php")
    print(f"   Login page status: {response.status_code}")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html')
    user_token = soup.find('input', {'name': 'user_token'})
    token_value = user_token.get('value', '') if user_token else ''
    print(f"   CSRF token: {token_value}")
    
    # Try login
    login_data = {
        'username': 'admin',
        'password': 'password',
        'Login': 'Login',
        'user_token': token_value
    }
    
    response = session.post("http://localhost:45/login.php", data=login_data)
    print(f"   Login response status: {response.status_code}")
    print(f"   Login response URL: {response.url}")
    
    if 'index.php' in response.url:
        print("   ✅ Manual authentication successful")
        
        # Test SQLi page
        response = session.get("http://localhost:45/vulnerabilities/sqli/")
        if 'User ID:' in response.text:
            print("   ✅ SQLi page accessible with manual auth")
        else:
            print("   ❌ SQLi page not accessible")
    else:
        print("   ❌ Manual authentication failed")
        
        # Check for error messages
        if 'Login failed' in response.text:
            print("   📄 Login failed message found")
        elif 'disabled' in response.text.lower():
            print("   📄 Login might be disabled")
            
except Exception as e:
    print(f"   ❌ Manual authentication error: {str(e)}")

print("\n🎯 Debugging complete!")
