#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test SQL injection detection on DVWA SQLi page
url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"
crawler = WebCrawler(url, username='admin', password='password')

print("Testing DVWA SQL injection page...")
pages = crawler.crawl()

if pages:
    page = pages[0]
    print(f"\nPage URL: {page['url']}")
    print(f"Parameters: {page.get('params', {})}")
    print(f"Forms: {len(page.get('forms', []))}")
    
    # Test SQL injection manually
    scanner = SQLInjectionScanner()
    
    # Test URL parameters
    if 'params' in page and page['params']:
        print("\n=== Testing URL Parameters ===")
        params = page['params']
        print(f"Parameters to test: {params}")
        
        # Test a few payloads manually
        test_payloads = ["'", "' OR '1'='1", "1' UNION SELECT null--"]
        
        for payload in test_payloads:
            print(f"\n--- Testing payload: {payload} ---")
            test_params = params.copy()
            test_params['id'] = payload
            
            # Use the crawler's authenticated session
            response = crawler.session.get(url, params=test_params)
            print(f"Status: {response.status_code}")
            print(f"URL: {response.url}")
            
            # Check for SQL errors
            content = response.text.lower()
            sql_errors = [
                "sql syntax", "mysql_fetch", "mysql_num_rows", 
                "ora-", "microsoft ole db", "odbc drivers error",
                "postgresql", "sqlite", "you have an error in your sql syntax"
            ]
            
            found_error = False
            for error in sql_errors:
                if error in content:
                    print(f"✅ FOUND SQL ERROR: {error}")
                    found_error = True
                    break
            
            if not found_error:
                # Check if content changed (DVWA doesn't show errors in low security)
                original_response = crawler.session.get(url, params=params)
                content_length_diff = abs(len(response.text) - len(original_response.text))
                if content_length_diff > 50:
                    print(f"✅ CONTENT CHANGED: {content_length_diff} chars difference (likely vulnerable)")
                else:
                    print("No SQL error or content change detected")
else:
    print("No pages found!")
