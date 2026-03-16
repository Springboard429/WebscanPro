#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test SQL injection detection manually
url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"
crawler = WebCrawler(url, username='admin', password='password')

print("Crawling and scanning...")
pages = crawler.crawl()

if pages:
    page = pages[0]  # SQL injection page
    print(f"\nTesting page: {page['url']}")
    print(f"Parameters: {page['params']}")
    print(f"Forms: {len(page.get('forms', []))}")
    
    # Test SQL injection manually
    scanner = SQLInjectionScanner()
    
    # Test URL parameters
    if 'params' in page and page['params']:
        print("\n=== Testing URL Parameters ===")
        vulns = scanner.scan_url_parameters(page['url'], page['params'])
        print(f"Found {len(vulns)} SQL injection vulnerabilities in URL parameters")
        for vuln in vulns:
            print(f"  - {vuln}")
    
    # Test forms
    if 'forms' in page:
        print("\n=== Testing Forms ===")
        vulns = scanner.scan_forms(page['forms'])
        print(f"Found {len(vulns)} SQL injection vulnerabilities in forms")
        for vuln in vulns:
            print(f"  - {vuln}")
            
else:
    print("No pages found!")
