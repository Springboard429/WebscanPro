#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test SQL injection detection manually
url = "http://localhost:45/vulnerabilities/sqli"
crawler = WebCrawler(url, username='admin', password='password')

print("Testing SQL injection detection manually...")
crawler.crawl()  # Just to authenticate

# Test parameters
params = {'id': '1', 'Submit': 'Submit'}
scanner = SQLInjectionScanner()

print(f"\nTesting URL: {url}")
print(f"Parameters: {params}")

# Test each payload manually
payloads = ["'", "' OR '1'='1", "1' UNION SELECT null--"]

for payload in payloads:
    print(f"\n--- Testing payload: {payload} ---")
    test_params = params.copy()
    test_params['id'] = payload
    
    # Use authenticated session
    response = crawler.session.get(url, params=test_params)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    # Check if redirected to login
    if 'login.php' in response.url:
        print("❌ Redirected to login - session lost!")
    else:
        print("✅ Session maintained")
        
        # Check content
        content_length = len(response.text)
        print(f"Content length: {content_length}")
        
        # Look for SQL errors
        content_lower = response.text.lower()
        sql_errors = ["sql syntax", "mysql_fetch", "mysql_num_rows", "ora-", "you have an error in your sql syntax"]
        
        found_error = False
        for error in sql_errors:
            if error in content_lower:
                print(f"✅ SQL ERROR FOUND: {error}")
                found_error = True
                break
        
        if not found_error:
            # Check for content changes
            original_response = crawler.session.get(url, params=params)
            diff = abs(len(response.text) - len(original_response.text))
            if diff > 50:
                print(f"✅ CONTENT CHANGED: {diff} chars (likely vulnerable)")
            else:
                print("No obvious vulnerability indicators")
