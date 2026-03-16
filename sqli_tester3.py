import os
import json
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from openai import OpenAI
import dotenv
from bs4 import BeautifulSoup

dotenv.load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------

API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.1-8b-instant"

INPUT_FILE = "urls_and_forms.json"
OUTPUT_FILE = "vulnerabilities.json"

LOGIN_URL = "http://localhost:8080/login.php"
USERNAME = "admin"
PASSWORD = "password"

session = requests.Session()

# -----------------------------
# LOAD URLS
# -----------------------------

def load_data():
    with open(INPUT_FILE, "r") as f:
        return json.load(f)

# -----------------------------
# DVWA LOGIN
# -----------------------------

def login_dvwa():

    print(" Logging into DVWA")

    r = session.get(LOGIN_URL)

    soup = BeautifulSoup(r.text, "html.parser")

    token = soup.find("input", {"name": "user_token"})

    if token:
        token = token.get("value")
    else:
        print(" Login token not found")
        return

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login",
        "user_token": token
    }

    session.post(LOGIN_URL, data=data)

    print("[+] Login successful")

# -----------------------------
# GENERATE SQL PAYLOADS
# -----------------------------

def generate_payloads():

    prompt = """
Generate 20 SQL injection payloads.

Return ONLY a JSON list.

Example:
["' OR 1=1--","' OR '1'='1","' UNION SELECT NULL--"]
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        payloads = json.loads(text)
    except:
        payloads = [p.strip() for p in text.split("\n") if p.strip()]

    # Ensure only 20 payloads
    payloads = payloads[:20]

    return payloads

# -----------------------------
# SQL INJECTION DETECTION
# -----------------------------

def is_sqli(response):

    text = response.text.lower()

    # Normal SQL Injection (DVWA SQLi lab)
    if text.count("first name:") > 1:
        return True

    # Blind SQL Injection (DVWA Blind SQLi lab)
    if "user id exists in the database" in text:
        return True

    # SQL error based detection
    errors = [
        "sql syntax",
        "mysql_fetch",
        "syntax error",
        "warning: mysql",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]

    for error in errors:
        if error in text:
            return True

    return False

# -----------------------------
# TEST URL PARAMETERS
# -----------------------------

def test_url_params(url, payloads):

    vulnerabilities = []

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if not params:
        return vulnerabilities

    for param in params:

        for payload in payloads:

            new_params = params.copy()

            # parse_qs requires list values
            new_params[param] = [payload]

            new_query = urlencode(new_params, doseq=True)

            new_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))

            try:

                r = session.get(new_url, timeout=10)

                if is_sqli(r):

                    print("\n[!] SQLi detected")
                    print("URL:", new_url)
                    print("Payload:", payload)

                    vulnerabilities.append({
                        "url": new_url,
                        "payload": payload
                    })

            except:
                continue

    return vulnerabilities

# -----------------------------
# MAIN
# -----------------------------

def main():

    print("\n Logging into DVWA")
    login_dvwa()

    print("\n Loading targets")

    data = load_data()

    urls = data.get("urls", [])

    print("[+] URLs found:", len(urls))

    print("\n Generating SQL payloads using LLM")

    payloads = generate_payloads()

    print(" Payloads generated:", len(payloads))

    vulnerabilities = []

    print("\n Testing URL parameters")

    for url in urls:

        vulns = test_url_params(url, payloads)

        vulnerabilities.extend(vulns)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\n Scan completed")
    print(" Vulnerabilities detected:", len(vulnerabilities))
    print(" Results saved to", OUTPUT_FILE)

if __name__ == "__main__":
    main()
