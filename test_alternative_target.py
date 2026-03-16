#!/usr/bin/env python3
"""
Test scanner with a different target website
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.scan_controller import ScanController
import time

def test_alternative_target():
    print("🔍 Testing scanner with alternative target...")
    print("=" * 50)
    
    # Try with a different test site
    test_urls = [
        "http://httpbin.org/forms/post",  # Test forms
        "https://httpbin.org/get?id=test",  # Test parameters
        "http://example.com",  # Basic test
    ]
    
    for url in test_urls:
        print(f"\n🎯 Testing: {url}")
        try:
            scanner = ScanController(
                target_url=url,
                scan_id="test_alternative",
                crawl_depth=1
            )
            
            start_time = time.time()
            result = scanner.start_scan()
            end_time = time.time()
            
            print(f"⏱️ Time: {end_time - start_time:.2f} seconds")
            print(f"📊 Status: {result.get('status', 'Unknown')}")
            print(f"🔍 Vulnerabilities: {len(result.get('vulnerabilities', []))}")
            
            if result.get('vulnerabilities'):
                print("✅ Found vulnerabilities!")
                break
            else:
                print("❌ No vulnerabilities found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
if __name__ == "__main__":
    test_alternative_target()
