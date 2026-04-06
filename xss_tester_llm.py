import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()


# ---------------- GENERATE PAYLOADS ----------------
def generate_payloads():

    print("[+] Generating XSS payloads using Ollama...")

    prompt = """
Generate 10 valid XSS payloads.
Return ONLY payloads line by line.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5",
                "prompt": prompt,
                "stream": False
            }
        )

        text = response.json()["response"]

        payloads = [
            p.strip() for p in text.split("\n") if p.strip()
        ]

        # ✅ FILTER ONLY VALID PAYLOADS
        payloads = [
            p for p in payloads
            if "<script" in p or "onerror" in p or "onload" in p or "javascript:" in p
        ]

        return payloads

    except Exception as e:
        print("⚠️ Ollama failed, using default payloads")

        return [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>"
        ]

# ---------------- LOGIN ----------------
def login():

    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token_value = token["value"] if token else None

    data = {
        "username": "admin",
        "password": "password",
        "Login": "Login"
    }

    if token_value:
        data["user_token"] = token_value

    session.post(LOGIN_URL, data=data)

    session.cookies.set("security", "low")

    print("[+] Logged in & security LOW")


# ---------------- LOAD FORMS ----------------
def load_forms():

    with open("forms.json", "r") as f:
        return json.load(f)


# ---------------- XSS DETECTION ----------------
def is_vulnerable(response_text, payload):

    return payload.lower() in response_text.lower()


# ---------------- TEST FORMS ----------------
def test_forms():

    forms = load_forms()
    payloads = generate_payloads()

    vulnerabilities = []

    for form in forms:

        url = form["page"]

        # 🔥 ONLY XSS TARGETS
        if not any(x in url for x in ["xss_r", "xss_s", "csp"]):
            continue

        action = url   # override (IMPORTANT)
        method = form["method"]

        print(f"\nTesting: {url}")

        for payload in payloads:

            for input_field in form["inputs"]:

                name = input_field.get("name")

                if not name:
                    continue

                data = {}

                # safe build
                for inp in form["inputs"]:
                    if inp.get("name"):
                        data[inp["name"]] = "test"

                data[name] = payload

                try:

                    if method == "post":
                        response = session.post(action, data=data)
                    else:
                        response = session.get(action, params=data)

                    if is_vulnerable(response.text, payload):

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

                        print(f"[!] XSS FOUND → {name}")

                        break

                except:
                    pass

    with open("xss_vulnerabilities_llm.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\n[+] Scan complete")


# ---------------- MAIN ----------------
if __name__ == "__main__":

    login()
    test_forms()