import requests
import json
from urllib.parse import urljoin
import re
import os   # ✅ ADD THIS

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def generate_xss_payloads():
    prompt = """
    Generate 10 different XSS payloads.
    Each payload should be on a new line.
    Avoid explanations.
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    payloads = response.choices[0].message.content.strip().split("\n")
    return payloads

def login_dvwa(session, base_url):
    login_url = base_url + "/login.php"

    # Step 1: Get login page
    response = session.get(login_url)

    # Step 2: Extract CSRF token
    token_match = re.search(r"user_token' value='(.+?)'", response.text)

    if not token_match:
        print("[-] CSRF token not found")
        return False

    user_token = token_match.group(1)

    # Step 3: Send login request with token
    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token
    }

    response = session.post(login_url, data=login_data)

    # Step 4: Verify login
    if "Login failed" in response.text:
        print("[-] Login failed")
        return False

    print("[+] Login successful")

    # Step 5: Set security LOW (also needs token sometimes)
    security_url = base_url + "/security.php"

    response = session.get(security_url)
    token_match = re.search(r"user_token' value='(.+?)'", response.text)

    if token_match:
        security_token = token_match.group(1)

        security_data = {
            "security": "low",
            "seclev_submit": "Submit",
            "user_token": security_token
        }

        session.post(security_url, data=security_data)

    print("[+] Security level set to LOW")

    return True

# -------------------------
# LOAD PAYLOADS
# -------------------------
def load_payloads(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


# -------------------------
# TEST XSS FORMS
# -------------------------
def test_form_xss(url, form, session, payloads):
    vulnerabilities = []

    action = url
    method = form.get("method", "get").lower()

    for payload in payloads:
        print(f"Testing payload: {payload}")

        data = {}

    for input_field in form.get("inputs", []):
        name = input_field.get("name")
        input_type = input_field.get("type", "text")

        if not name:
            continue

        if input_type in ["text", "textarea"]:
            data[name] = payload
        else:
            data[name] = input_field.get("value", "")   

        # Send request
        if method == "post":
            session.post(action, data=data)

    # 🔥 IMPORTANT: fetch page again
            response = session.get(url)

        else:
            response = session.get(action, params=data)

        print(response.text[:300])

        # 🔥 PUT YOUR NEW DETECTION HERE
        if payload in response.text or any(x in response.text.lower() for x in ["<script", "onerror", "onload"]):
            print(f"[!] Possible XSS at {url}")

            vulnerabilities.append({
                "url": url,
                "form_action": action,
                "method": method,
                "vulnerable_input": list(data.keys()),
                "payload": payload,
                "evidence": "Reflected or stored payload detected",
                "severity": "High"
            })

    return vulnerabilities


# -------------------------
# MAIN FUNCTION
# -------------------------
import requests

def main():
    base_url = "http://localhost"

    session = requests.Session()

    if not login_dvwa(session, base_url):
        return

    if not session:
        return

    # Load files
    with open("urls_and_forms.json") as f:
        urls_data = json.load(f)

    payloads = load_payloads("xss_payloads.txt")

    all_vulnerabilities = []

    # Loop through URLs
    for url, forms in urls_data.items():

        # Only test XSS pages
        if "xss" not in url:
            continue

        print(f"\n[+] Testing URL: {url}")

        for form in forms:
            vulns = test_form_xss(url, form, session, payloads)
            all_vulnerabilities.extend(vulns)

    # Save results
    with open("xss_vulnerabilities.json", "w") as f:
        json.dump(all_vulnerabilities, f, indent=4)

    print(f"\n[+] Testing complete. Found {len(all_vulnerabilities)} vulnerabilities.")
    print("[+] Results saved to xss_vulnerabilities.json")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    main()

def load_payloads(file_path):
    with open(file_path, "r") as f:
        payloads = [line.strip() for line in f if line.strip()]
    return payloads

payloads = load_payloads("payload.txt")

print("[+] Loaded Payloads:")
for p in payloads:
    print(p)