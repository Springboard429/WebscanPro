import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()


# ---------------- LOAD PAYLOADS ----------------
def load_payloads(file_path="payloads.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("payloads.txt not found")
        return []


# ---------------- LOGIN ----------------
def login():

    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token_value = token["value"] if token else None

    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token_value:
        login_data["user_token"] = token_value

    response = session.post(LOGIN_URL, data=login_data)

    if response.status_code == 200:
        print("[+] Login successful")

        session.cookies.set("security", "low")
        print("[+] Security level set to LOW")

    else:
        print("[-] Login failed")
        exit()


# ---------------- SQL ERROR DETECTION ----------------
def is_vulnerable(response_text):

    database_errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "mysql_fetch",
        "syntax error",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]

    for error in database_errors:
        if error in response_text.lower():
            return True

    return False


# ---------------- LOAD FORMS ----------------
def load_forms():
    with open("forms.json", "r") as f:
        return json.load(f)


# ---------------- TEST FORMS ----------------
def test_forms():

    forms = load_forms()
    payloads = load_payloads()

    vulnerabilities = []

    for form in forms:

        url = form["page"]
        action = form["action"]
        method = form["method"]

        if action.endswith("#") or action == BASE_URL:
            action = url

        print(f"\nTesting: {url}")

        for payload in payloads:

            for input_field in form["inputs"]:

                if input_field["type"] not in ["text", "hidden", "password"]:
                    continue

                name = input_field["name"]

                if not name:
                    continue

                data = {}

                for inp in form["inputs"]:
                    data[inp["name"]] = inp.get("value", "")

                data[name] = payload

                try:

                    if method.lower() == "post":
                        response = session.post(action, data=data)
                    else:
                        response = session.get(action, params=data)

                    if is_vulnerable(response.text):

                        vuln = {
                            "url": url,
                            "form_action": action,
                            "method": method,
                            "vulnerable_input": name,
                            "payload": payload,
                            "error_detected": "Database error message found",
                            "remediation": "Use parameterized queries (prepared statements) instead of string concatenation."
                        }

                        vulnerabilities.append(vuln)

                        print(f"[!] Vulnerable: {name} with payload {payload}")

                except Exception as e:
                    print("Error:", e)

    with open("vulnerabilities.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\nScan complete. Results saved to vulnerabilities.json")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    login()
    test_forms()