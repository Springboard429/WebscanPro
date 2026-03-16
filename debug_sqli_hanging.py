#!/usr/bin/env python3
"""
Debug SQL Injection hanging issue
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.scan_controller import ScanController
import time

def test_sqli_hanging():
    print("🔍 Testing SQL Injection hanging issue...")
    print("=" * 50)
    
    target_url = "http://testphp.vulnweb.com/artists.php?artist=1"
    print(f"🎯 Target URL: {target_url}")
    
    try:
        # Create scan controller with minimal settings
        scanner = ScanController(
            target_url=target_url,
            scan_id="debug_sqli_hanging",
            crawl_depth=1  # Minimal crawling
        )
        
        print("1️⃣ Starting scan...")
        start_time = time.time()
        
        # Run the scan with timeout
        result = scanner.start_scan()
        
        end_time = time.time()
        print(f"⏱️ Scan completed in {end_time - start_time:.2f} seconds")
        
        print(f"📊 Results:")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Vulnerabilities found: {len(result.get('vulnerabilities', []))}")
        
        # Show first few vulnerabilities
        vulns = result.get('vulnerabilities', [])
        for i, vuln in enumerate(vulns[:5]):
            print(f"   {i+1}. {vuln.get('type', 'Unknown')} - {vuln.get('url', 'N/A')}")
        
        if len(vulns) > 5:
            print(f"   ... and {len(vulns) - 5} more")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sqli_hanging()
