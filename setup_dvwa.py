#!/usr/bin/env python3

import requests

# Check DVWA setup and try to create database
print("🔧 Setting up DVWA Database...")

session = requests.Session()

# Get setup page
response = session.get("http://localhost:45/setup.php")
print(f"Setup page status: {response.status_code}")

if 'Create / Reset Database' in response.text:
    print("✅ Found database setup button")
    
    # Try to create database
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html')
    
    # Look for the create/reset button form
    create_button = soup.find('input', {'name': 'create_db'})
    
    if create_button:
        print("🔧 Attempting to create database...")
        
        # Submit the form to create database
        setup_data = {
            'create_db': 'Create / Reset Database'
        }
        
        response = session.post("http://localhost:45/setup.php", data=setup_data)
        print(f"Setup response status: {response.status_code}")
        print(f"Setup response URL: {response.url}")
        
        if 'Login' in response.text or 'login.php' in response.url:
            print("✅ Database created successfully!")
            print("🎯 DVWA should now be ready for authentication")
        else:
            print("❌ Database creation may have failed")
            print("📄 Response preview:")
            print(response.text[:500])
    else:
        print("❌ Could not find create database button")
else:
    print("❌ DVWA setup page not showing database creation option")
    print("📄 Page content preview:")
    print(response.text[:500])
