#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test SQL injection detection with the new parameter addition
url = "http://localhost:45/index.php"
crawler = WebCrawler(url, username='admin', password='password')

print("Testing SQL injection detection with new parameter handling...")
pages = crawler.crawl()

print(f"\nFound {len(pages)} pages")

# Find SQL injection pages and test them
for i, page in enumerate(pages):
    if 'sqli' in page['url']:
        print(f"\n=== SQL Injection Page {i+1}: {page['url']} ===")
        print(f"Parameters: {page.get('params', {})}")
        
        if page.get('params'):
            # Test SQL injection
            scanner = SQLInjectionScanner()
            vulns = scanner.scan_url_parameters(page['url'], page['params'], session=crawler.session)
            print(f"SQL Injection Vulnerabilities Found: {len(vulns)}")
            
            for vuln in vulns:
                print(f"  ✅ {vuln['type']} - {vuln['parameter']} - {vuln['payload']}")
                print(f"     URL: {vuln['url']}")
        else:
            print("  ❌ No parameters found!")
