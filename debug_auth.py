#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler

# Test authentication directly
print("🔍 Testing DVWA Authentication...")

crawler = WebCrawler("http://localhost:45/", username='admin', password='password')

# Test accessing a protected page directly
print("\n📋 Testing direct access to SQL injection page...")
response = crawler.session.get("http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit")
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print(f"Content length: {len(response.text)}")

if 'login.php' in response.url:
    print("❌ Not authenticated - redirected to login")
else:
    print("✅ Authenticated successfully")
    
# Check if we can see the SQL injection form
if 'User ID:' in response.text and 'Submit' in response.text:
    print("✅ SQL injection page content visible")
else:
    print("❌ SQL injection page not accessible")
    
print(f"\n📄 First 500 chars of response:")
print(response.text[:500])
