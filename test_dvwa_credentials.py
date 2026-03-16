#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Check DVWA login page and try different credentials
print("🔍 Testing Different DVWA Credentials...")
print("="*60)

session = requests.Session()

# Get login page and CSRF token
response = session.get("http://localhost:45/login.php")
soup = BeautifulSoup(response.text, 'html')
user_token = soup.find('input', {'name': 'user_token'})
token_value = user_token.get('value', '') if user_token else ''

print(f"CSRF Token: {token_value}")

# Test different credential combinations
credentials = [
    ('admin', 'password'),
    ('admin', 'admin'),
    ('user', 'password'),
    ('test', 'test'),
    ('dvwa', 'dvwa'),
    ('root', 'toor'),
    ('admin', ''),
    ('', 'password')
]

for username, password in credentials:
    print(f"\n🔑 Testing: '{username}' / '{password}'")
    
    login_data = {
        'username': username,
        'password': password,
        'Login': 'Login',
        'user_token': token_value
    }
    
    response = session.post("http://localhost:45/login.php", data=login_data)
    
    if 'index.php' in response.url:
        print("✅ SUCCESS! Authentication worked!")
        
        # Test SQL injection page
        response = session.get("http://localhost:45/vulnerabilities/sqli/")
        if 'User ID:' in response.text:
            print("✅ SQL injection page accessible!")
            
            # Now test with WebScanPro using these credentials
            print(f"\n🎯 Testing WebScanPro with working credentials...")
            import subprocess
            import sys
            
            cmd = [
                'python', 'main.py',
                '--url', 'http://localhost:45/',
                '--username', username,
                '--password', password,
                '--scan-type', 'sqli',
                '--crawl-depth', '1',
                '--no-external-apis'
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if 'Found' in result.stdout and 'vulnerabilities' in result.stdout:
                print("✅ WebScanPro found vulnerabilities!")
            else:
                print("❌ WebScanPro still having issues")
                
        break
    else:
        print("❌ Failed")

# Check if DVWA needs database reset
print(f"\n🔧 Checking DVWA setup...")
response = requests.get("http://localhost:45/setup.php")
if 'Create / Reset Database' in response.text:
    print("⚠️  DVWA database might need to be reset!")
    print("   Visit: http://localhost:45/setup.php")
else:
    print("✅ DVWA setup page not accessible")

print(f"\n🎯 Debugging complete!")
