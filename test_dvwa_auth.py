#!/usr/bin/env python3

import requests

# Test with session cookie (you need to get this from browser after login)
session = requests.Session()

# Add the session cookie you got from browser
# Replace 'your_session_cookie_here' with actual cookie value
session.cookies.set('PHPSESSID', 'your_session_cookie_here', domain='localhost')

url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"

try:
    response = session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if 'sql injection' in response.text.lower():
        print("✅ SUCCESS: Access to SQL injection page!")
        print("Now you can test with WebScanPro using session cookies")
    elif 'login' in response.text.lower():
        print("❌ FAILED: Still redirecting to login")
        print("You need to get the correct session cookie")
    else:
        print("❓ UNKNOWN: Unexpected response")
        
except Exception as e:
    print(f"Error: {e}")
