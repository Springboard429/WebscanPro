#!/usr/bin/env python3

import sys
sys.path.append('.')

from core.scan_controller import ScanController
import time

# Test with limited scope to avoid hanging
print("🔍 Testing Scan Controller with Limited Scope...")
print("="*60)

url = "http://testphp.vulnweb.com/artists.php?artist=1"
scan_type = "sqli"
crawl_depth = 1  # Limit crawl depth

print(f"🎯 URL: {url}")
print(f"🎯 Scan Type: {scan_type}")
print(f"🎯 Crawl Depth: {crawl_depth}")

start_time = time.time()

try:
    # Create scan controller
    scanner = ScanController(
        target_url=url,
        scan_id="debug_test",
        crawl_depth=crawl_depth
    )
    
    print("✅ Scan Controller created")
    
    # Start scan with timeout
    print("🚀 Starting scan...")
    results = scanner.start_scan()
    
    end_time = time.time()
    scan_duration = end_time - start_time
    
    print(f"\n📊 RESULTS:")
    print(f"   Scan Duration: {scan_duration:.2f} seconds")
    print(f"   Vulnerabilities Found: {len(results.get('vulnerabilities', []))}")
    
    # Show first few vulnerabilities
    vulns = results.get('vulnerabilities', [])
    for i, vuln in enumerate(vulns[:3]):
        print(f"   {i+1}. {vuln.get('type', 'Unknown')} in {vuln.get('parameter', 'unknown')} - {vuln.get('url', 'N/A')}")
    
    print(f"\n✅ Scan completed successfully!")
    
except Exception as e:
    end_time = time.time()
    scan_duration = end_time - start_time
    print(f"\n❌ Scan failed after {scan_duration:.2f} seconds")
    print(f"   Error: {str(e)}")
    import traceback
    traceback.print_exc()
