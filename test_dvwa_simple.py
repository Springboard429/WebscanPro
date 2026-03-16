#!/usr/bin/env python3
"""
Simple DVWA test to verify scanning works
"""
import subprocess
import sys
import os

def test_dvwa_scan():
    print("🔍 Testing DVWA Scan with Simple Command...")
    print("=" * 50)
    
    # Simple command that should work
    cmd = [
        'python', 'main.py',
        '--url', 'http://localhost:45/',
        '--scan-type', 'all',
        '--crawl-depth', '1',
        '--username', 'admin',
        '--password', 'password'
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    print(f"📁 Directory: {os.getcwd()}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"\n📊 Exit Code: {result.returncode}")
        print(f"📝 Output Length: {len(result.stdout)} chars")
        
        # Look for vulnerability indicators
        if "Found" in result.stdout and "vulnerabilities" in result.stdout:
            print("✅ VULNERABILITIES FOUND!")
            # Extract count
            import re
            vuln_match = re.search(r'Found (\d+) vulnerabilities', result.stdout)
            if vuln_match:
                count = vuln_match.group(1)
                print(f"🎯 Count: {count} vulnerabilities")
        else:
            print("❌ No vulnerabilities found in output")
            
        # Show last few lines of output
        lines = result.stdout.strip().split('\n')
        print(f"\n📋 Last 10 lines of output:")
        for line in lines[-10:]:
            print(f"   {line}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Scan timed out")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_dvwa_scan()
