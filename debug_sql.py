#!/usr/bin/env python3

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner

# Test the complete flow
url = 'http://testphp.vulnweb.com/artists.php?artist=1'
crawler = WebCrawler(url)
pages = crawler.crawl()

print(f'Crawled {len(pages)} pages')
for page in pages:
    print(f'Page URL: {page["url"]}')
    print(f'Page params: {page.get("params", {})}')
    print(f'Forms: {len(page.get("forms", []))}')
    
    # Test SQL injection on this page
    scanner = SQLInjectionScanner()
    if 'params' in page and page['params']:
        vulns = scanner.scan_url_parameters(page['url'], page['params'])
        print(f'SQL vulns found: {len(vulns)}')
        for vuln in vulns:
            print(f'  - {vuln["type"]} in {vuln["parameter"]}')
    else:
        print('No parameters to test')
    print('---')
