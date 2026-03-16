import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE = "http://localhost/"
LOGIN_URL = urljoin(BASE, "login.php")
START_URL = urljoin(BASE, "index.php")

session = requests.Session()


# ---------- LOGIN ----------
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

    res = session.post(LOGIN_URL, data=data)

    if res.status_code != 200:
        print("Login failed")
        exit()

    print("Login success")


# ---------- FETCH URLS ----------
def fetch_urls(base_url):
    res = session.get(base_url)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        full = urljoin(BASE, a["href"])

        if full.startswith(BASE):
            links.append(full)

    return links


# ---------- EXTRACT FORMS ----------
def extract_forms(url):
    forms_data = []

    res = session.get(url)   # SAME SESSION
    soup = BeautifulSoup(res.text, "html.parser")

    for form in soup.find_all("form"):

        action = urljoin(BASE, form.get("action"))

        # ignore login form
        if action.endswith("login.php"):
            continue

        form_info = {
            "page": url,
            "action": action,
            "method": form.get("method", "get").lower(),
            "inputs": []
        }

        for inp in form.find_all("input"):
            form_info["inputs"].append({
                "name": inp.get("name"),
                "type": inp.get("type", "text")
            })

        forms_data.append(form_info)

    return forms_data


# ---------- MAIN ----------
login()

urls = fetch_urls(START_URL)

all_forms = []

for u in urls:
    forms = extract_forms(u)
    all_forms.extend(forms)

# ---- remove duplicates ----
unique = []
seen = set()

for f in all_forms:
    key = json.dumps(f, sort_keys=True)
    if key not in seen:
        seen.add(key)
        unique.append(f)

with open("forms.json", "w") as f:
    json.dump(unique, f, indent=4)

print("Forms saved to forms.json")