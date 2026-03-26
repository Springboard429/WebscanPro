import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()


# ---------------- LOAD PAYLOADS ----------------
def load_payloads(file_path="xss_payloads.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("xss_payloads.txt not found")
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


# ---------------- XSS DETECTION ----------------
def is_xss_vulnerable(response_text, payload):
    return payload in response_text


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

        for input_field in form["inputs"]:

            if input_field["type"] not in ["text", "hidden", "password", "textarea"]:
                continue

            name = input_field["name"]

            if not name:
                continue

            for payload in payloads:

                data = {}

                for inp in form["inputs"]:
                    data[inp["name"]] = inp.get("value", "")

                data[name] = payload

                try:

                    if method.lower() == "post":
                        response = session.post(action, data=data)
                    else:
                        response = session.get(action, params=data)

                    print(f"Testing payload: {payload[:30]}...")

                    if is_xss_vulnerable(response.text, payload):

                        vuln = {
                            "url": url,
                            "form_action": action,
                            "method": method,
                            "vulnerable_input": name,
                            "payload": payload,
                            "error_detected": "Payload reflected in HTML response",
                            "remediation": "Use context-aware output encoding (e.g. htmlspecialchars() in PHP)."
                        }

                        vulnerabilities.append(vuln)

                        print(f"[!] Vulnerable: {name} with payload {payload}")

                        break   

                except Exception as e:
                    print("Error:", e)

    with open("xss_vulnerabilities.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\nScan complete. Results saved to xss_vulnerabilities.json")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    login()
    test_forms()