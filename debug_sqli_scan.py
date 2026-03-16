#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner
import time

# Debug the SQL injection scanning process
print("🔍 Debugging SQL Injection Scan Process...")
print("="*60)

# Test URL
url = "http://testphp.vulnweb.com/artists.php?artist=1"
print(f"🎯 Target URL: {url}")

# Step 1: Test crawling
print("\n1️⃣ Testing WebCrawler...")
crawler = WebCrawler(url)
pages = crawler.crawl()
print(f"✅ Crawled {len(pages)} pages")

for i, page in enumerate(pages[:3]):  # Show first 3 pages
    print(f"   Page {i+1}: {page['url']}")
    print(f"      Params: {page.get('params', {})}")
    print(f"      Forms: {len(page.get('forms', []))}")

# Step 2: Test SQL injection scanner directly
print("\n2️⃣ Testing SQL Injection Scanner...")
scanner = SQLInjectionScanner()

total_vulns = []
for page in pages:
    print(f"\n🔍 Scanning page: {page['url']}")
    
    # Test URL parameters
    if 'params' in page and page['params']:
        print(f"   Testing {len(page['params'])} parameters...")
        try:
            vulns = scanner.scan_url_parameters(page['url'], page['params'], crawler=crawler)
            print(f"   Found {len(vulns)} URL parameter vulnerabilities")
            total_vulns.extend(vulns)
        except Exception as e:
            print(f"   ❌ Error in URL parameter scan: {str(e)}")
    
    # Test forms
    if 'forms' in page and page['forms']:
        print(f"   Testing {len(page['forms'])} forms...")
        try:
            vulns = scanner.scan_forms(page['forms'], crawler=crawler)
            print(f"   Found {len(vulns)} form vulnerabilities")
            total_vulns.extend(vulns)
        except Exception as e:
            print(f"   ❌ Error in form scan: {str(e)}")
    
    # Limit to first few pages for debugging
    if len(total_vulns) > 5 or len(pages) > 3:
        break

print(f"\n📊 RESULTS:")
print(f"   Total vulnerabilities found: {len(total_vulns)}")
for vuln in total_vulns[:3]:  # Show first 3
    print(f"   - {vuln.get('type', 'Unknown')} in {vuln.get('parameter', 'unknown')}")

print(f"\n🎯 Debugging complete!")
