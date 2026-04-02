import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "http://localhost:8080/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

session = requests.Session()
vulnerabilities = []

# -----------------------------
# LOGIN
# -----------------------------
def login():
    res = session.get(LOGIN_URL)
    soup = BeautifulSoup(res.text, "html.parser")

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

    print("[+] Logged in")

# -----------------------------
# LOAD URLS
# -----------------------------
def load_urls():
    with open("urls.json", "r") as f:
        return json.load(f)

# -----------------------------
# BROKEN ACCESS CONTROL
# -----------------------------
def test_broken_access_control(url):
    print(f"\n[+] Testing BAC: {url}")

    temp_session = requests.Session()

    try:
        res = temp_session.get(url, allow_redirects=True)

        if res.status_code == 200 and "login.php" not in res.url:

            print("[!!!] BAC Found")

            vulnerabilities.append({
                "url": url,
                "vulnerability": "Broken Access Control",
                "vulnerable_input": "Direct URL Access",
                "description": "Page is accessible without authentication.",
                "remediation": "Ensure authentication checks before allowing access to protected resources."
            })

    except:
        pass

# -----------------------------
# GET FORMS
# -----------------------------
def get_forms(url):
    try:
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.find_all("form")
    except:
        return []

# -----------------------------
# IDOR TEST (MENTOR FORMAT)
# -----------------------------
def test_idor(url):
    print(f"\n[+] Testing IDOR: {url}")

    forms = get_forms(url)
    id_keywords = ["id", "user", "uid", "account", "profile"]

    for form in forms:
        action = form.get("action")
        method = form.get("method", "get").lower()
        inputs = form.find_all("input")

        for inp in inputs:
            name = inp.get("name")

            if not name:
                continue

            if any(k in name.lower() for k in id_keywords):

                print(f"[+] Testing parameter: {name}")

                responses = []

                for test_id in ["1", "2", "3"]:

                    data = {}

                    for i in inputs:
                        n = i.get("name")
                        if not n:
                            continue

                        if n == name:
                            data[n] = test_id
                        else:
                            data[n] = "test"

                    target = urljoin(url, action)

                    if method == "post":
                        res = session.post(target, data=data)
                    else:
                        res = session.get(target, params=data)

                    responses.append(len(res.text))

                # detection
                if len(set(responses)) > 1:

                    print("[!!!] IDOR Found")

                    vulnerabilities.append({
                        "url": url,
                        "vulnerability": "Insecure Direct Object Reference (IDOR)",
                        "vulnerable_input": name,
                        "description": "Manipulating the ID parameter returns different user data.",
                        "remediation": "Implement proper access control checks to ensure users can only access their own data."
                    })

# -----------------------------
# SAVE
# -----------------------------
def save_results():
    with open("access_control_vulnerabilities.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print(f"\n[+] Saved {len(vulnerabilities)} vulnerabilities")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    urls = load_urls()

    login()

    for url in urls:
        test_broken_access_control(url)
        test_idor(url)

    save_results()