#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test SQL injection detection on crawled pages
url = "http://localhost:45/index.php"
crawler = WebCrawler(url, username='admin', password='password')

print("Testing DVWA crawling and SQL injection detection...")
pages = crawler.crawl()

print(f"\nFound {len(pages)} pages:")

for i, page in enumerate(pages):
    print(f"\n=== Page {i+1}: {page['url']} ===")
    
    # Check if this is the SQL injection page
    if 'sqli' in page['url']:
        print("🎯 SQL INJECTION PAGE FOUND!")
        print(f"Parameters: {page.get('params', {})}")
        print(f"Forms: {len(page.get('forms', []))}")
        
        # Test SQL injection manually on this page
        scanner = SQLInjectionScanner()
        
        # Test URL parameters
        if 'params' in page and page['params']:
            print("\n--- Testing URL Parameters ---")
            params = page['params']
            print(f"Parameters: {params}")
            
            # Test with authenticated session
            vulns = scanner.scan_url_parameters(page['url'], params, session=crawler.session)
            print(f"SQL Injection Vulnerabilities Found: {len(vulns)}")
            
            for vuln in vulns:
                print(f"  ✅ {vuln['type']} - {vuln['parameter']} - {vuln['payload']}")
        
        # Test forms
        if 'forms' in page and page['forms']:
            print("\n--- Testing Forms ---")
            for j, form in enumerate(page['forms']):
                print(f"Form {j+1}: {form.get('url', 'N/A')} - {form.get('method', 'GET')}")
                
            vulns = scanner.scan_forms(page['forms'], session=crawler.session)
            print(f"SQL Injection Form Vulnerabilities Found: {len(vulns)}")
            
            for vuln in vulns:
                print(f"  ✅ {vuln['type']} - {vuln['parameter']} - {vuln['payload']}")
    else:
        print(f"Other page - Parameters: {len(page.get('params', {}))}, Forms: {len(page.get('forms', []))}")
