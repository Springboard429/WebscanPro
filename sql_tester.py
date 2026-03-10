import requests
import json
import sys
import re
from urllib.parse import urljoin

# -----------------------------
# CONFIGURATION
# -----------------------------
SITE_URL = "http://localhost:8080/"
LOGIN_URL = "http://localhost:8080/login.php"


# SQL error signatures
ERROR_SIGNATURES = [
    "sql syntax",
    "warning: mysql",
    "mysql_fetch",
    "syntax error",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "pdoexception",
    "sqlstate"
]


# -----------------------------
# Load payloads
# -----------------------------
def get_payload_list(file_name="payloads.txt"):

    payload_list = []

    try:
        with open(file_name, "r") as file:
            for row in file:

                row = row.strip()

                if row:
                    payload_list.append(row)

    except FileNotFoundError:
        print("payloads.txt not found")
        sys.exit()

    return payload_list


# -----------------------------
# DVWA Login
# -----------------------------
def dvwa_login():

    session = requests.Session()

    try:
        page = session.get(LOGIN_URL)

    except requests.exceptions.RequestException:
        print("Could not connect to DVWA")
        return None

    token = None

    if "user_token" in page.text:

        match = re.search(r"name='user_token' value='(.+?)'", page.text)

        if match:
            token = match.group(1)

    credentials = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token:
        credentials["user_token"] = token

    session.post(LOGIN_URL, data=credentials)

    print("[+] Logged into DVWA")

    return session


# -----------------------------
# Check SQL error
# -----------------------------
def detect_sql_error(html):

    html = html.lower()

    for sig in ERROR_SIGNATURES:

        if sig in html:
            return True

    return False


# -----------------------------
# Scan form
# -----------------------------
def scan_form(form_data, session, payloads):

    found = []

    page_url = form_data.get("page")
    action = form_data.get("action", page_url)

    # make absolute URL
    action = urljoin(SITE_URL, action)

    method = form_data.get("method", "get").lower()
    inputs = form_data.get("inputs", [])

    print("Scanning:", action)

    for payload in payloads:

        data = {}

        for field in inputs:

            name = field.get("name")

            if name:
                data[name] = payload

        try:

            if method == "post":
                res = session.post(action, data=data)

            else:
                res = session.get(action, params=data)

        except requests.exceptions.RequestException:
            continue

        if detect_sql_error(res.text):

            vuln = {
                "url": action,
                "method": method,
                "payload": payload,
                "issue": "Possible SQL Injection",
                "fix": "Use prepared statements / parameterized queries"
            }

            found.append(vuln)

            print("[!] SQL Injection detected with:", payload)

            break

    return found


# -----------------------------
# Main Scanner
# -----------------------------
def run_scanner():

    session = dvwa_login()

    if not session:
        sys.exit()

    payloads = get_payload_list()

    try:
        with open("output.json") as f:
            forms = json.load(f)

    except FileNotFoundError:
        print("output.json not found")
        sys.exit()

    results = []

    print("\n--- SQL Injection Scan Started ---\n")

    for form in forms:

        vulns = scan_form(form, session, payloads)

        results.extend(vulns)

    with open("vulnerabilities.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nScan complete")
    print("Total vulnerabilities:", len(results))
    print("Results saved in vulnerabilities.json")


# Run scanner
run_scanner()