import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import dotenv
from datetime import datetime

dotenv.load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://localhost:8080"
LOGIN_URL = BASE_URL + "/login.php"

USERNAME = "admin"
PASSWORD = "password"

OUTPUT_FILE = "xss_vulnerabilities.json"
MARKER = "XSS123"

session = requests.Session()

# -----------------------------
# LLM CLIENT (GROQ)
# -----------------------------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

# -----------------------------
# LOGIN
# -----------------------------
def login():
    print("[+] Logging in...")

    r = session.get(LOGIN_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    token = token.get("value") if token else ""

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login",
        "user_token": token
    }

    session.post(LOGIN_URL, data=data)
    print("[+] Logged in")

# -----------------------------
# GENERATE PAYLOADS
# -----------------------------
def generate_payloads():
    print("[+] Generating payloads...")

    prompt = f"""
Generate 5 simple XSS payloads.
Each must trigger alert('{MARKER}').
Return only Python list.
"""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        payloads = eval(res.choices[0].message.content.strip())
        return payloads

    except:
        print("[!] Using fallback payloads")
        return [
            f"<script>alert('{MARKER}')</script>",
            f"<img src=x onerror=alert('{MARKER}')>"
        ]

# -----------------------------
# VALIDATE XSS USING LLM
# -----------------------------
def confirm_xss(response_text, payload):
    snippet = response_text[:1000]

    prompt = f"""
If payload appears unescaped in HTML, return YES.
Otherwise return NO.

Payload: {payload}
Response: {snippet}
"""

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return "YES" in res.choices[0].message.content.upper()

    except:
        return False

# -----------------------------
# TEST FORMS
# -----------------------------
def test_forms(url, payloads):
    vulns = []

    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    forms = soup.find_all("form")

    for form in forms:
        action = form.get("action")
        method = form.get("method", "get").lower()

        target = url if not action else urljoin(url, action)
        inputs = form.find_all("input")

        for payload in payloads:
            data = {}

            for inp in inputs:
                name = inp.get("name")
                value = inp.get("value", "")

                if name:
                    if inp.get("type") == "hidden":
                        data[name] = value
                    else:
                        data[name] = payload

            print("[TEST]", target, payload)

            # Submit form
            if method == "post":
                res = session.post(target, data=data)
            else:
                res = session.get(target, params=data)

            # Reflected XSS
            if MARKER in res.text:
                if confirm_xss(res.text, payload):
                    vulns.append({
                        "type": "Reflected XSS",
                        "url": target,
                        "payload": payload,
                        "severity": "High",
                        "time": datetime.now().isoformat()
                    })

            # Stored XSS
            check = session.get(url)
            if MARKER in check.text:
                if confirm_xss(check.text, payload):
                    vulns.append({
                        "type": "Stored XSS",
                        "url": url,
                        "payload": payload,
                        "severity": "High",
                        "time": datetime.now().isoformat()
                    })

    return vulns

# -----------------------------
# SAVE RESULTS (APPEND)
# -----------------------------
def save_results(new_vulns):

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                existing = json.load(f)
            except:
                existing = []
    else:
        existing = []

    # Avoid duplicates
    for vuln in new_vulns:
        if vuln not in existing:
            existing.append(vuln)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(existing, f, indent=4)

# -----------------------------
# MAIN
# -----------------------------
def main():
    login()

    urls = [
        BASE_URL + "/vulnerabilities/xss_r/",
        BASE_URL + "/vulnerabilities/xss_s/"
    ]

    payloads = generate_payloads()
    all_vulns = []

    for url in urls:
        print("\n[*] Testing:", url)
        all_vulns.extend(test_forms(url, payloads))

    save_results(all_vulns)

    print("\n[+] Scan Completed")
    print("[+] Found:", len(all_vulns))
    print("[+] Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
