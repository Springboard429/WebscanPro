#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Quick check and fix for DVWA
print("🔍 Quick DVWA Status Check...")
print("="*50)

try:
    # Check if DVWA is running
    response = requests.get("http://localhost:45/", timeout=5)
    print(f"✅ DVWA Status: {response.status_code}")
    
    if 'login.php' in response.url:
        print("✅ DVWA requires login")
        
        # Try to login
        session = requests.Session()
        response = session.get("http://localhost:45/login.php")
        soup = BeautifulSoup(response.text, 'html')
        user_token = soup.find('input', {'name': 'user_token'})
        token_value = user_token.get('value', '') if user_token else ''
        
        login_data = {
            'username': 'admin',
            'password': 'password',
            'Login': 'Login',
            'user_token': token_value
        }
        
        response = session.post("http://localhost:45/login.php", data=login_data)
        
        if 'index.php' in response.url:
            print("✅ Login successful!")
            
            # Check if we can access SQLi page
            response = session.get("http://localhost:45/vulnerabilities/sqli/")
            if 'User ID:' in response.text:
                print("✅ SQLi page accessible!")
                print("🎯 DVWA is ready for scanning!")
            else:
                print("❌ SQLi page not accessible")
                print("🔧 DVWA might need database reset")
        else:
            print("❌ Login failed")
            print("🔧 Need to reset DVWA database")
    else:
        print("❌ DVWA not responding correctly")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("🔧 DVWA might not be running")

print("\n🎯 Check complete!")
