#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Test authenticated access to DVWA SQL injection page
session = requests.Session()

# Login to DVWA
login_url = "http://localhost:45/login.php"
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html')
user_token = soup.find('input', {'name': 'user_token'}).get('value')

login_data = {
    'username': 'admin',
    'password': 'password',
    'Login': 'Login',
    'user_token': user_token
}

response = session.post(login_url, data=login_data)
print(f"Login status: {response.status_code}")
print(f"Login redirected to: {response.url}")

# Now test SQL injection page
sqli_url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"
response = session.get(sqli_url)

print(f"\nSQL injection page status: {response.status_code}")
print(f"URL: {response.url}")

if "sql injection" in response.text.lower():
    print("✅ SUCCESS: Can access SQL injection page!")
    
    # Look for the vulnerability form
    soup = BeautifulSoup(response.text, 'html')
    forms = soup.find_all('form')
    print(f"Found {len(forms)} forms")
    
    for i, form in enumerate(forms):
        action = form.get('action', '')
        method = form.get('method', 'get')
        inputs = form.find_all('input')
        print(f"\nForm {i+1}:")
        print(f"  Action: {action}")
        print(f"  Method: {method}")
        print(f"  Inputs: {len(inputs)}")
        
        for input_tag in inputs:
            name = input_tag.get('name', '')
            input_type = input_tag.get('type', '')
            print(f"    - {name}: {input_type}")
            
else:
    print("❌ FAILED: Cannot access SQL injection page")
    print("First 500 characters of response:")
    print(response.text[:500])
