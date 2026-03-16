#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.crawler import WebCrawler

# Test what the crawler extracts from DVWA SQL injection page
url = "http://localhost:45/vulnerabilities/sqli/?id=1&Submit=Submit#"
crawler = WebCrawler(url, username='admin', password='password')

print("Crawling DVWA SQL injection page...")
pages = crawler.crawl()

print(f"\nFound {len(pages)} pages:")
for i, page in enumerate(pages):
    print(f"\nPage {i+1}:")
    print(f"  URL: {page['url']}")
    print(f"  Params: {page.get('params', {})}")
    print(f"  Forms: {len(page.get('forms', []))}")
    
    for j, form in enumerate(page.get('forms', [])):
        print(f"    Form {j+1}:")
        print(f"      Action: {form.get('action', 'N/A')}")
        print(f"      Method: {form.get('method', 'N/A')}")
        print(f"      Inputs: {len(form.get('inputs', []))}")
        
        for k, inp in enumerate(form.get('inputs', [])):
            print(f"        Input {k+1}: {inp.get('name', 'N/A')} ({inp.get('type', 'N/A')})")
