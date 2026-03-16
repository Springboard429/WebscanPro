#!/usr/bin/env python3

import requests

# Test what DVWA actually returns
url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"

try:
    response = requests.get(url, timeout=10, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
    print(f"Content-Length: {len(response.text)}")
    print("\nFirst 500 characters of response:")
    print(response.text[:500])
    
    # Check for login redirect
    if response.status_code == 302:
        print(f"\nRedirect Location: {response.headers.get('location', 'N/A')}")
    
    # Check for login form in content
    if 'login' in response.text.lower() or 'password' in response.text.lower():
        print("\n❌ DETECTED: Login page content - DVWA requires authentication!")
    elif 'sql injection' in response.text.lower():
        print("\n✅ DETECTED: SQL injection page content - Authentication bypassed!")
    else:
        print("\n❓ UNKNOWN: Unexpected content type")
        
except Exception as e:
    print(f"Error: {e}")
