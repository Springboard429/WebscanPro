import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

def run_command(command, description):
    """Helper function to run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"[*] STARTING: {description}")
    print(f"[*] COMMAND: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='')
        process.wait()
        
        if process.returncode != 0:
            print(f"\n[-] ERROR: {description} failed with exit code {process.returncode}")
            return False
        return True
    except Exception as e:
        print(f"\n[-] EXCEPTION during {description}: {e}")
        return False

def consolidate_reports():
    """Combines all the individual vulnerability JSONs into one final report."""
    print("\n[*] Consolidating vulnerability reports...")
    final_report = {
        "scan_metadata": {
            "timestamp": datetime.now().isoformat(),
            "scanner": "WebScanPro Automated Pipeline"
        },
        "vulnerabilities": {
            "sql_injection": [],
            "cross_site_scripting": [],
            "access_control_and_idor": []
        },
        "total_vulnerabilities": 0
    }

    try:
        with open('modules/sqli_vulnerabilities.json', 'r') as f:
            final_report["vulnerabilities"]["sql_injection"] = json.load(f)
    except FileNotFoundError:
        print("[-] SQLi report not found. Skipping.")

    try:
        with open('modules/xss_vulnerabilities.json', 'r') as f:
            final_report["vulnerabilities"]["cross_site_scripting"] = json.load(f)
    except FileNotFoundError:
        print("[-] XSS report not found. Skipping.")

    try:
        with open('modules/access_control_vulnerabilities.json', 'r') as f:
            final_report["vulnerabilities"]["access_control_and_idor"] = json.load(f)
    except FileNotFoundError:
        print("[-] Access Control report not found. Skipping.")

    total = (len(final_report["vulnerabilities"]["sql_injection"]) +
             len(final_report["vulnerabilities"]["cross_site_scripting"]) +
             len(final_report["vulnerabilities"]["access_control_and_idor"]))
    
    final_report["total_vulnerabilities"] = total

    with open('final_report.json', 'w') as f:
        json.dump(final_report, f, indent=4)
        
    print(f"[+] Consolidated report saved to 'final_report.json'")
    print(f"[+] Total Vulnerabilities Found: {total}")

def main():
    parser = argparse.ArgumentParser(description='WebScanPro - Automated Web Vulnerability Scanner')
    parser.add_argument('--url', required=True, help='Target Base URL (e.g., http://localhost)')
    parser.add_argument('--login-url', required=True, help='Target Login URL (e.g., http://localhost/login.php)')
    
    args = parser.parse_args()
    
    crawler_cmd = [sys.executable, "main.py", "--url", args.url, "--login", "--login-url", args.login_url, "-o", "result.json"]
    if not run_command(crawler_cmd, "Web Crawler & Reconnaissance"):
        print("[-] Crawler failed. Halting pipeline.")
        sys.exit(1)

    sqli_script = os.path.join("modules", "sqli_tester.py")
    sqli_cmd = [sys.executable, sqli_script, args.url, args.login_url, "result.json"]
    run_command(sqli_cmd, "SQL Injection Testing")

    xss_script = os.path.join("modules", "xss_tester.py")
    xss_cmd = [sys.executable, xss_script, args.url, args.login_url, "result.json"]
    run_command(xss_cmd, "Cross-Site Scripting (XSS) Testing")

    ac_script = os.path.join("modules", "access_control_tester.py")
    ac_cmd = [sys.executable, ac_script, args.url, args.login_url, "result.json"]
    run_command(ac_cmd, "Access Control & IDOR Testing")

    print(f"\n{'='*60}")
    print("[*] PIPELINE COMPLETE. GENERATING FINAL REPORT.")
    print(f"{'='*60}")
    consolidate_reports()

if __name__ == "__main__":
    main()