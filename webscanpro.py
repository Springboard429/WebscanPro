import os
import sys
import json
import subprocess
import argparse
from datetime import datetime


# -------------------------------
# RUN COMMAND
# -------------------------------
def run_command(command, description):
    print("\n" + "="*60)
    print(f"[+] STARTING: {description}")
    print(f"[+] COMMAND: {' '.join(command)}")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode != 0:
            print(f"\n[-] ERROR: {description} failed")
            return False

        return True

    except Exception as e:
        print(f"\n[-] EXCEPTION during {description}: {e}")
        return False


# -------------------------------
# CONSOLIDATE REPORTS
# -------------------------------
def consolidate_reports():
    print("\n[+] Consolidating vulnerability reports...")

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
        with open("vulnerabilities_llm.json", "r") as f:
            final_report["vulnerabilities"]["sql_injection"] = json.load(f)
    except:
        print("[-] SQL report not found. Skipping.")

    try:
        with open("vulnerabilities_xss.json", "r") as f:
            final_report["vulnerabilities"]["cross_site_scripting"] = json.load(f)
    except:
        print("[-] XSS report not found. Skipping.")

    try:
        with open("access_control_vulnerabilities.json", "r") as f:
            final_report["vulnerabilities"]["access_control_and_idor"] = json.load(f)
    except:
        print("[-] Access Control report not found. Skipping.")

    total = (
        len(final_report["vulnerabilities"]["sql_injection"]) +
        len(final_report["vulnerabilities"]["cross_site_scripting"]) +
        len(final_report["vulnerabilities"]["access_control_and_idor"])
    )

    final_report["total_vulnerabilities"] = total

    with open("final_report.json", "w") as f:
        json.dump(final_report, f, indent=4)

    print("\n[+] Consolidated report saved to 'final_report.json'")
    print(f"[+] Total Vulnerabilities Found: {total}")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="WebScanPro - Automated Web Vulnerability Scanner"
    )

    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--login-url", default="http://localhost:8080/login.php")

    args = parser.parse_args()

    # -------------------------------
    # CRAWLER
    # -------------------------------
    crawler_cmd = [
        sys.executable,
        "crawler.py",
        "--url", args.url,
        "--login", args.login_url,
        "-o", "output.json"
    ]

    if not run_command(crawler_cmd, "Web Crawler & Reconnaissance"):
        print("[-] Crawler failed. Halting pipeline.")
        sys.exit(1)

    # -------------------------------
    # SQL TESTER
    # -------------------------------
    sqli_script ="ai_payload_generator.py"

    sqli_cmd = [
        sys.executable,
        sqli_script,
        args.url,
        args.login_url,
        "output.json"
    ]

    run_command(sqli_cmd, "SQL Injection Testing")

    # -------------------------------
    # XSS TESTER
    # -------------------------------
    xss_script ="xss_ai.py"

    xss_cmd = [
        sys.executable,
        xss_script,
        args.url,
        args.login_url,
        "output.json"
    ]

    run_command(xss_cmd, "Cross-Site Scripting (XSS) Testing")

    # -------------------------------
    # ACCESS CONTROL + IDOR
    # -------------------------------
    ac_script ="access_control.py"

    ac_cmd = [
        sys.executable,
        ac_script,
        args.url,
        args.login_url,
        "output.json"
    ]

    run_command(ac_cmd, "Access Control & IDOR Testing")

    # -------------------------------
    # FINAL REPORT
    # -------------------------------
    print("\n" + "="*60)
    print("[*] PIPELINE COMPLETE. GENERATING FINAL REPORT.")

    consolidate_reports()


# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    main()