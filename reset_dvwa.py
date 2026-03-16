#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Reset DVWA database
print("🔧 Resetting DVWA Database...")
print("="*60)

session = requests.Session()

# Get setup page
response = session.get("http://localhost:45/setup.php")
print(f"Setup page status: {response.status_code}")

if 'Create / Reset Database' in response.text:
    print("✅ Found database setup button")
    
    soup = BeautifulSoup(response.text, 'html')
    user_token = soup.find('input', {'name': 'user_token'})
    token_value = user_token.get('value', '') if user_token else ''
    print(f"CSRF Token: {token_value}")
    
    # Reset database
    setup_data = {
        'create_db': 'Create / Reset Database',
        'user_token': token_value
    }
    
    print("🔄 Resetting database...")
    response = session.post("http://localhost:45/setup.php", data=setup_data)
    print(f"Setup response status: {response.status_code}")
    print(f"Setup response URL: {response.url}")
    
    if 'login.php' in response.text.lower() or 'successfully' in response.text.lower():
        print("✅ Database reset successful!")
        
        # Now test authentication with default credentials
        print("\n🔑 Testing authentication with default credentials...")
        
        # Get new login page
        response = session.get("http://localhost:45/login.php")
        soup = BeautifulSoup(response.text, 'html')
        user_token = soup.find('input', {'name': 'user_token'})
        token_value = user_token.get('value', '') if user_token else ''
        
        # Try default DVWA credentials
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
                print("✅ SQL injection page accessible!")
                print("🎯 DVWA is now ready for scanning!")
                
                # Test with WebScanPro
                print("\n🚀 Testing WebScanPro...")
                import subprocess
                import sys
                
                cmd = [
                    'python', 'main.py',
                    '--url', 'http://localhost:45/',
                    '--username', 'admin',
                    '--password', 'password',
                    '--scan-type', 'sqli',
                    '--crawl-depth', '1',
                    '--no-external-apis'
                ]
                
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if 'Found' in result.stdout and 'vulnerabilities' in result.stdout:
                    print("✅ WebScanPro found vulnerabilities!")
                    # Extract vulnerability count
                    for line in result.stdout.split('\n'):
                        if 'Found' in line and 'vulnerabilities' in line:
                            print(f"📊 {line.strip()}")
                else:
                    print("❌ WebScanPro still having issues")
            else:
                print("❌ SQL injection page not accessible")
        else:
            print("❌ Authentication still failed")
    else:
        print("❌ Database reset may have failed")
        print("📄 Response preview:")
        print(response.text[:500])
else:
    print("❌ DVWA setup page not showing database creation option")

print("\n🎯 DVWA setup complete!")
